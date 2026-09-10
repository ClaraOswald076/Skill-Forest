"""技能合并端点对 source==target 的守卫回归测试。

背景：merge_skills 不检查 source 与 target 是否同一行。source==target 时
db.delete(source) 会把目标技能自己删掉并提交，随后 refresh 已删的行抛
ObjectDeletedError → 500——用户看到"服务器错误"，实际删除已生效。

运行：python -m pytest tests/ -q（需自备 pytest，运行时依赖同 requirements.txt）
"""
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
from backend.routers.skills import merge_skills as merge_skills_route
from backend.schemas.skill import MergeRequest


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    yield session
    session.close()
    engine.dispose()


def _make_skill(db, name, **kw):
    skill = Skill(name=name, category_l1="大类", category_l2="中类", **kw)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def test_merge_rejects_same_source_and_target(db):
    skill = _make_skill(db, "Python")

    with pytest.raises(HTTPException) as exc_info:
        merge_skills_route(MergeRequest(source_id=skill.id, target_id=skill.id), db)

    assert exc_info.value.status_code == 400
    # 技能必须原地不动：不能被"合并进自己"删掉
    assert db.query(Skill).filter(Skill.id == skill.id).first() is not None


def test_merge_distinct_skills_still_works(db):
    source = _make_skill(db, "Python", description="基础语法")
    target = _make_skill(db, "Python 进阶")

    result = merge_skills_route(
        MergeRequest(source_id=source.id, target_id=target.id), db
    )

    assert result["ok"] is True
    assert db.query(Skill).filter(Skill.id == source.id).first() is None
    merged = db.query(Skill).filter(Skill.id == target.id).first()
    assert merged is not None
    assert "基础语法" in merged.description
