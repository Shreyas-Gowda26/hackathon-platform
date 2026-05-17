from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.registration import RegistrationCreate, RegistrationUpdate
from app.routes.dependencies import get_current_user, require_role

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.post("/", status_code=201)
def register_for_event(
    data: RegistrationCreate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)

    # Check if event exists
    cursor.execute("SELECT * FROM Events WHERE event_id = %s", (data.event_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if already registered
    cursor.execute(
        "SELECT * FROM Registrations WHERE user_id = %s AND event_id = %s",
        (current_user["user_id"], data.event_id)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Already registered for this event")

    cursor.execute(
        "INSERT INTO Registrations (user_id, event_id) VALUES (%s, %s)",
        (current_user["user_id"], data.event_id)
    )
    db.commit()
    return {"message": "Registered successfully", "registration_id": cursor.lastrowid}


@router.get("/my")
def my_registrations(
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT r.*, e.event_name, e.start_date, e.end_date, e.status
        FROM Registrations r
        JOIN Events e ON r.event_id = e.event_id
        WHERE r.user_id = %s""",
        (current_user["user_id"],)
    )
    return cursor.fetchall()


@router.get("/event/{event_id}")
def get_event_registrations(
    event_id: int,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT r.*, u.name, u.email, u.role
        FROM Registrations r
        JOIN Users u ON r.user_id = u.user_id
        WHERE r.event_id = %s""",
        (event_id,)
    )
    return cursor.fetchall()


@router.put("/{registration_id}")
def update_registration_status(
    registration_id: int,
    data: RegistrationUpdate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "UPDATE Registrations SET status = %s WHERE registration_id = %s",
        (data.status, registration_id)
    )
    db.commit()
    return {"message": "Registration status updated"}


@router.delete("/{registration_id}")
def cancel_registration(
    registration_id: int,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Registrations WHERE registration_id = %s AND user_id = %s",
        (registration_id, current_user["user_id"])
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Registration not found")
    cursor.execute(
        "DELETE FROM Registrations WHERE registration_id = %s",
        (registration_id,)
    )
    db.commit()
    return {"message": "Registration cancelled"}