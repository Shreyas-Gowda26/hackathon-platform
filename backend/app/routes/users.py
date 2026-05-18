from typing import Optional

from fastapi import APIRouter, Depends
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.routes.dependencies import require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def list_users(
    role: Optional[str] = None,
    db: MySQLConnection = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    cursor = db.cursor(dictionary=True)
    if role:
        cursor.execute(
            "SELECT user_id, name, email, phone, role FROM Users WHERE role = %s ORDER BY user_id",
            (role,),
        )
    else:
        cursor.execute(
            "SELECT user_id, name, email, phone, role FROM Users ORDER BY user_id"
        )
    return cursor.fetchall()
