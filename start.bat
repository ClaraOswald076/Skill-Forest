@echo off
chcp 65001 >nul
title 技能树 ^& 任务管理系统

echo ============================================
echo   技能树 ^& 任务管理系统
echo   启动中...
echo ============================================

:: Start Python backend
echo [1/2] 启动后端服务 (http://127.0.0.1:8765)...
start "SkillTree Backend" cmd /c "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8765"

:: Wait for backend to be ready (up to 60s)
echo        等待后端就绪...
set /a WAIT_TRIES=0
:wait_backend
timeout /t 1 >nul
curl -sf http://127.0.0.1:8765/api/health >nul 2>&1
if not errorlevel 1 goto backend_ready
set /a WAIT_TRIES+=1
if %WAIT_TRIES% geq 60 goto backend_failed
goto wait_backend

:backend_ready
echo        后端就绪！

:: Start Vite frontend
echo [2/2] 启动前端界面 (http://localhost:5173)...
start "SkillTree Frontend" cmd /c "npx vite --host"

:: Wait for frontend (up to 60s)
echo        等待前端就绪...
set /a WAIT_TRIES=0
:wait_frontend
timeout /t 1 >nul
curl -sf http://localhost:5173 >nul 2>&1
if not errorlevel 1 goto frontend_ready
set /a WAIT_TRIES+=1
if %WAIT_TRIES% geq 60 goto frontend_failed
goto wait_frontend

:frontend_ready
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
goto :eof

:backend_failed
echo [错误] 后端 60 秒内未能就绪，已放弃启动。常见原因：
echo   - 依赖未安装：先执行 pip install -r requirements.txt
echo   - 8765 端口被占用：netstat -ano ^| findstr 8765
pause
exit /b 1

:frontend_failed
echo [错误] 前端 60 秒内未能就绪，已放弃启动。常见原因：
echo   - 依赖未安装：先执行 npm install
echo   - 5173 端口被占用
pause
exit /b 1
