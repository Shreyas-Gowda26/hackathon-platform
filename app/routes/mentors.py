from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.mentor import MentorAssign
from app.routes.dependencies import get_current_user, require_role

router = APIRouter(prefix="/mentors", tags=["Mentors"])


@router.post("/assign", status_code=201)
def assign_mentor(
    data: MentorAssign,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)

    # Check mentor exists and has mentor role
    cursor.execute(
        "SELECT * FROM Users WHERE user_id = %s AND role = 'mentor'",
        (data.mentor_id,)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Mentor not found or user is not a mentor")

    # Check team exists
    cursor.execute("SELECT * FROM Teams WHERE team_id = %s", (data.team_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if already assigned
    cursor.execute(
        "SELECT * FROM MentorAssignments WHERE mentor_id = %s AND team_id = %s",
        (data.mentor_id, data.team_id)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Mentor already assigned to this team")

    cursor.execute(
        "INSERT INTO MentorAssignments (mentor_id, team_id) VALUES (%s, %s)",
        (data.mentor_id, data.team_id)
    )
    db.commit()
    return {"message": "Mentor assigned successfully", "id": cursor.lastrowid}


@router.delete("/remove")
def remove_mentor(
    data: MentorAssign,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM MentorAssignments WHERE mentor_id = %s AND team_id = %s",
        (data.mentor_id, data.team_id)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Assignment not found")

    cursor.execute(
        "DELETE FROM MentorAssignments WHERE mentor_id = %s AND team_id = %s",
        (data.mentor_id, data.team_id)
    )
    db.commit()
    return {"message": "Mentor removed from team"}


@router.get("/team/{team_id}")
def get_team_mentors(
    team_id: int,
    db: MySQLConnection = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)

    # Check team exists
    cursor.execute("SELECT * FROM Teams WHERE team_id = %s", (team_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Team not found")

    cursor.execute(
        """SELECT u.user_id, u.name, u.email, u.phone
        FROM MentorAssignments ma
        JOIN Users u ON ma.mentor_id = u.user_id
        WHERE ma.team_id = %s""",
        (team_id,)
    )
    return cursor.fetchall()


@router.get("/my-teams")
def get_mentor_teams(
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("mentor"))
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT t.team_id, t.team_name, e.event_name, e.start_date, e.end_date,
        u.name as leader_name
        FROM MentorAssignments ma
        JOIN Teams t ON ma.team_id = t.team_id
        JOIN Events e ON t.event_id = e.event_id
        JOIN Users u ON t.leader_id = u.user_id
        WHERE ma.mentor_id = %s""",
        (current_user["user_id"],)
    )
    return cursor.fetchall()


@router.get("/mentor/{mentor_id}")
def get_mentor_assignments(
    mentor_id: int,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)

    # Check mentor exists
    cursor.execute(
        "SELECT * FROM Users WHERE user_id = %s AND role = 'mentor'",
        (mentor_id,)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Mentor not found")

    cursor.execute(
        """SELECT t.team_id, t.team_name, e.event_name,
        e.start_date, e.end_date
        FROM MentorAssignments ma
        JOIN Teams t ON ma.team_id = t.team_id
        JOIN Events e ON t.event_id = e.event_id
        WHERE ma.mentor_id = %s""",
        (mentor_id,)
    )
    return cursor.fetchall()