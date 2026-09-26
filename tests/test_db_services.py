"""service 层数据库读写路径的回归测试（skill / todo / job / dashboard）。

背景：此前 service 层与数据库交互零覆盖，历史上 #5/#16/#23 等缺陷都出在
service/DB 层。本文件用内存 SQLite（StaticPool）按用例隔离建表，
只测当前 main 的真实行为，LLM 边界完全不参与（这些服务本身不依赖 LLM）。

说明：backend.database 在 import 时会创建 <仓库>/data 目录并构建引擎，
但本文件所有用例都使用独立的内存库，绝不连接真实引擎，不产生 data/skilltree.db。

运行：python -m pytest tests/ -q（需先 pip install -r requirements-dev.txt，
另需 requirements.txt 中的 sqlalchemy/pydantic/python-dotenv/openai/fastapi）
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models.job import Job
from backend.models.skill import Skill
from backend.models.todo_item import TodoItem
from backend.services import dashboard_service, job_service, skill_service, todo_service
from backend.schemas.job import JobCreate
from backend.schemas.skill import SkillCreate, SkillUpdate
from backend.schemas.todo import TodoCreate, TodoUpdate
from backend.schemas.analysis import ExtractedSkill, GeneratedTodo, JobSaveRequest


@pytest.fixture
def db():
    """每个用例独立的内存 SQLite：共享单连接，按需建表，用例结束即销毁。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


def _make_skill(db, name, l1="编程语言", l2="Python", l3="", proficiency="认识",
                status="not_started", description=""):
    """种子技能：category_l1/l2 非空，必须带。"""
    skill = Skill(name=name, category_l1=l1, category_l2=l2, category_l3=l3,
                  proficiency=proficiency, status=status, description=description)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def _make_job(db, title="测试岗位", raw_text="jd 原文"):
    job = Job(title=title, raw_text=raw_text)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def _make_todo(db, job_id, description="任务", status="pending"):
    todo = TodoItem(job_id=job_id, description=description, status=status)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# ─── skill_service ───────────────────────────────────────

def test_create_skill_persists_with_defaults(db):
    skill = skill_service.create_skill(db, SkillCreate(
        name="FastAPI", description="Web 框架", category_l1="编程语言", category_l2="Python",
    ))
    assert skill.id is not None
    # 未显式传入的字段走模型/列默认值
    assert skill.proficiency == "认识"
    assert skill.status == "not_started"
    assert skill.category_l3 == ""
    # 真的落库了：重新查一遍
    assert db.query(Skill).filter(Skill.name == "FastAPI").count() == 1


def test_get_skills_filters_by_status_and_category(db):
    _make_skill(db, "Python", l1="编程语言", l2="Python", status="completed")
    _make_skill(db, "Django", l1="编程语言", l2="Python", status="not_started")
    _make_skill(db, "SQL", l1="数据库", l2="SQL")

    assert [s.name for s in skill_service.get_skills(db, status="completed")] == ["Python"]
    assert [s.name for s in skill_service.get_skills(db, category_l1="数据库")] == ["SQL"]
    # 组合过滤：编程语言大类下未开始的是 Django
    assert [s.name for s in skill_service.get_skills(db, status="not_started", category_l1="编程语言")] == ["Django"]
    # 组合过滤无结果不报错
    assert skill_service.get_skills(db, status="completed", category_l1="数据库") == []
    # 无过滤时按 l1/l2/l3/name 排序返回全部
    # （SQLite 文本比较按字节序：中文“数”的字节小于“编”，故“数据库”组排在前面）
    assert [s.name for s in skill_service.get_skills(db)] == ["SQL", "Django", "Python"]


def test_get_skill_and_find_by_name(db):
    skill = _make_skill(db, "Docker")
    assert skill_service.get_skill(db, skill.id).name == "Docker"
    assert skill_service.get_skill(db, 99999) is None
    assert skill_service.find_skill_by_name(db, "Docker").id == skill.id
    # 精确匹配，不做模糊/大小写归一
    assert skill_service.find_skill_by_name(db, "docker") is None
    assert skill_service.find_skill_by_name(db, "不存在的技能") is None


