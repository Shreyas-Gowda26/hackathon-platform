from pydantic import BaseModel

class MentorAssign(BaseModel):
    mentor_id: int
    team_id: int

class MentorRemove(BaseModel):
    mentor_id: int
    team_id: int