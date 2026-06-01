"""Skill ORM model."""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from backend.database import Base
from backend.models.associations import skill_jobs, todo_skills


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, default="")
    category_l1 = Column(String(100), nullable=False, index=True)  # 大类
    category_l2 = Column(String(100), nullable=False, index=True)  # 中类
    category_l3 = Column(String(100), default="", index=True)       # 小类
    proficiency = Column(String(20), default="认识")    # 认识|熟悉|熟练|完全掌握
    status = Column(String(20), default="not_started") # not_started|in_progress|completed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Many-to-many: skills <-> jobs
    source_jobs = relationship("Job", secondary=skill_jobs, back_populates="skills")
    # Many-to-many: skills <-> todo_items
    todo_items = relationship("TodoItem", secondary=todo_skills, back_populates="skills")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_l1": self.category_l1,
            "category_l2": self.category_l2,
            "category_l3": self.category_l3,
            "proficiency": self.proficiency,
            "status": self.status,
            "source_job_ids": [j.id for j in self.source_jobs] if self.source_jobs else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
