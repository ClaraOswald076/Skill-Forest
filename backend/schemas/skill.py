"""Pydantic schemas for Skill."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str = ""
    category_l1: str = Field(..., max_length=100)
    category_l2: str = Field(..., max_length=100)
    category_l3: str = ""
    proficiency: str = "认识"
    status: str = "not_started"


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_l1: Optional[str] = None
    category_l2: Optional[str] = None
    category_l3: Optional[str] = None
    proficiency: Optional[str] = None
    status: Optional[str] = None


class SkillResponse(BaseModel):
    id: int
    name: str
    description: str
    category_l1: str
    category_l2: str
    category_l3: str
    proficiency: str
    status: str
    source_job_ids: List[int] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class SkillTreeNode(BaseModel):
    key: str
    title: str
    type: str  # "l1", "l2", "l3", "skill"
    skill: Optional[SkillResponse] = None
    children: List["SkillTreeNode"] = []


class SkillTreeResponse(BaseModel):
    tree: List[SkillTreeNode]


class MergeRequest(BaseModel):
    source_id: int
    target_id: int
