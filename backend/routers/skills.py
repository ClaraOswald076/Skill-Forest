"""Skill router — CRUD + tree + merge."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.skill import SkillCreate, SkillUpdate, SkillResponse, MergeRequest
from backend.services import skill_service

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=List[SkillResponse])
def list_skills(
    status: Optional[str] = None,
    category_l1: Optional[str] = None,
    db: Session = Depends(get_db),
):
    skills = skill_service.get_skills(db, status=status, category_l1=category_l1)
    return [s.to_dict() for s in skills]


@router.get("/tree")
def get_skill_tree(db: Session = Depends(get_db)):
    tree = skill_service.get_skill_tree(db)
    return {"tree": tree}


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = skill_service.get_skill(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill.to_dict()


@router.post("", response_model=SkillResponse)
def create_skill(data: SkillCreate, db: Session = Depends(get_db)):
    skill = skill_service.create_skill(db, data)
    return skill.to_dict()


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(skill_id: int, data: SkillUpdate, db: Session = Depends(get_db)):
    skill = skill_service.update_skill(db, skill_id, data)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill.to_dict()


@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    ok = skill_service.delete_skill(db, skill_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"ok": True}


@router.post("/merge")
def merge_skills(data: MergeRequest, db: Session = Depends(get_db)):
    if data.source_id == data.target_id:
        raise HTTPException(status_code=400, detail="不能把技能合并进它自己")
    target = skill_service.merge_skills(db, data.source_id, data.target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Source or target skill not found")
    return {"ok": True, "merged_skill": target.to_dict()}
