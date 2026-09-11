"""Analysis router — DeepSeek-powered job requirement analysis."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.services import skill_service, deepseek_service

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/preview", response_model=AnalysisResponse)
def preview_analysis(data: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze job requirements text and return structured results.
    Does NOT save anything — just preview for user confirmation.
    """
    # Get all existing skills for context
    existing_skills = skill_service.get_all_skills_as_dicts(db)

    # Call DeepSeek
    try:
        result = deepseek_service.analyze_job_requirements(
            raw_text=data.raw_text,
            existing_skills=existing_skills,
            job_title=data.job_title,
            company=data.company,
        )
    except deepseek_service.AnalysisError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result
