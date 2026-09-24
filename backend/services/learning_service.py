"""Learning service — tutorial, chat, quiz, error book."""

import json
import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from openai import OpenAI

from backend.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_PRO_MODEL,
)
from backend.models.learning import LearningModule, ChatSession, ChatMessage, QuizAttempt, ErrorBook
from backend.models.todo_item import TodoItem
from backend.models.skill import Skill

logger = logging.getLogger(__name__)

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# ─── Tutorial ───────────────────────────────────────────

TUTORIAL_SYSTEM_PROMPT = """你是一位耐心的技术导师，专门为初学者从零开始讲解技术概念。

你的讲解风格：
1. 从最基础的概念开始，假设读者没有任何先验知识
2. 使用类比和生活中的例子来解释抽象概念
3. 逐步深入，每个新概念都建立在之前的基础上
4. 使用口语化的中文，避免堆砌术语
5. 在关键技术点上使用 Markdown 格式（标题、列表、代码块、强调）
6. 包含"常见疑问"小节，预判初学者的困惑

输出格式：使用 Markdown，包含清晰的标题层次。总长度 2000-4000 字。"""


def get_or_generate_tutorial(db: Session, todo_id: int, regenerate: bool = False) -> Optional[LearningModule]:
    """Get cached tutorial or generate a new one."""
    todo = db.query(TodoItem).options(
        joinedload(TodoItem.skills),
        joinedload(TodoItem.job),
    ).filter(TodoItem.id == todo_id).first()
    if not todo:
        return None

    # Return cached if exists and not regenerating
    existing = db.query(LearningModule).filter(LearningModule.todo_id == todo_id).first()
    if existing and not regenerate:
        return existing

    # Build skills context
    skills_info = []
    for s in (todo.skills or []):
        skills_info.append(f"- {s.name} ({s.category_l1}/{s.category_l2}): {s.description or '暂无描述'} [当前掌握程度: {s.proficiency}]")

    skills_text = "\n".join(skills_info) if skills_info else "（无关联技能）"
    proficiency_summary = ", ".join([f"{s.name}={s.proficiency}" for s in (todo.skills or [])])

    user_prompt = f"""请为以下学习任务生成一份完整的 0 基础入门教程。

## 学习目标
{todo.description}

## 关联技能及用户当前水平
{skills_text}

## 要求掌握程度
{todo.proficiency_required}

请为以上内容生成一份 Markdown 格式的教程，从最基础的概念开始讲解。"""

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_PRO_MODEL,
            messages=[
                {"role": "system", "content": TUTORIAL_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=8192,
        )
        content = response.choices[0].message.content or ""

        if existing:
            existing.tutorial_content = content
            existing.tutorial_version = (existing.tutorial_version or 1) + 1
            existing.last_generated_at = datetime.now()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            module = LearningModule(todo_id=todo_id, tutorial_content=content)
            db.add(module)
            db.commit()
            db.refresh(module)
            return module
    except Exception as e:
        logger.error(f"Tutorial generation failed: {e}")
        raise


def get_cached_tutorial(db: Session, todo_id: int) -> Optional[LearningModule]:
    return db.query(LearningModule).filter(LearningModule.todo_id == todo_id).first()


# ─── Chat ───────────────────────────────────────────────

CHAT_SYSTEM_PROMPT_TEMPLATE = """你是一个技能学习助手。你正在帮助用户学习以下内容：

## 学习任务
{todo_description}

## 关联技能及用户当前水平
{skills_context}

## 参考教程（用户正在学习的材料）
{tutorial_content}

## 你的角色
- 回答用户关于以上技能的任何问题
- 用通俗易懂的中文解释概念
- 如果用户问的问题不在教程范围内，可以基于你的知识回答
- 当用户表现出困惑时，主动询问是否需要更详细的解释
- 不要编造事实。如果不确定，诚实说明"""

MAX_CHAT_HISTORY = 20  # Number of recent message pairs to include


def create_chat_session(db: Session, todo_id: int, title: str = "新对话") -> ChatSession:
    session = ChatSession(todo_id=todo_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_chat_sessions(db: Session, todo_id: int) -> List[ChatSession]:
    return db.query(ChatSession).options(
        joinedload(ChatSession.messages)
    ).filter(ChatSession.todo_id == todo_id).order_by(ChatSession.updated_at.desc()).all()


def get_chat_session(db: Session, session_id: int) -> Optional[ChatSession]:
    return db.query(ChatSession).options(
        joinedload(ChatSession.messages)
    ).filter(ChatSession.id == session_id).first()


def delete_chat_session(db: Session, session_id: int) -> bool:
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True


def update_chat_session(db: Session, session_id: int, data: dict) -> Optional[ChatSession]:
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        return None
    for key, value in data.items():
        if hasattr(session, key):
            setattr(session, key, value)
    db.commit()
    db.refresh(session)
    return session


def send_chat_message(db: Session, session_id: int, message: str) -> dict:
    """Send a message in a chat session and get AI reply."""
    session = db.query(ChatSession).options(
        joinedload(ChatSession.messages),
        joinedload(ChatSession.todo).joinedload(TodoItem.skills),
    ).filter(ChatSession.id == session_id).first()
    if not session:
        raise ValueError("Session not found")

    # Save user message
    user_msg = ChatMessage(session_id=session_id, role="user", content=message)
    db.add(user_msg)
    db.commit()

    # Build conversation context
    todo = session.todo
    if not todo:
        raise ValueError("Associated todo not found")

    # Skills context
    skills_lines = []
    for s in (todo.skills or []):
        skills_lines.append(f"- {s.name}: {s.proficiency} ({s.category_l1}/{s.category_l2})")
    skills_context = "\n".join(skills_lines) if skills_lines else "无关联技能"

    # Tutorial content (truncated to first 3000 chars if long)
    tutorial_content = "（暂无教程）"
    module = db.query(LearningModule).filter(LearningModule.todo_id == todo.id).first()
    if module:
        tutorial_content = module.tutorial_content[:3000]

    # System message
    system_msg = CHAT_SYSTEM_PROMPT_TEMPLATE.format(
        todo_description=todo.description,
        skills_context=skills_context,
        tutorial_content=tutorial_content,
    )

    # Build message list for API
    api_messages = [{"role": "system", "content": system_msg}]

    all_messages = sorted(session.messages, key=lambda m: m.created_at or "")
    recent = all_messages[-(MAX_CHAT_HISTORY * 2):]  # Last N pairs

    if len(all_messages) > MAX_CHAT_HISTORY * 2:
        api_messages.append({"role": "system", "content": "（...之前的对话已省略，以下是最近的对话...）"})

    for m in recent:
        api_messages.append({"role": m.role, "content": m.content})

    # Call DeepSeek
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_PRO_MODEL,
            messages=api_messages,
            temperature=0.7,
            max_tokens=4096,
        )
        ai_content = response.choices[0].message.content or ""
        reasoning = response.choices[0].message.reasoning_content or ""
        tokens = response.usage.total_tokens if response.usage else 0

        ai_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=ai_content,
            reasoning_content=reasoning,
            tokens_used=tokens,
        )
        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)
        db.refresh(user_msg)

        # Update session timestamp
        session.updated_at = datetime.now()
        db.commit()

        return {"user_message": user_msg, "ai_message": ai_msg}
    except Exception as e:
        # 失败不落伪 assistant 消息：异常原文一旦入库就会被当成历史，
        # 随后续每轮请求回传给 LLM。用户发言已落库，这里原样上抛由路由转 502。
        logger.error(f"Chat message failed: {e}")
        raise


