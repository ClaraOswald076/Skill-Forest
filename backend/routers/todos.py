"""TodoItem router — list + update."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from backend.services import todo_service

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=List[TodoResponse])
def list_todos(
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    skill_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    todos = todo_service.get_todos(db, job_id=job_id, status=status, skill_id=skill_id)
    return [t.to_dict() for t in todos]


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = todo_service.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo.to_dict()


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, data: TodoUpdate, db: Session = Depends(get_db)):
    todo = todo_service.update_todo(db, todo_id, data)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo.to_dict()


@router.post("", response_model=TodoResponse)
def create_todo(data: TodoCreate, db: Session = Depends(get_db)):
    todo = todo_service.create_todo(db, data)
    return todo.to_dict()
