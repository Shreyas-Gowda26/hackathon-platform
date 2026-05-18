from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.evaluation import EvaluationCreate, EvaluationUpdate
from app.routes.dependencies import get_current_user, require_role

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("/", status_code=201)
def evaluate_project(
    data: EvaluationCreate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("judge"))
):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """SELECT p.*, t.team_id FROM Projects p
        JOIN Teams t ON p.team_id = t.team_id
        WHERE p.project_id = %s""",
        (data.project_id,),
    )
    project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project["status"] != "submitted":
        raise HTTPException(status_code=400, detail="Project must be submitted before evaluation")

    cursor.execute(
        "SELECT * FROM JudgeAssignments WHERE judge_id = %s AND team_id = %s",
        (current_user["user_id"], project["team_id"]),
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=403, detail="You are not assigned to evaluate this team")

    # Validate score range
    if not 0 <= data.score <= 100:
        raise HTTPException(status_code=400, detail="Score must be between 0 and 100")

    try:
        cursor.execute(
            """INSERT INTO Evaluations (judge_id, project_id, score, feedback)
            VALUES (%s, %s, %s, %s)""",
            (current_user["user_id"], data.project_id, data.score, data.feedback)
        )
        db.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="You have already evaluated this project")

    return {"message": "Evaluation submitted", "evaluation_id": cursor.lastrowid}


@router.get("/project/{project_id}")
def get_project_evaluations(
    project_id: int,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "judge"))
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT e.*, u.name as judge_name
        FROM Evaluations e
        JOIN Users u ON e.judge_id = u.user_id
        WHERE e.project_id = %s""",
        (project_id,)
    )
    return cursor.fetchall()


@router.get("/project/{project_id}/average")
def get_average_score(
    project_id: int,
    db: MySQLConnection = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT 
            p.title,
            COUNT(e.evaluation_id) as total_judges,
            ROUND(AVG(e.score), 2) as average_score,
            MAX(e.score) as highest_score,
            MIN(e.score) as lowest_score
        FROM Projects p
        LEFT JOIN Evaluations e ON p.project_id = e.project_id
        WHERE p.project_id = %s
        GROUP BY p.project_id""",
        (project_id,)
    )
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.put("/{evaluation_id}")
def update_evaluation(
    evaluation_id: int,
    data: EvaluationUpdate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("judge"))
):
    cursor = db.cursor(dictionary=True)

    # Judge can only update their own evaluation
    cursor.execute(
        "SELECT * FROM Evaluations WHERE evaluation_id = %s AND judge_id = %s",
        (evaluation_id, current_user["user_id"])
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Evaluation not found")

    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    query = "UPDATE Evaluations SET " + ", ".join(f"{k} = %s" for k in fields)
    query += " WHERE evaluation_id = %s"
    cursor.execute(query, (*fields.values(), evaluation_id))
    db.commit()
    return {"message": "Evaluation updated"}


@router.get("/leaderboard/{event_id}")
def get_leaderboard(
    event_id: int,
    db: MySQLConnection = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT 
            t.team_name,
            p.title as project_title,
            p.repo_link,
            p.demo_link,
            COUNT(e.evaluation_id) as total_judges,
            ROUND(AVG(e.score), 2) as average_score
        FROM Teams t
        JOIN Projects p ON t.team_id = p.team_id
        LEFT JOIN Evaluations e ON p.project_id = e.project_id
        WHERE t.event_id = %s
        GROUP BY p.project_id
        ORDER BY average_score DESC""",
        (event_id,)
    )
    return cursor.fetchall()