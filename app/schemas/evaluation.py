from pydantic import BaseModel
from typing import Optional

class EvaluationCreate(BaseModel):
    project_id: int
    score: int
    feedback: Optional[str] = None

class EvaluationUpdate(BaseModel):
    score: Optional[int] = None
    feedback: Optional[str] = None