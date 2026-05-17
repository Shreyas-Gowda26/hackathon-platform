from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.routes.dependencies import get_current_user, require_role
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", status_code=201)
def create_project(
    data: ProjectCreate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)

    # Check team exists
    cursor.execute("SELECT * FROM Teams WHERE team_id = %s", (data.team_id,))
    team = cursor.fetchone()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Only team leader can submit project
    if team["leader_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only team leader can submit project")

    # Check if project already exists for this team
    cursor.execute("SELECT * FROM Projects WHERE team_id = %s", (data.team_id,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Team already has a project")

    cursor.execute(
        """INSERT INTO Projects 
        (team_id, title, description, repo_link, demo_link, status)
        VALUES (%s, %s, %s, %s, %s, 'draft')""",
        (data.team_id, data.title, data.description,
         data.repo_link, data.demo_link)
    )
    db.commit()
    return {"message": "Project created", "project_id": cursor.lastrowid}


@router.get("/")
def get_all_projects(db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT p.*, t.team_name, e.event_name
        FROM Projects p
        JOIN Teams t ON p.team_id = t.team_id
        JOIN Events e ON t.event_id = e.event_id"""
    )
    return cursor.fetchall()


@router.get("/{project_id}")
def get_project(
    project_id: int,
    db: MySQLConnection = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT p.*, t.team_name, e.event_name
        FROM Projects p
        JOIN Teams t ON p.team_id = t.team_id
        JOIN Events e ON t.event_id = e.event_id
        WHERE p.project_id = %s""",
        (project_id,)
    )
    project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}")
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)

    # Check project exists and user is team leader
    cursor.execute(
        """SELECT p.*, t.leader_id FROM Projects p
        JOIN Teams t ON p.team_id = t.team_id
        WHERE p.project_id = %s""",
        (project_id,)
    )
    project = cursor.fetchone()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project["leader_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Only team leader can update project")

    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    # If submitting, set submission_time
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
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM Projects WHERE project_id = %s", (project_id,))
    db.commit()
    return {"message": "Project deleted"}