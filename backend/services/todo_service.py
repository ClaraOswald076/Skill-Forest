"""TodoItem CRUD service."""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from backend.models.todo_item import TodoItem
from backend.models.skill import Skill
from backend.schemas.todo import TodoCreate, TodoUpdate


def get_todos(
    db: Session,
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    skill_id: Optional[int] = None,
) -> list:
    """List todos with optional filters."""
    q = db.query(TodoItem).options(
        joinedload(TodoItem.job),
        joinedload(TodoItem.skills),
    )

    if job_id is not None:
        q = q.filter(TodoItem.job_id == job_id)
    if status:
        q = q.filter(TodoItem.status == status)
    if skill_id is not None:
        q = q.join(TodoItem.skills).filter(Skill.id == skill_id)

    return q.order_by(TodoItem.created_at.desc()).all()


def get_todo(db: Session, todo_id: int) -> Optional[TodoItem]:
    return db.query(TodoItem).options(
        joinedload(TodoItem.job),
        joinedload(TodoItem.skills),
    ).filter(TodoItem.id == todo_id).first()


def update_todo(db: Session, todo_id: int, data: TodoUpdate) -> Optional[TodoItem]:
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        return None

    update_data = data.model_dump(exclude_unset=True)
    skill_ids = update_data.pop("skill_ids", None)

    for key, value in update_data.items():
        setattr(todo, key, value)

    if skill_ids is not None:
        skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
        todo.skills = skills

    db.commit()
    db.refresh(todo)
    return todo


def create_todo(db: Session, data: TodoCreate) -> TodoItem:
    todo = TodoItem(
        job_id=data.job_id,
        description=data.description,
        proficiency_required=data.proficiency_required,
        notes=data.notes,
    )
    if data.skill_ids:
        skills = db.query(Skill).filter(Skill.id.in_(data.skill_ids)).all()
        todo.skills = skills

    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo
