from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.judge import JudgeAssign
from app.routes.dependencies import get_current_user, require_role

router = APIRouter(prefix="/judges", tags=["Judges"])


@router.get("/assignments")
def list_all_assignments(
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT ja.id, ja.judge_id, ja.team_id,
        u.name AS judge_name, t.team_name, e.event_name
        FROM JudgeAssignments ja
        JOIN Users u ON ja.judge_id = u.user_id
        JOIN Teams t ON ja.team_id = t.team_id
        JOIN Events e ON t.event_id = e.event_id
        ORDER BY ja.id DESC"""
    )
    return cursor.fetchall()


@router.post("/assign", status_code=201)
def assign_judge(
    data: JudgeAssign,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM Users WHERE user_id = %s AND role = 'judge'",
        (data.judge_id,),
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Judge not found or user is not a judge")

    cursor.execute("SELECT * FROM Teams WHERE team_id = %s", (data.team_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Team not found")

    cursor.execute(
        "SELECT * FROM JudgeAssignments WHERE judge_id = %s AND team_id = %s",
        (data.judge_id, data.team_id),
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Judge already assigned to this team")

    cursor.execute(
        "INSERT INTO JudgeAssignments (judge_id, team_id) VALUES (%s, %s)",
        (data.judge_id, data.team_id),
    )
    db.commit()
    return {"message": "Judge assigned successfully", "id": cursor.lastrowid}


@router.delete("/remove")
def remove_judge(
    data: JudgeAssign,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "DELETE FROM JudgeAssignments WHERE judge_id = %s AND team_id = %s",
        (data.judge_id, data.team_id),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.commit()
    return {"message": "Judge removed from team"}


@router.get("/my-teams")
def get_judge_teams(
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("judge")),
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT t.team_id, t.team_name, e.event_name, e.start_date, e.end_date,
        u.name AS leader_name,
        p.project_id, p.title AS project_title, p.status AS project_status
        FROM JudgeAssignments ja
        JOIN Teams t ON ja.team_id = t.team_id
        JOIN Events e ON t.event_id = e.event_id
        JOIN Users u ON t.leader_id = u.user_id
        LEFT JOIN Projects p ON p.team_id = t.team_id
        WHERE ja.judge_id = %s
        ORDER BY t.team_id""",
        (current_user["user_id"],),
    )
    return cursor.fetchall()
