from pydantic import BaseModel, field_validator
from typing import Optional

class EvaluationCreate(BaseModel):
    project_id: int
    score: int
    feedback: Optional[str] = None

    @field_validator("score")
    @classmethod
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v

class EvaluationUpdate(BaseModel):
    score: Optional[int] = None
    feedback: Optional[str] = None

    @field_validator("score")
    @classmethod
    def validate_score(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v