def test_get_all_skills_as_dicts_shape(db):
    skill = _make_skill(db, "Python", l1="编程语言", l2="Python", l3="基础", description="脚本语言")
    dicts = skill_service.get_all_skills_as_dicts(db)
    assert dicts == [{
        "id": skill.id,
        "name": "Python",
        "description": "脚本语言",
        "category_l1": "编程语言",
        "category_l2": "Python",
        "category_l3": "基础",
    }]


def test_update_skill_partial_update_keeps_other_fields(db):
    skill = _make_skill(db, "Python", proficiency="认识")
    updated = skill_service.update_skill(db, skill.id, SkillUpdate(proficiency="熟练"))
    # exclude_unset：只改传入的字段
    assert updated.proficiency == "熟练"
    assert updated.name == "Python"
    assert updated.status == "not_started"


def test_update_skill_missing_returns_none(db):
    assert skill_service.update_skill(db, 424242, SkillUpdate(name="X")) is None


def test_delete_skill_returns_true_then_false(db):
    skill = _make_skill(db, "临时技能")
    assert skill_service.delete_skill(db, skill.id) is True
    assert db.query(Skill).count() == 0
    # 再删同一个 id：不存在，返回 False
    assert skill_service.delete_skill(db, skill.id) is False


def test_merge_skills_transfers_associations_and_deletes_source(db):
    job_a = _make_job(db, title="岗位A")
    job_b = _make_job(db, title="岗位B")
    source = _make_skill(db, "Python 基础", proficiency="熟练", description="来源补充",
                         l1="编程语言", l2="Python")
    target = _make_skill(db, "Python", proficiency="认识", description="目标描述",
                         l1="编程语言", l2="Python")
    source.source_jobs.append(job_a)
    target.source_jobs.append(job_b)
    todo = _make_todo(db, job_a.id, description="学 Python")
    todo.skills.append(source)
    db.commit()

    merged = skill_service.merge_skills(db, source.id, target.id)

    # 源被删、返回目标
    assert merged.id == target.id
    assert skill_service.get_skill(db, source.id) is None
    assert db.query(Skill).count() == 1
    # 岗位关联转移：目标现在挂 A、B 两个岗位
    assert {j.title for j in merged.source_jobs} == {"岗位A", "岗位B"}
    # 任务关联转移：原挂源技能的 todo 现在挂目标
    db.refresh(todo)
    assert [s.id for s in todo.skills] == [target.id]
    # 熟练(3) > 认识(1)：取源的高掌握度
    assert merged.proficiency == "熟练"
    # 描述拼接：目标描述 + "; " + 来源补充
    assert merged.description == "目标描述; 来源补充"


def test_merge_skills_keeps_higher_target_proficiency(db):
    source = _make_skill(db, "技能甲", proficiency="认识", description="补充说明")
    target = _make_skill(db, "技能乙", proficiency="完全掌握", description="补充说明")
    merged = skill_service.merge_skills(db, source.id, target.id)
    # 目标掌握度更高：保持不变
    assert merged.proficiency == "完全掌握"
    # 源描述已是目标描述的子串：不重复拼接
    assert merged.description == "补充说明"


def test_merge_skills_missing_side_returns_none_and_keeps_both(db):
    a = _make_skill(db, "技能甲")
    b = _make_skill(db, "技能乙")
    assert skill_service.merge_skills(db, a.id, 987654) is None
    assert skill_service.merge_skills(db, 987654, b.id) is None
    # 守卫路径不应误删任何一侧
    assert {s.name for s in db.query(Skill).all()} == {"技能甲", "技能乙"}


def test_get_skill_tree_nests_levels(db):
    # 空 l3 且该 l2 下唯一：技能直接挂在 l2 下
    solo = _make_skill(db, "SQL", l1="数据库", l2="SQL")
    # 命名 l3：先挂 l3 节点，技能再挂 l3 下
    other = _make_skill(db, "FastAPI", l1="编程语言", l2="Python", l3="Web 框架")
    tree = skill_service.get_skill_tree(db)

    # 树顶层按 l1 字节序排（“数” < “编”）
    assert [node["title"] for node in tree] == ["数据库", "编程语言"]
    python_l2 = tree[1]["children"][0]
    assert python_l2["key"] == "l2:编程语言/Python"
    # l2 下：一个 l3 节点（内含 FastAPI）
    assert [c["type"] for c in python_l2["children"]] == ["l3"]
    l3_node = python_l2["children"][0]
    assert l3_node["key"] == "l3:编程语言/Python/Web 框架"
    assert l3_node["children"][0]["skill"]["id"] == other.id
    # 数据库 l2 下：l3 为空且唯一，技能直接挂 l2
    sql_l2 = tree[0]["children"][0]
    assert sql_l2["children"][0]["type"] == "skill"
    assert sql_l2["children"][0]["skill"]["id"] == solo.id


