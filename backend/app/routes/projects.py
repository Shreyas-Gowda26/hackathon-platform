from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.routes.dependencies import get_current_user, require_role
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["Projects"])

PROJECT_SELECT = """
    SELECT p.*, t.team_name, t.event_id, e.event_name
    FROM Projects p
    JOIN Teams t ON p.team_id = t.team_id
    JOIN Events e ON t.event_id = e.event_id
"""


@router.post("/", status_code=201)
def create_project(
    data: ProjectCreate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Teams WHERE team_id = %s", (data.team_id,))
    team = cursor.fetchone()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team["leader_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only team leader can submit project")

    cursor.execute("SELECT * FROM Projects WHERE team_id = %s", (data.team_id,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Team already has a project")

    cursor.execute(
        """INSERT INTO Projects
        (team_id, title, description, repo_link, demo_link, status)
        VALUES (%s, %s, %s, %s, %s, 'draft')""",
        (data.team_id, data.title, data.description, data.repo_link, data.demo_link),
    )
    db.commit()
    return {"message": "Project created", "project_id": cursor.lastrowid}


@router.get("/")
def get_projects(
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    cursor = db.cursor(dictionary=True)
    role = current_user["role"]
    user_id = current_user["user_id"]

    if role == "admin":
        cursor.execute(PROJECT_SELECT + " ORDER BY p.project_id DESC")
    elif role == "participant":
        cursor.execute(
            PROJECT_SELECT
            + """ WHERE p.team_id IN (
                SELECT tm.team_id FROM TeamMembers tm
                WHERE tm.user_id = %s AND tm.status = 'accepted'
            ) ORDER BY p.project_id DESC""",
            (user_id,),
        )
    elif role == "judge":
        cursor.execute(
            PROJECT_SELECT
            + """ WHERE p.status = 'submitted'
            AND t.team_id IN (
                SELECT team_id FROM JudgeAssignments WHERE judge_id = %s
            ) ORDER BY p.project_id DESC""",
            (user_id,),
        )
    elif role == "mentor":
        cursor.execute(
            PROJECT_SELECT
            + """ WHERE t.team_id IN (
                SELECT team_id FROM MentorAssignments WHERE mentor_id = %s
            ) ORDER BY p.project_id DESC""",
            (user_id,),
        )
    else:
        raise HTTPException(status_code=403, detail="Access forbidden")

    return cursor.fetchall()


@router.get("/{project_id}")
def get_project(
    project_id: int,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(PROJECT_SELECT + " WHERE p.project_id = %s", (project_id,))
    project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not _can_view_project(cursor, current_user, project):
        raise HTTPException(status_code=403, detail="You cannot view this project")

    return project


def _can_view_project(cursor, current_user: dict, project: dict) -> bool:
    role = current_user["role"]
    user_id = current_user["user_id"]

    if role == "admin":
        return True

    team_id = project["team_id"]

    if role == "participant":
        cursor.execute(
            """SELECT 1 FROM TeamMembers
            WHERE team_id = %s AND user_id = %s AND status = 'accepted'""",
            (team_id, user_id),
        )
        return cursor.fetchone() is not None

    if role == "judge":
        if project["status"] != "submitted":
            return False
        cursor.execute(
            "SELECT 1 FROM JudgeAssignments WHERE judge_id = %s AND team_id = %s",
            (user_id, team_id),
        )
        return cursor.fetchone() is not None

    if role == "mentor":
        cursor.execute(
            "SELECT 1 FROM MentorAssignments WHERE mentor_id = %s AND team_id = %s",
            (user_id, team_id),
        )
        return cursor.fetchone() is not None

    return False


@router.put("/{project_id}")
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """SELECT p.*, t.leader_id FROM Projects p
        JOIN Teams t ON p.team_id = t.team_id
        WHERE p.project_id = %s""",
        (project_id,),
    )
    project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project["leader_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only team leader can update project")

    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    if fields.get("status") == "submitted":
        fields["submission_time"] = datetime.utcnow()

    query = "UPDATE Projects SET " + ", ".join(f"{k} = %s" for k in fields)
    query += " WHERE project_id = %s"
    cursor.execute(query, (*fields.values(), project_id))
    db.commit()
    return {"message": "Project updated"}


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM Projects WHERE project_id = %s", (project_id,))
    db.commit()
    return {"message": "Project deleted"}
