"""deepseek_service 纯函数的回归测试。

运行：python -m pytest tests/ -q（需先 pip install -r requirements-dev.txt）
"""
import json

from backend.services.deepseek_service import _recover_truncated_json


def test_valid_json_returned_unchanged():
    # 合法 JSON 必须原样返回：键名含转义引号、字符串值含花括号/方括号
    # 这三类输入在旧版会被引号/括号计数改坏
    for raw in (
        '{"a\\"b": 1}',
        '{"a": "{"}',
        '{"a": "["}',
        '{"a": [1, 2], "b": {"c": 3}}',
    ):
        assert _recover_truncated_json(raw) == raw
        json.loads(_recover_truncated_json(raw))


def test_truncated_nested_structure_recovers():
    # 真实截断场景：嵌套结构 + 未闭合字符串，闭合顺序必须是 " } ] }
    raw = '{"skills": [{"name": "Python", "desc": "web'
    out = _recover_truncated_json(raw)
    assert json.loads(out) == {"skills": [{"name": "Python", "desc": "web"}]}


def test_trailing_comma_cleaned():
    out = _recover_truncated_json('{"job_title": "X",')
    assert json.loads(out) == {"job_title": "X"}


def test_dangling_escape_before_truncation():
    # 截断点恰好在转义符后：先去掉悬挂的反斜杠再补引号
    raw = '{"desc": "line1\\'
    out = _recover_truncated_json(raw)
    assert json.loads(out) == {"desc": "line1"}


def test_broken_json_returned_as_is():
    # 多余闭合属于坏 JSON 而非截断，修不动就原样交还给调用方的重试路径
    raw = '{"a": 1}}'
    assert _recover_truncated_json(raw) == raw


def test_empty_input_returns_empty_object():
    assert _recover_truncated_json("") == "{}"
