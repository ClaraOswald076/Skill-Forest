"""DeepSeek API integration for job requirement analysis."""

import json
import logging
from typing import List, Optional

from openai import OpenAI

from backend.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_PRO_MODEL,
    DEEPSEEK_FLASH_MODEL,
)
from backend.prompts.system_prompt import SYSTEM_PROMPT
from backend.schemas.analysis import AnalysisResponse, MergeSuggestion
from backend.utils.similarity import compute_skill_similarity

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)


def analyze_job_requirements(
    raw_text: str,
    existing_skills: List[dict],
    job_title: str = "",
    company: str = "",
) -> AnalysisResponse:
    """
    Main analysis pipeline:
    1. Send JD text + all existing skills to DeepSeek
    2. Parse the JSON response (with recovery for truncated output)
    3. Compute secondary merge suggestions for borderline cases
    4. Return structured AnalysisResponse
    """
    # Compact the existing skills list — only send what the API needs
    compact_skills = _compact_existing_skills(existing_skills)
    existing_skills_json = json.dumps(compact_skills, ensure_ascii=False)

    # Truncate JD if it's excessively long (>5000 chars)
    jd_text = raw_text if len(raw_text) <= 5000 else raw_text[:5000] + "\n...(文本过长已截断)"

    user_message = f"""## 数据库中已存在的技能列表
{existing_skills_json if compact_skills else '（空，当前没有任何已有技能）'}

## 岗位要求原文
{jd_text}

请分析以上岗位要求，提取技能并生成学习任务。"""

    # Try up to 3 times, with increasing measures on each retry
    for attempt in range(3):
        try:
            # On retry, reduce context further
            if attempt == 1:
                # Second try: use even more compact skills list
                minimal_skills = [{"id": s["id"], "name": s["name"]} for s in existing_skills]
                skills_json = json.dumps(minimal_skills, ensure_ascii=False)
                user_message = f"""## 数据库中已存在的技能列表（仅名称）
{skills_json if minimal_skills else '（空）'}

## 岗位要求原文
{jd_text}

请分析以上岗位要求，提取技能并生成学习任务。"""
            elif attempt == 2:
                # Third try: no existing skills, shorter JD
                user_message = f"""## 岗位要求原文
{jd_text[:3000]}

请分析以上岗位要求，提取技能并生成学习任务。"""

            response = client.chat.completions.create(
                model=DEEPSEEK_PRO_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=16384,  # Increased from 4096 to avoid truncation
            )

            content = response.choices[0].message.content or ""
            # Strip markdown code fences if present
            content = _extract_json(content)
            # Try to fix truncated JSON
            content = _recover_truncated_json(content)
            result = json.loads(content)

            # Parse into AnalysisResponse
            analysis = AnalysisResponse(
                job_title=result.get("job_title", job_title),
                company=result.get("company", company),
                skills=result.get("skills", []),
                todos=result.get("todos", []),
                merge_suggestions=[],
                summary=result.get("summary", ""),
            )

            # Run secondary merge check for borderline cases
            analysis.merge_suggestions = _secondary_merge_check(
                analysis.skills, existing_skills
            )

            return analysis

        except (json.JSONDecodeError, KeyError, Exception) as e:
            logger.warning(f"DeepSeek API attempt {attempt + 1} failed: {e}")
            if attempt == 2:
                # Return empty result on final failure
                return AnalysisResponse(
                    job_title=job_title,
                    company=company,
                    skills=[],
                    todos=[],
                    merge_suggestions=[],
                    summary=f"分析失败: {str(e)}",
                )

    # Should not reach here
    return AnalysisResponse(job_title=job_title, company=company)


def _compact_existing_skills(skills: List[dict]) -> List[dict]:
    """Reduce existing skills to essential fields to save context space."""
    compacted = []
    for s in skills:
        compacted.append({
            "id": s["id"],
            "name": s["name"],
            "cat": f"{s.get('category_l1', '')}/{s.get('category_l2', '')}",
            "desc": (s.get("description", "") or "")[:80],  # truncate long descriptions
        })
    return compacted


def _recover_truncated_json(content: str) -> str:
    """
    Attempt to fix common JSON truncation issues:
    - Unclosed strings (add closing quote)
    - Unclosed objects/arrays (add closing brackets in the right order)
    - Trailing commas before end of object

    Valid JSON is returned unchanged; broken (non-truncated) JSON is
    returned as-is so the caller's retry path can handle it.
    """
    if not content:
        return "{}"

    text = content.strip()
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Walk the text tracking string context, so quotes and braces inside
    # string values don't get counted as structure
    stack = []
    in_string = False
    escaped = False
    for ch in text:
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in '{[':
            stack.append(ch)
        elif ch in '}]':
            if not stack or stack[-1] != ('{' if ch == '}' else '['):
                return text  # mismatched closer: broken, not truncated
            stack.pop()

    repaired = text
    if in_string:
        if escaped:
            repaired = repaired[:-1]  # drop the dangling escape before closing
        repaired += '"'
    repaired = repaired.rstrip()
    if repaired.endswith(','):
        repaired = repaired[:-1]
    repaired += ''.join('}' if c == '{' else ']' for c in reversed(stack))

    try:
        json.loads(repaired)
        return repaired
    except json.JSONDecodeError:
        return text


def generate_dashboard_insight(stats: dict) -> str:
    """Generate a brief insight for the dashboard (uses flash model for speed)."""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_FLASH_MODEL,
            messages=[
                {"role": "system", "content": "你是一个学习进度分析师。根据提供的统计数据，用1-2句话总结用户的学习进展，给出鼓励和建议。"},
                {"role": "user", "content": json.dumps(stats, ensure_ascii=False)},
            ],
            temperature=0.7,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


def _extract_json(content: str) -> str:
    """Extract JSON from markdown code fences if present."""
    content = content.strip()
    if content.startswith("```"):
        # Remove opening fence
        lines = content.split("\n")
        if lines[0].startswith("```") and len(lines) > 1:
            content = "\n".join(lines[1:])
        # Remove closing fence
        if content.endswith("```"):
            content = content[:-3]
    return content.strip()


def _secondary_merge_check(
    extracted_skills: list,
    existing_skills: List[dict],
) -> List[MergeSuggestion]:
    """
    For skills where the API was uncertain (confidence 0.75-0.85),
    compute a secondary similarity check using difflib.
    Also catch skills that the API missed (high local similarity, low API confidence).
    """
    suggestions = []

    for skill in extracted_skills:
        skill_dict = skill.model_dump() if hasattr(skill, 'model_dump') else skill
        name = skill_dict.get("name", "")
        desc = skill_dict.get("description", "")

        # Already decided to merge with high confidence — skip
        if skill_dict.get("merge_with_existing_id") and skill_dict.get("merge_confidence", 0) >= 0.85:
            continue

        # Check against all existing skills
        for existing in existing_skills:
            local_sim = compute_skill_similarity(
                name, existing["name"], desc, existing.get("description", "")
            )

            if local_sim >= 0.80:
                # Determine action
                api_merge_id = skill_dict.get("merge_with_existing_id")
                if api_merge_id == existing["id"]:
                    action = "merge"  # API agrees
                elif api_merge_id is None and local_sim >= 0.85:
                    action = "merge"  # API missed, local found high similarity
                else:
                    action = "keep_separate"

                suggestions.append(MergeSuggestion(
                    existing_skill_id=existing["id"],
                    existing_skill_name=existing["name"],
                    new_skill_name=name,
                    similarity=round(local_sim, 2),
                    action=action,
                ))

    return suggestions
