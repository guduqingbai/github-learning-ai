#!/usr/bin/env python3
"""
🛡️ 守护进程看门狗 — 进程挂了自动重启
被开机自启调用，持续监控 daemon_launcher.py
"""
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "data" / "watchdog.log"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [看门狗] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def main():
    (BASE_DIR / "data").mkdir(exist_ok=True)
    os.chdir(str(BASE_DIR))

    log("🛡️ 看门狗启动")
    log(f"工作目录: {BASE_DIR}")

    restart_count = 0
    while True:
        try:
            log("🚀 启动守护进程...")
            proc = subprocess.Popen(
                [sys.executable, "daemon_launcher.py"],
                cwd=str(BASE_DIR),
                stdout=open(BASE_DIR / "data" / "daemon_launcher_out.log", "a"),
                stderr=subprocess.STDOUT,
            )
            log(f"守护进程已启动 (PID: {proc.pid})")

            # 等待进程退出（阻塞）
            proc.wait()

            restart_count += 1
            log(f"⚠️ 守护进程退出了 (返回码: {proc.returncode}, 已重启{restart_count}次)")

            # 清理锁文件
            lock = BASE_DIR / "data" / "daemon.lock"
            if lock.exists():
                lock.unlink()

        except Exception as e:
            log(f"❌ 看门狗异常: {e}")

        log("30秒后重启守护进程...")
        time.sleep(30)


if __name__ == "__main__":
    main()
