"""TodoItem ORM model."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base
from backend.models.associations import todo_skills


class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="pending")              # pending|in_progress|completed
    proficiency_required = Column(String(20), default="熟悉")    # 认识|熟悉|熟练|完全掌握
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    job = relationship("Job", back_populates="todo_items")
    skills = relationship("Skill", secondary=todo_skills, back_populates="todo_items")

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_title": self.job.title if self.job else "",
            "description": self.description,
            "status": self.status,
            "proficiency_required": self.proficiency_required,
            "skill_ids": [s.id for s in self.skills] if self.skills else [],
            "skill_names": [s.name for s in self.skills] if self.skills else [],
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
