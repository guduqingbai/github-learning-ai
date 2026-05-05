#!/usr/bin/env python3
"""星期八自主思考守护进程 — 唯一启动入口"""
import os, sys, time
from pathlib import Path

os.chdir(str(Path(__file__).parent))

# ── 宪法完整性校验（系统启动前的红线检查）──
from constitution import verify_integrity
if not verify_integrity():
    print("❌ 宪法文件完整性校验失败！系统拒绝启动")
    sys.exit(1)
print("✅ 宪法完整性校验通过")

from thinking_daemon import get_daemon

LOCK_FILE = Path("data") / "thinking.lock"
LOCK_FILE.parent.mkdir(exist_ok=True)

# 文件锁单例（原子操作，无 TOCTOU 竞态）
lock_fd = None
try:
    # Windows 文件锁
    import msvcrt
    lock_fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_RDWR | os.O_TRUNC)
    msvcrt.locking(lock_fd, msvcrt.LK_NBLCK, 1)
except ImportError:
    try:
        # Unix 文件锁
        import fcntl
        lock_fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_RDWR)
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except ImportError:
        pass
except (BlockingIOError, PermissionError, OSError):
    print("星期八已在运行中（无法获取文件锁）")
    if lock_fd is not None:
        os.close(lock_fd)
    sys.exit(0)

if lock_fd is None:
    # 降级：PID 文件（无文件锁支持时）
    PID_FILE = Path("data") / "thinking.pid"
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
    if lock_fd is not None:
        os.close(lock_fd)
    # 降级 PID 文件清理
    pid_file = Path("data") / "thinking.pid"
    if pid_file.exists():
        pid_file.unlink()
