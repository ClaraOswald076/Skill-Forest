"""Pydantic schemas for Dashboard."""

from typing import List, Optional
from pydantic import BaseModel


class DomainCompletion(BaseModel):
    category_l1: str  # 大类名称
    total_skills: int
    completed_skills: int
    completion_rate: float  # 0.0 - 1.0


class ExpertiseItem(BaseModel):
    category_l1: str
    category_l2: str
    skill_count: int
    avg_proficiency_level: float  # 1=认识, 2=熟悉, 3=熟练, 4=完全掌握
    top_skills: List[str] = []


class BestMatchingJob(BaseModel):
    job_id: int
    job_title: str
    company: str = ""
    total_skills_required: int
    completed_skills: int
    match_rate: float  # 0.0 - 1.0


class DashboardResponse(BaseModel):
    total_skills: int = 0
    completed_skills: int = 0
    overall_completion_rate: float = 0.0
    total_todos: int = 0
    completed_todos: int = 0
    total_jobs: int = 0
    domains: List[DomainCompletion] = []
    best_matching_job: Optional[BestMatchingJob] = None
    deepest_expertise: List[ExpertiseItem] = []
    recent_activity: str = ""
