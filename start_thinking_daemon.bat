@echo off
REM ⚠️ DEPRECATED — 请使用 python start_thinking.py 启动
cd /d "%~dp0"

:: 爬虫守护进程（pythonw = 无窗口后台运行）
start "CrawlerDaemon" /B pythonw -c "
import sys, time
sys.path.insert(0, '.')
from crawler_daemon import CrawlerDaemon
daemon = CrawlerDaemon()
daemon.start()
while daemon.is_running:
    time.sleep(10)
"

:restart
echo [%date% %time%] 启动思考守护进程... >> data\thinking_daemon.log
pythonw -c "
from thinking_daemon import get_daemon
import time, sys, traceback
daemon = get_daemon()
daemon.cycle_interval = 1800
daemon.start()
while daemon.is_running:
    time.sleep(10)
" 2>> data\thinking_daemon.log
echo [%date% %time%] 守护进程退出，30秒后重启... >> data\thinking_daemon.log
timeout /t 30 /nobreak >nul
goto restart
