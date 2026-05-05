#!/usr/bin/env python3
"""星期八自主思考守护进程 — 永久启动入口"""
import os, sys, time
from pathlib import Path

os.chdir(str(Path(__file__).parent))

# ── 宪法完整性校验（系统启动前的红线检查）──
from constitution_gate import verify_integrity
if not verify_integrity():
    print("❌ 宪法文件完整性校验失败！系统拒绝启动")
    sys.exit(1)
print("✅ 宪法完整性校验通过")

from thinking_daemon import get_daemon

PID_FILE = Path("data") / "thinking.pid"
PID_FILE.parent.mkdir(exist_ok=True)

# 单例检查
if PID_FILE.exists():
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        print(f"星期八已在运行中 (PID: {pid})")
        sys.exit(0)
    except (OSError, ValueError):
        pass

PID_FILE.write_text(str(os.getpid()))

daemon = get_daemon()
daemon.max_interval = 1800  # 30分钟一轮
daemon.start()

print(f"🧠 星期八自主思考守护进程已启动 (PID: {os.getpid()})")
print(f"   循环间隔: {daemon.max_interval}s")
print(f"   日志: {daemon.log_file}")

try:
    while True:
        time.sleep(10)
        # 健康检查：如果守护线程挂了就重启
        if not daemon.is_running:
            print("守护线程已停止，尝试重启...", file=sys.stderr)
            daemon.start()
except KeyboardInterrupt:
    print("\n收到中断信号，停止守护进程...")
except Exception as e:
    print(f"主循环异常: {e}", file=sys.stderr)
finally:
    daemon.stop()
    if PID_FILE.exists():
        PID_FILE.unlink()
