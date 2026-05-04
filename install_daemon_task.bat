@echo off
REM 安装星期八自主思考守护进程为 Windows 计划任务
REM 实现：开机自启 + 每30分钟检查（崩溃自动重启）
REM 以管理员身份运行！

set VBS_SCRIPT="C:\Users\吴文豪\claude-code-projects\github-learning\start_daemon.vbs"
set TASK_NAME="XingQiBa Thinking Daemon"

echo ==========================================
echo 安装星期八守护进程计划任务
echo ==========================================

REM 删除旧任务（如果存在）
schtasks /Delete /TN %TASK_NAME% /F 2>nul

REM 创建新任务：开机启动
schtasks /Create /SC ONSTART /DELAY 0000:30 /TN %TASK_NAME% /TR %VBS_SCRIPT% /RL HIGHEST /F

REM 添加每30分钟触发（崩溃自动重启）
schtasks /Create /SC MINUTE /MO 30 /TN "%TASK_NAME% (keepalive)" /TR %VBS_SCRIPT% /RL HIGHEST /F

echo.
echo 计划任务创建完成！
echo.
echo 任务说明:
echo   - 开机 30 秒后自动启动守护进程
echo   - 每 30 分钟检查一次（自动重启已停止的进程）
echo   - 以后台无窗口方式运行 (pythonw.exe)
echo.
echo 管理命令:
echo   立即启动:   schtasks /Run /TN %TASK_NAME%
echo   停止守护进程: python stop_daemon.py
echo   查看状态:   schtasks /Query /TN %TASK_NAME%
echo   卸载:       schtasks /Delete /TN %TASK_NAME% /F ^&^& schtasks /Delete /TN "%TASK_NAME% (keepalive)" /F
echo.
pause