# ─── todo_service ────────────────────────────────────────

def test_create_todo_links_skills_with_defaults(db):
    job = _make_job(db)
    s1 = _make_skill(db, "技能一")
    s2 = _make_skill(db, "技能二")
    todo = todo_service.create_todo(db, TodoCreate(
        job_id=job.id, description="掌握两者", skill_ids=[s1.id, s2.id],
    ))
    assert todo.status == "pending"          # 列默认值
    assert todo.proficiency_required == "熟悉"
    assert {s.id for s in todo.skills} == {s1.id, s2.id}


def test_get_todos_filters_by_job_status_skill(db):
    job_a = _make_job(db, title="岗位A")
    job_b = _make_job(db, title="岗位B")
    skill = _make_skill(db, "技能一")
    t1 = todo_service.create_todo(db, TodoCreate(job_id=job_a.id, description="任务1",
                                                 skill_ids=[skill.id]))
    t2 = todo_service.create_todo(db, TodoCreate(job_id=job_b.id, description="任务2"))
    todo_service.update_todo(db, t2.id, TodoUpdate(status="completed"))

    assert {t.id for t in todo_service.get_todos(db, job_id=job_a.id)} == {t1.id}
    assert {t.id for t in todo_service.get_todos(db, status="completed")} == {t2.id}
    assert {t.id for t in todo_service.get_todos(db, skill_id=skill.id)} == {t1.id}
    # 组合过滤无结果不报错
    assert todo_service.get_todos(db, job_id=job_b.id, status="pending") == []
    assert len(todo_service.get_todos(db)) == 2


def test_get_todo_returns_none_for_missing(db):
    assert todo_service.get_todo(db, 777) is None


def test_update_todo_status_transitions(db):
    job = _make_job(db)
    todo = todo_service.create_todo(db, TodoCreate(job_id=job.id, description="原始描述"))

    step1 = todo_service.update_todo(db, todo.id, TodoUpdate(status="in_progress"))
    assert step1.status == "in_progress"
    assert step1.description == "原始描述"   # 部分更新不动其他字段

    step2 = todo_service.update_todo(db, todo.id, TodoUpdate(status="completed"))
    assert step2.status == "completed"

    assert todo_service.update_todo(db, 88888, TodoUpdate(status="completed")) is None


def test_update_todo_replaces_skill_set(db):
    job = _make_job(db)
    s1 = _make_skill(db, "技能一")
    s2 = _make_skill(db, "技能二")
    todo = todo_service.create_todo(db, TodoCreate(job_id=job.id, description="任务",
                                                   skill_ids=[s1.id, s2.id]))
    updated = todo_service.update_todo(db, todo.id, TodoUpdate(skill_ids=[s2.id]))
    assert [s.id for s in updated.skills] == [s2.id]


# ─── job_service ─────────────────────────────────────────

def test_create_job_fills_defaults(db):
    job = job_service.create_job(db, JobCreate(raw_text="一段 JD", title=""))
    # 空 title 落默认值，url 归一成空串
    assert job.title == "未命名岗位"
    assert job.url == ""
    assert job.raw_text == "一段 JD"


def test_get_job_missing_returns_none(db):
    assert job_service.get_job(db, 31337) is None


