"""聊天链路对 LLM 失败的回归测试。

背景：此前 send_chat_message 在 LLM 抛异常时把 str(e) 拼成伪 assistant 消息落库，
前端渲染成一条正常回复无法区分，且异常原文会随后续每轮请求回传给 LLM 当上下文。

运行：python -m pytest tests/ -q（需自备 pytest，运行时依赖同 requirements.txt）
"""
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models.job import Job
from backend.models.learning import ChatSession, ChatMessage
from backend.models.todo_item import TodoItem
from backend.routers.learning import send_chat_message as send_chat_route
from backend.schemas.learning import ChatSendRequest
from backend.services import learning_service


class _ExplodingCreate:
    def create(self, **kw):
        raise RuntimeError("Error code: 401 - Invalid API key")


class _BrokenClient:
    def __init__(self):
        self.chat = type("Chat", (), {})()
        self.chat.completions = _ExplodingCreate()


class _Msg:
    def __init__(self, content):
        self.content = content
        self.reasoning_content = ""


class _Choice:
    def __init__(self, content):
        self.message = _Msg(content)


class _Resp:
    def __init__(self, content):
        self.choices = [_Choice(content)]
        self.usage = None


class _RecordingCreate:
    def __init__(self):
        self.calls = []

    def create(self, **kw):
        self.calls.append(kw)
        return _Resp("好的，正常回复。")


class _GoodClient:
    def __init__(self):
        self.chat = type("Chat", (), {})()
        self.chat.completions = _RecordingCreate()


@pytest.fixture
def env():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    job = Job(title="后端", raw_text="jd")
    session.add(job)
    session.flush()
    todo = TodoItem(job_id=job.id, description="掌握 HTTP")
    session.add(todo)
    session.flush()
    chat = ChatSession(todo_id=todo.id)
    session.add(chat)
    session.commit()
    yield session, chat.id
    session.close()


def _send(session, chat_id, message="什么是三次握手？"):
    return send_chat_route(data=ChatSendRequest(session_id=chat_id, message=message), db=session)


def test_llm_failure_returns_502_without_fake_reply(env):
    # LLM 挂掉必须 502，且库里只有用户的发言，没有伪 assistant 回复
    session, chat_id = env
    learning_service.client = _BrokenClient()
    with pytest.raises(HTTPException) as exc:
        _send(session, chat_id)
    assert exc.value.status_code == 502
    messages = session.query(ChatMessage).filter(ChatMessage.session_id == chat_id).all()
    assert [m.role for m in messages] == ["user"]
    assert all("Invalid API key" not in (m.content or "") for m in messages)


def test_failure_text_never_replayed_into_next_context(env):
    # 失败的下一轮请求，回传给 LLM 的上下文里不得出现异常原文
    session, chat_id = env
    learning_service.client = _BrokenClient()
    with pytest.raises(HTTPException):
        _send(session, chat_id)

    good = _GoodClient()
    learning_service.client = good
    _send(session, chat_id, "那我该先学什么？")
    history = [m["content"] for m in good.chat.completions.calls[0]["messages"] if m["role"] != "system"]
    assert all("Invalid API key" not in c for c in history)
    assert any("什么是三次握手？" in c for c in history)


def test_success_still_persists_both_messages(env):
    # 正常路径不受影响：用户与 AI 两条消息都落库
    session, chat_id = env
    learning_service.client = _GoodClient()
    resp = _send(session, chat_id)
    assert resp.ai_message.content == "好的，正常回复。"
    roles = [m.role for m in session.query(ChatMessage).filter(ChatMessage.session_id == chat_id).all()]
    assert roles == ["user", "assistant"]
