@echo off
REM ⚠️ DEPRECATED — 使用 python start_thinking.py 启动（本文件保留仅作参考）
echo ============================================================
echo   ⚠️  start_thinking_daemon.bat 已弃用
echo   请使用: python start_thinking.py
echo ============================================================
echo.
cd /d "%~dp0"
python start_thinking.py
pause
