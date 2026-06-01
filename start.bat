@echo off
chcp 65001 >nul
title 技能树 & 任务管理系统

echo ============================================
echo   技能树 ^& 任务管理系统
echo   启动中...
echo ============================================

:: Start Python backend
echo [1/2] 启动后端服务 (http://127.0.0.1:8765)...
start "SkillTree Backend" cmd /c "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765"

:: Wait for backend to be ready
echo        等待后端就绪...
:wait_backend
timeout /t 1 >nul
curl -s http://127.0.0.1:8765/api/health >nul 2>&1
if errorlevel 1 goto wait_backend

echo        后端就绪！

:: Start Vite frontend
echo [2/2] 启动前端界面 (http://localhost:5173)...
start "SkillTree Frontend" cmd /c "npx vite --host"

:: Wait for frontend
echo        等待前端就绪...
:wait_frontend
timeout /t 1 >nul
curl -s http://localhost:5173 >nul 2>&1
if errorlevel 1 goto wait_frontend

:: Open browser
echo ============================================
echo   启动完成！正在打开浏览器...
echo ============================================
start http://localhost:5173

echo.
echo 按任意键关闭所有服务...
pause >nul

:: Cleanup
taskkill /FI "WINDOWTITLE eq SkillTree Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq SkillTree Frontend*" /T /F >nul 2>&1
echo 服务已关闭。
