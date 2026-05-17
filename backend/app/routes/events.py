from fastapi import APIRouter, Depends, HTTPException
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.event import EventCreate, EventUpdate
from app.routes.dependencies import get_current_user, require_role

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", status_code=201)
def create_event(
    event: EventCreate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """INSERT INTO Events 
        (event_name, description, start_date, end_date, max_team_size, min_team_size, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (event.event_name, event.description, event.start_date,
         event.end_date, event.max_team_size, event.min_team_size,
         current_user["user_id"])
    )
    db.commit()
    return {"message": "Event created", "event_id": cursor.lastrowid}


@router.get("/")
def get_all_events(db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Events")
    return cursor.fetchall()


@router.get("/{event_id}")
def get_event(event_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Events WHERE event_id = %s", (event_id,))
    event = cursor.fetchone()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}")
def update_event(
    event_id: int,
    event: EventUpdate,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)
    fields = {k: v for k, v in event.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    query = "UPDATE Events SET " + ", ".join(f"{k} = %s" for k in fields)
    query += " WHERE event_id = %s"
    cursor.execute(query, (*fields.values(), event_id))
    db.commit()
    return {"message": "Event updated"}


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM Events WHERE event_id = %s", (event_id,))
    db.commit()
    return {"message": "Event deleted"}