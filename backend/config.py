"""Application configuration."""

import os

# DeepSeek API — 从环境变量读取，或在此填入你的 API Key
# 获取地址: https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-请替换为你的API密钥")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_PRO_MODEL = "deepseek-v4-pro"
DEEPSEEK_FLASH_MODEL = "deepseek-v4-flash"

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