# ─── Quiz ────────────────────────────────────────────────

QUIZ_GENERATION_PROMPT = """你是一个严格的技能测评出题人。根据指定的技能和学习目标，生成一套测试题。

要求掌握的技能：{skills}
目标掌握程度：{target_proficiency}
学习任务描述：{todo_description}

请生成一套测试，包含：
- 15 道单选题（每题 4 个选项，标注正确答案）
- 3 道大题（简答/论述题，考察理解深度，标注评分要点）
- 5 道名词解释题（解释关键术语，标注关键要点）

返回严格 JSON 格式（不要包含在 markdown 代码块中）：
{{
  "questions": [
    {{
      "q_number": 1,
      "question_type": "choice",
      "question_text": "题目内容",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A"
    }},
    {{
      "q_number": 16,
      "question_type": "essay",
      "question_text": "大题题目",
      "options": [],
      "correct_answer": "评分要点：1. ... 2. ... 3. ..."
    }},
    {{
      "q_number": 19,
      "question_type": "definition",
      "question_text": "请解释以下术语：...",
      "options": [],
      "correct_answer": "关键要点：..."
    }}
  ]
}}"""


def generate_quiz(db: Session, todo_id: int) -> QuizAttempt:
    """Generate a quiz for a todo item."""
    todo = db.query(TodoItem).options(
        joinedload(TodoItem.skills),
    ).filter(TodoItem.id == todo_id).first()
    if not todo:
        raise ValueError("Todo not found")

    skills_names = [s.name for s in (todo.skills or [])]
    skills_text = ", ".join(skills_names) if skills_names else "通用技能"

    prompt = QUIZ_GENERATION_PROMPT.format(
        skills=skills_text,
        target_proficiency=todo.proficiency_required,
        todo_description=todo.description,
    )

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_PRO_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=8192,
        )
        content = response.choices[0].message.content or ""
        # Strip markdown fences
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:])
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        questions_data = json.loads(content)

        attempt = QuizAttempt(
            todo_id=todo_id,
            questions_json=json.dumps(questions_data, ensure_ascii=False),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt
    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")
        raise


def get_quiz_attempt(db: Session, attempt_id: int) -> Optional[QuizAttempt]:
    return db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()


def list_quiz_attempts(db: Session, todo_id: int) -> List[QuizAttempt]:
    return db.query(QuizAttempt).filter(
        QuizAttempt.todo_id == todo_id
    ).order_by(QuizAttempt.created_at.desc()).all()


GRADING_PROMPT = """你是一个严格的评分老师。请根据标准答案，对学生的答卷进行评分。

试卷题目及答案：
{exam_json}

学生答案：
{answers_json}

评分规则：
- 单选题（choice）：答对得 2 分，答错得 0 分
- 大题（essay）：根据知识准确度、逻辑完整度、表达清晰度评分（满分 10 分），给出详细评语
- 名词解释（definition）：根据准确度和完整度评分（满分 6 分），给出纠正或补充

返回严格 JSON（不要 markdown 代码块）：
{{
  "results": [
    {{ "q_number": 1, "score": 2, "max_score": 2, "is_correct": true, "explanation": "" }},
    {{ "q_number": 2, "score": 0, "max_score": 2, "is_correct": false, "explanation": "正确答案是 B，因为..." }}
  ],
  "total_score": 45,
  "max_score": 60,
  "overall_feedback": "总体评价和建议"
}}"""


def _clean_grading(grading) -> dict:
    """评分 LLM 的输出形状不受我们控制：顶层多键、条目缺键是常态。
    这里在写库之前清洗成响应与错题本需要的最小结构，坏条目跳过而不是炸掉整卷。"""
    if not isinstance(grading, dict):
        raise ValueError(f"评分结果格式异常：期望 JSON 对象，实际是 {type(grading).__name__}")
    results = []
    for r in grading.get("results") or []:
        if not isinstance(r, dict) or "q_number" not in r:
            logger.warning(f"跳过缺少 q_number 的评分条目: {r}")
            continue
        try:
            q_number = int(r["q_number"])
        except (TypeError, ValueError):
            logger.warning(f"跳过 q_number 无法解析的评分条目: {r}")
            continue
        results.append({
            "q_number": q_number,
            "score": r.get("score", 0),
            "max_score": r.get("max_score", 0),
            "is_correct": bool(r.get("is_correct", False)),
            "explanation": r.get("explanation", ""),
        })
    return {
        "results": results,
        "total_score": grading.get("total_score", 0),
        "max_score": grading.get("max_score", 0),
        "overall_feedback": grading.get("overall_feedback", ""),
    }


def submit_quiz(db: Session, attempt_id: int, answers: List[dict]) -> dict:
    """Submit quiz answers for grading."""
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise ValueError("Quiz attempt not found")
    if attempt.submitted_at:
        raise ValueError("Quiz already submitted")

    # Save answers
    attempt.answers_json = json.dumps(answers, ensure_ascii=False)
    db.commit()

    # Grade
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_PRO_MODEL,
            messages=[{
                "role": "user",
                "content": GRADING_PROMPT.format(
                    exam_json=attempt.questions_json,
                    answers_json=json.dumps(answers, ensure_ascii=False),
                ),
            }],
            temperature=0.3,
            max_tokens=4096,
        )
        content = response.choices[0].message.content or ""
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:])
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # 清洗必须发生在任何写库之前，否则坏 JSON 会留下"分数已提交、响应却 500"的悬状态
        grading = _clean_grading(json.loads(content))

        attempt.graded_json = json.dumps(grading, ensure_ascii=False)
        attempt.total_score = grading.get("total_score", 0)
        attempt.max_score = grading.get("max_score", 0)
        attempt.submitted_at = datetime.now()
        db.commit()

        # Save wrong answers to error book
        _save_errors(db, attempt, grading.get("results", []), answers)

        return grading
    except Exception as e:
        logger.error(f"Quiz grading failed: {e}")
        raise


