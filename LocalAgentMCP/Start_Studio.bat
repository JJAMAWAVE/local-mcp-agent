@echo off
title Local AI Studio Launcher
color 0b

echo ========================================================
echo    LOCAL AI STUDIO - SYSTEM STARTUP
echo ========================================================
echo.

:: 1. 작업 폴더로 이동 (경로 보정)
cd /d "C:\local-mcp-agent\LocalAgentMCP"

:: 2. 서버 실행 (새 창에서 실행하여 백그라운드 유지)
echo [System] Starting Studio Server...
start "AI Studio Server" cmd /k "python studio_server.py"

:: 3. 서버가 켜질 때까지 잠시 대기 (2초)
echo [System] Waiting for server to initialize...
timeout /t 2 >nul

:: 4. 웹 브라우저 실행
echo [System] Opening Studio UI...
start http://localhost:8000

echo.
echo [Success] Studio is running!
echo You can close this window, but keep the 'AI Studio Server' window open.
pause