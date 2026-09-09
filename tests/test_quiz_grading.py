"""评分链路对 LLM 输出漂移的容错回归测试。

背景：评分 LLM 返回的 JSON 形状不可控。此前 submit_quiz 把原始 dict 直接透传，
顶层多一个 attempt_id 键响应必 500；results 缺 q_number 错题本整批丢失且无法重交。

运行：python -m pytest tests/ -q（需自备 pytest，运行时依赖同 requirements.txt）
"""
import json

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models.job import Job
from backend.models.learning import QuizAttempt, ErrorBook
from backend.models.skill import Skill
from backend.models.todo_item import TodoItem
from backend.routers.learning import submit_quiz as submit_quiz_route
from backend.schemas.learning import QuizSubmitRequest
from backend.services import learning_service


class _Msg:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content):
        self.message = _Msg(content)


class _Resp:
    def __init__(self, content):
        self.choices = [_Choice(content)]


class StubClient:
    def __init__(self, content):
        self.chat = type("Chat", (), {})()
        self.chat.completions = type("Completions", (), {})()
        self.chat.completions.create = lambda **kw: _Resp(content)


QUESTIONS = {"questions": [
    {
        "q_number": 1,
        "question_type": "choice",
        "question_text": "HTTP 302 表示什么？",
        "options": ["A. 永久重定向", "B. 临时重定向", "C. 未找到", "D. 服务器错误"],
        "correct_answer": "B",
    },
]}


@pytest.fixture
def env():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    job = Job(title="后端工程师", raw_text="jd")
    session.add(job)
    session.flush()
    skill = Skill(name="HTTP 基础", category_l1="计算机网络", category_l2="协议")
    session.add(skill)
    session.flush()
    todo = TodoItem(job_id=job.id, description="掌握 HTTP 状态码")
    todo.skills.append(skill)
    session.add(todo)
    session.flush()
    attempt = QuizAttempt(todo_id=todo.id, questions_json=json.dumps(QUESTIONS, ensure_ascii=False))
    session.add(attempt)
    session.commit()
    yield session, attempt.id
    session.close()


def _grade(session, attempt_id, payload):
    learning_service.client = StubClient(json.dumps(payload, ensure_ascii=False))
    req = QuizSubmitRequest(attempt_id=attempt_id, answers=[{"q_number": 1, "answer": "B"}])
    return submit_quiz_route(data=req, db=session)


def test_extra_top_level_key_is_dropped(env):
    # LLM 自作主张多带 attempt_id 键：旧版响应必 500，但分数其实已入库
    session, attempt_id = env
    resp = _grade(session, attempt_id, {
        "attempt_id": 999,
        "results": [{"q_number": 1, "score": 2, "max_score": 2, "is_correct": True}],
        "total_score": 2,
        "max_score": 60,
        "overall_feedback": "全对",
    })
    assert resp.attempt_id == attempt_id
    assert resp.total_score == 2


def test_result_missing_q_number_is_skipped_not_fatal(env):
    # 一条结果缺 q_number（写成了 q_no）：旧版 KeyError 500、错题本整批丢失
    session, attempt_id = env
    resp = _grade(session, attempt_id, {
        "results": [
            {"q_no": 1, "score": 0, "max_score": 2, "is_correct": False, "explanation": "坏条目"},
            {"q_number": 1, "score": 0, "max_score": 2, "is_correct": False, "explanation": "答错了"},
        ],
        "total_score": 0,
        "max_score": 60,
        "overall_feedback": "需要复习 HTTP 重定向",
    })
    assert len(resp.results) == 1
    assert resp.results[0].explanation == "答错了"
    # 答错的题要进错题本，缺键的那条跳过但不拖垮整卷
    assert session.query(ErrorBook).count() == 1


def test_non_object_grading_rejected_before_commit(env):
    # 合法 JSON 但不是对象：必须 400 且 submitted_at 不落，用户能直接重交
    session, attempt_id = env
    with pytest.raises(HTTPException) as exc:
        _grade(session, attempt_id, ["抱歉，我无法按格式返回"])
    assert exc.value.status_code == 400
    attempt = session.get(QuizAttempt, attempt_id)
    assert attempt.submitted_at is None
    assert session.query(ErrorBook).count() == 0

    # 同一份答卷换成正常输出后立即可重交成功
    resp = _grade(session, attempt_id, {
        "results": [{"q_number": 1, "score": 2, "max_score": 2, "is_correct": True}],
        "total_score": 2,
        "max_score": 60,
        "overall_feedback": "全对",
    })
    assert resp.total_score == 2


def test_malformed_json_is_retryable(env):
    # 压根不是 JSON：400、未提交、可重交（与旧版行为一致，但确认没有误伤重试路径）
    session, attempt_id = env
    learning_service.client = StubClient("这不是 JSON")
    req = QuizSubmitRequest(attempt_id=attempt_id, answers=[{"q_number": 1, "answer": "B"}])
    with pytest.raises(HTTPException) as exc:
        submit_quiz_route(data=req, db=session)
    assert exc.value.status_code == 400
    attempt = session.get(QuizAttempt, attempt_id)
    assert attempt.submitted_at is None
