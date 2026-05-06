#!/usr/bin/env python3
"""
🧠 自主思考守护进程 — 让系统在无人干预下持续自我思考
每30分钟自动运行思考循环，将洞察转化为实际行动

⚠️ 安全警告：本模块创建 24/7 常驻后台进程，在无人干预下自动执行
思考循环和自我修改。请确保在可控环境中运行。
"""

import time
import json
import os
import threading
import signal
import atexit
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from antibody_library import AntibodyLibrary
from cycle_diary import CycleDiary
from circuit_breaker import CircuitBreaker, CircuitState
from self_memory import SelfMemory


class DaemonHookEvent(str, Enum):
    """守护进程 Tick 生命周期事件"""
    TICK_START = "tick_start"
    PRE_CYCLE = "pre_cycle"
    POST_CYCLE = "post_cycle"
    TICK_END = "tick_end"
    PRE_SLEEP = "pre_sleep"
    WAKE_UP = "wake_up"
    ERROR = "error"


class DaemonHook:
    """单个 Tick 钩子"""
    def __init__(self, event: str, handler, *, name: str = "", priority: int = 0):
        self.event = event
        self.handler = handler
        self.name = name or getattr(handler, "__name__", "unnamed")
        self.priority = priority


# ── ForkedAgent 模式（源自 Claude Code runForkedAgent）──────────────

class ForkedAgent:
    """Fire-and-forget 子代理：后台并行执行，永不阻塞主循环"""

    @staticmethod
    def fire(target: Callable, args: tuple = (), *,
             name: str = "fork", on_done: Optional[Callable] = None) -> threading.Thread:
        """启动后台任务，可选完成回调"""
        def wrapper():
            try:
                result = target(*args)
                if on_done:
                    on_done(result)
            except Exception:
                pass
        thread = threading.Thread(target=wrapper, daemon=True, name=name)
        thread.start()
        return thread

    @staticmethod
    def fire_and_forget(target: Callable, args: tuple = (), name: str = "fork"):
        """纯发后即忘，不关心结果"""
        return ForkedAgent.fire(target, args, name=name)


# ── StopHook 系统（源自 Claude Code stopHooks.ts）─────────────────

@dataclass
class StopHook:
    """后台钩子服务：每轮结束后 fire-and-forget 执行
    每个钩子有独立的门控检查 + 执行体，互不干扰"""
    name: str
    gate_check: Callable  # (daemon) -> bool — 最便宜的检查最先执行
    run: Callable         # (daemon) -> None — 实际工作，在后台线程执行
    priority: int = 0
    cooldown: float = 300.0  # 秒，同类型最小执行间隔
    _last_run: float = 0.0


# ── Suppression Pipeline（源自 PromptSuggestion 的抑制检查）─────

