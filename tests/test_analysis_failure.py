"""分析失败不再谎报成功的回归测试。

运行：python -m pytest tests/ -q（需先 pip install -r requirements-dev.txt）
"""
import json
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from openai import APIConnectionError, AuthenticationError

from backend.database import get_db
from backend.routers import analysis
from backend.services import deepseek_service, skill_service
from backend.services.deepseek_service import AnalysisError


def _auth_error():
    # openai v1 的 AuthenticationError 需要 httpx.Response 才能构造
    response = httpx.Response(
        401, request=httpx.Request("POST", "https://api.deepseek.com/chat/completions"))
    return AuthenticationError("Authentication Fails", response=response, body=None)


def _conn_error():
    request = httpx.Request("POST", "https://api.deepseek.com/chat/completions")
    return APIConnectionError(message="connection refused", request=request)


def _llm_response(payload):
    content = json.dumps(payload, ensure_ascii=False)
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(analysis.router)
    app.dependency_overrides[get_db] = lambda: iter([None])
    with patch.object(skill_service, "get_all_skills_as_dicts", lambda db: []):
        yield TestClient(app)


def test_auth_failure_raises_analysis_error():
    # 最常见触发：没配 API key，三次重试全 401 后必须抛而不是返回空壳
    with patch.object(deepseek_service.client.chat.completions, "create",
                      side_effect=_auth_error()):
        with pytest.raises(AnalysisError) as exc_info:
            deepseek_service.analyze_job_requirements(
                "负责后端开发，熟悉 Python", [], job_title="后端")
    assert "密钥" in str(exc_info.value)


def test_connection_failure_maps_to_friendly_reason():
    with patch.object(deepseek_service.client.chat.completions, "create",
                      side_effect=_conn_error()):
        with pytest.raises(AnalysisError) as exc_info:
            deepseek_service.analyze_job_requirements("负责后端开发", [])
    assert "连接" in str(exc_info.value)


def test_empty_extraction_raises_analysis_error():
    # LLM 正常返回但技能与任务双空：同样不能以成功形态返回
    with patch.object(deepseek_service.client.chat.completions, "create",
                      return_value=_llm_response({"skills": [], "todos": [], "summary": ""})):
        with pytest.raises(AnalysisError) as exc_info:
            deepseek_service.analyze_job_requirements("无实质内容", [])
    assert "提取" in str(exc_info.value)


def test_normal_result_still_returned():
    # 有产出时行为不变：AnalysisResponse 原样返回
    payload = {
        "job_title": "后端",
        "skills": [{"name": "Python", "description": "语言",
                    "category_l1": "编程语言", "category_l2": "Python"}],
        "todos": [],
        "summary": "ok",
    }
    with patch.object(deepseek_service.client.chat.completions, "create",
                      return_value=_llm_response(payload)):
        result = deepseek_service.analyze_job_requirements("Python 后端", [], job_title="后端")
    assert [s.name for s in result.skills] == ["Python"]


def test_preview_returns_502_without_leaking_upstream_error(client):
    # HTTP 层：502 + 用户可读 detail，上游异常原文不进响应体
    with patch.object(deepseek_service.client.chat.completions, "create",
                      side_effect=_auth_error()):
        r = client.post("/api/analysis/preview", json={"raw_text": "负责后端开发"})
    assert r.status_code == 502
    detail = r.json()["detail"]
    assert "Error code" not in detail
    assert "密钥" in detail
