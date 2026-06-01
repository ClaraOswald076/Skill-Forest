"""Association tables for many-to-many relationships."""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Table, func

from backend.database import Base

# Many-to-many: skills <-> jobs
skill_jobs = Table(
    "skill_jobs",
    Base.metadata,
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Column("job_id", Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, default=func.now()),
)

# Many-to-many: todo_items <-> skills
todo_skills = Table(
    "todo_skills",
    Base.metadata,
    Column("todo_id", Integer, ForeignKey("todo_items.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)
