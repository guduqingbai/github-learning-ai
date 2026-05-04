#!/usr/bin/env python3
"""停止正在运行的守护进程（通过 pythonw.exe 进程名匹配）"""

import subprocess
import sys
import os

def stop_daemon():
    """查找并终止 thinking_daemon.py 相关的 pythonw.exe 进程"""
    script_path = os.path.abspath(__file__)
    project_dir = os.path.dirname(script_path)

    # 用 tasklist 查找 pythonw.exe
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq pythonw.exe", "/FO", "CSV", "/NH"],
        capture_output=True, text=True
    )

    if "pythonw.exe" not in result.stdout:
        print("⚠️  没有运行中的守护进程")
        return

    # 通过 wmic 找到具体加载了 thinking_daemon.py 的进程
    try:
        proc = subprocess.run(
            ["wmic", "path", "win32_process", "where",
             'name="pythonw.exe"', "get", "ProcessId,CommandLine", "/FORMAT:CSV"],
            capture_output=True, text=True, timeout=10
        )
        lines = proc.stdout.strip().split("\n")
        pids = []
        for line in lines[1:]:  # skip header
            parts = line.split(",")
            if len(parts) >= 3 and "thinking_daemon" in parts[-1]:
                pid = parts[-2].strip()
                if pid.isdigit():
                    pids.append(pid)

        for pid in pids:
            subprocess.run(["taskkill", "/PID", pid, "/F"], check=True)
            print(f"✅ 已终止守护进程 (PID: {pid})")

        if not pids:
            print("⚠️  未找到 thinking_daemon 相关进程")

    except subprocess.TimeoutExpired:
        print("❌ wmic 查询超时")

    # 清理标志文件
    flag_file = os.path.join(project_dir, "daemon_running.flag")
    if os.path.exists(flag_file):
        os.remove(flag_file)
        print("🧹 已清理运行标志文件")


if __name__ == "__main__":
    stop_daemon()
