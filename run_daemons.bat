@echo off
cd /d "%~dp0"
echo [%date% %time%] 启动所有守护进程...

:: 思考守护进程
start "ThinkingDaemon" /B python -c "
from thinking_daemon import get_daemon
import time
daemon = get_daemon()
daemon.cycle_interval = 1800
daemon.start()
while daemon.is_running:
    time.sleep(10)
" > data\thinking_daemon.log 2>&1
echo [%date% %time%] 思考守护进程已启动 (PID: !ERRORLEVEL!)

:: 爬虫守护进程
start "CrawlerDaemon" /B python -c "
import sys
sys.path.insert(0, '.')
from crawler_daemon import CrawlerDaemon
import time
daemon = CrawlerDaemon()
daemon.start()
while daemon.is_running:
    time.sleep(10)
" > data\crawler_daemon_out.log 2>&1
echo [%date% %time%] 爬虫守护进程已启动

echo 所有守护进程已启动，运行中...
