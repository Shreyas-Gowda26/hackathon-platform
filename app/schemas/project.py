from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    team_id: int
    title: str
    description: Optional[str] = None
    repo_link: Optional[str] = None
    demo_link: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    repo_link: Optional[str] = None
    demo_link: Optional[str] = None
    status: Optional[str] = None