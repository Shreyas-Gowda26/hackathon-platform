from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.team import TeamCreate, TeamUpdate, AddMember, RespondInvite
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
        WHERE tm.user_id = %s AND t.event_id = %s AND tm.status = 'accepted'""",
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

    # Add creator as first member — auto accepted
    cursor.execute(
        """INSERT INTO TeamMembers (team_id, user_id, status, invited_by)
        VALUES (%s, %s, 'accepted', %s)""",
        (team_id, current_user["user_id"], current_user["user_id"])
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


@router.get("/my-invites")
def get_my_invites(
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT tm.id, tm.status, tm.invited_by,
        t.team_id, t.team_name,
        e.event_name, e.start_date, e.end_date,
        u.name as invited_by_name
        FROM TeamMembers tm
        JOIN Teams t ON tm.team_id = t.team_id
        JOIN Events e ON t.event_id = e.event_id
        JOIN Users u ON tm.invited_by = u.user_id
        WHERE tm.user_id = %s AND tm.status = 'pending'""",
        (current_user["user_id"],)
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

    cursor.execute(
        """SELECT u.user_id, u.name, u.email, u.role, tm.status
        FROM TeamMembers tm
        JOIN Users u ON tm.user_id = u.user_id
        WHERE tm.team_id = %s""",
        (team_id,)
    )
    team["members"] = cursor.fetchall()
    return team


@router.post("/{team_id}/invite", status_code=201)
def invite_member(
    team_id: int,
    data: AddMember,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)

    # Only team leader can invite
    cursor.execute(
        "SELECT * FROM Teams WHERE team_id = %s AND leader_id = %s",
        (team_id, current_user["user_id"])
    )
    team = cursor.fetchone()
    if not team:
        raise HTTPException(status_code=403, detail="Only team leader can invite members")

    # Check receiver exists
    cursor.execute("SELECT * FROM Users WHERE user_id = %s", (data.user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    # Check max team size (count only accepted members)
    cursor.execute(
        """SELECT e.max_team_size FROM Teams t
        JOIN Events e ON t.event_id = e.event_id
        WHERE t.team_id = %s""",
        (team_id,)
    )
    event = cursor.fetchone()
    cursor.execute(
        "SELECT COUNT(*) as count FROM TeamMembers WHERE team_id = %s AND status = 'accepted'",
        (team_id,)
    )
    count = cursor.fetchone()["count"]
    if count >= event["max_team_size"]:
        raise HTTPException(status_code=400, detail="Team is already full")

    # Check already invited or in team
    cursor.execute(
        "SELECT * FROM TeamMembers WHERE team_id = %s AND user_id = %s",
        (team_id, data.user_id)
    )
    existing = cursor.fetchone()
    if existing:
        if existing["status"] == "pending":
            raise HTTPException(status_code=400, detail="Invite already sent to this user")
        if existing["status"] == "accepted":
            raise HTTPException(status_code=400, detail="User is already a team member")
        if existing["status"] == "rejected":
            # Allow re-inviting after rejection
            cursor.execute(
                "UPDATE TeamMembers SET status = 'pending', invited_by = %s WHERE team_id = %s AND user_id = %s",
                (current_user["user_id"], team_id, data.user_id)
            )
            db.commit()
            return {"message": "Invite re-sent successfully"}

    cursor.execute(
        """INSERT INTO TeamMembers (team_id, user_id, status, invited_by)
        VALUES (%s, %s, 'pending', %s)""",
        (team_id, data.user_id, current_user["user_id"])
    )
    db.commit()
    return {"message": "Invite sent successfully"}


@router.put("/invites/{member_id}/respond")
def respond_to_invite(
    member_id: int,
    data: RespondInvite,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)

    if data.status not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'accepted' or 'rejected'")

    # Check invite exists and belongs to current user
    cursor.execute(
        "SELECT * FROM TeamMembers WHERE id = %s AND user_id = %s AND status = 'pending'",
        (member_id, current_user["user_id"])
    )
    invite = cursor.fetchone()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found or already responded")

    cursor.execute(
        "UPDATE TeamMembers SET status = %s WHERE id = %s",
        (data.status, member_id)
    )
    db.commit()
    return {"message": f"Invite {data.status} successfully"}


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