def _save_errors(db: Session, attempt: QuizAttempt, results: List[dict], answers: List[dict]):
    """Save incorrect answers to the error book."""
    questions = json.loads(attempt.questions_json).get("questions", [])
    # 题目本身也是 LLM 生成的，个别缺 q_number 不应让整本错题本落空
    q_map = {q.get("q_number"): q for q in questions if isinstance(q, dict)}
    answer_map = {a.get("q_number"): a.get("answer", "") for a in answers}

    for r in results:
        if not r.get("is_correct", True):
            q = q_map.get(r["q_number"], {})
            # Find associated skill
            todo = db.query(TodoItem).options(joinedload(TodoItem.skills)).filter(
                TodoItem.id == attempt.todo_id
            ).first()
            skill_id = todo.skills[0].id if todo and todo.skills else None

            entry = ErrorBook(
                quiz_attempt_id=attempt.id,
                todo_id=attempt.todo_id,
                skill_id=skill_id,
                question_type=q.get("question_type", "unknown"),
                question_text=q.get("question_text", ""),
                user_answer=answer_map.get(r["q_number"], ""),
                correct_answer=q.get("correct_answer", ""),
                explanation=r.get("explanation", ""),
            )
            db.add(entry)
    db.commit()


# ─── Error Book ──────────────────────────────────────────

