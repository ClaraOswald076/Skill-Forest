"""学习任务回链技能的容错回归测试。

背景：todos[].skill_names 与 skills[].name 是 LLM 输出的两个独立字段，旧版只做
字面精确匹配，大小写/首尾空白/引用合并目标名一律静默丢关联且无任何提示。

运行：python -m pytest tests/ -q（需自备 pytest，运行时依赖同 requirements.txt）
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.skill import Skill
from backend.services.job_service import save_job_with_analysis
from backend.schemas.analysis import JobSaveRequest


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _save(db, todos, skills=None, merge_decisions=None):
    """跑一遍完整保存流程，返回 (result, {描述: 关联技能名列表})。"""
    pre = Skill(name="PyTorch", description="已有技能",
                category_l1="AI/机器学习", category_l2="机器学习框架")
    db.add(pre)
    db.commit()
    req = JobSaveRequest(
        raw_text="熟练掌握 PyTorch、Docker、机器学习",
        title="算法工程师",
        skills=skills or [
            {"name": "PyTorch框架", "description": "d", "category_l1": "AI/机器学习",
             "category_l2": "机器学习框架", "merge_with_existing_id": pre.id},
            {"name": "Docker", "description": "d", "category_l1": "框架与工具", "category_l2": "DevOps工具"},
            {"name": "机器学习", "description": "d", "category_l1": "AI/机器学习", "category_l2": "机器学习框架"},
        ],
        todos=todos,
        merge_decisions=merge_decisions or {"PyTorch框架": "merge"},
    )
    res = save_job_with_analysis(db, req)
    linked = {t.description: [s.name for s in t.skills] for t in res["job"].todo_items}
    return res, linked


def test_exact_match_control(db):
    # 对照组：字面精确命中行为不变
    res, linked = _save(db, [{"description": "T1", "skill_names": ["Docker"]}])
    assert linked["T1"] == ["Docker"]
    assert res["links_unmatched"] == []


def test_case_and_whitespace_paraphrase_still_link(db):
    # 大小写、首尾空白这类同义改写不应丢关联
    res, linked = _save(db, [
        {"description": "T2", "skill_names": ["pytorch"]},
        {"description": "T3", "skill_names": ["Docker "]},
    ])
    assert linked["T2"] == ["PyTorch"]
    assert linked["T3"] == ["Docker"]
    assert res["links_unmatched"] == []


def test_merge_alias_reference_links(db):
    # merge 路径：todo 引用「已存在技能」的名字，旧版以提取名为键必然 miss
    res, linked = _save(db, [{"description": "T5", "skill_names": ["PyTorch"]}])
    assert linked["T5"] == ["PyTorch"]
    assert res["skills_merged"] == 1


def test_untranslatable_name_reported_not_linked(db):
    # 中英改写超出猜测能力：保持不关联，但必须有记录可查，不再静默
    res, linked = _save(db, [{"description": "T4", "skill_names": ["Machine Learning"]}])
    assert linked["T4"] == []
    assert len(res["links_unmatched"]) == 1
    entry = res["links_unmatched"][0]
    assert entry["skill_names"] == ["Machine Learning"]
    assert entry["description"] == "T4"
    assert entry["todo_id"] is not None
