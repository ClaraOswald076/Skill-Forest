"""Learning router — tutorial, chat, quiz, error book."""

import json as json_module
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.learning import (
    TutorialGenerateRequest, TutorialResponse,
    ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse, ChatSessionListItem,
    ChatSendRequest, ChatSendResponse,
    QuizGenerateRequest, QuizGenerateResponse, QuizSubmitRequest, QuizSubmitResponse,
    QuizAttemptResponse,
    ErrorBookEntryResponse, ErrorBookUpdate, ErrorStats,
)
from backend.services import learning_service

router = APIRouter(prefix="/api/learning", tags=["learning"])


# ── Tutorial ──

@router.post("/tutorial/generate", response_model=TutorialResponse)
def generate_tutorial(data: TutorialGenerateRequest, db: Session = Depends(get_db)):
    try:
        module = learning_service.get_or_generate_tutorial(
            db, data.todo_id, regenerate=data.regenerate
        )
        if not module:
            raise HTTPException(status_code=404, detail="Todo not found")
        return module.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"教程生成失败: {str(e)}")


@router.get("/tutorial/{todo_id}", response_model=TutorialResponse)
def get_tutorial(todo_id: int, db: Session = Depends(get_db)):
    module = learning_service.get_cached_tutorial(db, todo_id)
    if not module:
        raise HTTPException(status_code=404, detail="Tutorial not found. Generate first.")
    return module.to_dict()


# ── Chat ──

@router.post("/chat/sessions", response_model=ChatSessionResponse)
def create_chat_session(data: ChatSessionCreate, db: Session = Depends(get_db)):
    session = learning_service.create_chat_session(db, data.todo_id, data.title)
    return session.to_dict(include_messages=True)


@router.get("/chat/sessions", response_model=List[ChatSessionListItem])
def list_chat_sessions(todo_id: int, db: Session = Depends(get_db)):
    sessions = learning_service.list_chat_sessions(db, todo_id)
    return [s.to_dict() for s in sessions]


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    session = learning_service.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict(include_messages=True)


@router.delete("/chat/sessions/{session_id}")
def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    ok = learning_service.delete_chat_session(db, session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


@router.patch("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
def update_chat_session(session_id: int, data: ChatSessionUpdate, db: Session = Depends(get_db)):
    session = learning_service.update_chat_session(
        db, session_id, data.model_dump(exclude_unset=True)
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict(include_messages=True)


@router.post("/chat/send", response_model=ChatSendResponse)
def send_chat_message(data: ChatSendRequest, db: Session = Depends(get_db)):
    try:
        result = learning_service.send_chat_message(db, data.session_id, data.message)
        return ChatSendResponse(
            user_message=result["user_message"].to_dict(),
            ai_message=result["ai_message"].to_dict(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 服务调用失败: {str(e)}")


# ── Quiz ──

@router.post("/quiz/generate", response_model=QuizGenerateResponse)
def generate_quiz(data: QuizGenerateRequest, db: Session = Depends(get_db)):
    try:
        attempt = learning_service.generate_quiz(db, data.todo_id)
        questions_data = json_module.loads(attempt.questions_json)
        return QuizGenerateResponse(
            attempt_id=attempt.id,
            todo_id=attempt.todo_id,
            questions=questions_data.get("questions", []),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"题目生成失败: {str(e)}")


@router.get("/quiz/attempts", response_model=List[QuizAttemptResponse])
def list_quiz_attempts(todo_id: int, db: Session = Depends(get_db)):
    attempts = learning_service.list_quiz_attempts(db, todo_id)
    return [a.to_dict() for a in attempts]


@router.get("/quiz/attempts/{attempt_id}", response_model=QuizAttemptResponse)
def get_quiz_attempt(attempt_id: int, db: Session = Depends(get_db)):
    attempt = learning_service.get_quiz_attempt(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt.to_dict()


@router.post("/quiz/submit", response_model=QuizSubmitResponse)
def submit_quiz(data: QuizSubmitRequest, db: Session = Depends(get_db)):
    try:
        answers = [a.model_dump() for a in data.answers]
        grading = learning_service.submit_quiz(db, data.attempt_id, answers)
        return QuizSubmitResponse(attempt_id=data.attempt_id, **grading)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评分失败: {str(e)}")


# ── Error Book ──

@router.get("/errors", response_model=List[ErrorBookEntryResponse])
def list_errors(
    skill_id: Optional[int] = None,
    reviewed: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    entries = learning_service.get_error_entries(db, skill_id=skill_id, reviewed=reviewed)
    return [e.to_dict() for e in entries]


@router.get("/errors/stats", response_model=ErrorStats)
def get_error_stats(db: Session = Depends(get_db)):
    return learning_service.get_error_stats(db)


@router.patch("/errors/{entry_id}", response_model=ErrorBookEntryResponse)
def update_error(entry_id: int, data: ErrorBookUpdate, db: Session = Depends(get_db)):
    entry = learning_service.update_error_entry(
        db, entry_id, data.model_dump(exclude_unset=True)
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry.to_dict()


@router.delete("/errors/{entry_id}")
def delete_error(entry_id: int, db: Session = Depends(get_db)):
    ok = learning_service.delete_error_entry(db, entry_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"ok": True}
