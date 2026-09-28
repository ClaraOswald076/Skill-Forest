"""Job CRUD service."""

import difflib
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session, joinedload

from backend.models.job import Job
from backend.models.skill import Skill
from backend.models.todo_item import TodoItem
from backend.schemas.job import JobCreate
from backend.schemas.analysis import JobSaveRequest, ExtractedSkill, GeneratedTodo

logger = logging.getLogger(__name__)


def _normalize_skill_name(name: str) -> str:
    return name.strip().casefold()


def _resolve_skill(name: str, skill_map: Dict[str, Skill], alias_map: Dict[str, Skill]) -> Optional[Skill]:
    """Resolve a todo's skill reference to a saved Skill: exact -> normalized -> fuzzy."""
    if name in skill_map:
        return skill_map[name]
    normalized = _normalize_skill_name(name)
    if normalized in alias_map:
        return alias_map[normalized]
    if alias_map:
        close = difflib.get_close_matches(normalized, list(alias_map.keys()), n=1, cutoff=0.85)
        if close:
            return alias_map[close[0]]
    return None


def get_jobs(db: Session) -> list:
    """List all jobs with skill/todo counts."""
    jobs = db.query(Job).options(
        joinedload(Job.skills),
        joinedload(Job.todo_items),
    ).order_by(Job.created_at.desc()).all()
    return jobs


def get_job(db: Session, job_id: int) -> Optional[Job]:
    return db.query(Job).options(
        joinedload(Job.skills),
        joinedload(Job.todo_items).joinedload(TodoItem.skills),
    ).filter(Job.id == job_id).first()


def create_job(db: Session, data: JobCreate) -> Job:
    job = Job(
        title=data.title or "未命名岗位",
        company=data.company,
        url=data.url or "",
        raw_text=data.raw_text,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, job_id: int) -> bool:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return False
    # Clean up orphaned skills (skills that only belong to this job and have no todos)
    for skill in list(job.skills):
        if len(skill.source_jobs) == 1 and len(skill.todo_items) == 0:
            db.delete(skill)
    db.delete(job)
    db.commit()
    return True


def save_job_with_analysis(db: Session, data: JobSaveRequest) -> dict:
    """
    Full pipeline: create job, create/merge skills, create todos, link them.
    Returns {"job": Job, "skills_created": int, "skills_merged": int, "todos_created": int,
             "links_unmatched": list}
    """
    # 1. Create job
    job = Job(
        title=data.title or "未命名岗位",
        company=data.company,
        url=data.url or "",
        raw_text=data.raw_text,
    )
    db.add(job)
    db.flush()  # Get job.id

    stats = {"skills_created": 0, "skills_merged": 0, "todos_created": 0, "links_unmatched": []}

    # 2. Process skills
    skill_map: Dict[str, Skill] = {}  # skill_name -> Skill ORM object
    alias_map: Dict[str, Skill] = {}  # normalized name -> Skill, for todo backlink fallback

    for es in data.skills:
        decision = data.merge_decisions.get(es.name, "keep_separate")

        if decision == "merge" and es.merge_with_existing_id:
            # Merge into existing skill
            existing = db.query(Skill).filter(Skill.id == es.merge_with_existing_id).first()
            if existing:
                if job not in existing.source_jobs:
                    existing.source_jobs.append(job)
                skill_map[es.name] = existing
                # Todos tend to reference the existing skill's name, not the extracted one
                alias_map.setdefault(_normalize_skill_name(es.name), existing)
                alias_map.setdefault(_normalize_skill_name(existing.name), existing)
                stats["skills_merged"] += 1
                continue

        # Create new skill
        skill = Skill(
            name=es.name,
            description=es.description,
            category_l1=es.category_l1,
            category_l2=es.category_l2,
            category_l3=es.category_l3,
            proficiency="认识",
            status="not_started",
        )
        skill.source_jobs.append(job)
        db.add(skill)
        db.flush()
        skill_map[es.name] = skill
        alias_map.setdefault(_normalize_skill_name(es.name), skill)
        stats["skills_created"] += 1

    # 3. Process todos
    for gt in data.todos:
        todo = TodoItem(
            job_id=job.id,
            description=gt.description,
            proficiency_required=gt.proficiency_required,
            status="pending",
        )
        db.add(todo)
        db.flush()

        # Link todo to skills by name; LLM may paraphrase names between the
        # skills and todos fields, so fall back to normalized/fuzzy matching
        # and record what still cannot be linked instead of dropping silently
        unmatched = []
        for sname in gt.skill_names:
            skill = _resolve_skill(sname, skill_map, alias_map)
            if skill is not None:
                todo.skills.append(skill)
            else:
                unmatched.append(sname)
        if unmatched:
            logger.warning(
                f"Todo skill backlink unmatched for job '{job.title}': {unmatched} "
                f"(todo: {gt.description[:50]!r})"
            )
            stats["links_unmatched"].append({
                "todo_id": todo.id,
                "description": gt.description,
                "skill_names": unmatched,
            })

        stats["todos_created"] += 1

    db.commit()
    db.refresh(job)

    return {
        "job": job,
        "skills_created": stats["skills_created"],
        "skills_merged": stats["skills_merged"],
        "todos_created": stats["todos_created"],
        "links_unmatched": stats["links_unmatched"],
    }
