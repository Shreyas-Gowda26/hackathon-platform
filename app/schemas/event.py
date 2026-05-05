from pydantic import BaseModel
from datetime import date
from enum import Enum
from typing import Optional

class StatusEnum(str, Enum):
    upcoming = "upcoming"
    ongoing = "ongoing"
    completed = "completed"

class EventCreate(BaseModel):
    event_name: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    max_team_size: int = 4
    min_team_size: int = 1

class EventUpdate(BaseModel):
    event_name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[StatusEnum] = None
    max_team_size: Optional[int] = None
    min_team_size: Optional[int] = None