def test_delete_job_cleans_orphan_skill_keeps_shared_and_todo_backed(db):
    job_a = _make_job(db, title="岗位A")
    job_b = _make_job(db, title="岗位B")
    orphan = _make_skill(db, "孤儿技能")            # 只属于 A、无任务 → 随岗位删除
    shared = _make_skill(db, "共享技能")            # A、B 共有 → 保留
    todo_backed = _make_skill(db, "有任务的技能")    # 只属于 A 但有任务 → 保留
    for s in (orphan, shared, todo_backed):
        s.source_jobs.append(job_a)
    shared.source_jobs.append(job_b)
    todo = _make_todo(db, job_a.id, description="保技能的任务")
    todo.skills.append(todo_backed)
    db.commit()

    assert job_service.delete_job(db, job_a.id) is True
    assert job_service.delete_job(db, job_a.id) is False  # 重复删除返回 False

    remaining = {s.name for s in db.query(Skill).all()}
    assert remaining == {"共享技能", "有任务的技能"}
    # 共享技能与 B 的关联保留、与 A 的关联随岗位消失
    db.refresh(shared)
    assert [j.title for j in shared.source_jobs] == ["岗位B"]
    # 级联删除：A 的任务一并消失，B 的不受影响
    assert db.query(TodoItem).filter(TodoItem.job_id == job_a.id).count() == 0
    job_b_todo = _make_todo(db, job_b.id, description="B 的任务")
    assert job_b_todo.job_id == job_b.id


def test_save_job_with_analysis_creates_skills_todos_and_links(db):
    req = JobSaveRequest(
        raw_text="JD 原文", title="后端工程师", company="某公司",
        skills=[
            ExtractedSkill(name="FastAPI", description="Web 框架",
                           category_l1="编程语言", category_l2="Python"),
            ExtractedSkill(name="MySQL", description="关系型数据库",
                           category_l1="数据库", category_l2="SQL"),
        ],
        todos=[
            GeneratedTodo(description="学 FastAPI 路由", skill_names=["FastAPI"]),
            GeneratedTodo(description="学 SQL 查询", skill_names=["MySQL", "列表里没有的技能"]),
        ],
    )
    result = job_service.save_job_with_analysis(db, req)

    assert result["skills_created"] == 2
    assert result["skills_merged"] == 0
    assert result["todos_created"] == 2
    job = result["job"]
    assert job.id is not None and job.title == "后端工程师"

    # 技能按分析结果落库，初始 认识 / not_started，并关联岗位
    skills = {s.name: s for s in db.query(Skill).all()}
    assert set(skills) == {"FastAPI", "MySQL"}
    assert all(s.proficiency == "认识" and s.status == "not_started" for s in skills.values())
    assert all(job.id in [j.id for j in s.source_jobs] for s in skills.values())

    # 任务按名字挂技能：匹配不上的名字被静默跳过，任务本身照常落库
    todos = {t.description: t for t in db.query(TodoItem).all()}
    assert {t.description for t in todos.values()} == {"学 FastAPI 路由", "学 SQL 查询"}
    assert all(t.status == "pending" for t in todos.values())
    assert [s.name for s in todos["学 FastAPI 路由"].skills] == ["FastAPI"]
    assert [s.name for s in todos["学 SQL 查询"].skills] == ["MySQL"]


def test_save_job_with_analysis_merge_decision_reuses_existing_skill(db):
    existing = _make_skill(db, "Python", l1="编程语言", l2="Python")
    other_job = _make_job(db, title="旧岗位")
    existing.source_jobs.append(other_job)
    db.commit()

    req = JobSaveRequest(
        raw_text="JD", title="新岗位",
        skills=[ExtractedSkill(name="Python", description="已有技能",
                               category_l1="编程语言", category_l2="Python",
                               merge_with_existing_id=existing.id)],
        todos=[GeneratedTodo(description="巩固 Python", skill_names=["Python"])],
        merge_decisions={"Python": "merge"},
    )
    result = job_service.save_job_with_analysis(db, req)

    # 走合并分支：不新建技能行，已有技能挂上新岗位
    assert result["skills_created"] == 0
    assert result["skills_merged"] == 1
    assert db.query(Skill).filter(Skill.name == "Python").count() == 1
    db.refresh(existing)
    assert {j.title for j in existing.source_jobs} == {"旧岗位", "新岗位"}
    # 任务按名字挂到的是这份已有技能
    todo = db.query(TodoItem).one()
    assert [s.id for s in todo.skills] == [existing.id]


