"""Pydantic schemas for Job."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    raw_text: str
    url: str = ""
    title: str = ""
    company: str = ""


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    url: str = ""
    raw_text: str = ""
    skill_ids: List[int] = []
    skill_count: int = 0
    todo_count: int = 0
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    skills: List["SkillResponse"] = []
    todos: List["TodoResponse"] = []


# Avoid circular imports — import at end
from backend.schemas.skill import SkillResponse  # noqa: E402
from backend.schemas.todo import TodoResponse    # noqa: E402
JobDetailResponse.model_rebuild()
