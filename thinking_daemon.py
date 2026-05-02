#!/usr/bin/env python3
"""
🧠 自主思考守护进程 — 让系统在无人干预下持续自我思考
每30分钟自动运行思考循环，将洞察转化为实际行动
"""

import time
import json
import threading
import signal
import atexit
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ThinkingDaemon:
    """自主思考守护进程"""

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.log_file = self.data_dir / "thinking_daemon.log"
        self.state_file = self.data_dir / "thinking_daemon_state.json"

        # 守护进程状态
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._thinking_agent = None
        self._modification_engine = None

        # 配置（可被自我修改调整）
        self.cycle_interval = 1800  # 30分钟
        self.thinking_depth = 3
        self.heal_threshold = 0.7   # 重要性超过此值的洞察触发自我修复

        # 统计
        self.cycle_count = 0
        self.last_cycle_time: Optional[str] = None

        # 注册退出处理
        atexit.register(self._shutdown)
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except (ValueError, AttributeError):
            pass  # 非主线程或Windows下某些信号不可用

        self._load_state()
        self._log("自主思考守护进程初始化完成")

    def _signal_handler(self, signum, frame):
        self._log(f"收到信号 {signum}，正在关闭...")
        self.stop()

    def _shutdown(self):
        if self.is_running:
            self.stop()

    # ---- 生命周期 ----

    def start(self):
        """启动守护进程"""
        if self.is_running:
            self._log("已在运行中")
            return False

        self.is_running = True
        self._thread = threading.Thread(target=self._daemon_loop, daemon=True)
        self._thread.start()
        self._log("自主思考守护进程已启动")
        return True

    def stop(self):
        """停止守护进程"""
        if not self.is_running:
            return
        self.is_running = False
        self._save_state()
        self._log("自主思考守护进程已停止")

    # ---- 核心循环 ----

    def _daemon_loop(self):
        """守护进程主循环"""
        while self.is_running:
            try:
                self._run_thinking_cycle()
                self.cycle_count += 1
                self.last_cycle_time = datetime.now().isoformat()
                self._save_state()
            except Exception as e:
                self._log(f"思考循环异常: {e}")

            # 等待到下一个周期（每秒检查是否该停止）
            for _ in range(self.cycle_interval):
                if not self.is_running:
                    return
                time.sleep(1)

    def _run_thinking_cycle(self):
        """执行一轮完整的思考→行动循环"""
        self._log(f"开始第 {self.cycle_count + 1} 轮思考循环")

        # 1. 延迟导入（避免循环依赖）
        if self._thinking_agent is None:
            from self_thinking_agent import SelfThinkingAgent
            self._thinking_agent = SelfThinkingAgent()

        if self._modification_engine is None:
            from self_modification_engine import SelfModificationEngine
            self._modification_engine = SelfModificationEngine()

        # 2. 运行思考循环
        insights = self._thinking_agent.run_thinking_cycle(depth=self.thinking_depth)

        if not insights:
            self._log("本轮没有新的洞察")
            return

        self._log(f"生成了 {len(insights)} 个洞察")

        # 3. 尝试将洞察转化为自我修改
        heals_applied = self._apply_heals(insights)

        if heals_applied > 0:
            self._log(f"应用了 {heals_applied} 个自我修复")

    def _apply_heals(self, insights: list) -> int:
        """根据洞察尝试自我修复"""
        applied = 0

        for insight in insights:
            # 检查洞察是否包含修改建议
            findings = insight.get("findings", [])
            summary = insight.get("summary", "")
            topic = insight.get("topic", "")

            # 寻找可修复的代码问题
            for finding in findings:
                if "文档缺失" in finding or "模块文档缺失" in finding:
                    # 尝试为对应文件添加文档
                    filepath = self._extract_file_from_topic(topic)
                    if filepath:
                        result = self._modification_engine.add_module_docstring(filepath)
                        if result.get("success"):
                            applied += 1
                            self._log(f"✅ 已修复: {filepath} 添加模块文档")

            # 检查 summary 中是否有可修复的问题
            if "裸 except" in summary or "bare except" in summary:
                filepath = self._extract_file_from_topic(topic)
                if filepath:
                    result = self._modification_engine.fix_bare_excepts(filepath)
                    if result.get("success"):
                        applied += 1
                        self._log(f"✅ 已修复: {filepath} 修复裸 except")

        return applied

    # ---- 查询接口 ----

    def get_status(self) -> Dict[str, Any]:
        """获取守护进程状态"""
        return {
            "running": self.is_running,
            "cycle_count": self.cycle_count,
            "cycle_interval": self.cycle_interval,
            "thinking_depth": self.thinking_depth,
            "heal_threshold": self.heal_threshold,
            "last_cycle": self.last_cycle_time,
            "modification_stats": self._modification_engine.get_modification_stats()
            if self._modification_engine else {},
        }

    def update_config(self, **kwargs):
        """动态更新配置（可被系统自我调用）"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self._log(f"配置更新: {key} = {value}")

    # ---- 内部方法 ----

    def _load_state(self):
        """加载持久化状态"""
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text(encoding="utf-8"))
                self.cycle_count = state.get("cycle_count", 0)
                self.last_cycle_time = state.get("last_cycle_time")
                self.cycle_interval = state.get("cycle_interval", 1800)
                self.thinking_depth = state.get("thinking_depth", 3)
                self._log(f"加载状态: 已运行 {self.cycle_count} 轮")
            except Exception:
                pass

    def _save_state(self):
        """持久化当前状态"""
        try:
            state = {
                "cycle_count": self.cycle_count,
                "last_cycle_time": self.last_cycle_time,
                "cycle_interval": self.cycle_interval,
                "thinking_depth": self.thinking_depth,
                "heal_threshold": self.heal_threshold,
                "updated_at": datetime.now().isoformat(),
            }
            self.state_file.write_text(
                json.dumps(state, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            self._log(f"状态保存失败: {e}")

    def _log(self, message: str):
        """记录日志"""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] [思考守护进程] {message}"
        print(entry)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception:
            pass

    @staticmethod
    def _extract_file_from_topic(topic: str) -> Optional[str]:
        """从洞察 topic 提取文件名"""
        if not topic:
            return None
        # topic 格式如 "xxx 模块分析" 或 "xxx vs yyy"
        for suffix in [" 模块分析", " 相似度分析"]:
            if suffix in topic:
                name = topic.replace(suffix, "")
                py = Path(f"{name}.py")
                if py.exists():
                    return str(py)
        return None


# ---- 全局单例 ----

_daemon_instance: Optional[ThinkingDaemon] = None


def get_daemon() -> ThinkingDaemon:
    """获取全局守护进程实例"""
    global _daemon_instance
    if _daemon_instance is None:
        _daemon_instance = ThinkingDaemon()
    return _daemon_instance


def main():
    """启动守护进程"""
    print("🧠 自主思考守护进程")
    print("=" * 60)
    daemon = get_daemon()
    daemon.start()

    try:
        # 主线程保持活动
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    finally:
        daemon.stop()
        status = daemon.get_status()
        print(f"\n📊 运行统计:")
        print(f"   思考轮次: {status['cycle_count']}")
        print(f"   运行状态: {'运行中' if status['running'] else '已停止'}")


if __name__ == "__main__":
    main()
