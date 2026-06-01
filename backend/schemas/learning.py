"""Pydantic schemas for learning module."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Tutorial ──

class TutorialGenerateRequest(BaseModel):
    todo_id: int
    regenerate: bool = False


class TutorialResponse(BaseModel):
    id: int
    todo_id: int
    tutorial_content: str
    tutorial_version: int
    last_generated_at: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ── Chat ──

class ChatSessionCreate(BaseModel):
    todo_id: int
    title: str = "新对话"


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    deep_thinking: Optional[bool] = None


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    reasoning_content: str = ""
    tokens_used: int = 0
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class ChatSessionListItem(BaseModel):
    id: int
    todo_id: int
    title: str
    deep_thinking: bool = False
    message_count: int = 0
    last_message_preview: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    todo_id: int
    title: str
    deep_thinking: bool = False
    messages: List[ChatMessageResponse] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ChatSendRequest(BaseModel):
    session_id: int
    message: str


class ChatSendResponse(BaseModel):
    user_message: ChatMessageResponse
    ai_message: ChatMessageResponse


# ── Quiz ──

class QuizGenerateRequest(BaseModel):
    todo_id: int


class QuizQuestion(BaseModel):
    q_number: int
    question_type: str  # "choice" | "essay" | "definition"
    question_text: str
    options: List[str] = []  # only for choice type
    correct_answer: str = ""


class QuizGenerateResponse(BaseModel):
    attempt_id: int
    todo_id: int
    questions: List[QuizQuestion] = []


class QuizAnswer(BaseModel):
    q_number: int
    answer: str


class QuizSubmitRequest(BaseModel):
    attempt_id: int
    answers: List[QuizAnswer] = []


class GradedResult(BaseModel):
    q_number: int
    score: float
    max_score: float
    is_correct: bool
    explanation: str = ""


class QuizSubmitResponse(BaseModel):
    attempt_id: int
    results: List[GradedResult] = []
    total_score: float = 0
    max_score: float = 0
    overall_feedback: str = ""


class QuizAttemptResponse(BaseModel):
    id: int
    todo_id: int
    questions_json: str = ""
    answers_json: str = ""
    started_at: Optional[str] = None
    submitted_at: Optional[str] = None
    graded_json: str = ""
    total_score: Optional[float] = None
    max_score: Optional[float] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ── Error Book ──

class ErrorBookEntryResponse(BaseModel):
    id: int
    quiz_attempt_id: Optional[int] = None
    todo_id: int
    skill_id: Optional[int] = None
    question_type: str
    question_text: str
    user_answer: str
    correct_answer: str
    explanation: str = ""
    reviewed: bool = False
    created_at: Optional[str] = None
    reviewed_at: Optional[str] = None

    class Config:
        from_attributes = True


class ErrorBookUpdate(BaseModel):
    reviewed: Optional[bool] = None


class ErrorStats(BaseModel):
    total: int = 0
    reviewed: int = 0
    unreviewed: int = 0
    by_skill: List[dict] = []
