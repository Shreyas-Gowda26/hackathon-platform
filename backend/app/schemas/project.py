from pydantic import BaseModel, field_validator
from typing import Optional

class ProjectCreate(BaseModel):
    team_id: int
    title: str
    description: Optional[str] = None
    repo_link: Optional[str] = None
    demo_link: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Title must be at least 3 characters")
        if len(v) > 150:
            raise ValueError("Title must be under 150 characters")
        return v

    @field_validator("repo_link", "demo_link")
    @classmethod
    def validate_links(cls, v):
        if v is None:
            return v
        if not v.startswith(("http://", "https://")):
            raise ValueError("Link must start with http:// or https://")
        return v


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    repo_link: Optional[str] = None
    demo_link: Optional[str] = None
    status: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Title must be at least 3 characters")
        if len(v) > 150:
            raise ValueError("Title must be under 150 characters")
        return v

    @field_validator("repo_link", "demo_link")
    @classmethod
    def validate_links(cls, v):
        if v is None:
            return v
        if not v.startswith(("http://", "https://")):
            raise ValueError("Link must start with http:// or https://")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        if v not in ["draft", "submitted"]:
            raise ValueError("Status must be 'draft' or 'submitted'")
        return v