def test_save_job_with_analysis_merge_stale_id_falls_back_to_create(db):
    # 决策说要合并，但指向的 existing_id 不存在：当前行为是退回新建
    req = JobSaveRequest(
        raw_text="JD", title="岗位",
        skills=[ExtractedSkill(name="Redis", description="缓存",
                               category_l1="数据库", category_l2="缓存",
                               merge_with_existing_id=987654)],
        merge_decisions={"Redis": "merge"},
    )
    result = job_service.save_job_with_analysis(db, req)
    assert result["skills_created"] == 1
    assert result["skills_merged"] == 0
    created = db.query(Skill).one()
    assert created.name == "Redis"


# ─── dashboard_service ───────────────────────────────────

def test_dashboard_empty_db_is_all_zero(db):
    stats = dashboard_service.get_dashboard_stats(db)
    assert stats.total_skills == 0
    assert stats.completed_skills == 0
    assert stats.overall_completion_rate == 0.0
    assert stats.total_todos == 0
    assert stats.completed_todos == 0
    assert stats.total_jobs == 0
    assert stats.domains == []
    assert stats.best_matching_job is None
    assert stats.deepest_expertise == []
    assert stats.recent_activity == "暂无学习活动"


def test_dashboard_best_matching_job_skips_job_without_skills(db):
    job_empty = _make_job(db, title="无技能岗位")
    job_full = _make_job(db, title="全完岗位")
    done = _make_skill(db, "已完成技能", status="completed")
    done.source_jobs.append(job_full)
    db.commit()

    stats = dashboard_service.get_dashboard_stats(db)
    # 没挂技能的岗位不参与比较（当前实现直接 continue）
    assert stats.best_matching_job.job_id == job_full.id
    assert stats.best_matching_job.job_title == "全完岗位"
    assert stats.best_matching_job.match_rate == 1.0


def test_dashboard_aggregates_counts_domains_expertise_and_activity(db):
    # 编程语言/Python 组：两项技能 → 进入专深度榜
    s1 = _make_skill(db, "技能甲", l1="编程语言", l2="Python",
                     proficiency="熟练", status="completed")
    s2 = _make_skill(db, "技能乙", l1="编程语言", l2="Python",
                     proficiency="认识", status="in_progress")
    # 数据库组：只有一项 → 只进领域完成度，不进专深度榜
    s3 = _make_skill(db, "技能丙", l1="数据库", l2="SQL",
                     proficiency="完全掌握", status="completed")

    job_a = _make_job(db, title="岗位A")
    job_b = _make_job(db, title="岗位B")
    s1.source_jobs.append(job_a)                      # A：1/1 完成 = 100%
    s2.source_jobs.append(job_b)
    s3.source_jobs.append(job_b)                      # B：1/2 完成 = 50%
    _make_todo(db, job_a.id, description="进行中任务", status="in_progress")
    _make_todo(db, job_b.id, description="已完成任务", status="completed")
    db.commit()

    stats = dashboard_service.get_dashboard_stats(db)

    # 总量与总完成率：2/3 → 0.67
    assert stats.total_skills == 3
    assert stats.completed_skills == 2
    assert stats.overall_completion_rate == 0.67
    assert stats.total_jobs == 2
    assert stats.total_todos == 2
    assert stats.completed_todos == 1

    # 领域完成度（按 category_l1 聚合）
    domains = {d.category_l1: d for d in stats.domains}
    assert set(domains) == {"编程语言", "数据库"}
    assert domains["编程语言"].total_skills == 2
    assert domains["编程语言"].completed_skills == 1
    assert domains["编程语言"].completion_rate == 0.5
    assert domains["数据库"].completion_rate == 1.0

    # 最佳匹配岗位：完成率最高的 A
    assert stats.best_matching_job.job_id == job_a.id
    assert stats.best_matching_job.completed_skills == 1
    assert stats.best_matching_job.total_skills_required == 1

    # 专深度榜：只有凑满 2 项的组上榜，按平均掌握度排序
    assert len(stats.deepest_expertise) == 1
    item = stats.deepest_expertise[0]
    assert (item.category_l1, item.category_l2) == ("编程语言", "Python")
    assert item.skill_count == 2
    assert item.avg_proficiency_level == 2.0   # (熟练3 + 认识1) / 2
    assert item.top_skills == ["技能甲", "技能乙"]

    # 最近活动：有 1 项 in_progress 技能
    assert stats.recent_activity == "有 1 项技能正在学习中"
