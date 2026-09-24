"""岗位保存对 LLM 重名技能输出的容错回归测试。

背景：分析 LLM 偶尔对同一技能返回两条同名条目（分类不同）。此前
save_job_with_analysis 逐条新建不做提交内去重：同名 Skill 落库两条、
技能树出现重复节点，且 skill_map 被后者覆盖导致 todo 只挂到后一条。

运行：python -m pytest tests/ -q（需自备 pytest，运行时依赖同 requirements.txt）
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models.skill import Skill
from backend.models.todo_item import TodoItem
from backend.schemas.analysis import JobSaveRequest
from backend.services import job_service


def _env():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _request(skills, todos, merge_decisions=None):
    return JobSaveRequest(
        raw_text="熟练掌握 Python；熟悉 Python 数据处理生态。",
        title="数据工程师",
        skills=skills,
        todos=todos,
        merge_decisions=merge_decisions or {},
    )


def test_same_name_skills_deduped_within_one_submission():
    # 空库、零合并决策：同名双条只落库一条，todo 关联到保留的那条
    db = _env()
    result = job_service.save_job_with_analysis(db, _request(
        skills=[
            {"name": "Python", "description": "语言本体", "category_l1": "编程语言",
             "category_l2": "Python", "proficiency": "熟练",
             "merge_with_existing_id": None, "merge_confidence": 0.0},
            {"name": "Python", "description": "数据处理生态", "category_l1": "编程语言",
             "category_l2": "Python", "category_l3": "数据处理", "proficiency": "熟悉",
             "merge_with_existing_id": None, "merge_confidence": 0.0},
        ],
        todos=[{"description": "用 Python 写一个异步爬虫",
                "skill_names": ["Python"], "proficiency_required": "熟练"}],
    ))

    skills = db.query(Skill).all()
    assert [s.name for s in skills] == ["Python"]
    assert skills[0].description == "语言本体"  # 保留先出现的条目

    todo = db.query(TodoItem).first()
    assert [s.id for s in todo.skills] == [skills[0].id]

    assert result["skills_created"] == 1
    assert result["skills_deduped"] == 1
    assert result["todos_created"] == 1


def test_distinct_names_and_merge_path_unaffected():
    # 不同名条目正常落库；指向已有技能的合并决策也不受去重影响
    db = _env()
    existing = Skill(name="HTTP 基础", category_l1="计算机网络", category_l2="协议")
    db.add(existing)
    db.commit()

    result = job_service.save_job_with_analysis(db, _request(
        skills=[
            {"name": "HTTP 基础", "description": "状态码与握手", "category_l1": "计算机网络",
             "category_l2": "协议", "proficiency": "熟悉",
             "merge_with_existing_id": existing.id, "merge_confidence": 0.9},
            {"name": "Nginx", "description": "反向代理", "category_l1": "框架与工具",
             "category_l2": "Web 服务", "proficiency": "认识",
             "merge_with_existing_id": None, "merge_confidence": 0.0},
        ],
        todos=[{"description": "配置一次反向代理",
                "skill_names": ["Nginx"], "proficiency_required": "认识"}],
        merge_decisions={"HTTP 基础": "merge"},
    ))

    names = sorted(s.name for s in db.query(Skill).all())
    assert names == ["HTTP 基础", "Nginx"]
    assert result["skills_merged"] == 1
    assert result["skills_created"] == 1
    assert result["skills_deduped"] == 0
