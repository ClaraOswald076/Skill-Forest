"""Application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

# 支持 README 里的方式 3：复制 .env.example 为 .env 填密钥
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# DeepSeek API — 从环境变量读取，或在此填入你的 API Key
# 获取地址: https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY_PLACEHOLDER = "sk-请替换为你的API密钥"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", DEEPSEEK_API_KEY_PLACEHOLDER)
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_PRO_MODEL = "deepseek-v4-pro"
DEEPSEEK_FLASH_MODEL = "deepseek-v4-flash"


def is_api_key_configured() -> bool:
    """未设置、为空或仍是占位符都算未配置，供启动告警与 /api/health 使用。"""
    return bool(DEEPSEEK_API_KEY) and DEEPSEEK_API_KEY != DEEPSEEK_API_KEY_PLACEHOLDER

# Database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "skilltree.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Server
HOST = "127.0.0.1"
PORT = 8765

# Proficiency levels
PROFICIENCY_LEVELS = ["认识", "熟悉", "熟练", "完全掌握"]

# Skill statuses
SKILL_STATUSES = ["not_started", "in_progress", "completed"]

# Todo statuses
TODO_STATUSES = ["pending", "in_progress", "completed"]

# Merge threshold
MERGE_SIMILARITY_THRESHOLD = 0.80
MERGE_UNCERTAIN_LOW = 0.75
MERGE_UNCERTAIN_HIGH = 0.85
