"""Skill CRUD service."""

from typing import Optional, List
from sqlalchemy.orm import Session

from backend.models.skill import Skill
from backend.models.associations import skill_jobs, todo_skills
from backend.schemas.skill import SkillCreate, SkillUpdate
from backend.utils.tree_builder import build_skill_tree


def get_skills(
    db: Session,
    status: Optional[str] = None,
    category_l1: Optional[str] = None,
) -> list:
    """List skills with optional filters."""
    q = db.query(Skill)
    if status:
        q = q.filter(Skill.status == status)
    if category_l1:
        q = q.filter(Skill.category_l1 == category_l1)
    return q.order_by(Skill.category_l1, Skill.category_l2, Skill.category_l3, Skill.name).all()


def get_skill(db: Session, skill_id: int) -> Optional[Skill]:
    return db.query(Skill).filter(Skill.id == skill_id).first()


def get_all_skills_as_dicts(db: Session) -> List[dict]:
    """Return all skills as plain dicts (for sending to DeepSeek API)."""
    skills = db.query(Skill).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "category_l1": s.category_l1,
            "category_l2": s.category_l2,
            "category_l3": s.category_l3,
        }
        for s in skills
    ]


def create_skill(db: Session, data: SkillCreate) -> Skill:
    skill = Skill(
        name=data.name,
        description=data.description,
        category_l1=data.category_l1,
        category_l2=data.category_l2,
        category_l3=data.category_l3,
        proficiency=data.proficiency,
        status=data.status,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def update_skill(db: Session, skill_id: int, data: SkillUpdate) -> Optional[Skill]:
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(skill, key, value)
    db.commit()
    db.refresh(skill)
    return skill


def delete_skill(db: Session, skill_id: int) -> bool:
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        return False
    db.delete(skill)
    db.commit()
    return True


def merge_skills(db: Session, source_id: int, target_id: int) -> Optional[Skill]:
    """
    Merge source skill into target skill:
    - Transfer all job and todo associations from source to target
    - Keep target's proficiency if it's higher
    - Delete source skill
    """
    source = db.query(Skill).filter(Skill.id == source_id).first()
    target = db.query(Skill).filter(Skill.id == target_id).first()
    if not source or not target:
        return None

    # Transfer job associations
    for job in source.source_jobs:
        if job not in target.source_jobs:
            target.source_jobs.append(job)

    # Transfer todo associations
    for todo in source.todo_items:
        if todo not in target.todo_items:
            target.todo_items.append(todo)

    # Keep higher proficiency
    prof_levels = {"认识": 1, "熟悉": 2, "熟练": 3, "完全掌握": 4}
    if prof_levels.get(source.proficiency, 1) > prof_levels.get(target.proficiency, 1):
        target.proficiency = source.proficiency

    # Merge descriptions
    if source.description and source.description not in target.description:
        target.description = target.description + "; " + source.description if target.description else source.description

    db.delete(source)
    db.commit()
    db.refresh(target)
    return target


def get_skill_tree(db: Session) -> list:
    """Get full skill tree as nested structure."""
    skills = get_skills(db)
    skill_dicts = [s.to_dict() for s in skills]
    return build_skill_tree(skill_dicts)


def find_skill_by_name(db: Session, name: str) -> Optional[Skill]:
    """Find a skill by exact name match."""
    return db.query(Skill).filter(Skill.name == name).first()
