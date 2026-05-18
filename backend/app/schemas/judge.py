from pydantic import BaseModel


class JudgeAssign(BaseModel):
    judge_id: int
    team_id: int
