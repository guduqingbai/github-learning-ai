#!/usr/bin/env python3
"""
🚀 统一守护进程启动器 — PID锁防多开，思考+爬虫+交易三守护
"""
import os
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
os.chdir(str(BASE_DIR))
LOCK_FILE = BASE_DIR / "data" / "daemon.lock"
LOG_FILE = BASE_DIR / "data" / "daemon_launcher.log"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [启动器] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def acquire_lock() -> bool:
    try:
        (BASE_DIR / "data").mkdir(exist_ok=True)
        if LOCK_FILE.exists():
            pid = int(LOCK_FILE.read_text().strip())
            try:
                os.kill(pid, 0)
                log(f"⚠️ 已有守护进程在运行 (PID: {pid})")
                return False
            except OSError:
                log("发现过期锁文件，覆盖")
        LOCK_FILE.write_text(str(os.getpid()))
        return True
    except Exception as e:
        log(f"锁获取失败: {e}")
        return False


def release_lock():
    try:
        if LOCK_FILE.exists() and int(LOCK_FILE.read_text().strip()) == os.getpid():
            LOCK_FILE.unlink()
    except Exception:
        pass


def thinking_loop():
    """思考守护进程主循环：每30分钟跑一轮"""
    from thinking_daemon import get_daemon
    daemon = get_daemon()
    daemon.cycle_interval = 1800
    log("🧠 思考守护进程启动")
    while True:
        try:
            daemon._run_thinking_cycle()
            daemon.cycle_count += 1
            daemon.last_cycle_time = datetime.now().isoformat()
            daemon._save_state()
            daemon._write_health_status()
        except Exception as e:
            log(f"⚠️ 思考循环异常: {e}")
            try:
                daemon._write_health_status(error=str(e)[:100])
            except Exception:
                pass
        # 等30分钟，每秒检查是否退出
        for _ in range(daemon.cycle_interval):
            time.sleep(1)


def crawler_loop():
    """爬虫守护进程主循环：首次立即执行，之后每2小时"""
    from crawler_daemon import CrawlerDaemon
    daemon = CrawlerDaemon()
    log("🕷️ 爬虫守护进程启动")
    # 首次立即执行
    daemon.run_crawl_task()
    # 之后每2小时
    while True:
        for _ in range(7200):  # 2小时 = 7200秒
            time.sleep(1)
        daemon.run_crawl_task()


def trading_loop():
    """交易监控守护进程：每10分钟扫描一次市场"""
    try:
        from trading_bot import MarketMonitor
        monitor = MarketMonitor()
        log("📈 交易监控守护进程启动 (间隔600秒)")
        while True:
            try:
                result = monitor.run_scan()
                signal_count = result.get("total_signals", 0)
                log(f"📊 市场扫描完成: {signal_count} 个信号")
            except Exception as e:
                log(f"⚠️ 交易扫描异常: {e}")
            for _ in range(600):  # 10分钟
                time.sleep(1)
    except ImportError as e:
        log(f"⚠️ 交易监控不可用 (请先安装 ccxt): {e}")
    except Exception as e:
        log(f"⚠️ 交易监控启动失败: {e}")


def main():
    log(f"守护进程启动器 v1.0 (PID: {os.getpid()})")

    if not acquire_lock():
        log("退出：已有实例在运行")
        sys.exit(1)

    try:
        t1 = threading.Thread(target=thinking_loop, daemon=True)
        t1.start()
        time.sleep(0.5)

        t2 = threading.Thread(target=crawler_loop, daemon=True)
        t2.start()

        t3 = threading.Thread(target=trading_loop, daemon=True)
        t3.start()
        time.sleep(0.5)

        log("✅ 所有守护进程已启动，主线程保活中...")

        # 主线程监控保活
        while True:
            time.sleep(30)
            if not t1.is_alive():
                log("⚠️ 思考线程死亡，重启")
                t1 = threading.Thread(target=thinking_loop, daemon=True)
                t1.start()
            if not t2.is_alive():
                log("⚠️ 爬虫线程死亡，重启")
                t2 = threading.Thread(target=crawler_loop, daemon=True)
                t2.start()
            if not t3.is_alive():
                log("⚠️ 交易线程死亡，重启")
                t3 = threading.Thread(target=trading_loop, daemon=True)
                t3.start()

    except KeyboardInterrupt:
        log("用户中断")
    finally:
        release_lock()


if __name__ == "__main__":
    main()
