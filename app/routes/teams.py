from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.team import TeamCreate, TeamUpdate, AddMember
from app.routes.dependencies import get_current_user, require_role

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", status_code=201)
def create_team(
    data: TeamCreate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)

    # Check event exists
    cursor.execute("SELECT * FROM Events WHERE event_id = %s", (data.event_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Event not found")

    # Check user is registered for the event
    cursor.execute(
        "SELECT * FROM Registrations WHERE user_id = %s AND event_id = %s",
        (current_user["user_id"], data.event_id)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=400, detail="You must register for the event first")

    # Check user not already in a team for this event
    cursor.execute(
        """SELECT tm.* FROM TeamMembers tm
        JOIN Teams t ON tm.team_id = t.team_id
        WHERE tm.user_id = %s AND t.event_id = %s""",
        (current_user["user_id"], data.event_id)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="You are already in a team for this event")

    # Create team
    cursor.execute(
        "INSERT INTO Teams (team_name, event_id, leader_id) VALUES (%s, %s, %s)",
        (data.team_name, data.event_id, current_user["user_id"])
    )
    db.commit()
    team_id = cursor.lastrowid

    # Add creator as first member
    cursor.execute(
        "INSERT INTO TeamMembers (team_id, user_id) VALUES (%s, %s)",
        (team_id, current_user["user_id"])
    )
    db.commit()
    return {"message": "Team created", "team_id": team_id}


@router.get("/event/{event_id}")
def get_teams_by_event(
    event_id: int,
    db: MySQLConnection = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT t.*, u.name as leader_name
        FROM Teams t
        JOIN Users u ON t.leader_id = u.user_id
        WHERE t.event_id = %s""",
        (event_id,)
    )
    return cursor.fetchall()


@router.get("/{team_id}")
def get_team(
    team_id: int,
    db: MySQLConnection = Depends(get_db)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Teams WHERE team_id = %s", (team_id,))
    team = cursor.fetchone()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Get members
    cursor.execute(
        """SELECT u.user_id, u.name, u.email, u.role
        FROM TeamMembers tm
        JOIN Users u ON tm.user_id = u.user_id
        WHERE tm.team_id = %s""",
        (team_id,)
    )
    team["members"] = cursor.fetchall()
    return team


@router.post("/{team_id}/members", status_code=201)
def add_member(
    team_id: int,
    data: AddMember,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)

    # Only team leader can add members
    cursor.execute(
        "SELECT * FROM Teams WHERE team_id = %s AND leader_id = %s",
        (team_id, current_user["user_id"])
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=403, detail="Only team leader can add members")

    # Check max team size
    cursor.execute(
        """SELECT e.max_team_size FROM Teams t
        JOIN Events e ON t.event_id = e.event_id
        WHERE t.team_id = %s""",
        (team_id,)
    )
    event = cursor.fetchone()
    cursor.execute(
        "SELECT COUNT(*) as count FROM TeamMembers WHERE team_id = %s",
        (team_id,)
    )
    count = cursor.fetchone()["count"]
    if count >= event["max_team_size"]:
        raise HTTPException(status_code=400, detail="Team is already full")

    try:
        cursor.execute(
            "INSERT INTO TeamMembers (team_id, user_id) VALUES (%s, %s)",
            (team_id, data.user_id)
        )
        db.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="User already in this team")

    return {"message": "Member added successfully"}


@router.delete("/{team_id}/members/{user_id}")
def remove_member(
    team_id: int,
    user_id: int,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Teams WHERE team_id = %s AND leader_id = %s",
        (team_id, current_user["user_id"])
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=403, detail="Only team leader can remove members")

    cursor.execute(
        "DELETE FROM TeamMembers WHERE team_id = %s AND user_id = %s",
        (team_id, user_id)
    )
    db.commit()
    return {"message": "Member removed"}