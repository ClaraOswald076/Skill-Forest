"""Job CRUD service."""

from typing import Dict, Optional
from sqlalchemy.orm import Session, joinedload

from backend.models.job import Job
from backend.models.skill import Skill
from backend.models.todo_item import TodoItem
from backend.schemas.job import JobCreate
from backend.schemas.analysis import JobSaveRequest, ExtractedSkill, GeneratedTodo


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
    Returns {"job": Job, "skills_created": int, "skills_merged": int, "todos_created": int}
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

    stats = {"skills_created": 0, "skills_merged": 0, "todos_created": 0}

    # 2. Process skills
    skill_map: Dict[str, Skill] = {}  # skill_name -> Skill ORM object

    for es in data.skills:
        decision = data.merge_decisions.get(es.name, "keep_separate")

        if decision == "merge" and es.merge_with_existing_id:
            # Merge into existing skill
            existing = db.query(Skill).filter(Skill.id == es.merge_with_existing_id).first()
            if existing:
                if job not in existing.source_jobs:
                    existing.source_jobs.append(job)
                skill_map[es.name] = existing
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

        # Link todo to skills by name
        for sname in gt.skill_names:
            if sname in skill_map:
                todo.skills.append(skill_map[sname])

        stats["todos_created"] += 1

    db.commit()
    db.refresh(job)

    return {
        "job": job,
        "skills_created": stats["skills_created"],
        "skills_merged": stats["skills_merged"],
        "todos_created": stats["todos_created"],
    }
