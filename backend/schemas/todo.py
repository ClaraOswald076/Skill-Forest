"""Pydantic schemas for TodoItem."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    job_id: int
    description: str
    proficiency_required: str = "熟悉"
    skill_ids: List[int] = []
    notes: str = ""


class TodoUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    proficiency_required: Optional[str] = None
    notes: Optional[str] = None
    skill_ids: Optional[List[int]] = None


class TodoResponse(BaseModel):
    id: int
    job_id: int
    job_title: str = ""
    description: str
    status: str
    proficiency_required: str
    skill_ids: List[int] = []
    skill_names: List[str] = []
    notes: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
