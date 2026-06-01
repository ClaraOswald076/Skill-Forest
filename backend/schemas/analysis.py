"""Pydantic schemas for Analysis (DeepSeek integration)."""

from typing import Optional, List
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    raw_text: str
    url: str = ""
    job_title: str = ""
    company: str = ""


class ExtractedSkill(BaseModel):
    name: str
    description: str
    category_l1: str
    category_l2: str
    category_l3: str = ""
    proficiency: str = "认识"
    merge_with_existing_id: Optional[int] = None  # null = new skill
    merge_confidence: float = 0.0  # 0.0 - 1.0


class GeneratedTodo(BaseModel):
    description: str
    skill_names: List[str] = []  # matched by name
    proficiency_required: str = "熟悉"


class MergeSuggestion(BaseModel):
    existing_skill_id: int
    existing_skill_name: str
    new_skill_name: str
    similarity: float  # 0.0 - 1.0
    action: str = "keep_separate"  # "merge" | "keep_separate"


class JobSaveRequest(BaseModel):
    """Request to save a job after analysis preview."""
    raw_text: str
    url: str = ""
    title: str = ""
    company: str = ""
    skills: List[ExtractedSkill] = []
    todos: List[GeneratedTodo] = []
    merge_decisions: dict = {}  # skill_name -> "merge" | "keep_separate"


class AnalysisResponse(BaseModel):
    job_title: str
    company: str
    skills: List[ExtractedSkill] = []
    todos: List[GeneratedTodo] = []
    merge_suggestions: List[MergeSuggestion] = []
    summary: str = ""