def get_error_entries(
    db: Session,
    skill_id: Optional[int] = None,
    reviewed: Optional[bool] = None,
) -> List[ErrorBook]:
    q = db.query(ErrorBook)
    if skill_id is not None:
        q = q.filter(ErrorBook.skill_id == skill_id)
    if reviewed is not None:
        q = q.filter(ErrorBook.reviewed == reviewed)
    return q.order_by(ErrorBook.created_at.desc()).all()


def get_error_stats(db: Session) -> dict:
    total = db.query(ErrorBook).count()
    reviewed = db.query(ErrorBook).filter(ErrorBook.reviewed == True).count()
    unreviewed = total - reviewed

    # By skill
    from sqlalchemy import func as sqlfunc
    by_skill_rows = db.query(
        ErrorBook.skill_id,
        sqlfunc.count(ErrorBook.id),
        Skill.name,
    ).outerjoin(Skill, ErrorBook.skill_id == Skill.id).group_by(
        ErrorBook.skill_id, Skill.name
    ).all()

    by_skill = [
        {"skill_id": row[0] or 0, "skill_name": row[2] or "未分类", "count": row[1]}
        for row in by_skill_rows
    ]

    return {"total": total, "reviewed": reviewed, "unreviewed": unreviewed, "by_skill": by_skill}


def update_error_entry(db: Session, entry_id: int, data: dict) -> Optional[ErrorBook]:
    entry = db.query(ErrorBook).filter(ErrorBook.id == entry_id).first()
    if not entry:
        return None
    for key, value in data.items():
        if hasattr(entry, key):
            setattr(entry, key, value)
    if data.get("reviewed") and not entry.reviewed_at:
        from datetime import datetime
        entry.reviewed_at = datetime.now()
    db.commit()
    db.refresh(entry)
    return entry


def delete_error_entry(db: Session, entry_id: int) -> bool:
    entry = db.query(ErrorBook).filter(ErrorBook.id == entry_id).first()
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True
