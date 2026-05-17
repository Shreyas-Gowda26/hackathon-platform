from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector.connection import MySQLConnection
from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, TokenResponse
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", status_code=201)
def register(user: UserRegister, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    # Check if email already exists
    cursor.execute("SELECT user_id FROM Users WHERE email = %s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)
    cursor.execute(
        "INSERT INTO Users (name, email, phone, role, password_hash) VALUES (%s, %s, %s, %s, %s)",
        (user.name, user.email, user.phone, user.role, hashed)
    )
    db.commit()
    return {"message": "User registered successfully", "user_id": cursor.lastrowid}


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Users WHERE email = %s", (user.email,))
    db_user = cursor.fetchone()

    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "sub": str(db_user["user_id"]),
        "role": db_user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user["role"],
        "user_id": db_user["user_id"]
    }