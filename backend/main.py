"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import HOST, PORT, is_api_key_configured
from backend.database import init_db
from backend.routers import skills, jobs, todos, analysis, dashboard, learning

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized.")
    if not is_api_key_configured():
        logger.warning(
            "DeepSeek API Key 未配置：岗位分析/教程/测评/聊天等 AI 功能将失败。"
            "请复制 .env.example 为 .env 并填入 DEEPSEEK_API_KEY。"
        )
    yield


app = FastAPI(
    title="Skill Tree & Todo List",
    description="技能树与工作任务管理系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all localhost dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(skills.router)
app.include_router(jobs.router)
app.include_router(todos.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(learning.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "key_configured": is_api_key_configured()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
