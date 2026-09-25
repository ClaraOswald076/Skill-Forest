"""评分 prompt 与出题规则的口径自洽回归。

背景：#26——GRADING_PROMPT 的返回示例写死 "max_score": 60，而出题侧固定
15 单选 + 3 大题 + 5 名词解释、评分规则上限 2/10/6 分，真实满分 90。
LLM 对 JSON 示例的锚定强于对规则文字的遵循，示例错了满分口径就跟着错，
前端 QuizResult 再拿它算得分率，整体虚高约 1.5 倍。
"""
import re

from backend.services.learning_service import GRADING_PROMPT, QUIZ_GENERATION_PROMPT


def _int(pattern: str, text: str) -> int:
    return int(re.search(pattern, text).group(1))


def _example_max_score() -> int:
    return _int(r'"total_score":\s*\d+,\s*\n\s*"max_score":\s*(\d+)', GRADING_PROMPT)


def _rule_max_score() -> int:
    n_choice = _int(r"(\d+)\s*道单选题", QUIZ_GENERATION_PROMPT)
    n_essay = _int(r"(\d+)\s*道大题", QUIZ_GENERATION_PROMPT)
    n_def = _int(r"(\d+)\s*道名词解释", QUIZ_GENERATION_PROMPT)
    per_choice = _int(r"单选题（choice）：答对得\s*(\d+)\s*分", GRADING_PROMPT)
    per_essay = _int(r"大题（essay）：.*?满分\s*(\d+)\s*分", GRADING_PROMPT)
    per_def = _int(r"名词解释（definition）：.*?满分\s*(\d+)\s*分", GRADING_PROMPT)
    return n_choice * per_choice + n_essay * per_essay + n_def * per_def


def test_grading_prompt_example_matches_scoring_rules():
    example_max = _example_max_score()
    assert example_max == _rule_max_score(), (
        f"GRADING_PROMPT 示例 max_score={example_max}，"
        f"但出题题量×规则上限={_rule_max_score()}，示例会把 LLM 的满分口径带偏"
    )


def test_grading_prompt_example_total_within_max():
    total = _int(r'"total_score":\s*(\d+),', GRADING_PROMPT)
    assert total <= _example_max_score(), "示例 total_score 不能超过示例自己声明的满分"
