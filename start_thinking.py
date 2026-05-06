#!/usr/bin/env python3
"""星期八自主思考守护进程 — 唯一启动入口"""
import os
import subprocess
import sys
import time
from pathlib import Path

os.chdir(str(Path(__file__).parent))

# ── 宪法完整性校验（系统启动前的红线检查）──
from constitution import verify_integrity
if not verify_integrity():
    print("❌ 宪法文件完整性校验失败！系统拒绝启动")
    sys.exit(1)
print("✅ 宪法完整性校验通过")

from thinking_daemon import get_daemon

daemon = get_daemon()
daemon.max_interval = 1800  # 30分钟一轮
daemon.start()

print(f"🧠 星期八自主思考守护进程已启动 (PID: {os.getpid()})")
print(f"   循环间隔: {daemon.max_interval}s")
print(f"   日志: {daemon.log_file}")

try:
    while True:
        time.sleep(10)
        # 双重检查：is_running 标志 + 线程实际存活
        if not daemon.is_running or not (daemon._thread and daemon._thread.is_alive()):
            if daemon.is_running:
                print("⚠️ 守护线程已死亡但标志仍在，重置...", file=sys.stderr)
                daemon.is_running = False
            print("守护线程已停止，尝试重启...", file=sys.stderr)
            daemon.start()
except KeyboardInterrupt:
    print("\n收到中断信号，停止守护进程...")
except Exception as e:
    print(f"主循环异常: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
finally:
    daemon.stop()
