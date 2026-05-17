from pydantic import BaseModel, field_validator
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

    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Event name must be at least 3 characters")
        if len(v) > 150:
            raise ValueError("Event name must be under 150 characters")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v, info):
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v

    @field_validator("max_team_size")
    @classmethod
    def validate_max_team_size(cls, v):
        if v < 1:
            raise ValueError("Max team size must be at least 1")
        if v > 10:
            raise ValueError("Max team size cannot exceed 10")
        return v

    @field_validator("min_team_size")
    @classmethod
    def validate_min_team_size(cls, v, info):
        if v < 1:
            raise ValueError("Min team size must be at least 1")
        if "max_team_size" in info.data and v > info.data["max_team_size"]:
            raise ValueError("Min team size cannot exceed max team size")
        return v

class EventUpdate(BaseModel):
    event_name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[StatusEnum] = None
    max_team_size: Optional[int] = None
    min_team_size: Optional[int] = None