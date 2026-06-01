"""Job ORM model."""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from backend.database import Base
from backend.models.associations import skill_jobs


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(300), default="")
    company = Column(String(200), default="")
    url = Column(String(1000), default="")
    raw_text = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=func.now())

    # Many-to-many: jobs <-> skills
    skills = relationship("Skill", secondary=skill_jobs, back_populates="source_jobs")
    # One-to-many: job -> todo_items
    todo_items = relationship("TodoItem", back_populates="job", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "url": self.url or "",
            "raw_text": self.raw_text or "",
            "skill_ids": [s.id for s in self.skills] if self.skills else [],
            "skill_count": len(self.skills) if self.skills else 0,
            "todo_count": len(self.todo_items) if self.todo_items else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
