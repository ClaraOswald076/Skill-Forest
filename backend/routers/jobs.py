"""Job router — CRUD + save with analysis."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.job import JobCreate, JobResponse, JobDetailResponse
from backend.schemas.analysis import JobSaveRequest
from backend.services import job_service, skill_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    jobs = job_service.get_jobs(db)
    return [j.to_dict() for j in jobs]


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = job.to_dict()
    result["skills"] = [s.to_dict() for s in job.skills] if job.skills else []
    result["todos"] = [t.to_dict() for t in job.todo_items] if job.todo_items else []
    return result


@router.post("", response_model=JobDetailResponse)
def create_job_with_analysis(data: JobSaveRequest, db: Session = Depends(get_db)):
    """Save a job with pre-analyzed skills and todos."""
    result = job_service.save_job_with_analysis(db, data)
    job = result["job"]
    resp = job.to_dict()
    resp["skills"] = [s.to_dict() for s in job.skills] if job.skills else []
    resp["todos"] = [t.to_dict() for t in job.todo_items] if job.todo_items else []
    for key in ("skills_created", "skills_merged", "skills_deduped", "todos_created"):
        resp[key] = result[key]
    return resp


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    ok = job_service.delete_job(db, job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"ok": True}
