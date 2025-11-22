@echo off
title MCP System Launcher
color 0a

echo ========================================================
echo    MCP LOCAL AGENT SYSTEM - STARTUP SEQUENCE
echo ========================================================
echo.
echo 1. Killing old processes...
taskkill /F /IM python.exe /T >nul 2>&1

echo 2. Starting Launcher (Background)...
start "MCP Launcher" cmd /k "python launcher.py"

echo 3. Waiting for Launcher to initialize...
timeout /t 3 >nul

echo 4. Opening Dashboard...
start dashboard.html

echo.
echo ========================================================
echo    SYSTEM READY. CONTROL VIA WEB DASHBOARD.
echo ========================================================
echo.
pause