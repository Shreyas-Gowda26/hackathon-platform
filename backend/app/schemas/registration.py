from pydantic import BaseModel

class RegistrationCreate(BaseModel):
    event_id: int

class RegistrationUpdate(BaseModel):
    status: str