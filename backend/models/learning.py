"""Learning module ORM models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base


class LearningModule(Base):
    """Cached AI-generated tutorial for a todo item."""
    __tablename__ = "learning_modules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    todo_id = Column(Integer, ForeignKey("todo_items.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tutorial_content = Column(Text, nullable=False)
    tutorial_version = Column(Integer, default=1)
    last_generated_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    todo = relationship("TodoItem", backref="learning_module", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "todo_id": self.todo_id,
            "tutorial_content": self.tutorial_content,
            "tutorial_version": self.tutorial_version,
            "last_generated_at": self.last_generated_at.isoformat() if self.last_generated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChatSession(Base):
    """A chat conversation session for a todo item."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    todo_id = Column(Integer, ForeignKey("todo_items.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), default="新对话")
    deep_thinking = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan",
                            order_by="ChatMessage.created_at")
    todo = relationship("TodoItem", backref="chat_sessions")

    def to_dict(self, include_messages=False):
        d = {
            "id": self.id,
            "todo_id": self.todo_id,
            "title": self.title,
            "deep_thinking": self.deep_thinking,
            "message_count": len(self.messages) if self.messages else 0,
            "last_message_preview": self.messages[-1].content[:80] if self.messages else "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_messages:
            d["messages"] = [m.to_dict() for m in self.messages] if self.messages else []
        return d


class ChatMessage(Base):
    """A single message in a chat session."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(10), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    reasoning_content = Column(Text, default="")
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    session = relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "reasoning_content": self.reasoning_content or "",
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class QuizAttempt(Base):
    """A quiz attempt for a todo item."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    todo_id = Column(Integer, ForeignKey("todo_items.id", ondelete="CASCADE"), nullable=False, index=True)
    questions_json = Column(Text, nullable=False)  # Full quiz JSON from DeepSeek
    answers_json = Column(Text, default="{}")       # User's answers
    started_at = Column(DateTime, default=func.now())
    submitted_at = Column(DateTime, nullable=True)
    graded_json = Column(Text, default="")          # Grading results JSON
    total_score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())

    todo = relationship("TodoItem", backref="quiz_attempts")

    def to_dict(self):
        return {
            "id": self.id,
            "todo_id": self.todo_id,
            "questions_json": self.questions_json,
            "answers_json": self.answers_json,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "graded_json": self.graded_json,
            "total_score": self.total_score,
            "max_score": self.max_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ErrorBook(Base):
    """Persistent error notebook — wrong answers saved across quiz attempts."""
    __tablename__ = "error_book"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="SET NULL"), nullable=True, index=True)
    todo_id = Column(Integer, ForeignKey("todo_items.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    question_type = Column(String(20), nullable=False)  # "choice" | "essay" | "definition"
    question_text = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    reviewed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    reviewed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_attempt_id": self.quiz_attempt_id,
            "todo_id": self.todo_id,
            "skill_id": self.skill_id,
            "question_type": self.question_type,
            "question_text": self.question_text,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "reviewed": self.reviewed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
