from pydantic import BaseModel
from typing import Optional

class TeamCreate(BaseModel):
    team_name: str
    event_id: int

class TeamUpdate(BaseModel):
    team_name: Optional[str] = None

class AddMember(BaseModel):
    user_id: int

class RespondInvite(BaseModel):
    status: str  # accepted | rejected