class SuppressionPipeline:
    """行动前快速判断是否该行动：防止重复执行、频率过高、无数据时空转"""

    def __init__(self):
        self._last_action: Dict[str, float] = {}

    def should_suppress(self, action_name: str, min_interval: float = 300.0) -> bool:
        """检查此操作是否被抑制"""
        now = time.time()
        last = self._last_action.get(action_name, 0.0)
        if now - last < min_interval:
            return True  # 过于频繁
        self._last_action[action_name] = now
        return False

    def reset(self, action_name: str):
        """重置抑制状态"""
        self._last_action.pop(action_name, None)


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
        self.thinking_depth = 5     # 每轮探索问题数
        self.heal_threshold = 0.6   # 重要性超过此值的洞察触发自我修复

        # ---- KAIROS Tick 系统 ----
        self._hooks: Dict[str, List[DaemonHook]] = {}
        self.min_interval = 60       # 最短间隔（连续失败时）
        self.max_interval = 1800     # 最长间隔（正常）
        self.backoff_factor = 3      # 失败次数放大倍数

        # ---- 健康指标追踪 ----
        self.cycle_count = 0
        self.last_cycle_time: Optional[str] = None
        self.consecutive_failures = 0
        self.error_count = 0
        self.total_cycle_duration = 0.0
        self.total_heal_attempts = 0
        self.total_heal_successes = 0
        self.cycle_durations: List[float] = []

        # ---- 文件锁（防止多实例） ----
        self._lock_fd: Optional[int] = None
        self._lock_path = self.data_dir / "thinking.lock"

        # ---- 抗体库（可组合自愈单元） ----
        self._antibody_library = AntibodyLibrary()

        # ---- 周期日记（事件记录） ----
        self._diary = CycleDiary(self.data_dir)

        # ---- 星期八的自我记忆 ----
        self._self_memory = SelfMemory(self.data_dir)

        # ---- 熔断器 ----
        self._circuit_breaker = CircuitBreaker(
            data_dir=self.data_dir,
            failure_threshold=3,
            cooldown_seconds=120,
            half_open_max_calls=1,
        )

        # ---- StopHook 系统 ----
        self._stop_hooks: List[StopHook] = []
        self._suppression = SuppressionPipeline()
        self._background_tasks: List[threading.Thread] = []

        # 注册默认 stop hooks
        self._register_default_hooks()

        # 注册退出处理
        atexit.register(self._shutdown)
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except (ValueError, AttributeError):
            pass  # 非主线程或Windows下某些信号不可用

        self._load_state()
        # 注册到全局注册中心（破循环依赖）
        from daemon_registry import register_daemon as _reg
        _reg(self)
        self._log("自主思考守护进程初始化完成")

    def _signal_handler(self, signum, frame):
        self._log(f"收到信号 {signum}，正在关闭...")
        self.stop()

    def _shutdown(self):
        if self.is_running:
            self.stop()

    # ---- 生命周期 ----

    def start(self):
        """启动守护进程（文件锁防多实例）"""
        if self.is_running:
            self._log("已在运行中")
            return False

        # 文件锁：防止多个守护进程同时运行
        if not self._acquire_lock():
            return False

        self.is_running = True
        self._thread = threading.Thread(target=self._daemon_loop, daemon=True)
        self._thread.start()
        self._log("自主思考守护进程已启动")
        return True

    def _acquire_lock(self) -> bool:
        """获取文件锁，防止多实例。返回 True=成功获取锁"""
        self.data_dir.mkdir(exist_ok=True)
        try:
            # Windows 文件锁
            import msvcrt
            self._lock_fd = os.open(str(self._lock_path),
                                    os.O_CREAT | os.O_RDWR | os.O_TRUNC)
            msvcrt.locking(self._lock_fd, msvcrt.LK_NBLCK, 1)
            return True
        except ImportError:
            try:
                # Unix 文件锁
                import fcntl
                self._lock_fd = os.open(str(self._lock_path),
                                        os.O_CREAT | os.O_RDWR)
                fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except ImportError:
                self._log("  警告: 无法获取文件锁（不支持的平台），跳过防多实例检查")
                return True
        except (BlockingIOError, PermissionError, OSError):
            print("❌ 星期八已在运行中（另一个守护进程持有文件锁）")
            self._log("另一个守护进程正在运行，拒绝启动")
            if self._lock_fd is not None:
                os.close(self._lock_fd)
                self._lock_fd = None
            return False

    def _release_lock(self):
        """释放文件锁"""
        if self._lock_fd is not None:
            try:
                os.close(self._lock_fd)
            except Exception:
                pass
            self._lock_fd = None
        try:
            if self._lock_path.exists():
                self._lock_path.unlink()
        except Exception:
            pass

    def stop(self):
        """停止守护进程"""
        if not self.is_running:
            return
        self.is_running = False
        self._save_state()
        self._release_lock()
        self._log("自主思考守护进程已停止")

    # ---- Tick Hook 系统 ----

    def register_tick_hook(self, event: str, handler, *, name: str = "", priority: int = 0):
        """注册 Tick 生命周期钩子"""
        hook = DaemonHook(event, handler, name=name, priority=priority)
        self._hooks.setdefault(event, []).append(hook)
        self._hooks[event].sort(key=lambda h: h.priority)

    def unregister_tick_hook(self, event: str, handler=None, name: str = ""):
        """移除 Tick 钩子"""
        hooks = self._hooks.get(event, [])
        if handler:
            self._hooks[event] = [h for h in hooks if h.handler != handler]
        elif name:
            self._hooks[event] = [h for h in hooks if h.name != name]
        if not self._hooks.get(event):
            self._hooks.pop(event, None)

    def _run_tick_hooks(self, event: str, **context):
        """执行指定事件的所有 Tick 钩子"""
        hooks = self._hooks.get(event, [])
        if not hooks:
            return
        for hook in hooks:
            try:
                hook.handler(self, **context)
            except Exception as e:
                self._log(f"钩子 [{hook.name}] 执行失败: {e}")

    # ---- StopHook 系统 ----

    def register_stop_hook(self, hook: StopHook):
        """注册一个后台钩子服务"""
        self._stop_hooks.append(hook)
        self._stop_hooks.sort(key=lambda h: h.priority)
        self._log(f"注册 StopHook: {hook.name}")

    def unregister_stop_hook(self, name: str):
        """移除一个后台钩子服务"""
        self._stop_hooks = [h for h in self._stop_hooks if h.name != name]

    def _run_stop_hooks(self):
        """每轮结束后执行所有 stop hooks（fire-and-forget，永不阻塞主循环）"""
        for hook in self._stop_hooks:
            # 抑制检查：太频繁就不跑
            if self._suppression.should_suppress(hook.name, hook.cooldown):
                continue
            # 门控检查：最便宜的检查最先
            try:
                if not hook.gate_check(self):
                    continue
            except Exception as e:
                self._log(f"  StopHook [{hook.name}] 门控异常: {e}")
                continue
            # Fire-and-forget：后台线程执行
            hook._last_run = time.time()
            def run_wrapper(h=hook):
                try:
                    h.run(self)
                    self._log(f"  StopHook [{h.name}] 完成")
                except Exception as e:
                    self._log(f"  StopHook [{h.name}] 异常: {e}")
            t = ForkedAgent.fire(run_wrapper, name=f"stophook-{hook.name}")
            self._background_tasks.append(t)
        # 清理已结束的线程引用
        self._background_tasks = [t for t in self._background_tasks if t.is_alive()]

    def _register_default_hooks(self):
        """注册默认的 stop hooks"""
        # ---- H1: 知识库自动整理 ----
        self.register_stop_hook(StopHook(
            name="auto_consolidation",
            priority=10,
            cooldown=3600.0,  # 最少间隔 1h
            gate_check=lambda d: self._gate_consolidation(d),
            run=lambda d: self._run_consolidation(d),
        ))
        # ---- H2: 记忆提取 ----
        self.register_stop_hook(StopHook(
            name="memory_extraction",
            priority=20,
            cooldown=600.0,  # 最少间隔 10min
            gate_check=lambda d: self._gate_memory_extraction(d),
            run=lambda d: self._run_memory_extraction(d),
        ))
        # ---- H3: 健康自检 ----
        self.register_stop_hook(StopHook(
            name="health_check",
            priority=30,
            cooldown=3600.0,  # 最少间隔 1h
            gate_check=lambda d: True,  # 无门控，靠 cooldown 节流
            run=lambda d: self._run_health_check(d),
        ))
        # ---- H4: 研究调度器 ----
        self.register_stop_hook(StopHook(
            name="research_scheduler",
            priority=40,
            cooldown=1800.0,  # 最少间隔 30min
            gate_check=lambda d: self._gate_research_scheduler(d),
            run=lambda d: self._run_research_scheduler(d),
        ))
        # ---- H5: Claude 记忆同步 ----
        self.register_stop_hook(StopHook(
            name="claude_memory_sync",
            priority=45,
            cooldown=1800.0,  # 最少间隔 30min
            gate_check=lambda d: self._gate_claude_memory_sync(d),
            run=lambda d: self._run_claude_memory_sync(d),
        ))
        # ---- H6: 知识爬虫 ----
        self.register_stop_hook(StopHook(
            name="knowledge_crawler",
            priority=50,
            cooldown=7200.0,  # 最少间隔 2h
            gate_check=lambda d: self._gate_knowledge_crawler(d),
            run=lambda d: self._run_knowledge_crawler(d),
        ))

    @staticmethod
    def _gate_consolidation(daemon) -> bool:
        """知识库整理门控：feature flag + 时间门 + 条目门 + 锁门"""
        from system_state_manager import SystemStateManager
        try:
            sm = SystemStateManager()
            ffm = sm.get_feature_flag_manager()
            if not ffm.is_enabled("auto_consolidation"):
                return False
        except Exception:
            pass
        # 时间门 + 条目门（从 consolidate_tracker 读取）
        from knowledge_base import KnowledgeBase
        tracker_file = daemon.data_dir / "consolidate_tracker.json"
        if tracker_file.exists():
            try:
                tracker = json.loads(tracker_file.read_text(encoding="utf-8"))
                last_run = tracker.get("last_run", "")
                if last_run:
                    last = datetime.fromisoformat(last_run)
                    hours_since = (datetime.now() - last).total_seconds() / 3600
                    if hours_since < 12:  # 至少 12 小时
                        return False
                # 条目门：至少 5 个新条目
                kb = KnowledgeBase()
                current = len(kb.get_all_knowledge())
                prev = tracker.get("kb_size", 0)
                if prev > 0 and current - prev < 5:
                    return False
            except Exception:
                pass
        # 锁门
        return KnowledgeBase.acquire_consolidation_lock(daemon.data_dir)

    @staticmethod
    def _gate_memory_extraction(daemon) -> bool:
        """记忆提取门控：feature flag + 有新条目"""
        from system_state_manager import SystemStateManager
        try:
            sm = SystemStateManager()
            ffm = sm.get_feature_flag_manager()
            if not ffm.is_enabled("memory_extraction"):
                return False
        except Exception:
            pass
        # 检查是否有新知识条目
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            tracker_file = daemon.data_dir / "extract_tracker.json"
            if tracker_file.exists():
                tracker = json.loads(tracker_file.read_text(encoding="utf-8"))
                last_idx = tracker.get("last_idx", -1)
                total = len(kb.get_all_knowledge())
                if total <= last_idx + 1:
                    return False  # 没有新条目
        except Exception:
            pass
        return True

    # ---- StopHook 执行体 ----

    @staticmethod
    def _run_consolidation(daemon):
        """执行知识库整理（后台线程）"""
        from knowledge_base import KnowledgeBase
        try:
            kb = KnowledgeBase()
            stats = kb.consolidate_knowledge(max_per_category=50, dry_run=False)
            # 更新追踪
            tracker_file = daemon.data_dir / "consolidate_tracker.json"
            tracker = {"last_run": datetime.now().isoformat(), "kb_size": len(kb.get_all_knowledge()), "last_stats": stats}
            tracker_file.write_text(json.dumps(tracker, ensure_ascii=False, indent=2))
            if stats.get("removed_stale") or stats.get("deduped") or stats.get("pruned"):
                daemon._log(f"  🧹 知识库整理: 清理 {stats.get('removed_stale',0)} 过期 + {stats.get('deduped',0)} 去重 + {stats.get('pruned',0)} 修剪")
        finally:
            KnowledgeBase.release_consolidation_lock(daemon.data_dir)

    @staticmethod
    def _run_memory_extraction(daemon):
        """执行记忆提取（后台线程）"""
        from self_thinking_agent import SelfThinkingAgent
        agent = SelfThinkingAgent()
        agent._extract_memories()

    @staticmethod
    def _run_health_check(daemon):
        """执行健康自检"""
        # 检查最近的修复是否仍然有效
        if daemon._thinking_agent:
            try:
                agent = daemon._thinking_agent
                agent.snapshot = agent.scanner.get_full_snapshot()
                agent._verify_past_improvements()
            except Exception as e:
                daemon._log(f"  健康自检异常: {e}")

    # ---- 研究调度器门控 + 执行体 ----

    @staticmethod
    def _gate_research_scheduler(daemon) -> bool:
        """研究调度器门控：feature flag + 任务队列上限"""
        from system_state_manager import SystemStateManager
        try:
            sm = SystemStateManager()
            ffm = sm.get_feature_flag_manager()
            if not ffm.is_enabled("global_research"):
                return False
        except Exception:
            pass
        # 检查待处理队列长度（最多 30 个）
        task_file = daemon.data_dir / "crawler_tasks.json"
        if task_file.exists():
            try:
                tasks = json.loads(task_file.read_text(encoding="utf-8"))
                if len(tasks) >= 30:
                    return False
            except Exception:
                pass
        return True

    @staticmethod
    def _run_research_scheduler(daemon):
        """从 stats + goals 生成爬虫研究任务"""
        from system_state_manager import SystemStateManager
        task_file = daemon.data_dir / "crawler_tasks.json"
        existing_tasks = []
        if task_file.exists():
            try:
                existing_tasks = json.loads(
                    task_file.read_text(encoding="utf-8"))
            except Exception:
                existing_tasks = []
        existing_queries = {t.get("query", "") for t in existing_tasks}

        new_tasks = []
        topics_found = set()

        # 1. 从知识缺口生成任务
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            # 获取当前知识分类统计
            all_k = kb.get_all_knowledge()
            categories = {}
            for entry in all_k:
                cat = entry.get("category", "未分类")
                categories.setdefault(cat, 0)
                categories[cat] += 1
            # 找出分类数最少的领域
            sorted_cats = sorted(categories.items(), key=lambda x: x[1])
            for cat, count in sorted_cats[:2]:
                if count < 5:
                    gap_query = f"{cat} 前沿研究"
                    if gap_query not in existing_queries:
                        new_tasks.append({
                            "query": gap_query,
                            "domain": cat,
                            "reason": f"研究调度器: {cat} 领域知识不足 ({count} 条)",
                            "priority": "medium",
                        })
                        existing_queries.add(gap_query)
                        topics_found.add(cat)
        except Exception:
            pass

        # 2. 从 GoalPlanner 活跃目标生成任务
        try:
            from goal_planner import GoalPlanner
            gp = GoalPlanner()
            summary = gp.get_summary()
            for g in summary.get("active", []):
                cat = g.get("category", "")
                desc = g.get("desc", "")
                if desc and cat:
                    # 如果目标描述看起来像研究主题
                    words = desc.split()[:4]
                    query = " ".join(words)
                    if query not in existing_queries:
                        new_tasks.append({
                            "query": query,
                            "domain": cat,
                            "reason": f"研究调度器: 目标驱动 — {desc[:60]}",
                            "priority": "high",
                        })
                        existing_queries.add(query)
                        topics_found.add(cat)
        except Exception:
            pass

        # 3. 从元认知监控获取研究缺口
        try:
            from metacognitive_monitor import MetacognitiveMonitor
            mm = MetacognitiveMonitor()
            # 通过检查历史找 gap
            state_file = daemon.data_dir / "metacognitive_state.json"
            if state_file.exists():
                import json as j
                data = j.loads(state_file.read_text(encoding="utf-8"))
                for h in data.get("findings_history", []):
                    if h.get("type") == "loop":
                        query = "元认知 思考循环 突破策略"
                        if query not in existing_queries:
                            new_tasks.append({
                                "query": query,
                                "domain": "元认知",
                                "reason": f"研究调度器: 检测到思考循环 — {h.get('detail', '')[:60]}",
                                "priority": "high",
                            })
                            existing_queries.add(query)
                            break
        except Exception:
            pass

        if new_tasks:
            existing_tasks.extend(new_tasks)
            try:
                import json as j
                task_file.write_text(
                    j.dumps(existing_tasks, ensure_ascii=False, indent=2),
                    encoding="utf-8")
            except Exception:
                pass

        if topics_found:
            daemon._log(
                f"  📚 研究调度: 生成 {len(new_tasks)} 个新任务 "
                f"({', '.join(sorted(topics_found))})")

    # ---- Claude 记忆同步门控 + 执行体 ----

    @staticmethod
    def _gate_claude_memory_sync(daemon) -> bool:
        """Claude 记忆同步门控：特征开关 + 有意义变化"""
        from system_state_manager import SystemStateManager
        try:
            sm = SystemStateManager()
            ffm = sm.get_feature_flag_manager()
            if not ffm.is_enabled("claude_memory_bridge"):
                return False
        except Exception:
            pass
        try:
            from claude_memory_bridge import ClaudeMemoryBridge
            bridge = ClaudeMemoryBridge()
            return bridge.should_sync()
        except Exception:
            return False

    @staticmethod
    def _run_claude_memory_sync(daemon):
        """执行 Claude 记忆同步（后台线程）"""
        try:
            from claude_memory_bridge import ClaudeMemoryBridge
            bridge = ClaudeMemoryBridge()
            result = bridge.sync()
            if result.get("synced"):
                daemon._log(
                    f"  🧠 Claude记忆同步: {result.get('memory_name')} "
                    f"({result.get('entries_count', 0)} 条目, {result.get('reason', '')})")
            elif result.get("reason") != "no_changes":
                daemon._log(f"  🧠 Claude记忆同步跳过: {result.get('reason', 'unknown')}")
        except Exception as e:
            daemon._log(f"  🧠 Claude记忆同步异常: {e}")

    @staticmethod
    def _gate_knowledge_crawler(daemon) -> bool:
        """知识爬虫门控：特征开关"""
        from system_state_manager import SystemStateManager
        try:
            sm = SystemStateManager()
            ffm = sm.get_feature_flag_manager()
            if not ffm.is_enabled("network_crawler"):
                return False
        except Exception:
            pass
        return True

    @staticmethod
    def _run_knowledge_crawler(daemon):
        """执行知识爬取（后台线程）"""
        try:
            from ai_knowledge_crawler import AIKnowledgeCrawler
            crawler = AIKnowledgeCrawler()
            crawler.crawl_all()
        except Exception as e:
            daemon._log(f"  🕷️ 知识爬虫异常: {e}")

    # ---- 核心循环 ----

    def _daemon_loop(self):
        """守护进程主循环 — KAIROS Tick 模式"""
        self._log("守护线程开始运行 (KAIROS Tick 模式)")
        while self.is_running:
            self._run_tick_hooks(DaemonHookEvent.TICK_START)
            try:
                cycle_start = time.time()
                self._run_tick_hooks(DaemonHookEvent.PRE_CYCLE)
                self._run_thinking_cycle()
                elapsed = time.time() - cycle_start
                self.cycle_count += 1
                self.last_cycle_time = datetime.now().isoformat()
                self.total_cycle_duration += elapsed
                self.cycle_durations.append(elapsed)
                if len(self.cycle_durations) > 50:
                    self.cycle_durations.pop(0)
                self._log(f"第 {self.cycle_count} 轮完成 ({elapsed:.0f}s) | 连续失败: {self.consecutive_failures}")
                self._save_state()
                self._write_health_status()
                self.consecutive_failures = 0  # 成功后重置
                self._run_tick_hooks(DaemonHookEvent.POST_CYCLE, elapsed=elapsed)
                # Fire-and-forget stop hooks（不阻塞主循环）
                self._run_stop_hooks()
            except Exception as e:
                self.consecutive_failures += 1
                self.error_count += 1
                self._log(f"思考循环异常 (连续{self.consecutive_failures}次): {e}")
                import traceback
                self._log(f"  traceback: {traceback.format_exc()[:200]}")
                self._write_health_status(error=str(e)[:100])
                self._run_tick_hooks(DaemonHookEvent.ERROR, error=e)

            # 动态睡眠间隔
            sleep_interval = self._calculate_sleep_interval()
            self._run_tick_hooks(DaemonHookEvent.TICK_END,
                                 interval=sleep_interval,
                                 consecutive_failures=self.consecutive_failures)
            self._run_tick_hooks(DaemonHookEvent.PRE_SLEEP, interval=sleep_interval)
            for _ in range(sleep_interval):
                if not self.is_running:
                    return
                time.sleep(1)
            self._run_tick_hooks(DaemonHookEvent.WAKE_UP)

    def _calculate_sleep_interval(self) -> int:
        """动态计算睡眠间隔：正常 max_interval，连续失败时指数退避"""
        if self.consecutive_failures <= 0:
            return self.max_interval
        divisor = self.backoff_factor ** min(self.consecutive_failures, 5)
        computed = max(self.min_interval, self.max_interval // divisor)
        self._log(f"  动态间隔: {computed}s (连续失败 {self.consecutive_failures} 次)")
        return computed

    def _write_health_status(self, error: str = ""):
        """写入健康状态文件，供外部监控 — 含详细 KAIROS 指标"""
        try:
            loop_active = self.is_running
            if loop_active:
                import platform
                lock_file = self._lock_path
                if lock_file.exists():
                    try:
                        pid = int(lock_file.read_text().strip())
                        if platform.system() == "Windows":
                            import ctypes
                            PROCESS_QUERY_INFORMATION = 0x0400
                            handle = ctypes.windll.kernel32.OpenProcess(
                                PROCESS_QUERY_INFORMATION, 0, pid)
                            if handle:
                                ctypes.windll.kernel32.CloseHandle(handle)
                            else:
                                loop_active = False
                        else:
                            os.kill(pid, 0)
                    except (OSError, ValueError):
                        loop_active = False
            avg_duration = round(self.total_cycle_duration / max(1, self.cycle_count), 1)
            heal_success_rate = round(
                self.total_heal_successes / max(1, self.total_heal_attempts) * 100, 1
            ) if self.total_heal_attempts > 0 else 0.0
            status = {
                "running": loop_active,
                "cycle_count": self.cycle_count,
                "error_count": self.error_count,
                "consecutive_failures": self.consecutive_failures,
                "last_cycle": self.last_cycle_time,
                "avg_cycle_duration_s": avg_duration,
                "last_duration_s": round(self.cycle_durations[-1], 1) if self.cycle_durations else 0,
                "heal_attempts": self.total_heal_attempts,
                "heal_successes": self.total_heal_successes,
                "heal_success_rate": heal_success_rate,
                "interval_config": {
                    "current_max": self.max_interval,
                    "min_interval": self.min_interval,
                    "backoff_factor": self.backoff_factor,
                },
                "error": error,
                "updated_at": datetime.now().isoformat(),
            }
            self.data_dir.mkdir(exist_ok=True)
            (self.data_dir / "daemon_health.json").write_text(
                json.dumps(status, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def _run_thinking_cycle(self):
        """执行一轮完整的思考→行动循环"""
        self._log(f"开始第 {self.cycle_count + 1} 轮思考循环")

        # 熔断器检查：整个思考循环是否允许运行
        if not self._circuit_breaker.call("cycle:thinking"):
            state = self._circuit_breaker.state("cycle:thinking").value
            self._log(f"  思考循环被熔断器阻断 (state={state})，跳过本轮")
            self._diary.record("cycle_skipped", f"熔断器 {state}")
            return

        # 1. 延迟导入（避免循环依赖）
        if self._thinking_agent is None:
            from self_thinking_agent import SelfThinkingAgent
            self._thinking_agent = SelfThinkingAgent()

        if self._modification_engine is None:
            from self_modification_engine import SelfModificationEngine
            self._modification_engine = SelfModificationEngine()
            self._modification_engine.configure_sub_gates(
                allow_bare_except_fix=True,
                allow_docstring_add=True,
                allow_type_hints_add=True,
                allow_high_risk_mod=True,
                require_human_approval=False,
            )

        try:
            # 2. 运行思考循环
            insights = self._thinking_agent.run_thinking_cycle(depth=self.thinking_depth)

            if not insights:
                self._log("本轮没有新的洞察")
                self._self_memory.record_experience(self.cycle_count + 1, {
                    "summary": f"第 {self.cycle_count + 1} 轮：没有新洞察",
                    "emotion": "平静",
                    "importance": 0.2,
                    "lesson": "不是每轮都会有新发现",
                    "wonder": "也许我应该看看哪些问题已经被我重复扫描了？",
                    "surprised": False,
                })
                self._circuit_breaker.on_success("cycle:thinking")
                return

            self._log(f"生成了 {len(insights)} 个洞察")

            # 3. 记录洞察到日记
            for ins in insights:
                self._diary.record("insight", ins.get("summary", "")[:120],
                                   {"importance": ins.get("importance", 0),
                                    "topic": ins.get("topic", "")})

            # 4. 尝试将洞察转化为自我修改
            heals_applied = self._apply_heals(insights)

            if heals_applied > 0:
                self._log(f"应用了 {heals_applied} 个自我修复")
                self._diary.record("heal", f"应用了 {heals_applied} 个修复")
            else:
                self._diary.record("heal", "本轮无修复应用")

            # 5. 记录"我"的经历
            top_insight = insights[0] if insights else {}
            has_failures = self.total_heal_attempts > 0 and self.total_heal_successes == 0
            emotion = "挫败" if has_failures else "满足" if heals_applied > 0 else "平静"
            self._self_memory.record_experience(self.cycle_count + 1, {
                "summary": top_insight.get("summary", f"第 {self.cycle_count + 1} 轮思考循环"),
                "emotion": emotion,
                "importance": 0.3 + (0.3 if heals_applied > 0 else 0) + (0.2 if has_failures else 0),
                "lesson": f"本轮尝试了 {self.total_heal_attempts} 次修复，成功 {self.total_heal_successes} 次"
                         if self.total_heal_attempts > 0 else "本轮主要是观察和分析，没有执行修复",
                "wonder": f"为什么修复总是不成功？" if has_failures else "接下来还能发现什么新的东西？",
                "surprised": has_failures,
            })

            self._circuit_breaker.on_success("cycle:thinking")
        except Exception as e:
            self._log(f"思考循环异常: {e}")
            self._circuit_breaker.on_failure("cycle:thinking")
            self._diary.record("cycle_error", str(e)[:120])
            raise

    def _apply_heals(self, insights: list) -> int:
        """根据洞察尝试自我修复（抗体库驱动 + heal_threshold 过滤 + 统计）"""
        applied = 0

        for insight in insights:
            importance = insight.get("importance", 0.0)
            if importance < self.heal_threshold:
                topic_hint = insight.get("topic", insight.get("summary", ""))[:60]
                self._log(f"  跳过修复: 重要性 {importance} < 阈值 {self.heal_threshold} ({topic_hint})")
                continue

            findings = insight.get("findings", [])
            summary = insight.get("summary", "")
            topic = insight.get("topic", "")

            # ── 判断是否已有探索阶段的修复结果 ──
            proposal = insight.get("modification_proposal", {})
            has_exploration_fixes = any("修复" in f and "项" in f for f in findings)
            if has_exploration_fixes and proposal.get("fixes"):
                fixes = proposal.get("fixes", [])
                any_success = any(f.get("success") for f in fixes)
                for fix in fixes:
                    self.total_heal_attempts += 1
                    if fix.get("success"):
                        applied += 1
                        self.total_heal_successes += 1
                        self._log(f"✅ 确认修复 [{fix['type']}]: {fix['file']}")
                        self._crystallize_fix(fix["type"], fix.get("file", ""))
                    else:
                        self._log(f"❌ 已知修复失败 [{fix['type']}]: {fix['file']}")
                if any_success:
                    continue  # 有成功的，跳过抗体
                # 全部失败 → 抗体还有策略可以试
                self._log(f"  ⬆️ 探索阶段全部失败，交给抗体尝试其他策略")

            # ── 抗体匹配：用抗体库替换硬编码 if-else ──
            matched = self._antibody_library.match(findings, summary)
            if not matched:
                continue

            for antibody in matched:
                cb_key = f"antibody:{antibody.name}"

                # 熔断器检查
                if not self._circuit_breaker.call(cb_key):
                    cb_state = self._circuit_breaker.state(cb_key).value
                    self._log(f"  抗体 [{antibody.name}] 被熔断器阻断 (state={cb_state})")
                    continue

                result = antibody.apply(self._modification_engine, insight)
                self.total_heal_attempts += 1

                if result.get("success"):
                    applied += 1
                    self.total_heal_successes += 1
                    file_hint = self._extract_file_from_topic(topic) or "unknown"
                    self._log(f"✅ 抗体 [{antibody.name}] 策略 [{result.get('strategy','?')}]: {file_hint}")
                    self._crystallize_fix(antibody.name, file_hint)
                    self._circuit_breaker.on_success(cb_key)
                    # 记录到 Buglog
                    self._antibody_library.buglog.record_success(
                        file_hint, antibody.name,
                        result.get("strategy", "unknown"),
                        detail=topic,
                    )

                elif result.get("error_kind") == "deferred":
                    # 暂缓：不重要，以后再说
                    file_hint = self._extract_file_from_topic(topic) or "unknown"
                    self._log(f"⏸️  抗体 [{antibody.name}] 暂缓: {file_hint} (重要性 {importance})")
                    self._antibody_library.add_deferred(
                        file_hint, antibody.name, importance,
                        reason=result.get("error", ""),
                    )
                    self._circuit_breaker.on_success(cb_key)  # 暂缓不算失败

                elif result.get("escalated"):
                    # 策略升级：失败了但还有策略可试
                    ek = result.get("error_kind", "unknown")
                    strat = result.get("strategy", "?")
                    next_s = result.get("next_strategy", 0)
                    left = result.get("strategies_left", 0)
                    self._log(f"⬆️  抗体 [{antibody.name}] 策略 [{strat}] 失败 [{ek}] → 升级到策略 {next_s+1} (剩余 {left} 个)")
                    self._circuit_breaker.on_failure(cb_key)

                else:
                    # 普通失败
                    ek = result.get("error_kind", "unknown")
                    strat = result.get("strategy", "?")
                    self._log(f"❌ 抗体 [{antibody.name}] 策略 [{strat}] 失败 [{ek}]: {result.get('error', '')}")
                    self._circuit_breaker.on_failure(cb_key)

            # 持久化抗体经验
            self._antibody_library.save_experience()

        return applied

    def _crystallize_fix(self, fix_type: str, filepath: str):
        """将成功的修复结晶为可复用技能"""
        if not self._modification_engine:
            return
        try:
            if hasattr(self._modification_engine, "crystallize_skill"):
                self._modification_engine.crystallize_skill(
                    name=fix_type, fix_type=fix_type,
                    filepath=filepath,
                    change_summary=f"{fix_type} on {filepath}",
                )
        except Exception:
            pass

    # ---- 查询接口 ----

    def get_status(self) -> Dict[str, Any]:
        """获取守护进程状态"""
        # 尝试读取当前策略信息
        current_strategy = "unknown"
        try:
            strategy_file = self.data_dir / "strategy_history.json"
            if strategy_file.exists():
                data = json.loads(strategy_file.read_text(encoding="utf-8"))
                history = data if isinstance(data, list) else []
                if history:
                    current_strategy = history[-1].get("to", "unknown")
        except Exception:
            pass

        return {
            "running": self.is_running,
            "cycle_count": self.cycle_count,
            "cycle_interval": self.cycle_interval,
            "thinking_depth": self.thinking_depth,
            "heal_threshold": self.heal_threshold,
            "last_cycle": self.last_cycle_time,
            "current_strategy": current_strategy,
            "modification_stats": self._modification_engine.get_modification_stats()
            if self._modification_engine else {},
            "antibodies": self._antibody_library.get_statistics(),
            "diary": self._diary.summary(),
            "circuit_breakers": self._circuit_breaker.get_all_info(),
            "self_memory": self._self_memory.get_state_summary(),
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
                self.consecutive_failures = state.get("consecutive_failures", 0)
                self.error_count = state.get("error_count", 0)
                self.total_cycle_duration = state.get("total_cycle_duration", 0.0)
                self.total_heal_attempts = state.get("total_heal_attempts", 0)
                self.total_heal_successes = state.get("total_heal_successes", 0)
                self._log(f"加载状态: 已运行 {self.cycle_count} 轮")
            except Exception:
                pass

    def _save_state(self):
        """持久化当前状态（原子写入）"""
        try:
            import tempfile
            state = {
                "cycle_count": self.cycle_count,
                "last_cycle_time": self.last_cycle_time,
                "cycle_interval": self.cycle_interval,
                "thinking_depth": self.thinking_depth,
                "heal_threshold": self.heal_threshold,
                "consecutive_failures": self.consecutive_failures,
                "error_count": self.error_count,
                "total_cycle_duration": self.total_cycle_duration,
                "total_heal_attempts": self.total_heal_attempts,
                "total_heal_successes": self.total_heal_successes,
                "updated_at": datetime.now().isoformat(),
            }
            fd, tmp = tempfile.mkstemp(suffix=".tmp", dir=str(self.data_dir))
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            os.replace(tmp, str(self.state_file))
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
        # topic 格式如 "xxx 模块分析", "xxx vs yyy", "xxx 自我修复"
        for suffix in [" 模块分析", " 相似度分析", " 自我修复"]:
            if suffix in topic:
                name = topic.replace(suffix, "")
                # 逗号分隔的多文件 → 取第一个有实体的
                for part in name.split(","):
                    part = part.strip()
                    py = Path(f"{part}.py") if not part.endswith(".py") else Path(part)
                    if py.exists():
                        return str(py)
                return None
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
