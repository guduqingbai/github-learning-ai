@echo off
REM ⚠️ DEPRECATED — 请使用 python start_thinking.py 启动
cd /d "C:\Users\吴文豪\claude-code-projects\github-learning"
echo [%date% %time%] 启动星期八看门狗(崩溃自动重启)...
start "Week8Watchdog" /MIN pythonw watchdog.py
echo [%date% %time%] 看门狗已启动
echo 查看状态: type data\thinking_daemon_state.json
echo 查看看门狗日志: type data\watchdog.log
echo 查看启动器日志: type data\daemon_launcher.log
