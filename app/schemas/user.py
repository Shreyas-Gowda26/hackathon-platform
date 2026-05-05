from pydantic import BaseModel, EmailStr
from enum import Enum

class RoleEnum(str, Enum):
    participant = "participant"
    mentor = "mentor"
    judge = "judge"
    admin = "admin"

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: RoleEnum
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int