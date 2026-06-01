"""Dashboard aggregation service."""

from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from backend.models.skill import Skill
from backend.models.job import Job
from backend.models.todo_item import TodoItem
from backend.schemas.dashboard import (
    DashboardResponse,
    DomainCompletion,
    ExpertiseItem,
    BestMatchingJob,
)


PROFICIENCY_SCORES = {
    "认识": 1,
    "熟悉": 2,
    "熟练": 3,
    "完全掌握": 4,
}


def get_dashboard_stats(db: Session) -> DashboardResponse:
    # Total counts
    total_skills = db.query(Skill).count()
    completed_skills = db.query(Skill).filter(Skill.status == "completed").count()
    total_todos = db.query(TodoItem).count()
    completed_todos = db.query(TodoItem).filter(TodoItem.status == "completed").count()
    total_jobs = db.query(Job).count()

    overall_rate = completed_skills / total_skills if total_skills > 0 else 0.0

    # Domain completion (by category_l1)
    domains = []
    l1_results = db.query(
        Skill.category_l1,
        func.count(Skill.id).label("total"),
        func.sum(
            case((Skill.status == "completed", 1), else_=0)
        ).label("completed"),
    ).group_by(Skill.category_l1).all()

    for row in l1_results:
        domains.append(DomainCompletion(
            category_l1=row[0],
            total_skills=row[1],
            completed_skills=row[2] or 0,
            completion_rate=(row[2] or 0) / row[1] if row[1] > 0 else 0.0,
        ))

    # Best matching job
    best_job = _compute_best_matching_job(db)

    # Deepest expertise
    expertise = _compute_deepest_expertise(db)

    # Recent activity summary
    recent = _get_recent_activity(db)

    return DashboardResponse(
        total_skills=total_skills,
        completed_skills=completed_skills,
        overall_completion_rate=round(overall_rate, 2),
        total_todos=total_todos,
        completed_todos=completed_todos,
        total_jobs=total_jobs,
        domains=domains,
        best_matching_job=best_job,
        deepest_expertise=expertise,
        recent_activity=recent,
    )


def _compute_best_matching_job(db: Session) -> Optional[BestMatchingJob]:
    """Find the job with highest skill completion rate."""
    jobs = db.query(Job).all()
    if not jobs:
        return None

    best = None
    best_rate = -1.0

    for job in jobs:
        if not job.skills:
            continue
        total = len(job.skills)
        completed = sum(1 for s in job.skills if s.status == "completed")
        rate = completed / total
        if rate > best_rate:
            best_rate = rate
            best = BestMatchingJob(
                job_id=job.id,
                job_title=job.title,
                company=job.company,
                total_skills_required=total,
                completed_skills=completed,
                match_rate=round(rate, 2),
            )

    return best


def _compute_deepest_expertise(db: Session) -> list:
    """Find domains where user has highest proficiency."""
    skills = db.query(Skill).all()
    if not skills:
        return []

    # Group by (l1, l2)
    groups: Dict[Tuple, list] = {}
    for s in skills:
        key = (s.category_l1, s.category_l2)
        if key not in groups:
            groups[key] = []
        groups[key].append(s)

    results = []
    for (l1, l2), group_skills in groups.items():
        if len(group_skills) < 2:
            continue
        scores = [PROFICIENCY_SCORES.get(s.proficiency, 1) for s in group_skills]
        avg = sum(scores) / len(scores)
        top = sorted(group_skills, key=lambda s: PROFICIENCY_SCORES.get(s.proficiency, 1), reverse=True)[:3]

        results.append(ExpertiseItem(
            category_l1=l1,
            category_l2=l2,
            skill_count=len(group_skills),
            avg_proficiency_level=round(avg, 2),
            top_skills=[s.name for s in top],
        ))

    # Sort by avg proficiency desc
    results.sort(key=lambda x: x.avg_proficiency_level, reverse=True)
    return results[:5]


def _get_recent_activity(db: Session) -> str:
    """Generate a brief activity summary."""
    recent_skills = db.query(Skill).filter(
        Skill.status == "in_progress"
    ).count()

    if recent_skills > 0:
        return f"有 {recent_skills} 项技能正在学习中"
    return "暂无学习活动"
