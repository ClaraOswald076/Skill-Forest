"""DeepSeek key 配置检测回归测试。

背景：config.py 的默认 key 是占位符，没配 key 时服务照常启动、零提示，
用户点到 AI 功能才收到 401 且猜不到原因。is_api_key_configured 统一判定
"未设置/为空/仍是占位符"三种未配置状态，供启动告警与 /api/health 透出。

运行：python -m pytest tests/ -q（需自备 pytest，运行时依赖同 requirements.txt）
"""
import pytest

from backend import config
from backend.main import health_check


def test_placeholder_key_is_not_configured(monkeypatch):
    monkeypatch.setattr(config, "DEEPSEEK_API_KEY", config.DEEPSEEK_API_KEY_PLACEHOLDER)
    assert config.is_api_key_configured() is False


def test_empty_or_missing_key_is_not_configured(monkeypatch):
    monkeypatch.setattr(config, "DEEPSEEK_API_KEY", "")
    assert config.is_api_key_configured() is False


def test_real_key_is_configured(monkeypatch):
    monkeypatch.setattr(config, "DEEPSEEK_API_KEY", "sk-real-key-123456")
    assert config.is_api_key_configured() is True


def test_health_endpoint_reports_key_configured(monkeypatch):
    monkeypatch.setattr(config, "DEEPSEEK_API_KEY", config.DEEPSEEK_API_KEY_PLACEHOLDER)
    assert health_check() == {"status": "ok", "key_configured": False}

    monkeypatch.setattr(config, "DEEPSEEK_API_KEY", "sk-real-key-123456")
    assert health_check() == {"status": "ok", "key_configured": True}
