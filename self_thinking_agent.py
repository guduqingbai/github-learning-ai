#!/usr/bin/env python3
"""
🧠 自我思考Agent - 真正的自我思考核心能力
好奇心驱动的自我扫描→发现→探索→学习循环
所有输出基于真实项目数据，无随机模拟
"""

import json
import uuid
import os
import time
import ssl
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# ── 思维引擎组件（纯本地大脑）──
from thought_buffer import ThoughtGraph
from thought_continuity import ThoughtContinuityManager, ThoughtContinuityConfig
from thinking_engine import ThinkingEngine


# ---- Hook 事件系统（生命周期钩子，支持外部扩展） ----

class HookEvent:
    """思考循环生命周期事件"""
    # 全局
    CYCLE_START = "cycle_start"
    CYCLE_END = "cycle_end"
    # 扫描
    PRE_SCAN = "pre_scan"
    POST_SCAN = "post_scan"
    # 学习
    PRE_STUDY = "pre_study"
    POST_STUDY = "post_study"
    # 评估
    PRE_EVALUATE = "pre_evaluate"
    POST_EVALUATE = "post_evaluate"
    # 自我认知
    PRE_AWARENESS = "pre_awareness"
    POST_AWARENESS = "post_awareness"
    # 整理
    PRE_CONSOLIDATE = "pre_consolidate"
    POST_CONSOLIDATE = "post_consolidate"
    # 反思
    PRE_REFLECT = "pre_reflect"
    POST_REFLECT = "post_reflect"
    # 问题生成
    PRE_QUESTIONS = "pre_questions"
    POST_QUESTIONS = "post_questions"
    # 探索
    PRE_EXPLORE = "pre_explore"
    POST_EXPLORE = "post_explore"


class Hook:
    """单个钩子：绑定到特定事件的处理函数"""

    def __init__(self, event: str, handler, *, name: str = "", priority: int = 0):
        self.event = event
        self.handler = handler
        self.name = name or getattr(handler, "__name__", "unnamed")
        self.priority = priority

    def __repr__(self):
        return f"Hook(event={self.event}, name={self.name}, priority={self.priority})"


# ---- 结构化会话（ContentBlock 模式，源自 claw-code session.rs） ----

@dataclass
class ContentBlock:
    """结构化的内容块：带类型的可查询数据单元"""
    type: str  # "observation", "question", "insight", "scan", "heal", "reflection", "error"
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CycleMessage:
    """思考循环中的一条消息，包含角色和内容块列表"""
    role: str  # "system" | "assistant" | "tool"
    blocks: List[ContentBlock] = field(default_factory=list)
    timestamp: str = ""


def build_cycle_messages(*,
                         phase: str,
                         scan_data: Optional[Dict] = None,
                         study_data: Optional[List] = None,
                         evaluation: Optional[Dict] = None,
                         questions: Optional[List] = None,
                         insights: Optional[List] = None,
                         errors: Optional[List[str]] = None) -> List[CycleMessage]:
    """
    构建结构化的思考循环消息序列
    每个阶段生成带类型的 ContentBlock，便于后续查询和分析
    """
    ts = datetime.now().isoformat()
    messages = []

    # System: cycle phase context
    sys_blocks = [ContentBlock(type="phase", data={"phase": phase})]
    if scan_data:
        sys_blocks.append(ContentBlock(type="scan", data=scan_data))
    if study_data:
        sys_blocks.append(ContentBlock(type="study", data={"count": len(study_data), "topics": [s.get("topic", "")[:50] for s in study_data[:5]]}))
    if evaluation:
        sys_blocks.append(ContentBlock(type="evaluation", data=evaluation))
    messages.append(CycleMessage(role="system", blocks=sys_blocks, timestamp=ts))

    # Assistant: questions generated
    if questions:
        q_blocks = [ContentBlock(type="question", data={
            "text": q.question[:100],
            "action": q.explore_action,
            "target": q.target,
            "importance": q.importance,
        }) for q in questions[:10]]
        messages.append(CycleMessage(role="assistant", blocks=q_blocks, timestamp=ts))

    # Tool: insights / actions taken
    if insights:
        i_blocks = []
        for ins in insights:
            i_type = ins.get("action_taken", "insight")
            i_blocks.append(ContentBlock(type=i_type, data={
                "topic": ins.get("topic", ""),
                "summary": ins.get("summary", "")[:200],
            }))
        messages.append(CycleMessage(role="tool", blocks=i_blocks, timestamp=ts))

    # Tool: errors
    if errors:
        messages.append(CycleMessage(role="tool", blocks=[ContentBlock(type="error", data={"errors": errors})], timestamp=ts))

    return messages


# ---- 自我思考Agent ----

class SelfThinkingAgent:
    """自我思考Agent - 好奇心驱动的真实思考引擎"""

    def __init__(self):
        from self_scanner import SelfScanner
        from curiosity_engine import CuriosityEngine
        self.scanner = SelfScanner()
        self.curiosity = CuriosityEngine()
        self.snapshot = None
        self.diff = None
        self.questions: List = []
        self.thinking_log: List[Dict] = []
        self.data_dir = Path("data")
        self.log_file = self.data_dir / "self_thinking_log.json"
        self.growth_plan_file = self.data_dir / "growth_plan.json"
        self._skills = self._init_skills()
        # 钩子注册表：event → [(priority, Hook), ...]
        self._hooks: Dict[str, List[Hook]] = {}
        self._feature_flags = None  # 延迟初始化

        # ── 思维引擎组件（纯本地大脑）──
        self._thought_graph: Optional[ThoughtGraph] = None
        self._thought_continuity: Optional[ThoughtContinuityManager] = None
        self._thinking_engine: Optional[ThinkingEngine] = None
        self._last_local_think_cycle: int = -1  # -1 = 从未运行

        # ── 行为反馈层（从观察代码 → 观察行为） ──
        from behavior_feedback import BehaviorFeedback
        self._behavior_feedback = BehaviorFeedback(data_dir=self.data_dir)

        # ── 策略学习引擎（数据先行，再决策） ──
        self._strategy_learner = None  # 惰性初始化

        # ── 经验记忆 ──
        self._experience_tracker = None

        # ── 元认知监控 ──
        self._metacognitive_monitor: Optional["MetacognitiveMonitor"] = None

        # ── 自我画像 ──
        self._self_profile: Dict[str, Any] = {}

        # ── 策略学习循环 ──
        self._cycle_count = 0
        self._strategy_journal_file = self.data_dir / "strategy_journal.json"

        # 人格状态（从 Evolver 学习）
        self._personality: Optional["PersonalityState"] = None

        # 分层记忆（从 GenericAgent 学习）
        self._layered_memory: Optional["LayeredMemory"] = None

        # 自主研究（自建）
        self._research_integration: Optional["ResearchIntegration"] = None

        # ── 能力学习与差距分析 ──
        self._capability_registry = None
        self._directed_crawler = None
        self._gap_analyzer = None

    # ---- Hook 系统 ----

    def register_hook(self, event: str, handler, *, name: str = "", priority: int = 0):
        """
        在指定事件注册钩子
        priority 越低越先执行（默认 0）
        """
        hook = Hook(event, handler, name=name, priority=priority)
        self._hooks.setdefault(event, []).append(hook)
        self._hooks[event].sort(key=lambda h: h.priority)
        print(f"  🔌 注册钩子: {hook.name} → {event}")

    def unregister_hook(self, event: str, handler=None, name: str = ""):
        """移除钩子"""
        hooks = self._hooks.get(event, [])
        if handler:
            self._hooks[event] = [h for h in hooks if h.handler != handler]
        elif name:
            self._hooks[event] = [h for h in hooks if h.name != name]
        if not self._hooks.get(event):
            self._hooks.pop(event, None)

    def _run_hooks(self, event: str, **context):
        """执行指定事件的所有已注册钩子"""
        hooks = self._hooks.get(event, [])
        if not hooks:
            return
        for hook in hooks:
            try:
                hook.handler(self, **context)
            except Exception as e:
                print(f"  ⚠️ 钩子 [{hook.name}] 执行失败: {e}")

    def _check_feature(self, key: str) -> bool:
        """检查 feature flag 是否启用（延迟初始化）"""
        if self._feature_flags is None:
            try:
                from system_state_manager import SystemStateManager
                sm = SystemStateManager()
                self._feature_flags = sm.get_feature_flag_manager()
            except Exception:
                return True  # 初始化失败默认启用
        return self._feature_flags.is_enabled(key)

    # ── 纯本地思维引擎 ─────────────────────────────

    def _init_thinking_engine(self):
        """延迟初始化纯本地思考引擎"""
        if self._thought_graph is None:
            self._thought_graph = ThoughtGraph()
            self._thought_graph.migrate_from_legacy()
        if self._thought_continuity is None:
            self._thought_continuity = ThoughtContinuityManager(
                thought_graph=self._thought_graph,
                config=ThoughtContinuityConfig(
                    max_active_threads=3,
                    max_thread_depth=5,
                    stale_cycles_threshold=5,
                ),
            )
        if self._thinking_engine is None:
            from knowledge_graph import KnowledgeGraph
            from self_model import SelfModel
            from pattern_engine import PatternEngine
            from analogy_engine import AnalogyEngine

            kg = KnowledgeGraph()
            sm = SelfModel(kg)
            pe = PatternEngine(kg)
            ae = AnalogyEngine(kg)
            self._thinking_engine = ThinkingEngine(
                knowledge_graph=kg, self_model=sm,
                pattern_engine=pe, analogy_engine=ae,
            )

    def _should_do_local_thinking(self) -> bool:
        """
        判断本轮是否该进行深度本地思考。

        条件（满足任一即可）：
        1. 从未运行过
        2. 距上次思考 >= 3 轮
        3. 好奇心引擎生成了超过 5 个问题
        """
        if self._last_local_think_cycle < 0:
            return True
        cycles_since = getattr(self, '_cycle_count', 0) - self._last_local_think_cycle
        if cycles_since >= 3:
            return True
        if len(getattr(self, 'questions', [])) > 5:
            return True
        return False

    def _internal_think(self) -> List[Dict]:
        """
        内在思考：主动分析已有知识，不依赖外部触发。

        返回内在思考产生的新问题列表（Dictionary 格式，
        与 CuriosityQuestion 兼容）。
        """
        internal_qs = []
        try:
            from internal_thinker import InternalThinker
            it = InternalThinker()
            result = it.think()

            # 存储洞察到思维图
            for ins in result.get("insights", []):
                if self._thought_graph is not None:
                    self._thought_graph.add_thought(
                        topic=ins.content[:60],
                        content=ins.content,
                        thought_type="insight",
                        importance=ins.importance,
                        source="internal_thinker",
                    )

            # 转换问题格式
            for q in result.get("questions", []):
                try:
                    from curiosity_engine import CuriosityQuestion
                    internal_qs.append(CuriosityQuestion(
                        observation=f"[内在思考] 基于已有知识的自我提问",
                        question=q["question"],
                        importance=q.get("importance", 0.5),
                        explore_action=q.get("explore_action", "explore"),
                        target=q.get("target", ""),
                        context={"source": "internal_thinker"},
                        reason="系统主动思考已有知识",
                    ))
                except Exception:
                    pass

            if result.get("insights"):
                print(f"  💭 内在思考: {len(result['insights'])} 条洞察")
        except Exception as e:
            print(f"  ⚠️ 内在思考异常: {e}")

        return internal_qs

    def _crawl_and_learn(self) -> None:
        """
        执行爬虫任务并学习结果。

        每轮处理少量 pending 爬虫任务，将结果通过学习
        桥接器评估后入库，供后续 _study_knowledge 学习。
        """
        task_file = self.data_dir / "crawler_tasks.json"
        if not task_file.exists():
            return

        try:
            tasks = json.loads(task_file.read_text(encoding="utf-8"))
        except Exception:
            return

        if not tasks:
            return

        print(f"  🕷️ 爬虫队列: {len(tasks)} 个待处理，本轮执行 2 个")
        try:
            from ai_knowledge_crawler import AIKnowledgeCrawler
            crawler = AIKnowledgeCrawler()
            results = crawler.crawl_task_queue()
            if results:
                from crawler_learning_bridge import process_crawler_results
                stats = process_crawler_results(results)
                print(f"  📚 爬虫学习: 评估 {stats['evaluated']} 条, "
                      f"学习 {stats['learned']} 条, "
                      f"深挖 {stats['deep_dives']} 个主题")
        except Exception as e:
            print(f"  ⚠️ 爬虫执行异常: {e}")

    def _get_experience_tracker(self):
        """延迟初始化经验追踪器"""
        if self._experience_tracker is None:
            from experience_tracker import ExperienceTracker
            self._experience_tracker = ExperienceTracker()
        return self._experience_tracker

    def _get_metacognitive_monitor(self):
        """延迟初始化元认知监控器"""
        if self._metacognitive_monitor is None:
            from metacognitive_monitor import MetacognitiveMonitor
            self._metacognitive_monitor = MetacognitiveMonitor()
        return self._metacognitive_monitor

    def _get_personality(self):
        """延迟初始化人格状态"""
        if self._personality is None:
            from personality_state import PersonalityState
            self._personality = PersonalityState()
        return self._personality

    def _get_layered_memory(self):
        """延迟初始化分层记忆"""
        if self._layered_memory is None:
            from memory_layers import LayeredMemory
            self._layered_memory = LayeredMemory()
        return self._layered_memory

    def _get_research_integration(self):
        """延迟初始化研究集成"""
        if self._research_integration is None:
            from research_integration import ResearchIntegration
            self._research_integration = ResearchIntegration()
            self._research_integration.register_hooks(self)
        return self._research_integration

    def _get_capability_registry(self):
        """延迟初始化能力注册表"""
        if self._capability_registry is None:
            from capability_registry import CapabilityRegistry
            self._capability_registry = CapabilityRegistry()
        return self._capability_registry

    def _get_directed_crawler(self):
        """延迟初始化定向爬虫并注册 hook"""
        if self._directed_crawler is None:
            from directed_crawl import DirectedCrawler
            self._directed_crawler = DirectedCrawler()
            self._directed_crawler.register_hooks(self)
        return self._directed_crawler

    def _get_llm_integration(self):
        """延迟初始化 LLM 思考增强"""
        if not hasattr(self, '_llm_integration') or self._llm_integration is None:
            try:
                from llm_thinking import LLMThinkingIntegration
                self._llm_integration = LLMThinkingIntegration()
                self._llm_integration.register_hooks(self)
            except Exception as e:
                print(f"  ⚠️ LLM 增强初始化失败: {e}")
                self._llm_integration = None
        return self._llm_integration

    def _get_gap_analyzer(self):
        """延迟初始化差距分析器"""
        if self._gap_analyzer is None:
            from gap_analyzer import GapAnalyzer
            self._gap_analyzer = GapAnalyzer()
        return self._gap_analyzer

    def _get_daemon_stats(self) -> Dict[str, Any]:
        """获取守护进程运行时统计"""
        try:
            from thinking_daemon import get_daemon
            d = get_daemon()
            return {
                "cycle_count": d.cycle_count,
                "consecutive_failures": d.consecutive_failures,
                "error_count": d.error_count,
                "total_heal_attempts": d.total_heal_attempts,
                "total_heal_successes": d.total_heal_successes,
                "cycle_interval": d.cycle_interval,
            }
        except Exception:
            return {}

    def _get_thinking_engine_stats(self) -> Dict[str, Any]:
        """获取思考引擎统计"""
        if self._thinking_engine is not None:
            try:
                d = self._thinking_engine._previous_stats
                return {
                    "questions_generated": d.get("questions_generated", 0),
                    "insights_generated": d.get("insights_generated", 0),
                    "graph_entities": d.get("graph_entities", 0),
                    "isolated_entities": d.get("isolated_entities", 0),
                }
            except Exception:
                pass
        return {}

    def _build_self_profile(self) -> Dict[str, Any]:
        """构建当前自我画像并存入 self._self_profile"""
        try:
            from self_model import SelfModel
            sm = SelfModel()
            ds = self._get_daemon_stats()
            profile = sm.generate_self_profile({
                "experience_tracker": self._get_experience_tracker(),
                "metacognitive_monitor": self._get_metacognitive_monitor(),
                "knowledge_base": None,
                "daemon_stats": ds if ds else None,
            })
            # 单独补知识库数据
            try:
                from knowledge_base import KnowledgeBase
                kb = KnowledgeBase()
                profile["knowledge_domains"] = {}
                all_k = kb.get_all_knowledge()
                cat_counts = {}
                for e in all_k:
                    c = e.get("category", "未分类")
                    cat_counts[c] = cat_counts.get(c, 0) + 1
                if cat_counts:
                    mc = max(cat_counts.values())
                    profile["knowledge_domains"] = {
                        c: round(n / mc, 3)
                        for c, n in sorted(cat_counts.items(),
                                           key=lambda x: -x[1])
                    }
            except Exception:
                pass

            # 策略学习经验：从已回顾的策略日志中提取
            try:
                journal = []
                if self._strategy_journal_file.exists():
                    journal = json.loads(
                        self._strategy_journal_file.read_text(encoding="utf-8"))
                reviewed = [e for e in journal if e.get("effective") is not None]
                strat_lessons = {}
                for e in reviewed:
                    t = e.get("trigger", "")
                    eff = e.get("effective", False)
                    for param_key in e.get("changes", {}):
                        if param_key == "sub_gates":
                            continue
                        tag = f"{param_key}_adjusted"
                        lesson = strat_lessons.setdefault(t, {})
                        entry = lesson.setdefault(tag, {"effective": 0, "ineffective": 0, "total": 0})
                        if eff:
                            entry["effective"] += 1
                        else:
                            entry["ineffective"] += 1
                        entry["total"] += 1
                        # 自动总结有效/无效
                        if entry["total"] >= 2:
                            entry["verdict"] = "effective" if entry["effective"] > entry["ineffective"] else "ineffective"
                profile["strategy_lessons"] = strat_lessons
            except Exception:
                profile["strategy_lessons"] = {}

            self._self_profile = profile
        except Exception:
            self._self_profile = {}
        return self._self_profile

    def _load_self_context(self):
        """加载自我记忆中的状态（情绪、经历、暂缓问题），影响后续思考"""
        self._mood = "平静"
        self._recent_lessons = []
        self._deferred_targets = []

        try:
            from self_memory import SelfMemory
            from pathlib import Path
            mem = SelfMemory(Path("data"))
            self._mood = mem.get_mood()
            lessons = mem.recall_lessons(3)
            self._recent_lessons = [l.get("lesson", "") for l in lessons]
            important = mem.recall_important(0.7)
            if important:
                print(f"  🧠 自我状态: 情绪={self._mood}, "
                      f"深刻记忆={len(important)}条, 沉淀认知={len(lessons)}条")
        except Exception:
            pass

        try:
            from antibody_library import AntibodyLibrary
            lib = AntibodyLibrary(Path("data"))
            if lib.deferred:
                self._deferred_targets = [d["target"] for d in lib.deferred[-5:]]
                print(f"  ⏸️  暂缓问题: {len(lib.deferred)} 个等待新策略")
        except Exception:
            pass

    def _apply_metacognitive_adjustments(self, findings: List) -> None:
        """
        基于元认知发现实际改变系统参数。

        让 MetacognitiveMonitor 的 intervention 字符串变为可执行代码。
        """
        if not findings:
            return

        daemon = None
        try:
            from thinking_daemon import get_daemon
            daemon = get_daemon()
        except Exception:
            pass

        # 捕获调整前的系统状态
        pre_state = self._capture_daemon_state(daemon)

        # 从 PersonalityState 获取策略建议（从 Evolver 学习）
        personality = self._get_personality()
        strategy_hint = personality.suggest_strategy()
        pre_state["personality"] = personality.all_params()
        pre_state["suggested_strategy"] = strategy_hint

        # 检查是否需要强制切换策略（从 MetacognitiveMonitor 信号去重）
        try:
            forced_strategy = self._get_metacognitive_monitor().force_strategy_switch()
            if forced_strategy:
                print(f"  🔄 强制策略切换: → {forced_strategy}")
                # 强制切换影响人格参数
                if forced_strategy == "innovate":
                    personality.adjust("creativity", +0.2, reason="强制创新策略", force=True)
                    personality.adjust("risk_tolerance", +0.15, reason="强制创新策略", force=True)
                elif forced_strategy == "repair-only":
                    personality.adjust("creativity", -0.2, reason="强制修复策略", force=True)
                    personality.adjust("risk_tolerance", -0.2, reason="强制修复策略", force=True)
                elif forced_strategy == "harden":
                    personality.adjust("rigor", +0.2, reason="强制加固策略", force=True)
                    personality.adjust("obedience", +0.1, reason="强制加固策略", force=True)
        except Exception:
            pass

        adjustments = []
        journal_entries = []

        for finding in findings:
            ftype = finding.finding_type
            severity = finding.severity
            changes = {}

            if ftype == "loop" and severity > 0.3:
                # 循环检测：增大 depth 强制新颖性
                if daemon:
                    old = daemon.thinking_depth
                    new = min(8, old + 2)
                    daemon.update_config(thinking_depth=new)
                    changes["thinking_depth"] = [old, new]
                    adjustments.append(
                        f"循环 → 深度 {old}→{new}（强制新颖性）")

            elif ftype == "confidence" and severity > 0.5:
                # 低置信度：保守行事
                if daemon:
                    old_depth = daemon.thinking_depth
                    old_interval = daemon.cycle_interval
                    old_heal = daemon.heal_threshold
                    daemon.update_config(
                        thinking_depth=max(1, old_depth - 1),
                        cycle_interval=min(3600, old_interval + 600),
                        heal_threshold=0.85,
                    )
                    changes["thinking_depth"] = [old_depth, max(1, old_depth - 1)]
                    changes["cycle_interval"] = [old_interval, min(3600, old_interval + 600)]
                    changes["heal_threshold"] = [old_heal, 0.85]
                    adjustments.append(
                        f"低置信度 → 深度 {old_depth}→{max(1, old_depth - 1)}, "
                        f"间隔 {old_interval}→{min(3600, old_interval + 600)}, "
                        f"heal阈值 {old_heal}→0.85")
                # 只开安全 sub_gates
                try:
                    from self_modification_engine import SelfModificationEngine
                    engine = SelfModificationEngine()
                    engine.configure_sub_gates(
                        allow_bare_except_fix=True,
                        allow_docstring_add=True,
                        allow_unused_import_remove=False,
                        allow_destructive_change=False,
                    )
                    changes["sub_gates"] = ["mixed", "safe_only"]
                except Exception:
                    pass

            elif ftype == "stagnation" and severity > 0.4:
                # 停滞：缩短间隔，降低 heal_threshold 鼓励小修复
                if daemon:
                    old_interval = daemon.cycle_interval
                    old_heal = daemon.heal_threshold
                    daemon.update_config(
                        cycle_interval=max(600, old_interval - 300),
                        heal_threshold=0.5,
                    )
                    changes["cycle_interval"] = [old_interval, max(600, old_interval - 300)]
                    changes["heal_threshold"] = [old_heal, 0.5]
                    adjustments.append(
                        f"停滞 → 间隔 {old_interval}→{max(600, old_interval - 300)}, "
                        f"heal阈值 {old_heal}→0.5")

            elif ftype == "failure_risk" and severity > 0.5:
                # 高风险：保守行事
                if daemon:
                    old_depth = daemon.thinking_depth
                    old_heal = daemon.heal_threshold
                    daemon.update_config(
                        heal_threshold=0.9,
                        thinking_depth=max(1, old_depth - 1),
                    )
                    changes["heal_threshold"] = [old_heal, 0.9]
                    changes["thinking_depth"] = [old_depth, max(1, old_depth - 1)]
                    adjustments.append(
                        f"失败风险 → heal阈值 0.9, 深度 {old_depth}→{max(1, old_depth - 1)}")

            # 记录策略日志
            if changes:
                expected_text = {
                    "loop": "减少循环",
                    "confidence": "提升稳定性",
                    "stagnation": "加速进展",
                    "failure_risk": "降低风险",
                }.get(ftype, "")
                journal_entries.append({
                    "timestamp": datetime.now().isoformat(),
                    "cycle": self._cycle_count,
                    "trigger": ftype,
                    "severity": severity,
                    "changes": {k: {"from": v[0], "to": v[1]} for k, v in changes.items()},
                    "expected": expected_text,
                    "pre_state": pre_state,
                    "post_state": None,
                    "effective": None,
                })

        if adjustments:
            print(f"\n  ⚙️ 行为调整 ({len(adjustments)} 项):")
            for a in adjustments:
                print(f"    {a}")
            self._save_strategy_journal(journal_entries)

    def _capture_daemon_state(self, daemon=None) -> Dict[str, Any]:
        """捕获 daemon 当前状态快照，用于策略日志对比"""
        if daemon is None:
            try:
                from thinking_daemon import get_daemon
                daemon = get_daemon()
            except Exception:
                pass
        if daemon is None:
            return {}
        return {
            "thinking_depth": getattr(daemon, "thinking_depth", 0),
            "cycle_interval": getattr(daemon, "cycle_interval", 0),
            "heal_threshold": getattr(daemon, "heal_threshold", 0),
            "error_rate": getattr(daemon, "error_count", 0) / max(1, getattr(daemon, "total_heal_attempts", 1)),
            "health": self._self_profile.get("health", 0.5),
            "confidence": self._self_profile.get("confidence", 0.5),
        }

    def _save_strategy_journal(self, entries: List[Dict]) -> None:
        """追加策略日志到 data/strategy_journal.json"""
        try:
            existing = []
            if self._strategy_journal_file.exists():
                existing = json.loads(self._strategy_journal_file.read_text(encoding="utf-8"))
            existing.extend(entries)
            # 最多保留 100 条
            existing = existing[-100:]
            self._strategy_journal_file.parent.mkdir(exist_ok=True)
            self._strategy_journal_file.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    def _review_strategy_effectiveness(self) -> None:
        """
        策略回顾：检查上次调整的效果。

        在每轮开始时调用，读取策略日志中未评估的条目，
        对比调整前后的 daemon 状态，判断调整是否有效。
        """
        if not self._strategy_journal_file.exists():
            return

        try:
            journal = json.loads(self._strategy_journal_file.read_text(encoding="utf-8"))
        except Exception:
            return

        # 找出所有未评估的条目
        unreviewed = [e for e in journal if e.get("effective") is None]
        if not unreviewed:
            return

        current_state = self._capture_daemon_state()
        lessons = self._self_profile.setdefault("strategy_lessons", {})

        for entry in unreviewed:
            trigger = entry.get("trigger", "")
            pre = entry.get("pre_state", {})
            changes = entry.get("changes", {})
            expected = entry.get("expected", "")

            # 判断调整是否有效
            effective = self._judge_adjustment_effect(trigger, pre, current_state, changes)
            entry["post_state"] = current_state
            entry["effective"] = effective

            # 更新策略经验
            trigger_lessons = lessons.setdefault(trigger, {})
            for param_key in changes:
                if param_key == "sub_gates":
                    continue
                if effective:
                    tag = f"{param_key}_increase" if changes[param_key].get("to", 0) > changes[param_key].get("from", 0) else f"{param_key}_decrease"
                    trigger_lessons[tag] = trigger_lessons.get(tag, {"effective": 0, "ineffective": 0})
                    trigger_lessons[tag]["effective"] += 1
                else:
                    tag = f"{param_key}_increase" if changes[param_key].get("to", 0) > changes[param_key].get("from", 0) else f"{param_key}_decrease"
                    trigger_lessons[tag] = trigger_lessons.get(tag, {"effective": 0, "ineffective": 0})
                    trigger_lessons[tag]["ineffective"] += 1

            verdict = "✅ 有效" if effective else "❌ 无效"
            print(f"  📊 策略回顾 [{entry.get('cycle', '?')}] {trigger}: {verdict} ({expected})")

        # 写回日志
        try:
            self._strategy_journal_file.write_text(
                json.dumps(journal, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    def _judge_adjustment_effect(self, trigger: str, pre: Dict, post: Dict, changes: Dict) -> bool:
        """
        判断调整是否有效。

        根据不同的 trigger 判断对应指标是否改善：
        - loop → 检查 error_rate 是否下降
        - confidence → 检查 confidence 是否上升
        - stagnation → 检查 health 是否上升
        - failure_risk → 检查 error_rate 是否下降
        """
        if not pre or not post:
            return False

        if trigger == "loop":
            # 循环减少 → error_rate 下降或 health 上升
            return post.get("error_rate", 1) < pre.get("error_rate", 0) or \
                   post.get("health", 0) > pre.get("health", 0)
        elif trigger == "confidence":
            # 置信度上升
            return post.get("confidence", 0) > pre.get("confidence", 0)
        elif trigger == "stagnation":
            # 停滞减少 → health 上升
            return post.get("health", 0) > pre.get("health", 0)
        elif trigger == "failure_risk":
            # 风险降低 → error_rate 下降
            return post.get("error_rate", 1) < pre.get("error_rate", 0)
        return False

    def _do_local_think(self):
        """
        执行纯本地深度思考。

        使用 ThinkingEngine 整合知识图、自模型、
        模式引擎、类比引擎，不依赖任何外部 API。
        """
        self._init_thinking_engine()
        if self._thinking_engine is None:
            return

        try:
            result = self._thinking_engine.think()
            self._last_local_think_cycle = getattr(self, '_cycle_count', 0)

            # 将好奇心问题合并到 self.questions
            if result.curiosity_questions:
                from curiosity_engine import CuriosityQuestion
                for q in result.curiosity_questions:
                    self.questions.append(CuriosityQuestion(
                        observation=f"[{q.source}] {q.detail}",
                        question=q.question,
                        importance=q.confidence,
                        explore_action="explore",
                        target=q.related_entity,
                        context={"source": q.source},
                    ))
                    if self._thought_graph:
                        self._thought_graph.add_thought(
                            topic=q.related_entity or q.source,
                            content=q.question,
                            thought_type="curiosity",
                            source=q.source,
                            importance=q.confidence,
                        )
                print(f"  🧠 本地深度思考: {len(result.curiosity_questions)} 个好奇心问题")

            # 将洞察写入思维图
            if result.insights and self._thought_graph:
                for ins in result.insights[:5]:
                    self._thought_graph.add_thought(
                        topic=ins.category,
                        content=ins.content[:500],
                        thought_type="insight",
                        source="local_thinking",
                        importance=ins.importance,
                    )
                print(f"  💡 本地深度思考: {len(result.insights)} 条洞察")

                # 连续性后处理：链接洞察到父线程
                if self._thought_continuity is not None and self._check_feature("thinking_continuity"):
                    insight_dicts = [
                        {"topic": ins.category, "summary": ins.content[:500],
                         "importance": ins.importance}
                        for ins in result.insights[:5]
                    ]
                    self._thought_continuity.post_process_results(
                        results=insight_dicts,
                        cycle_count=getattr(self, '_cycle_count', 0),
                    )

            # 记录叙事
            narrative = result.narrative
            print(f"  📖 叙事摘要: {narrative.split(chr(10))[0][:80]}...")

        except Exception as e:
            print(f"  ⚠️ 本地深度思考失败: {e}")
            et = self._get_experience_tracker()
            et.record("local_thinking", "thinking_engine", "failure",
                      "exception", getattr(self, '_cycle_count', 0),
                      str(e)[:200])

    # ---- 模块化思考技能系统 ----

    def _init_skills(self) -> Dict[str, Dict[str, Any]]:
        """注册可用思考技能（元数据+执行体，类似SKILL.md模式）"""
        return {
            "gap_analysis": {
                "name": "知识缺口分析",
                "description": "对比知识库与 KNOWLEDGE_MAP，发现缺失领域并生成爬虫任务",
                "trigger": "knowledge_gaps > 0",
                "default_depth": 5,
                "icon": "🔍",
            },
            "global_research": {
                "name": "全球架构研究",
                "description": "搜索GitHub/arXiv获取自思考AI架构和最佳实践",
                "trigger": "self_architecture_kb_missing",
                "default_depth": 3,
                "icon": "🌐",
            },
            "code_quality": {
                "name": "代码质量审查",
                "description": "扫描代码漏洞、质量问题和异常模式",
                "trigger": "vulnerabilities > 0 or quality_issues > 0",
                "default_depth": 3,
                "icon": "🔧",
            },
            "self_scan": {
                "name": "自身扫描",
                "description": "扫描项目结构和自知识别覆盖情况",
                "trigger": "self_kb_coverage < 50%",
                "default_depth": 3,
                "icon": "📡",
            },
            "capability_audit": {
                "name": "能力差距审计",
                "description": "对比能力清单与爬取的外部能力参考，发现缺失能力并评估可行性",
                "trigger": "capability_gaps > 3",
                "default_depth": 3,
                "icon": "📋",
            },
            "full_cycle": {
                "name": "完整思考循环",
                "description": "运行所有思考技能（默认模式）",
                "trigger": "manual / scheduled",
                "default_depth": 4,
                "icon": "🧠",
            },
        }

    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有可用思考技能"""
        return [
            {
                "name": s["name"],
                "description": s["description"],
                "trigger": s["trigger"],
                "icon": s["icon"],
                "key": key,
            }
            for key, s in self._skills.items()
        ]

    def run_skill(self, skill_name: str, depth: Optional[int] = None) -> List[Dict]:
        """执行指定的思考技能"""
        skill = self._skills.get(skill_name)
        if not skill:
            print(f"⚠️  未知技能: {skill_name}")
            return []

        effective_depth = depth if depth is not None else skill["default_depth"]
        icon = skill["icon"]

        print(f"\n{icon} 执行思考技能: {skill['name']}")
        print(f"   描述: {skill['description']}")

        # 所有技能共享扫描阶段
        self._scan_project()

        if skill_name == "gap_analysis":
            return self._run_gap_skill(effective_depth)
        elif skill_name == "global_research":
            return self._run_research_skill(effective_depth)
        elif skill_name == "code_quality":
            return self._run_quality_skill(effective_depth)
        elif skill_name == "self_scan":
            return self._run_self_scan_skill(effective_depth)
        elif skill_name == "capability_audit":
            return self._run_capability_audit_skill(effective_depth)
        else:
            # full_cycle → 所有问题类型一起跑（原逻辑）
            return self._run_full_cycle(effective_depth)

    def _run_gap_skill(self, depth: int) -> List[Dict]:
        """知识缺口分析技能：只关注 gap 类问题"""
        self._generate_questions()
        gap_qs = [q for q in self.questions if q.explore_action == "add_crawler_task"]
        if not gap_qs:
            print("✅ 没有发现新的知识缺口")
            return []
        print(f"🔍 发现 {len(gap_qs)} 个知识缺口，探索 top {min(depth, len(gap_qs))}")
        return self._explore_and_store(gap_qs[:depth])

    def _run_research_skill(self, depth: int) -> List[Dict]:
        """全球研究技能：只关注 global_research 类问题"""
        self._generate_questions()
        research_qs = [q for q in self.questions if q.explore_action == "global_research"]
        if not research_qs:
            print("✅ 当前无需全球研究")
            return []
        print(f"🌐 发起 {len(research_qs)} 项全球研究，探索 top {min(depth, len(research_qs))}")
        return self._explore_and_store(research_qs[:depth])

    def _run_quality_skill(self, depth: int) -> List[Dict]:
        """代码质量技能：分析代码问题"""
        self._generate_questions()
        quality_qs = [q for q in self.questions if q.explore_action in ("check_state", "read_file")]
        if not quality_qs:
            print("✅ 未发现新的代码质量问题")
            return []
        print(f"🔧 发现 {len(quality_qs)} 个代码相关问题，探索 top {min(depth, len(quality_qs))}")
        return self._explore_and_store(quality_qs[:depth])

    def _run_self_scan_skill(self, depth: int) -> List[Dict]:
        """自身扫描技能：分析自知识覆盖"""
        self._generate_questions()
        self_qs = [q for q in self.questions if q.target == "project_self"]
        if not self_qs:
            print("✅ 项目自知识覆盖良好")
            return []
        return self._explore_and_store(self_qs[:depth])

    def _run_capability_audit_skill(self, depth: int) -> List[Dict]:
        """能力差距审计：比较注册能力 vs 外部参考，生成差距报告"""
        if not self._check_feature("capability_learning"):
            print("  ⏭️ capability_learning 已禁用")
            return []

        from knowledge_base import KnowledgeBase
        registry = self._get_capability_registry()
        analyzer = self._get_gap_analyzer()
        kb = KnowledgeBase()
        refs = kb.get_knowledge_by_category("能力参考")

        results = []

        # 正向：已有能力在外部有更强实现吗？
        for cap in registry.list():
            analysis = analyzer.compare_capability_vs_knowledge(cap, refs)
            for r in analysis[:depth]:
                results.append({
                    "type": "capability_gap",
                    "capability": r.capability_name,
                    "kb_topic": r.kb_entry_topic,
                    "similarity": r.similarity_score,
                    "suggestion": r.reason,
                })

        # 反向：外部有什么我完全没有的？
        missing = analyzer.find_missing_capabilities(refs)
        ranked = analyzer.rank_gaps_by_value(missing)
        for gap in ranked[:depth]:
            results.append({
                "type": "missing_capability",
                "topic": gap.topic,
                "relevance": gap.relevance_score,
                "impact": gap.potential_impact,
                "cost": gap.implementation_cost,
                "score": gap.overall_score,
            })

        print(f"  📋 能力差距审计完成: {len(results)} 项发现")
        return results

    def _get_capability_gap_context(self) -> Dict[str, Any]:
        """返回能力差距摘要（用于自我认知 JSON）"""
        if not self._check_feature("capability_learning"):
            return {"total_gaps": 0, "top_gaps": []}
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            refs = kb.get_knowledge_by_category("能力参考")
            analyzer = self._get_gap_analyzer()
            missing = analyzer.find_missing_capabilities(refs)
            ranked = analyzer.rank_gaps_by_value(missing)
            return {
                "total_gaps": len(ranked),
                "top_gaps": [g.topic for g in ranked[:5]],
                "last_audit": datetime.now().isoformat(),
            }
        except Exception:
            return {"total_gaps": 0, "top_gaps": []}

    def _explore_and_store(self, questions: List) -> List[Dict]:
        """通用探索+存储流程（被各个技能复用）
        单个问题失败不影响其他问题的探索
        """
        et = self._get_experience_tracker()
        cycle = getattr(self, '_cycle_count', 0)
        results = []
        for q in questions:
            print(f"\n  {'─'*30}")
            print(f"  ❓ {q.question[:90]}")
            problem = q.target or q.question[:80]
            action = q.explore_action

            # 经验引导（从 AgentEvolver Self-Navigating 学习）
            try:
                exp_ctx = et.get_experience_context(problem)
                if exp_ctx:
                    print(f"  📖 相关经验:\n{exp_ctx[:200]}")
            except Exception:
                pass

            # 人格状态门控（从 Evolver PersonalityState 学习）
            personality = self._get_personality()
            if action in ("global_research", "deep_learning"):
                q.importance = personality.gate_creativity(q.importance)

            try:
                exploration = self._explore_question(q)
                insight = self._generate_insight(q, exploration)
                # 从问题继承重要性评分（供 daemon _apply_heals 使用）
                insight["importance"] = getattr(q, 'importance', 0.5)
                if insight["importance"] <= 0.0:
                    print(f"  ⚠️ 问题重要性为 0: {q.question[:80]}")
                    insight["importance"] = 0.3  # 兜底：至少 0.3
                # 传递问题上下文（延续线程的 parent_thought_id 等）
                ctx = getattr(q, 'context', None) or {}
                if isinstance(ctx, dict) and any(k in ctx for k in ('parent_thought_id',)):
                    insight['context'] = ctx
                stored = self._store_insight(insight)
                results.append(insight)

                et.record(problem, action, "success", cycle=cycle)

                # ── 行为反馈：记录成功探索 ──
                try:
                    self._behavior_feedback.record(
                        cycle=cycle,
                        action_type=action,
                        target=q.target or problem,
                        question=q.question[:200],
                        result="success",
                        detail=insight.get("summary", "")[:200],
                    )
                except Exception:
                    pass

                # 技能结晶：从成功探索提取可复用技能
                try:
                    from skill_crystallizer import SkillCrystallizer
                    sc = SkillCrystallizer()
                    skill_id = sc.extract_skill(q, insight, cycle)
                    if skill_id:
                        print(f"  ⚡ 技能结晶: {skill_id}")
                except Exception:
                    pass

                if action == "add_crawler_task":
                    added = self._add_crawler_tasks(q)
                    print(f"  🎯 爬虫任务{'已添加' if added else '已存在'}")
                elif action == "global_research":
                    print(f"  🌐 研究任务已调度")
            except Exception as e:
                print(f"  ⚠️ 问题探索失败: {e}")
                error_type = type(e).__name__
                et.record(problem, action, "failure", error_type,
                          cycle, str(e)[:200])
                # ── 行为反馈：记录失败探索 ──
                try:
                    self._behavior_feedback.record(
                        cycle=cycle,
                        action_type=action,
                        target=q.target or problem,
                        question=q.question[:200],
                        result="failure",
                        detail=f"{error_type}: {str(e)[:200]}",
                    )
                except Exception:
                    pass
                err_insight = {
                    "observation": q.observation,
                    "question": q.question,
                    "summary": f"探索失败: {e}",
                    "action_taken": "error",
                    "importance": getattr(q, 'importance', 0.5),
                }
                ctx = getattr(q, 'context', None) or {}
                if isinstance(ctx, dict) and any(k in ctx for k in ('parent_thought_id',)):
                    err_insight['context'] = ctx
                results.append(err_insight)

        self._log_thinking_cycle(results)
        return results

    def _run_full_cycle(self, depth: int) -> List[Dict]:
        """完整思考循环：所有问题类型一起探索（原默认逻辑）"""
        self._generate_questions()
        if not self.questions:
            print("💤 当前没有特别的好奇心触发")
            return []

        print(f"❓ 生成了 {len(self.questions)} 个好奇心问题")
        return self._explore_and_store(self.questions[:depth])

    # ---- 核心循环 ----

    def run_thinking_cycle(self, depth: int = 3,
                            skill: Optional[str] = None) -> List[Dict]:
        """
        执行一轮思考循环

        Args:
            depth: 探索问题数量
            skill: 指定思考技能（None=full_cycle, 或技能名称）
        """
        print(f"\n{'='*60}")
        print(f"🧠 自我思考循环启动 [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"{'='*60}")

        self._run_hooks(HookEvent.CYCLE_START, depth=depth, skill=skill)

        # 确保定向爬虫 hook 已注册（惰性初始化，不阻塞）
        if self._check_feature("capability_learning"):
            try:
                self._get_directed_crawler()
            except Exception:
                pass

        # 确保 LLM 增强钩子已注册（惰性初始化，不阻塞）
        if self._check_feature("local_thinking"):
            try:
                self._get_llm_integration()
            except Exception:
                pass

        # 策略回顾：上次调整的效果如何？
        self._cycle_count += 1
        self._review_strategy_effectiveness()

        # 所有路径都需要先扫描
        if skill and skill in self._skills:
            if self._check_feature("self_scanner"):
                self._run_hooks(HookEvent.PRE_SCAN)
                self._scan_project()
                self._run_hooks(HookEvent.POST_SCAN)
            if self._check_feature("knowledge_learning"):
                self._study_knowledge()
            result = self.run_skill(skill, depth)
            self._run_hooks(HookEvent.CYCLE_END, result=result)
            return result

        # 默认路径：自我评估 → 学习 → 设目标 → 自我认知 → 生成问题 → 目标排序 → 探索
        if self._check_feature("self_scanner"):
            self._run_hooks(HookEvent.PRE_SCAN)
            self._scan_project()
            self._run_hooks(HookEvent.POST_SCAN)
        else:
            self.snapshot = {}

        # 验证过去的改进是否仍然有效（有修改历史才验证）
        if self._check_feature("self_modification"):
            mod_history = self.snapshot.get("modification_history", {})
            recent_mods = mod_history.get("recent", [])
            if recent_mods:
                self._verify_past_improvements()

        # 学习新知识（优先项目自身相关）
        learned = []
        if self._check_feature("knowledge_learning"):
            self._run_hooks(HookEvent.PRE_STUDY)
            learned = self._study_knowledge()
            self._run_hooks(HookEvent.POST_STUDY, learned=learned)

        # 自我评估：代码质量趋势、知识覆盖、能力缺口
        self._run_hooks(HookEvent.PRE_EVALUATE)
        evaluation = self._self_evaluate()
        self._run_hooks(HookEvent.POST_EVALUATE, evaluation=evaluation)

        # 构建自我画像（方向1：自我理解）
        self._build_self_profile()

        # 根据评估设定改进目标
        goals = self._set_improvement_goals(evaluation)

        # 构建自我认知报告（AutoDream 条件触发：时间 + 新数据 + 无冲突）
        if self._check_feature("cog_architecture"):
            self._run_hooks(HookEvent.PRE_AWARENESS)
            if self._should_run_self_awareness():
                self._build_self_awareness()
            self._run_hooks(HookEvent.POST_AWARENESS)

        # 能力差距审计（当 gap 数量超过阈值时自动触发）
        if self._check_feature("capability_learning"):
            try:
                from knowledge_base import KnowledgeBase
                kb = KnowledgeBase()
                refs = kb.get_knowledge_by_category("能力参考")
                if refs:
                    analyzer = self._get_gap_analyzer()
                    missing = analyzer.find_missing_capabilities(refs)
                    if len(missing) >= 3:
                        print(f"  📋 能力差距 > 阈值 ({len(missing)} 项), 触发能力审计")
                        self.run_skill("capability_audit", depth=2)
            except Exception:
                pass

        # 知识库自动整理（AutoDream 风格：24h + 5新条目 + 无冲突）
        if self._check_feature("auto_consolidation"):
            self._run_hooks(HookEvent.PRE_CONSOLIDATE)
            self._auto_consolidate()
            self._run_hooks(HookEvent.POST_CONSOLIDATE)

        # 反思：对上一轮行动做审计（结果符合预期吗？有死循环吗？）
        self._run_hooks(HookEvent.PRE_REFLECT)
        if self.thinking_log:
            self._self_reflect()
        self._run_hooks(HookEvent.POST_REFLECT)

        # 读取自我状态（情绪、经历、暂缓问题），用于影响问题生成
        self._load_self_context()

        # 好奇心引擎生成问题（基于扫描数据 + 自我状态）
        if self._check_feature("curiosity_engine"):
            self._run_hooks(HookEvent.PRE_QUESTIONS)
            self._generate_questions()
            self._run_hooks(HookEvent.POST_QUESTIONS, questions=self.questions)

        # ── 思考延续：从 ThoughtGraph 注入延续问题 ──
        self._init_thinking_engine()  # 确保 continuity 已初始化
        self._continuation_qs = []
        if (self._thought_continuity is not None
                and self._check_feature("thinking_continuity")
                and self._thought_graph is not None):
            try:
                self._continuation_qs = self._thought_continuity.inject_continuation_questions(
                    current_questions=self.questions,
                    cycle_count=getattr(self, '_cycle_count', 0),
                    snapshot=self.snapshot or {},
                )
                if self._continuation_qs and self._thought_continuity.should_reduce_new_questions():
                    print(f"  📏 深度优先: 已有 {len(self._continuation_qs)} 个活跃线程，减少新问题")
            except Exception as e:
                print(f"  ⚠️ 思考延续异常: {e}")

        # 学习触发的行动和问题
        action_questions = []
        study_questions = []
        if learned and self._check_feature("knowledge_learning"):
            action_questions = self._apply_study_actions(learned)
            study_questions = self._generate_questions_from_study(learned)
            self.questions = action_questions + study_questions + self.questions
            if action_questions or study_questions:
                print(f"  💡 学习触发了 {len(action_questions) + len(study_questions)} 个新问题")

        # ── 纯本地深度思考 ──
        if self._should_do_local_thinking():
            self._do_local_think()
            # ThinkingEngine 生成的 CuriosityQuestion 已合并到 self.questions

        # ── 内在思考：主动分析已有知识 ──
        internal_qs = self._internal_think()
        if internal_qs:
            self.questions.extend(internal_qs)
            print(f"  💭 内在思考产生了 {len(internal_qs)} 个新问题")

        # ── 执行爬虫任务并学习结果 ──
        # 新 web_research 系统已取代旧爬虫队列，二者互斥
        if self._check_feature("global_research") and not self._check_feature("web_research"):
            self._crawl_and_learn()

        # ── 自主研究集成（多源搜索+内容提取+综合） ──
        if self._check_feature("web_research"):
            self._get_research_integration()  # 确保 hooks 已注册

        # 按活跃目标重新排序问题（目标相关的优先探索）
        self.questions = self._prioritize_questions(self.questions)

        # 排序后注入延续问题到队列头部（确保它们被本轮探索）
        if getattr(self, '_continuation_qs', None):
            self.questions = self._continuation_qs + self.questions

        # 始终记录学习行动（即使 0 个行动）
        self._log_study_actions(learned,
                                action_questions + study_questions)

        if not self.questions:
            print("💤 当前没有特别的好奇心触发")
            self._run_hooks(HookEvent.CYCLE_END, result=[])
            return []

        # 策略深度覆盖：如果当前策略指定了探索深度
        effective_depth = depth
        if hasattr(self, '_current_strategy') and self._current_strategy:
            effective_depth = self._current_strategy.exploration_depth

        print(f"❓ 共 {len(self.questions)} 个好奇心问题")

        # ── 行动平衡：确保至少 1 个自修复问题被选中 ──
        # 优先 self_heal，其次才是读文件
        top_n = self.questions[:effective_depth]
        HEALABLE = {"self_heal", "code_quality_heal"}
        has_heal = any(q.explore_action in HEALABLE for q in top_n)
        if not has_heal:
            # 先找 self_heal，找不到再找 read_file/check_state
            for target_type in (HEALABLE, {"read_file", "check_state"}):
                for i, q in enumerate(self.questions[effective_depth:]):
                    if q.explore_action in target_type:
                        swap = effective_depth - 1
                        self.questions[swap], self.questions[effective_depth + i] = \
                            self.questions[effective_depth + i], self.questions[swap]
                        print(f"  ⚖️ 行动平衡: {q.explore_action} 替换 #{swap}")
                        break
                else:
                    continue
                break

        self._run_hooks(HookEvent.PRE_EXPLORE, questions=self.questions[:effective_depth])
        results = self._explore_and_store(self.questions[:effective_depth])
        self._run_hooks(HookEvent.POST_EXPLORE, results=results)

        # 元认知记录：本轮探索结果 → 思考主题
        try:
            monitor = self._get_metacognitive_monitor()
            for ins in results:
                topic = ins.get("topic", "") or ins.get("summary", "")[:60]
                if topic:
                    monitor.record_thought(topic)
            # 执行元认知检查（无 findings 也记录统计）
            et = self._get_experience_tracker()
            t_stats = self._get_thinking_engine_stats()
            d_stats = self._get_daemon_stats()
            mc_findings = monitor.check(
                experience_tracker=et, thinking_stats=t_stats,
                daemon_stats=d_stats)
            # 方向3：基于元认知发现调整行为
            self._apply_metacognitive_adjustments(mc_findings)

            # ── 策略选择：基于综合质量评分切换思考模式 ──
            try:
                from thinking_strategy import StrategyManager
                if not hasattr(self, '_strategy_manager'):
                    self._strategy_manager = StrategyManager()
                quality_report = monitor.compute_quality_score(
                    experience_tracker=et, thinking_stats=t_stats,
                    daemon_stats=d_stats)
                strategy = self._strategy_manager.select_strategy(
                    quality_report, cycle_count=getattr(self, '_cycle_count', 0))
                self._current_strategy = strategy
                self._quality_report = quality_report

                # 应用策略到 daemon 参数
                daemon_sm = None
                try:
                    from thinking_daemon import get_daemon
                    daemon_sm = get_daemon()
                except Exception:
                    pass
                if daemon_sm:
                    changes = self._strategy_manager.apply_to_daemon(daemon_sm)
                    if changes:
                        print(f"  ⚙️ 策略影响 daemon 参数:")
                        for k, (old, new) in changes.items():
                            print(f"    {k}: {old} → {new}")
            except Exception as strat_err:
                print(f"  ⚠️ 策略选择异常: {strat_err}")
        except Exception:
            pass

        # 将探索结果写入思维图 + 连续性后处理
        if self._thought_graph is not None and results:
            if self._thought_continuity is not None and self._check_feature("thinking_continuity"):
                self._thought_continuity.post_process_results(
                    results=results,
                    cycle_count=getattr(self, '_cycle_count', 0),
                )
            else:
                for ins in results:
                    self._thought_graph.add_thought(
                        topic=ins.get("topic", "未知"),
                        content=ins.get("summary", ins.get("detail", ""))[:500],
                        thought_type="insight",
                        importance=ins.get("importance", 0.5),
                        source="exploration",
                    )

        # 游标式逐轮记忆提取（extractMemories.ts 模式：每轮结束时执行）
        if self._check_feature("memory_extraction"):
            self._extract_memories()

        self._run_hooks(HookEvent.CYCLE_END, result=results)

        # ── 分层记忆：归档本轮经验（从 GenericAgent L0-L4 学习） ──
        try:
            lm = self._get_layered_memory()
            lm.add_to_index(
                topic=f"思考循环 #{self._cycle_count}",
                category="thinking_cycle",
                summary=f"探索 {len(results)} 个问题",
                ref=f"cycle_{self._cycle_count}",
            )
            lm.archive_session({
                "cycle": self._cycle_count,
                "results_count": len(results) if results else 0,
            })
        except Exception:
            pass

        # ── 背景审查：自动提取技能（从 Hermes Nudge Engine 学习） ──
        try:
            if results and self._cycle_count % 5 == 0:
                from skill_crystallizer import SkillCrystallizer
                sc = SkillCrystallizer()
                activities = [{
                    "tool_calls": len(results),
                    "errors": [{"overcome": True}] if r.get("summary") else [],
                    "action": r.get("action_taken", "explore"),
                    "target": r.get("topic", ""),
                    "steps": len(results),
                    "complex_task": len(results) > 3,
                } for r in results if isinstance(r, dict)]
                candidates = sc.background_review(activities)
                if candidates:
                    print(f"  🔍 背景审查: {len(candidates)} 个值得结晶的活动")
        except Exception:
            pass

        return results

    def _scan_project(self):
        """扫描项目当前状态"""
        self.snapshot = self.scanner.get_full_snapshot()
        self.diff = self.scanner.diff_from_previous(self.snapshot)
        self.scanner.save_snapshot(self.snapshot)

    def _study_knowledge(self) -> List[Dict]:
        """
        在思考之前先"学习"知识库中的新资料
        三级优先级：P0=项目自身, P1=系统相关概念, P2=其他按重要性
        P0 条目每 5 周期重新学习一次，避免学完就忘
        返回本轮学习的条目列表（可用于后续行动触发）
        """
        study_tracker = self.data_dir / "study_tracker.json"
        studied_topics = set()
        if study_tracker.exists():
            try:
                studied_topics = set(json.loads(study_tracker.read_text(encoding="utf-8")))
            except Exception:
                studied_topics = set()

        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            all_k = kb.get_all_knowledge()

            # 找没学过的
            unstudied = [k for k in all_k if k.get("topic", "") not in studied_topics]

            # 所有已学过的 P0 条目，每 5 周期重新学一次
            # 用 counter 文件追踪周期数
            cycle_counter = self.data_dir / "cycle_counter.json"
            counter_data = {"cycle": 0}
            if cycle_counter.exists():
                try:
                    counter_data = json.loads(cycle_counter.read_text(encoding="utf-8"))
                except Exception:
                    pass
            counter_data["cycle"] = counter_data.get("cycle", 0) + 1
            cycle_counter.write_text(json.dumps(counter_data))

            restudy = []
            if counter_data["cycle"] % 5 == 0:
                for k in all_k:
                    if k.get("category") == "项目自身" and k.get("topic", "") in studied_topics:
                        restudy.append(k)

            # 三级优先级排序
            project_keywords = ["self", "thinking", "cognition", "modification", "scanner", "curiosity"]

            def priority(entry):
                cat = entry.get("category", "")
                topic = entry.get("topic", "")
                imp = entry.get("importance", 0.5)
                if cat == "项目自身":
                    return (0, -imp)  # P0: 项目自身知识优先
                if any(kw in cat.lower() for kw in project_keywords) or \
                   any(kw in topic.lower() for kw in project_keywords):
                    return (1, -imp)  # P1: 系统相关概念
                return (2, -imp)  # P2: 其他

            unstudied.sort(key=priority)

            # 优先未学过的，不足时补充重新学习的 P0
            batch = unstudied[:5]
            if len(batch) < 5 and restudy:
                batch.extend(restudy[:5 - len(batch)])
            if not batch:
                return []

            # 验证批量条目的有效性（skeptical memory 模式：验证后再信任）
            verified_batch = []
            for entry in batch:
                topic = entry.get("topic", "")
                # 对"模块分析"类条目，验证对应的 .py 文件仍然存在
                if "模块分析" in topic:
                    for py_file in Path.cwd().glob("*.py"):
                        if py_file.stem in topic:
                            verified_batch.append(entry)
                            break
                    else:
                        print(f"  ⚠️ 跳过失效条目: {topic[:40]} (文件已不存在)")
                        continue
                else:
                    verified_batch.append(entry)
            batch = verified_batch
            if not batch:
                return []

            # 构建学习条目
            learned = []
            for entry in batch:
                studied_topics.add(entry.get("topic", ""))
                learned.append({
                    "topic": entry.get("topic", ""),
                    "source": entry.get("source", ""),
                    "importance": entry.get("importance", 0),
                    "category": entry.get("category", ""),
                    "content": entry.get("content", ""),
                    "key_concepts": entry.get("keywords", [])[:5],
                    "summary": (entry.get("content", "") or "")[:100],
                })

            # 保存学习追踪
            study_tracker.write_text(json.dumps(list(studied_topics), ensure_ascii=False), encoding="utf-8")

            # 记录学习日志
            study_log = self.data_dir / "study_log.json"
            study_entries = []
            if study_log.exists():
                try:
                    study_entries = json.loads(study_log.read_text(encoding="utf-8"))
                except Exception:
                    pass
            study_entries.append({
                "time": datetime.now().isoformat(),
                "batch_size": len(learned),
                "total_studied": len(studied_topics),
                "total_kb": len(all_k),
                "entries": [{
                    "topic": l["topic"],
                    "source": l["source"],
                    "importance": l["importance"],
                    "category": l["category"],
                    "key_concepts": l["key_concepts"],
                    "summary": l["summary"],
                } for l in learned],
            })
            study_log.write_text(json.dumps(study_entries, ensure_ascii=False, indent=2), encoding="utf-8")

            # 打印学习摘要
            print(f"\n  {'─'*40}")
            print(f"  📖 学习新知识 ({len(learned)}/{len(all_k)}):")
            for l in learned:
                tag = "🔬" if "[深度]" in l["topic"] else "📄"
                pri = "⭐ " if l.get("category") == "项目自身" else ""
                concepts = ", ".join(l["key_concepts"][:3])
                print(f"  {tag}{pri}{l['topic'][:60]}")
                if concepts:
                    print(f"     概念: {concepts}")
            print(f"  {'─'*40}")

            return learned

        except Exception as e:
            print(f"  ⚠️ 学习阶段异常: {e}")
            return []

    # ═══════════════════════════════════════
    #  🎯 自我评估与目标设定
    # ═══════════════════════════════════════

    def _self_evaluate(self) -> Dict[str, Any]:
        """
        自我评估：分析代码质量趋势、知识覆盖、能力缺口
        所有数据来自真实扫描结果，无随机值
        """
        snapshot = self.snapshot or {}
        now = datetime.now().isoformat()

        # 1. 代码质量
        py_files = snapshot.get("py_files", [])
        self_learning = snapshot.get("self_learning", {})
        code_issues = self_learning.get("code_quality_issues", 0)
        issues_detail = self_learning.get("code_quality_issue_list", [])

        # 2. 知识覆盖
        kb = snapshot.get("knowledge_base", {})
        total_kb = kb.get("total_entries", 0)
        categories = kb.get("category_breakdown", {})
        project_kb_count = categories.get("项目自身", 0)

        # 学习进度（从 study_tracker 读取）
        study_tracker = self.data_dir / "study_tracker.json"
        studied = 0
        if study_tracker.exists():
            try:
                studied = len(json.loads(study_tracker.read_text(encoding="utf-8")))
            except Exception:
                pass

        # 3. 修改历史
        mod_history = snapshot.get("modification_history", {})
        mod_success = mod_history.get("successful", 0)
        mod_total = mod_history.get("total_attempts", 0)
        mod_rate = round(mod_success / max(1, mod_total) * 100, 1)

        # 4. 项目文件状态（多少文件有文档、类型标注）
        doc_ratio = 0
        type_hint_ratio = 0
        if py_files:
            docced = sum(1 for f in py_files if f.get("has_docstring", False))
            typed = sum(1 for f in py_files if f.get("has_type_hints", False))
            doc_ratio = round(docced / len(py_files) * 100, 1)
            type_hint_ratio = round(typed / len(py_files) * 100, 1)

        # 5. 加载之前的评估数据做趋势对比
        prev_eval = self._load_growth_plan().get("last_evaluation", {})
        prev_issues = prev_eval.get("code_issues", code_issues)
        issues_trend = "improving" if code_issues < prev_issues else (
            "regressed" if code_issues > prev_issues else "stable")

        evaluation = {
            "timestamp": now,
            "code_issues": code_issues,
            "issues_trend": issues_trend,
            "issues_detail": issues_detail,
            "total_files": len(py_files),
            "doc_coverage": doc_ratio,
            "type_hint_coverage": type_hint_ratio,
            "kb_total": total_kb,
            "kb_project": project_kb_count,
            "kb_studied": studied,
            "kb_study_ratio": round(studied / max(1, total_kb) * 100, 1),
            "modifications_attempted": mod_total,
            "modifications_succeeded": mod_success,
            "modification_success_rate": mod_rate,
        }

        print(f"\n  {'─'*40}")
        print(f"  📊 自我评估")
        print(f"  代码质量: {code_issues} 个问题 ({issues_trend})")
        print(f"  文档覆盖率: {doc_ratio}% | 类型标注: {type_hint_ratio}%")
        print(f"  知识: {studied}/{total_kb} 已学 ({evaluation['kb_study_ratio']}%)")
        print(f"  修改成功率: {mod_rate}%")
        print(f"  {'─'*40}")

        return evaluation

    def _set_improvement_goals(self, evaluation: Dict[str, Any]) -> List[Dict]:
        """
        根据自我评估设定改进目标
        目标类型：fix（修复问题）、learn（学习知识）、improve（提升指标）
        """
        plan = self._load_growth_plan()
        completed_goals = plan.get("completed_goals", [])
        active_goals = plan.get("current_goals", [])
        prev_goal_ids = {g["id"] for g in active_goals}

        new_goals = []

        # 检查上一轮目标完成情况，标记完成/失败的
        for goal in active_goals:
            self._check_single_goal(goal, evaluation, completed_goals)

        # 清除已完成/失败的旧目标
        active_goals = [g for g in active_goals if g.get("status") == "active"]
        existing_types = {g.get("type") for g in active_goals}

        # 基于当前评估生成新目标（不重复已有类型的目标）
        # 目标1: 如果有代码问题，修复它们
        if evaluation["code_issues"] > 0 and "fix" not in existing_types:
            new_goals.append({
                "id": f"fix_issues_{datetime.now().strftime('%H%M%S')}",
                "type": "fix",
                "description": f"修复 {evaluation['code_issues']} 个代码质量问题",
                "success_criteria": "code_issues == 0",
                "priority": 0,
                "deadline_cycles": 3,
                "status": "active",
                "created": datetime.now().isoformat(),
            })

        # 目标2: 如果知识覆盖率低，学习项目自身知识
        kb_studied = evaluation.get("kb_studied", 0)
        kb_project = evaluation.get("kb_project", 0)
        if kb_project > 0 and kb_studied < kb_project and "learn" not in existing_types:
            new_goals.append({
                "id": f"learn_project_{datetime.now().strftime('%H%M%S')}",
                "type": "learn",
                "description": f"学习项目自身知识 ({kb_studied}/{kb_project} 已学)",
                "success_criteria": "kb_studied >= kb_project",
                "priority": 1,
                "deadline_cycles": 10,
                "status": "active",
                "created": datetime.now().isoformat(),
            })

        # 目标3: 如果文档覆盖率低，提升文档
        if evaluation["doc_coverage"] < 50 and "improve" not in existing_types:
            new_goals.append({
                "id": f"improve_docs_{datetime.now().strftime('%H%M%S')}",
                "type": "improve",
                "description": f"提升文档覆盖率 ({evaluation['doc_coverage']}% → 50%+)",
                "success_criteria": "doc_coverage >= 50",
                "priority": 2,
                "deadline_cycles": 15,
                "status": "active",
                "created": datetime.now().isoformat(),
            })

        # 合并新旧目标
        all_goals = active_goals + new_goals

        # 保存
        plan["current_goals"] = all_goals
        plan["completed_goals"] = completed_goals
        plan["last_evaluation"] = evaluation
        plan["updated"] = datetime.now().isoformat()
        self._save_growth_plan(plan)

        if new_goals:
            print(f"  🎯 新设 {len(new_goals)} 个改进目标:")
            for g in new_goals:
                print(f"    [{g['type']}] {g['description']}")
        else:
            print(f"  🎯 当前 {len(all_goals)} 个活跃目标")

        return all_goals

    def _check_single_goal(self, goal: Dict, evaluation: Dict[str, Any],
                           completed_goals: List):
        """检查单个目标是否完成"""
        criteria = goal.get("success_criteria", "")
        if not criteria:
            return

        try:
            # 简单条件检查
            if criteria == "code_issues == 0" and evaluation["code_issues"] == 0:
                goal["status"] = "completed"
                goal["completed_at"] = datetime.now().isoformat()
                completed_goals.append(goal)
                print(f"  ✅ 目标达成: {goal['description']}")
            elif "kb_studied >= kb_project" in criteria:
                if evaluation.get("kb_studied", 0) >= evaluation.get("kb_project", 0):
                    goal["status"] = "completed"
                    goal["completed_at"] = datetime.now().isoformat()
                    completed_goals.append(goal)
                    print(f"  ✅ 目标达成: {goal['description']}")
            elif "doc_coverage >= 50" in criteria:
                if evaluation.get("doc_coverage", 0) >= 50:
                    goal["status"] = "completed"
                    goal["completed_at"] = datetime.now().isoformat()
                    completed_goals.append(goal)
                    print(f"  ✅ 目标达成: {goal['description']}")

            # 检查是否超时
            if goal["status"] == "active":
                created = datetime.fromisoformat(goal["created"])
                elapsed_cycles = evaluation.get("_cycle_count", 0)
                if elapsed_cycles >= goal.get("deadline_cycles", 10):
                    goal["status"] = "failed"
                    goal["failed_at"] = datetime.now().isoformat()
                    completed_goals.append(goal)
                    print(f"  ⏰ 目标超期: {goal['description']}")
        except Exception:
            pass

    def _get_active_goal_topics(self) -> List[str]:
        """获取活跃目标相关的主题词，用于问题优先级排序"""
        plan = self._load_growth_plan()
        topics = []
        for g in plan.get("current_goals", []):
            if g.get("status") != "active":
                continue
            desc = g.get("description", "")
            gtype = g.get("type", "")
            if gtype == "fix":
                topics.extend(["修复", "except", "bug", "error"])
            elif gtype == "learn":
                topics.extend(["学习", "知识", "概念"])
            elif gtype == "improve":
                topics.extend(["文档", "docstring", "类型"])
        return topics

    def _load_growth_plan(self) -> Dict:
        """加载成长计划"""
        if self.growth_plan_file.exists():
            try:
                return json.loads(self.growth_plan_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"current_goals": [], "completed_goals": [], "last_evaluation": {}, "updated": ""}

    def _save_growth_plan(self, plan: Dict):
        """保存成长计划（原子写入：临时文件 → rename，防止写一半崩溃）"""
        try:
            import tempfile
            fd, tmp_path = tempfile.mkstemp(suffix=".tmp", dir=str(self.data_dir))
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            # 验证写入成功再 rename
            try:
                test = json.loads(open(tmp_path, encoding="utf-8").read())
                if "current_goals" not in test:
                    raise ValueError("计划数据验证失败")
            except Exception as e:
                os.unlink(tmp_path)
                print(f"  ⚠️ 写入验证失败，已丢弃: {e}")
                return
            os.replace(tmp_path, str(self.growth_plan_file))
        except Exception as e:
            print(f"  ⚠️ 成长计划保存失败: {e}")

    # ═══════════════════════════════════════
    #  🧠 自我认知系统
    # ═══════════════════════════════════════

    def _build_self_awareness(self) -> Dict[str, Any]:
        """
        构建自我认知报告：系统知道自己的结构、能力、历史、缺口
        这份报告存入 KB，供未来的自己学习
        """
        snapshot = self.snapshot or {}
        py_files = snapshot.get("py_files", [])
        mod_history = snapshot.get("modification_history", {})
        kb = snapshot.get("knowledge_base", {})
        now = datetime.now().isoformat()

        # 加载之前的自我认知，保留历史记录
        awareness_file = self.data_dir / "self_awareness.json"
        prev_awareness = {}
        if awareness_file.exists():
            try:
                prev_awareness = json.loads(awareness_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # 1. 模块清单
        modules = []
        for f in py_files:
            modules.append({
                "name": f.get("file", "?"),
                "lines": f.get("lines", 0),
                "classes": len(f.get("classes", [])),
                "functions": len(f.get("functions", [])),
                "imports": f.get("import_count", 0),
            })

        # 2. 能力清单（从注册表获取，自动发现 + 持久化）
        try:
            registry = self._get_capability_registry()
            capabilities = registry.to_serializable_list()
            print(f"  📋 能力清单: {len(capabilities)} 项 (已持久化)")
        except Exception:
            capabilities = []

        # 3. 改进历史（累积）
        prev_history = prev_awareness.get("improvement_history", [])
        mod_recent = mod_history.get("recent", [])
        new_improvements = []
        for m in mod_recent[-5:]:
            entry = {
                "what": m.get("detail", m.get("reason", "?")),
                "file": m.get("file", "?"),
                "when": m.get("timestamp", "?"),
                "status": m.get("status", "?"),
            }
            # 去重
            if entry not in prev_history and entry not in new_improvements:
                new_improvements.append(entry)

        improvement_history = prev_history + new_improvements
        improvement_history = improvement_history[-50:]  # 最多保留 50 条

        # 4. 当前目标
        plan = self._load_growth_plan()
        current_goals = [
            {"type": g["type"], "description": g["description"], "status": g["status"]}
            for g in plan.get("current_goals", [])
        ]

        # 5. 自我描述
        total_lines = sum(m["lines"] for m in modules)
        total_classes = sum(m["classes"] for m in modules)
        total_funcs = sum(m["functions"] for m in modules)
        mod_success = mod_history.get("successful", 0)
        mod_total = mod_history.get("total_attempts", 0)

        categories = kb.get("category_breakdown", {})
        project_kb = categories.get("项目自身", 0)

        awareness = {
            "version": prev_awareness.get("version", 0) + 1,
            "timestamp": now,
            "last_update": now,
            "modules": modules,
            "summary": {
                "total_files": len(modules),
                "total_lines": total_lines,
                "total_classes": total_classes,
                "total_functions": total_funcs,
            },
            "capabilities": capabilities,
            "capability_gaps": self._get_capability_gap_context(),
            "modification_stats": {
                "attempted": mod_total,
                "succeeded": mod_success,
                "projects_entries": project_kb,
            },
            "improvement_history": improvement_history,
            "current_goals": current_goals,
            "active_focus": self._determine_focus(current_goals),
        }

        # 保存
        try:
            awareness_file.write_text(
                json.dumps(awareness, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"  ⚠️ 自我认知保存失败: {e}")

        # 同时存入 KB
        self._store_self_awareness_to_kb(awareness)

        print(f"\n  {'─'*40}")
        print(f"  🧠 自我认知 (v{awareness['version']})")
        print(f"  {len(modules)} 文件 | {total_lines} 行 | {total_classes} 类 | {total_funcs} 函数")
        print(f"  {len(capabilities)} 项能力 | {mod_success}/{mod_total} 修改成功")
        print(f"  焦点: {awareness['active_focus']}")
        print(f"  {'─'*40}")

        return awareness

    def _determine_focus(self, goals: List[Dict]) -> str:
        """根据活跃目标确定当前焦点"""
        active = [g for g in goals if g.get("status") == "active"]
        if not active:
            return "探索新知识"
        # 优先级排序
        for gtype in ["fix", "learn", "improve"]:
            for g in active:
                if g["type"] == gtype:
                    return g["description"][:60]
        return active[0]["description"][:60]

    def _should_run_self_awareness(self) -> bool:
        """
        AutoDream 风格触发条件：时间 + 数据量 + 无冲突
        替代硬编码的 cycle_num % 5 == 0
        """
        awareness_file = self.data_dir / "self_awareness.json"
        if not awareness_file.exists():
            return True  # 还没有认知报告，立即创建

        try:
            prev = json.loads(awareness_file.read_text(encoding="utf-8"))
            from datetime import datetime, timezone

            # 条件1: 距离上次够久（至少 30 分钟）
            last_update = prev.get("timestamp", "")
            if last_update:
                last = datetime.fromisoformat(last_update)
                now = datetime.now(timezone.utc) if last_update.endswith("Z") else datetime.now()
                hours_since = (now - last).total_seconds() / 3600
                if hours_since < 0.5:
                    return False  # 不足 30 分钟，跳过

            # 条件2: 有足够的新数据
            snapshot = self.snapshot or {}
            prev_modules = len(prev.get("modules", []))
            curr_modules = len(snapshot.get("py_files", []))
            prev_history = len(prev.get("improvement_history", []))
            mod_history = snapshot.get("modification_history", {})
            curr_history = len(mod_history.get("recent", []))
            has_new_data = (curr_modules != prev_modules) or (curr_history > prev_history)

            # 条件3: 无冲突（没有其他进程正在写认知报告）
            lock_file = self.data_dir / "awareness.lock"
            if lock_file.exists():
                import os
                try:
                    pid = int(lock_file.read_text().strip())
                    os.kill(pid, 0)
                    return False  # 有其他进程在写
                except (OSError, ValueError):
                    lock_file.unlink(missing_ok=True)

            return has_new_data

        except Exception:
            return True

    def _auto_consolidate(self) -> bool:
        """
        AutoDream 风格知识库整理：三级门控 + 扫描节流

        原版 Claude Code autoDream 三级门控（按成本递增）：
        1. 时间门控：距上次整理至少 24 小时
        2. 会话门控（改为条目门控）：至少 5 个新条目
        3. 锁门控：无冲突（PID 文件锁）

        附加扫描节流：即使时间门控通过，10 分钟内不再扫描
        """
        from knowledge_base import KnowledgeBase

        # 扫描节流追踪
        tracker_file = self.data_dir / "consolidate_tracker.json"
        tracker = {"last_run": "", "kb_size": 0, "last_scan_at": 0}
        if tracker_file.exists():
            try:
                tracker = json.loads(tracker_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # --- 扫描节流 ---
        # 即使时间门控通过，10 分钟内不重复扫描
        last_scan = tracker.get("last_scan_at", 0)
        if last_scan and (time.time() - last_scan) < 600:  # 600s = 10min
            return False

        # 更新扫描时间
        tracker["last_scan_at"] = time.time()

        # --- 时间门控 ---
        last_run = tracker.get("last_run", "")
        if last_run:
            try:
                last = datetime.fromisoformat(last_run)
                now = datetime.now()
                hours_since = (now - last).total_seconds() / 3600
                if hours_since < 24:
                    return False
            except Exception:
                pass

        # --- 条目门控 ---
        try:
            kb = KnowledgeBase()
            current_size = len(kb.get_all_knowledge())
            prev_size = tracker.get("kb_size", 0)
            if prev_size > 0:
                new_entries = current_size - prev_size
                if new_entries < 5:
                    return False  # 数据还不够
        except Exception:
            return False

        # --- 锁门控 ---
        if not KnowledgeBase.acquire_consolidation_lock(self.data_dir):
            return False

        try:
            print(f"\n  {'─'*40}")
            print(f"  🧹 知识库自动整理 (AutoDream)")
            stats = kb.consolidate_knowledge(max_per_category=50, dry_run=False)

            # 更新追踪
            tracker["last_run"] = datetime.now().isoformat()
            tracker["kb_size"] = len(kb.get_all_knowledge())
            tracker["last_stats"] = stats
            tracker_file.write_text(json.dumps(tracker, ensure_ascii=False, indent=2))
            print(f"  {'─'*40}")

            return stats["removed_stale"] + stats["deduped"] + stats["pruned"] > 0
        except Exception as e:
            print(f"  ⚠️ 自动整理异常: {e}")
            return False
        finally:
            KnowledgeBase.release_consolidation_lock(self.data_dir)

    def _self_reflect(self):
        """
        反思审计：对上一轮思考循环的结果做质量检查
        Claude Code 泄露源码模式：Act → 审计 → Think
        检查：结果是否符合预期？是否有重复模式？是否有死循环？
        """
        if not self.thinking_log:
            return

        last = self.thinking_log[-1]
        insights = last.get("insights", [])
        prev = self.thinking_log[-2] if len(self.thinking_log) >= 2 else None

        findings = []

        # 1. 检查死循环：连续多轮产出完全相同的洞察
        if prev:
            prev_topics = {i.get("topic", "") for i in prev.get("insights", [])}
            curr_topics = {i.get("topic", "") for i in insights}
            overlap = prev_topics & curr_topics
            if len(overlap) > 0 and len(overlap) == len(curr_topics):
                findings.append(f"⚠️ 重复模式: {len(overlap)} 个洞察与上轮完全相同")
                self._log_reflection_finding("loop_detected",
                    f"检测到思考循环: {', '.join(list(overlap)[:3])}")

        # 2. 检查空产出：有好奇心但没产生洞察
        q_count = last.get("questions_count", 0)
        i_count = last.get("insights_generated", 0)
        if q_count > 0 and i_count == 0:
            findings.append(f"⚠️ 探索空转: {q_count} 个问题都没产出洞察")
            self._log_reflection_finding("empty_cycle",
                f"探索效率为 0/{q_count}")

        # 3. 检查修复有效性：self_heal 类型的改动，下次验证
        for ins in insights:
            if ins.get("action") == "self_heal":
                topic = ins.get("topic", "")
                findings.append(f"🔧 待验证修复: {topic[:50]}")
                self._log_reflection_finding("heal_pending",
                    f"修复待验证: {topic}")

        # 4. 经验记忆：跨周期重复失败检测
        try:
            et = self._get_experience_tracker()
            patterns = et.get_failure_patterns(min_count=3)
            for p in patterns[:3]:
                findings.append(
                    f"🔁 重复失败: '{p['problem'][:30]}' "
                    f"用 '{p['strategy']}' 已失败 {p['count']} 次 "
                    f"({p['error_type']})")
                self._log_reflection_finding("repeated_failure",
                    f"{p['problem']}|{p['strategy']}|{p['count']}次")
        except Exception:
            pass

        # 5. 元认知监控：思考质量评估
        try:
            monitor = self._get_metacognitive_monitor()
            # 记录本轮思考主题
            for ins in insights:
                topic = ins.get("topic", "") or ins.get("summary", "")[:60]
                if topic:
                    monitor.record_thought(topic)

            # 执行元认知检查
            et = self._get_experience_tracker()
            t_stats = self._get_thinking_engine_stats()
            d_stats = self._get_daemon_stats()
            m_findings = monitor.check(
                experience_tracker=et,
                thinking_stats=t_stats,
                daemon_stats=d_stats,
            )
            for mf in m_findings:
                findings.append(
                    f"[元认知] [{mf.finding_type}] (severity={mf.severity:.2f}) "
                    f"{mf.detail[:80]}")
                self._log_reflection_finding(
                    f"metacognitive_{mf.finding_type}", mf.detail)
            # 方向3：基于元认知发现实际改变行为
            self._apply_metacognitive_adjustments(m_findings)
        except Exception:
            import traceback
            findings.append(f"⚠️ 元认知监控异常: {traceback.format_exc()[:100]}")

        # 6. 行为反馈分析：从历史行为中学习
        try:
            bf = self._behavior_feedback
            failing = bf.get_failing_targets()
            for f in failing[:2]:
                findings.append(
                    f"🔁 行为反馈: '{f['target']}' "
                    f"失败 {f['failures']}/{f['attempts']} 次 "
                    f"({f['fail_rate']:.0%}) — 应减少此方向投入")
                self._log_reflection_finding(
                    "behavior_failure", f"{f['target']}|{f['fail_rate']:.0%}")

            successful = bf.get_successful_targets()
            for s in successful[:2]:
                findings.append(
                    f"✅ 行为反馈: '{s['target']}' "
                    f"成功 {s['successes']}/{s['attempts']} 次 "
                    f"({s['success_rate']:.0%}) — 可继续深入")
                self._log_reflection_finding(
                    "behavior_success", f"{s['target']}|{s['success_rate']:.0%}")
        except Exception as e:
            findings.append(f"⚠️ 行为反馈分析异常: {e}")

        # 7. 策略学习分析（数据先行阶段，只记录不干预）
        if hasattr(self, '_behavior_feedback') and len(self._behavior_feedback.records) >= 10:
            try:
                if self._strategy_learner is None:
                    from strategy_learner import StrategyLearner
                    self._strategy_learner = StrategyLearner(self._behavior_feedback)
                cycle = getattr(self, '_cycle_count', 0)
                result = self._strategy_learner.analyze(cycle)
                if result.get("status") == "analyzed":
                    findings.append(
                        f"🧠 策略学习: {result.get('summary', '')}")
                    # 打印策略清单到日志
                    s_summary = self._strategy_learner.get_strategy_summary()
                    if s_summary:
                        print(f"\n  {s_summary}")
            except Exception as e:
                pass  # 策略学习是可选的，不影响主流程

        if findings:
            print(f"\n  {'─'*40}")
            print(f"  🔍 反思审计 ({len(findings)} 项)")
            for f in findings:
                print(f"  {f}")
            print(f"  {'─'*40}")

    def _log_reflection_finding(self, finding_type: str, detail: str):
        """记录反思发现到 thinking_log"""
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "reflection",
                "finding_type": finding_type,
                "detail": detail,
            }
            log_file = self.data_dir / "self_thinking_log.json"
            existing = []
            if log_file.exists():
                with open(log_file, encoding="utf-8") as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _store_self_awareness_to_kb(self, awareness: Dict):
        """将自我认知报告存入知识库"""
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            summary = awareness["summary"]
            history = awareness["improvement_history"]
            recent_fixes = [h for h in history[-5:] if h.get("status") == "success"]

            kb.add_knowledge({
                "topic": f"自我认知报告 v{awareness['version']}",
                "content": (
                    f"自我认知报告 v{awareness['version']}\n"
                    f"结构: {summary['total_files']} 文件, {summary['total_lines']} 行代码, "
                    f"{summary['total_classes']} 个类, {summary['total_functions']} 个函数\n"
                    f"能力数: {len(awareness['capabilities'])}\n"
                    f"改进次数: {awareness['modification_stats']['succeeded']}/"
                    f"{awareness['modification_stats']['attempted']}\n"
                    f"最近改进: {', '.join(h['what'][:40] for h in recent_fixes) if recent_fixes else '无'}\n"
                    f"当前目标: {awareness['active_focus']}"
                ),
                "category": "项目自身",
                "importance": 0.95,
                "keywords": ["自我认知", "系统状态", "能力清单"],
                "source": "self_thinking",
            })
        except Exception as e:
            print(f"  ⚠️ 自我认知入KB失败: {e}")

    def _verify_past_improvements(self) -> List[Dict]:
        """
        验证过去的改进是否仍然有效
        检查已修复的文件是否真的不再有同样的问题
        """
        import ast
        awareness_file = self.data_dir / "self_awareness.json"
        if not awareness_file.exists():
            return []

        try:
            awareness = json.loads(awareness_file.read_text(encoding="utf-8"))
        except Exception:
            return []

        history = awareness.get("improvement_history", [])
        verifications = []

        # 检查最近的 bare except 修复是否仍然有效
        for entry in history[-10:]:
            what = entry.get("what", "")
            file = entry.get("file", "")
            if not file or "bare except" not in what.lower():
                continue

            py_path = Path(file)
            if not py_path.exists():
                verifications.append({
                    "file": file,
                    "fix": "bare_except",
                    "still_fixed": False,
                    "note": "文件已不存在",
                })
                continue

            try:
                tree = ast.parse(py_path.read_text(encoding="utf-8"))
                bare_found = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        for handler in node.handlers:
                            if handler.type is None:
                                bare_found = True
                verifications.append({
                    "file": file,
                    "fix": "bare_except",
                    "still_fixed": not bare_found,
                    "note": "修复仍然有效" if not bare_found else "裸 except 再次出现!",
                })
            except Exception as e:
                verifications.append({
                    "file": file,
                    "fix": "bare_except",
                    "still_fixed": False,
                    "note": f"验证失败: {e}",
                })

        # 输出验证结果
        if verifications:
            print(f"\n  {'─'*40}")
            print(f"  🔍 改进验证 ({len(verifications)} 项)")
            for v in verifications:
                status = "✅" if v["still_fixed"] else "❌"
                print(f"  {status} {v['file']}: {v['note']}")
            print(f"  {'─'*40}")

        return verifications

    def _prioritize_questions(self, questions: List) -> List:
        """
        6 因子加权评分：对好奇心问题重新排序。

        final_score = 0.25 * base_importance
                     + 0.20 * experience_factor
                     + 0.20 * goal_alignment
                     + 0.15 * knowledge_gap_severity
                     + 0.10 * metacognitive_urgency
                     + 0.10 * behavior_bias

        behavior_bias 来自行为反馈层：成功方向 +0.3, 失败方向 -0.3
        """
        if not questions:
            return questions

        profile = getattr(self, "_self_profile", {})

        # 1. 策略历史成功率
        strat_effect = profile.get("strategy_effectiveness", {})

        # 2. 目标优先级
        goal_prio = {}
        try:
            from goal_planner import GoalPlanner
            gp = GoalPlanner()
            goal_prio = gp.get_goal_priorities()
        except Exception:
            pass

        # 3. 知识领域强度
        kb_domains = profile.get("knowledge_domains", {})

        # 4. 元认知状态
        confidence = profile.get("confidence", 0.5)
        trends = profile.get("recent_trends", {})

        scored = []
        for q in questions:
            # base_importance (0.25)
            base = q.importance

            # experience_factor (0.20)
            exp = 0.5
            action = q.explore_action
            if action in strat_effect:
                exp = strat_effect[action] / 100.0
            elif action in ("read_file", "check_state"):
                exp = 0.7
            elif action in ("self_heal", "global_research"):
                exp = 0.6

            # behavior_bias (0.10) — 基于历史行为的方向偏好
            behavior_bias = self._behavior_feedback.get_bias(
                action_type=action, target=q.target or "") if hasattr(self, '_behavior_feedback') else 0.0

            # strategy_weight (参考值，暂不计入总分) — 策略学习引擎
            strategy_weight = 0.0
            if hasattr(self, '_strategy_learner') and self._strategy_learner is not None:
                cycle = getattr(self, '_cycle_count', 0)
                strategy_weight = self._strategy_learner.get_strategy_weight(
                    action_type=action, target=q.target or "", current_cycle=cycle)
            if strategy_weight != 0.0 and hasattr(q, 'context') and isinstance(q.context, dict):
                q.context['strategy_weight'] = strategy_weight

            # 技能加分：匹配已知技能的问题提升经验因子
            try:
                from skill_crystallizer import SkillCrystallizer
                sb = SkillCrystallizer().get_skill_boost(action, q.target or "")
                exp = min(1.0, exp + sb)
            except Exception:
                pass

            # goal_alignment (0.20)
            align = 0.0
            for cat, info in goal_prio.items():
                if isinstance(info, dict):
                    prio_val = info.get("priority", 0)
                else:
                    prio_val = info
                # 检查问题的操作类型是否匹配目标类别
                if ((cat == "knowledge" and action in ("add_crawler_task", "global_research", "deep_learning"))
                        or (cat == "code_quality" and action in ("self_heal", "check_state"))
                        or (cat == "architecture" and action in ("read_file", "compare_files"))):
                    align = max(align, prio_val)
                # 检查 target 是否含类别关键词
                target = (q.target or "").lower()
                if cat.lower() in target:
                    align = max(align, prio_val)

            # knowledge_gap_severity (0.15)
            gap = 0.3
            if q.target and kb_domains:
                for domain, strength in kb_domains.items():
                    if domain.lower() in q.target.lower():
                        gap = 1.0 - strength
                        break
            # 如果问题是知识缺口类型的，gap 更高
            if action in ("add_crawler_task", "global_research", "deep_learning"):
                gap = max(gap, 0.6)

            # metacognitive_urgency (0.10)
            meta = 0.3
            if confidence < 0.4:
                # 低置信度：偏安全操作
                if action in ("read_file", "check_state", "list_new_entries"):
                    meta = 0.8
                elif action in ("self_heal", "global_research"):
                    meta = 0.5
            if trends.get("loop") == "worsening":
                # 循环恶化：偏新颖操作
                if action not in ("read_file", "check_state"):
                    meta = max(meta, 0.6)
            elif trends.get("stagnation") == "worsening":
                # 停滞：偏探索操作
                if action in ("add_crawler_task", "global_research"):
                    meta = max(meta, 0.7)

            final = (
                0.25 * base
                + 0.20 * exp
                + 0.20 * align
                + 0.15 * gap
                + 0.10 * meta
                + 0.20 * behavior_bias
            )
            scored.append((final, q))

        scored.sort(key=lambda x: -x[0])
        return [q for _, q in scored]

    def _apply_study_actions(self, learned: List[Dict]) -> List:
        """
        对学习的内容生成行动：扫描实际代码找问题，触发修复或探索
        返回好奇心问题列表
        """
        from curiosity_engine import CuriosityQuestion
        questions = []
        import ast

        # 扫描实际项目代码找常见问题
        code_issues = {"bare_excepts": [], "no_docstrings": [], "long_functions": []}
        for py_file in Path.cwd().glob("*.py"):
            try:
                code = py_file.read_text(encoding="utf-8")
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        for handler in node.handlers:
                            if handler.type is None:
                                code_issues["bare_excepts"].append(py_file.name)
                    if isinstance(node, ast.FunctionDef):
                        if not ast.get_docstring(node):
                            if len(node.body) > 5:
                                code_issues["no_docstrings"].append(
                                    f"{py_file.name}:{node.name}"
                                )
            except Exception:
                continue

        # 将发现的代码问题转为好奇行动
        if code_issues["bare_excepts"]:
            unique_files = sorted(set(code_issues["bare_excepts"]))[:3]
            questions.append(CuriosityQuestion(
                observation=f"发现 {len(code_issues['bare_excepts'])} 处裸 except",
                question=f"有文件用了裸 except: {', '.join(unique_files)}，要不要修复？",
                importance=0.9,
                explore_action="self_heal",
                target=",".join(unique_files),
                context={"source": "code_scan", "type": "bare_except"}
            ))

        if code_issues["no_docstrings"]:
            files_with_issues = sorted(set(f.split(":")[0] for f in code_issues["no_docstrings"]))[:3]
            questions.append(CuriosityQuestion(
                observation=f"发现 {len(code_issues['no_docstrings'])} 个函数缺少文档",
                question=f"函数缺少文档: {', '.join(code_issues['no_docstrings'][:3])}，要补充吗？",
                importance=0.7,
                explore_action="self_heal",
                target=",".join(files_with_issues),
                context={
                    "source": "code_scan",
                    "type": "missing_doc",
                    "functions": code_issues["no_docstrings"][:5]
                }
            ))

        # 每轮至少生成一个探索问题（基于学习内容）
        if not questions and learned:
            entries_with_content = [l for l in learned if l.get("content")]
            if entries_with_content:
                entry = entries_with_content[0]
                questions.append(CuriosityQuestion(
                    observation=f"学习了新内容: {entry['topic'][:60]}",
                    question=f"刚学了 '{entry['topic'][:60]}'，对项目代码有启发吗？",
                    importance=entry.get("importance", 0.5),
                    explore_action="read_file",
                    target=self._find_target_file(entry["topic"]),
                    context={"source": "study_action", "topic": entry["topic"]}
                ))

        return questions

    def _generate_questions_from_study(self, learned: List[Dict]) -> List:
        """
        从学习的内容生成新的好奇心问题，让学到的知识驱动进一步探索
        """
        from curiosity_engine import CuriosityQuestion
        questions = []

        for entry in learned:
            topic = entry.get("topic", "")
            content = entry.get("content", "")
            importance = entry.get("importance", 0.5)
            key_concepts = entry.get("key_concepts", [])[:3]
            category = entry.get("category", "")

            # 1. 学到项目自身相关内容 → 检查对应代码文件
            if category == "项目自身":
                target_file = self._find_target_file(topic)
                if target_file:
                    questions.append(CuriosityQuestion(
                        observation=f"学习了项目自身知识: {topic[:60]}",
                        question=f"学习了 '{topic[:60]}'，检查这部分代码还有优化空间吗？",
                        importance=round(importance, 2),
                        explore_action="read_file",
                        target=target_file,
                        context={"source": "study_question", "category": category}
                    ))

            # 2. 学到新技术概念且重要性较高 → 深入搜索
            elif key_concepts and importance >= 0.6:
                domain = key_concepts[0]
                questions.append(CuriosityQuestion(
                    observation=f"学到新概念: {topic[:50]}",
                    question=f"'{topic[:60]}' 评分 {importance}，搜索更多关于 {domain} 的资料？",
                    importance=round(importance, 2),
                    explore_action="add_crawler_task",
                    target=topic[:60],
                    context={
                        "domain": domain,
                        "missing": [topic[:60]],
                        "source": "study_question",
                    }
                ))

            # 3. 条目内容较长/较重要 → 全球研究
            if len(content) > 300 and importance >= 0.7:
                questions.append(CuriosityQuestion(
                    observation=f"发现高质量知识: {topic[:50]}",
                    question=f"'{topic[:60]}' 内容质量很高，做全球深度研究？",
                    importance=round(importance + 0.1, 2),
                    explore_action="global_research",
                    target=topic[:60],
                    context={
                        "research_queries": [topic[:80], f"{topic[:60]} tutorial", f"{topic[:60]} best practices"],
                        "source": "study_question",
                    }
                ))

        return questions

    def _find_target_file(self, topic: str) -> str:
        """从学习 topic 推断对应的项目文件，找不到返回空字符串"""
        for py_file in Path.cwd().glob("*.py"):
            if py_file.stem in topic:
                return str(py_file)
        return ""

    def _log_study_actions(self, learned: List[Dict], questions: List):
        """记录学习触发的行动到 thinking_log"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "study_actions",
            "learned_count": len(learned),
            "actions_generated": len(questions),
            "actions": [
                {"observation": q.observation[:100], "action": q.explore_action, "target": q.target}
                for q in questions
            ] if questions else [],
            "learned_topics": [l["topic"][:60] for l in learned] if learned else [],
        }
        self.data_dir.mkdir(exist_ok=True)
        log_file = self.data_dir / "self_thinking_log.json"
        try:
            existing = []
            if log_file.exists():
                with open(log_file, encoding="utf-8") as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _generate_questions(self):
        """从扫描数据生成好奇心问题，跳过已发现的知识缺口"""
        # 加载缺口追踪器
        gap_tracker = self.data_dir / "gap_tracker.json"
        known_gaps = set()
        if gap_tracker.exists():
            try:
                data = json.loads(gap_tracker.read_text(encoding="utf-8"))
                known_gaps = set(data.get("gaps", []))
            except Exception:
                pass

        # 传入当前策略上下文（可选，不影响现有调用）
        strategy_context = {}
        if hasattr(self, '_strategy_manager') and self._strategy_manager:
            strategy_context = self._strategy_manager.get_question_filter()
        all_questions = self.curiosity.generate_questions(
            self.snapshot, self.diff, strategy_context=strategy_context)

        # 过滤已发现的缺口
        filtered = []
        for q in all_questions:
            if q.explore_action == "add_crawler_task":
                gap_key = q.target
                if gap_key in known_gaps:
                    continue
                known_gaps.add(gap_key)
            filtered.append(q)

        # 行为反馈过滤：长期失败的方向转为诊断修复，不直接跳过
        if not hasattr(self, '_diagnosed_actions'):
            self._diagnosed_actions: set = set()
        if hasattr(self, '_behavior_feedback') and len(self._behavior_feedback.records) >= 5:
            bias_filtered = []
            skip_counts: Dict[str, int] = {}
            for q in filtered:
                bias = self._behavior_feedback.get_bias(
                    action_type=q.explore_action, target=q.target or "")
                if bias <= -0.2:
                    action = q.explore_action
                    skip_counts[action] = skip_counts.get(action, 0) + 1
                    # 首次失败：生成诊断问题，不直接跳过
                    if action not in self._diagnosed_actions:
                        self._diagnosed_actions.add(action)
                        from curiosity_engine import CuriosityQuestion
                        recent = self._behavior_feedback.get_recent(20)
                        errors = [r.get("detail", "") for r in recent
                                  if r.get("action_type") == action and r.get("result") == "failure"]
                        error_sample = "; ".join(e for e in errors[:3] if e)[:150]
                        diag_q = CuriosityQuestion(
                            observation=f"行为反馈显示 '{action}' 操作反复失败",
                            question=f"搜索解决方案: '{action}' 操作反复失败，错误: {error_sample}",
                            importance=0.85,
                            explore_action="web_research",
                            target=f"修复 {action} 失败 {error_sample}",
                            reason=f"行为反馈全网诊断: {action} 连续失败",
                        )
                        bias_filtered.insert(0, diag_q)  # 诊断放最前面优先处理
                        skip_counts[action] = skip_counts.get(action, 0) - 1  # 不算跳过，算诊断
                    continue
                bias_filtered.append(q)
            if skip_counts:
                # 真正跳过的 = 已经是重复失败且已诊断过的
                real_skip = {k: v for k, v in skip_counts.items() if v > 0}
                new_diag = [k for k, v in skip_counts.items()
                           if k in self._diagnosed_actions and v <= 0]
                parts = []
                if real_skip:
                    parts.append(f"跳过 {sum(real_skip.values())} 个")
                if new_diag:
                    parts.append(f"诊断 {len(new_diag)} 个方向")
                if parts:
                    print(f"  🧠 行为反馈: {'，'.join(parts)}")
            filtered = bias_filtered

        # ── 每轮代码质量扫描：生成自修复问题 ──
        # 不依赖 learned 是否为空，确保 self_heal 问题每轮都有机会出现
        try:
            import ast
            code_issues = {"bare_excepts": [], "no_module_doc": []}
            for py_file in Path.cwd().glob("*.py"):
                code = py_file.read_text(encoding="utf-8")
                tree = ast.parse(code)
                # 裸 except 扫描
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        for handler in node.handlers:
                            if handler.type is None:
                                code_issues["bare_excepts"].append(py_file.name)
                # 模块级文档扫描（与 add_module_docstring 匹配）
                if not ast.get_docstring(tree):
                    code_issues["no_module_doc"].append(py_file.name)
            from curiosity_engine import CuriosityQuestion
            if code_issues["bare_excepts"]:
                uf = sorted(set(code_issues["bare_excepts"]))[:3]
                filtered.append(CuriosityQuestion(
                    observation=f"发现 {len(code_issues['bare_excepts'])} 处裸 except",
                    question=f"有文件用了裸 except: {', '.join(uf)}，修吗？",
                    importance=0.9, explore_action="self_heal",
                    target=",".join(uf),
                    context={"source": "code_scan", "type": "bare_except"}))
            if code_issues["no_module_doc"]:
                ff = code_issues["no_module_doc"][:3]
                filtered.append(CuriosityQuestion(
                    observation=f"发现 {len(code_issues['no_module_doc'])} 个文件缺模块文档",
                    question=f"模块缺文档: {', '.join(ff)}，补吗？",
                    importance=0.7, explore_action="self_heal",
                    target=",".join(ff),
                    context={"source": "code_scan", "type": "missing_doc"}))
        except Exception:
            pass  # 代码扫描失败不影响主流程

        # ── 每轮代码质量扩展扫描：长函数检测 ──
        try:
            import ast as _ast2
            code_issues_long = []
            for py_file in Path.cwd().glob("*.py"):
                code = py_file.read_text(encoding="utf-8")
                tree = _ast2.parse(code)
                for node in _ast2.walk(tree):
                    if isinstance(node, (_ast2.FunctionDef, _ast2.AsyncFunctionDef)):
                        start = node.lineno
                        end = getattr(node, 'end_lineno', start)
                        body_lines = end - start
                        if body_lines > 100:
                            code_issues_long.append(f"{py_file.name}:{node.name}({body_lines}行)")
            if code_issues_long:
                from curiosity_engine import CuriosityQuestion
                # 最多报5个
                long_samples = code_issues_long[:5]
                filtered.append(CuriosityQuestion(
                    observation=f"发现 {len(code_issues_long)} 个超长函数(>100行)",
                    question=f"超长函数: {', '.join(long_samples[:3])}，需要拆分重构吗？",
                    importance=0.65,
                    explore_action="read_file",
                    target=long_samples[0].split(":")[0],
                    context={"source": "code_scan", "type": "long_function", "functions": long_samples},
                ))
        except Exception:
            pass

        # ── 问题去重：同一(操作,目标)不无限循环 ──
        seen_file = self.data_dir / "seen_questions.json"
        dedup_limits = {
            "deep_learning": 30,    # 30轮内不重复问同一个KB条目
            "global_research": 20,  # 20轮内不重复研究
        }
        try:
            seen_data = {} if not seen_file.exists() else json.loads(
                seen_file.read_text(encoding="utf-8"))
            cycle = getattr(self, '_cycle_count', 0)

            deduped = []
            for q in filtered:
                limit = dedup_limits.get(q.explore_action, 0)
                if limit > 0:
                    key = f"{q.explore_action}:{q.target}"
                    last_seen = seen_data.get(key, -limit)
                    if cycle - last_seen < limit:
                        continue  # 冷却期内，跳过
                deduped.append(q)

            # 记录本轮选中问题
            for q in deduped:
                limit = dedup_limits.get(q.explore_action, 0)
                if limit > 0:
                    key = f"{q.explore_action}:{q.target}"
                    seen_data[key] = cycle

            seen_file.write_text(json.dumps(seen_data, ensure_ascii=False), encoding="utf-8")
            filtered = deduped
        except Exception:
            pass

        self.questions = filtered

        # 保存缺口追踪
        gap_tracker.write_text(json.dumps({
            "gaps": list(known_gaps),
            "updated": datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2))

    # ---- 探索方法 ----

    def _explore_question(self, q) -> Dict[str, Any]:
        """根据问题类型执行探索"""
        action = q.explore_action
        target = q.target

        # 经验记忆守卫：同一问题+策略失败 >= 3 次则跳过
        et = self._get_experience_tracker()
        problem = target or q.question[:80]
        if et.should_retry(problem, action, max_failures=3):
            alt_strategies = et.get_successful_strategies(problem)
            if alt_strategies:
                print(f"  ⏭️ '{problem[:40]}' 的 '{action}' 已失败多次，尝试替代策略: {alt_strategies[0]}")
                action = alt_strategies[0]
            else:
                print(f"  ⏭️ '{problem[:40]}' 的 '{action}' 已失败多次，跳过")
                return {"note": f"经验记忆跳过: {action} 对 {problem} 已失败 3+ 次"}

        if action == "read_file":
            return self._explore_read_file(target)
        elif action == "compare_files":
            files = target.split(",")
            if len(files) == 2:
                return self._explore_compare_files(files[0], files[1])
            return {"error": "need 2 files for comparison"}
        elif action == "add_crawler_task":
            if not self._check_feature("network_crawler"):
                return {"note": f"network_crawler 已禁用，跳过: {target}"}
            return self._explore_check_gap(q)
        elif action == "check_state":
            return self._explore_check_state(target)
        elif action == "list_new_entries":
            return self._explore_list_new_entries(q)
        elif action == "global_research":
            if not self._check_feature("global_research"):
                return {"note": f"global_research 已禁用，跳过: {target}"}
            return self._explore_global_research(q)
        elif action == "web_research":
            # 自主多源研究：替换原来的爬虫队列模式
            return self._explore_web_research(q)
        elif action == "self_heal":
            if not self._check_feature("self_modification"):
                return {"note": f"self_modification 已禁用，跳过修复: {target}"}
            return self._explore_self_heal(q)
        elif action == "code_quality_heal":
            if not self._check_feature("self_modification"):
                return {"note": f"self_modification 已禁用，跳过质量修复: {target}"}
            return self._explore_self_heal(q)
        elif action == "deep_learning":
            return self._explore_deep_learning(q)
        elif action == "llm_analysis":
            if not self._check_feature("local_thinking"):
                return {"note": f"local_thinking 已禁用，跳过 LLM 分析: {target}"}
            return self._explore_llm_analysis(q)
        else:
            return {"note": f"未知探索动作: {action}"}

    def _explore_read_file(self, filepath: str) -> Dict[str, Any]:
        """读取文件，提取结构信息"""
        full_path = Path(filepath)
        if not full_path.exists():
            full_path = Path.cwd() / filepath
        if not full_path.exists():
            return {"error": f"文件不存在: {filepath}"}

        try:
            import ast
            code = full_path.read_text(encoding="utf-8")
            tree = ast.parse(code)

            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({"name": node.name, "methods": methods})

            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            imports = []
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    imports.extend(a.name for a in n.names)
                elif isinstance(n, ast.ImportFrom):
                    if n.module:
                        imports.append(n.module)

            # 提取模块文档
            docstring = ast.get_docstring(tree) or ""

            top_imports = sorted(set(i.split(".")[0] for i in imports))
            return {
                "file": filepath,
                "lines": len(code.splitlines()),
                "classes": classes,
                "top_functions": funcs[:10],
                "function_count": len(funcs),
                "imports": top_imports,
                "import_count": len(top_imports),
                "docstring": docstring[:200] if docstring else "(无模块文档)",
                "has_main": any(
                    isinstance(n, ast.If) and
                    isinstance(n.test, ast.Compare) and
                    isinstance(n.test.left, ast.Name) and
                    n.test.left.id == "__name__"
                    for n in ast.walk(tree)
                ),
            }
        except SyntaxError as e:
            return {"error": f"语法错误: {e}"}

    def _explore_compare_files(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """对比两个文件的结构"""
        info_a = self._explore_read_file(file_a)
        info_b = self._explore_read_file(file_b)

        if "error" in info_a or "error" in info_b:
            return {"error": "无法比较"}

        imports_a = set(info_a.get("imports", []))
        imports_b = set(info_b.get("imports", []))

        overlap = imports_a & imports_b
        jaccard = len(overlap) / max(1, len(imports_a | imports_b))

        return {
            "file_a": file_a,
            "file_b": file_b,
            "import_overlap": list(overlap),
            "jaccard_similarity": round(jaccard, 2),
            "classes_a": len(info_a.get("classes", [])),
            "classes_b": len(info_b.get("classes", [])),
            "conclusion": "可能重复" if jaccard > 0.6 else "不太可能重复",
        }

    def _explore_check_gap(self, q) -> Dict[str, Any]:
        """检查知识缺口详情"""
        ctx = q.context
        domain = ctx.get("domain", q.target)
        missing = ctx.get("missing", [])

        return {
            "domain": domain,
            "missing_topics": missing,
            "gap_count": len(missing),
            "suggested_queries": [f"{t} 教程" if "基础" in t or "入门" in t else t
                                  for t in missing[:5]],
        }

    def _explore_check_state(self, target: str) -> Dict[str, Any]:
        """检查系统状态"""
        try:
            from system_state_manager import SystemStateManager
            sm = SystemStateManager()
            return {"state": sm.get_global_state()}
        except Exception as e:
            return {"error": str(e)}

    def _explore_list_new_entries(self, q) -> Dict[str, Any]:
        """列出新条目/待探索模块"""
        ctx = q.context
        undocumented = ctx.get("undocumented", [])
        if undocumented:
            return {
                "type": "undocumented_modules",
                "modules": undocumented,
                "count": len(undocumented),
            }
        kb_data = self.snapshot.get("knowledge_base", {})
        return {
            "type": "kb_summary",
            "categories": kb_data.get("category_breakdown", {}),
        }

    def _explore_web_research(self, q) -> Dict[str, Any]:
        """自主多源研究：即时搜索+读内容+综合答案"""
        target = q.target or q.question
        print(f"  🔬 自主研究: \"{target[:80]}\"")
        try:
            ri = self._get_research_integration()
            result = ri.execute_research(target)
            return result
        except Exception as e:
            print(f"  ⚠️ 研究失败: {e}")
            return {
                "observation": getattr(q, 'observation', ''),
                "question": q.question,
                "summary": f"研究执行异常: {e}",
                "action_taken": "web_research_error",
            }
        """全球研究：调爬虫和持续学习系统搜索全球资料"""
        ctx = q.context
        queries = ctx.get("research_queries", [])
        results = []

        print(f"   🌐 全球研究: 发起 {len(queries)} 个搜索查询")

        # 1. 添加爬虫任务到队列
        task_file = self.data_dir / "crawler_tasks.json"
        existing_tasks = []
        if task_file.exists():
            with open(task_file, encoding="utf-8") as f:
                existing_tasks = json.load(f)
        existing_queries = {t.get("query", "") for t in existing_tasks}

        added = 0
        for query in queries:
            if query not in existing_queries:
                existing_tasks.append({
                    "query": query,
                    "domain": "自思考架构研究",
                    "reason": f"好奇心引擎全球研究: {q.question[:80]}",
                    "priority": "high",
                })
                existing_queries.add(query)
                added += 1

        if added > 0:
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(existing_tasks, f, ensure_ascii=False, indent=2)

        # 2. 同时尝试直接调爬虫实时获取
        try:
            from ai_knowledge_crawler import AIKnowledgeCrawler
            crawler = AIKnowledgeCrawler()
            # 用前3个查询搜索GitHub（最重要的）
            for query in queries[:3]:
                try:
                    search_term = query.replace(" ", "+")
                    url = f"https://api.github.com/search/repositories?q={search_term}&sort=stars&per_page=3"
                    req = urllib.request.Request(url, headers={
                        "User-Agent": "Mozilla/5.0 (compatible; SelfThinkingBot/1.0)"
                    })
                    with urllib.request.urlopen(req, timeout=10, context=ssl._create_unverified_context()) as resp:
                        data = json.loads(resp.read().decode())
                        for repo in data.get("items", [])[:3]:
                            results.append({
                                "title": repo["full_name"],
                                "description": (repo.get("description") or "")[:200],
                                "stars": repo.get("stargazers_count", 0),
                                "url": repo["html_url"],
                                "source": "GitHub",
                            })
                    time.sleep(1)
                except Exception as e:
                    print(f"   ⚠️  搜索 '{query}' 失败: {e}")
        except Exception as e:
            print(f"   ⚠️  实时搜索异常: {e}")

        # 3. 尝试arXiv搜索
        try:
            for query in queries[:2]:
                try:
                    url = f"http://export.arxiv.org/api/query?search_query=all:{query.replace(' ', '+')}&sortBy=relevance&max_results=3"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=15, context=ssl._create_unverified_context()) as resp:
                        xml = resp.read().decode("utf-8")
                        import re as re_mod
                        titles = re_mod.findall(r"<title>(.*?)</title>", xml, re_mod.DOTALL)
                        for i, t in enumerate(titles[1:4], 1):
                            results.append({
                                "title": t.strip().replace("\n", " ")[:150],
                                "description": f"arXiv论文: {query}",
                                "stars": 0,
                                "url": f"https://arxiv.org/search/?query={query}",
                                "source": "arXiv",
                            })
                    time.sleep(3)
                except Exception:
                    pass
        except Exception:
            pass

        return {
            "research_topic": q.target,
            "queries_scheduled": len(queries),
            "crawler_tasks_added": added,
            "real_time_results": len(results),
            "sample_results": results[:5],
            "note": f"已添加 {added} 个爬虫任务，实时获取 {len(results)} 条结果。更多结果将在后台爬取。"
        }

    # ---- 自我修复探索 ----

    def _explore_self_heal(self, q) -> Dict[str, Any]:
        """探索并尝试修复代码问题"""
        from self_modification_engine import SelfModificationEngine
        engine = SelfModificationEngine()

        # 应用 feature flag 守卫到 sub_gates
        engine.configure_sub_gates(
            allow_bare_except_fix=self._check_feature("modification_bare_except"),
            allow_docstring_add=self._check_feature("modification_docstring"),
            allow_unused_import_remove=self._check_feature("modification_unused_import"),
            allow_destructive_change=self._check_feature("modification_destructive"),
        )

        fix_results = []
        ctx = q.context or {}
        fix_type = ctx.get("type", "bare_except")
        files = [f.strip() for f in q.target.split(",") if f.strip()]

        if fix_type == "bare_except":
            for file in files:
                result = engine.fix_bare_excepts(file)
                fix_results.append({
                    "type": "fix_bare_except",
                    "file": file,
                    "success": result.get("success", False),
                    "detail": result.get("error", "已修复"),
                    "error_kind": result.get("error_kind", ""),
                })

        elif fix_type == "missing_doc":
            for file in files:
                module_name = Path(file).stem
                result = engine.add_module_docstring(file, f"{module_name} module")
                fix_results.append({
                    "type": "add_docstring",
                    "file": file,
                    "success": result.get("success", False),
                    "detail": result.get("error", "已修复"),
                    "error_kind": result.get("error_kind", ""),
                })

        if not fix_results:
            fix_results.append({
                "type": "inspection",
                "file": q.target,
                "success": False,
                "detail": "未找到可自动修复的问题",
            })

        return {
            "target": q.target,
            "fixes_attempted": len(fix_results),
            "fixes_succeeded": sum(1 for r in fix_results if r["success"]),
            "fix_results": fix_results,
        }

    def _explore_deep_learning(self, q) -> Dict[str, Any]:
        """
        deep_learning 探索动作——原为无效的死代码路径。
        现在路由到能力差距分析：检查 KB 能力参考与该问题的目标主题，
        返回差距分析结果。
        """
        if not self._check_feature("capability_learning"):
            return {"note": f"capability_learning 已禁用，跳过: {q.target}"}

        target = q.target or q.question[:60]
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        refs = kb.get_knowledge_by_category("能力参考")
        target_refs = [r for r in refs
                       if target.lower() in r.get("topic", "").lower()] if refs else []

        analyzer = self._get_gap_analyzer()
        registry = self._get_capability_registry()
        missing = analyzer.find_missing_capabilities(target_refs or refs)

        return {
            "observation": q.observation,
            "question": q.question,
            "topic": target[:100],
            "summary": f"能力深度探索 [{target[:50]}]: 发现 {len(missing)} 个潜在能力差距",
            "missing_capabilities": [m.topic for m in missing[:5]],
            "action_taken": "deep_learning",
        }

    # ---- 洞察生成与存储 ----

    def _generate_insight(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从探索结果生成洞察"""
        if "error" in exploration:
            return {
                "observation": q.observation,
                "question": q.question,
                "summary": f"探索失败: {exploration['error']}",
                "action_taken": "error",
                "exploration": exploration,
            }

        if q.explore_action == "read_file":
            return self._insight_from_file(q, exploration)
        elif q.explore_action == "compare_files":
            return self._insight_from_comparison(q, exploration)
        elif q.explore_action == "add_crawler_task":
            return self._insight_from_gap(q, exploration)
        elif q.explore_action == "global_research":
            return self._insight_from_global_research(q, exploration)
        elif q.explore_action in ("self_heal", "code_quality_heal"):
            return self._insight_from_self_heal(q, exploration)
        elif q.explore_action == "deep_learning":
            return self._insight_from_deep_learning(q, exploration)
        else:
            return {
                "observation": q.observation,
                "question": q.question,
                "summary": f"探索 {q.target} 完成",
                "exploration": exploration,
            }

    def _insight_from_file(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从文件探索生成洞察"""
        file = exploration.get("file", q.target)
        classes = exploration.get("classes", [])
        funcs = exploration.get("top_functions", [])
        imports = exploration.get("imports", [])
        doc = exploration.get("docstring", "")
        lines = exploration.get("lines", 0)

        # 根据代码结构自动生成摘要
        parts = []
        if classes:
            class_desc = ", ".join(f"{c['name']}({len(c['methods'])}方法)" for c in classes[:5])
            parts.append(f"定义了 {len(classes)} 个类: {class_desc}")
        if funcs:
            parts.append(f"包含 {exploration.get('function_count', 0)} 个函数")
        if imports:
            parts.append(f"依赖 {exploration.get('import_count', 0)} 个外部模块")

        primary_purpose = doc[:100] if doc and doc != "(无模块文档)" else "模块文档缺失"
        summary = f"{file} ({lines}行): {primary_purpose}。{'; '.join(parts)}。"

        # 模块文档缺失本身也是一个发现
        findings = []
        if doc == "(无模块文档)":
            findings.append("模块级文档缺失")

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"{file.replace('.py', '')} 模块分析",
            "category": "项目自身",
            "content": f"{summary}\n\n结构:\n- 类: {json.dumps(classes, ensure_ascii=False)}\n- 主要函数: {funcs}\n- imports: {imports}",
            "keywords": [file.replace(".py", ""), "模块分析"] + \
                        ([c["name"] for c in classes[:3]] if classes else []),
            "findings": findings,
            "origin": "self_thinking",
        }

    def _explore_llm_analysis(self, q) -> Dict[str, Any]:
        """LLM 深度分析：调用本地模型分析代码问题"""
        try:
            from llm_client import get_llm_client
            from llm_prompts import get_prompt
        except ImportError:
            return {"note": "LLM 模块未安装，跳过分析"}

        client = get_llm_client()
        if not client.is_available():
            return {"note": "LLM 不可用，跳过分析"}

        target = getattr(q, 'target', '') or getattr(q, 'filepath', '') or ''
        context = ""
        if target and Path(target).exists():
            lines = Path(target).read_text(encoding="utf-8").split("\n")
            context = "\n".join(lines[:30])

        prompt = get_prompt(
            "llm_analysis",
            question=getattr(q, 'question', '代码分析'),
            target=target or '未知',
            context=context or '无',
        )
        result = client.chat("你是一个代码分析助手。保持简洁。", prompt)

        if not result.success:
            return {"note": f"LLM 分析失败: {result.error}"}

        return {
            "observation": getattr(q, 'observation', ''),
            "question": getattr(q, 'question', ''),
            "summary": result.content[:200],
            "topic": f"LLM 分析: {target or '通用'}",
            "category": "llm_analysis",
            "content": result.content,
            "keywords": ["llm", target.replace('.py', '')] if target else ["llm"],
            "origin": "self_thinking",
        }

    def _insight_from_comparison(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        s = exploration.get("jaccard_similarity", 0)
        a = exploration.get("file_a", "")
        b = exploration.get("file_b", "")
        conclusion = exploration.get("conclusion", "")

        summary = f"对比 {a} 和 {b}: import 相似度 {s:.0%}，{conclusion}。"

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"{a} vs {b} 相似度分析",
            "category": "项目自身",
            "content": summary,
            "keywords": [a.replace(".py", ""), b.replace(".py", ""), "相似度分析"],
            "findings": [],
            "origin": "self_thinking",
        }

    def _insight_from_gap(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        domain = exploration.get("domain", q.target)
        missing = exploration.get("missing_topics", [])

        summary = f"发现知识缺口: {domain} 领域缺 {len(missing)} 个子话题，已生成爬虫任务。"

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"知识缺口: {domain}",
            "category": "项目自身",
            "content": f"领域 {domain} 缺少以下知识: {', '.join(missing)}。已生成定向爬虫任务。",
            "keywords": [domain, "知识缺口"],
            "findings": [f"缺失 {len(missing)} 个话题"],
            "origin": "self_thinking",
            "action_taken": "add_crawler_tasks",
        }

    def _insight_from_global_research(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从全球研究生成洞察"""
        topic = exploration.get("research_topic", "global")
        results = exploration.get("sample_results", [])
        tasks = exploration.get("crawler_tasks_added", 0)
        realtime = exploration.get("real_time_results", 0)

        # 从实时结果提炼要点
        top_results = ""
        for r in results[:3]:
            top_results += f"- [{r['source']}] {r['title']} ({r.get('stars', 0)}⭐) {r.get('description', '')[:80]}\n"

        summary = f"全球研究 [{topic}]: 已调度 {tasks} 个爬虫任务"
        if results:
            summary += f"，实时获取 {len(results)} 条结果\n{top_results[:200]}"

        content = (
            f"好奇心驱动全球研究: {q.question}\n\n"
            f"搜索查询:\n"
            + "\n".join(f"- {qq}" for qq in q.context.get("research_queries", []))
            + f"\n\n实时结果:\n{top_results}"
            + f"\n爬虫将持续在后台上获取更多资料。"
        )

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"全球研究: {topic}",
            "category": "项目自身",
            "content": content,
            "keywords": [topic, "全球研究", "架构探索"],
            "findings": [f"调度了 {tasks} 个爬虫任务", f"实时获取 {realtime} 条结果"],
            "origin": "self_thinking",
            "action_taken": "global_research",
        }

    def _insight_from_self_heal(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从自我修复探索生成洞察"""
        target = exploration.get("target", q.target)
        attempted = exploration.get("fixes_attempted", 0)
        succeeded = exploration.get("fixes_succeeded", 0)
        fix_results = exploration.get("fix_results", [])

        detail_lines = []
        for fix in fix_results:
            status = "✅" if fix["success"] else "❌"
            detail_lines.append(f"  {status} [{fix['type']}] {fix['file']}: {fix['detail']}")

        summary = f"自我修复 [{target}]: 尝试 {attempted} 项修复，成功 {succeeded} 项\n" + "\n".join(detail_lines)

        # 构建 findings：保留修复统计 + 附加问题关键词（供 daemon._apply_heals 匹配）
        base_finding = f"修复 {succeeded}/{attempted} 项" if attempted > 0 else "无需修复"
        issue_keywords = []
        if "裸 except" in q.question or "bare except" in q.question.lower():
            issue_keywords.append("裸 except")
        if "文档" in q.question or "docstring" in q.question.lower():
            issue_keywords.append("文档缺失")
        findings = [base_finding] + issue_keywords

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"{Path(target).stem} 自我修复",
            "category": "项目自身",
            "content": f"好奇心引擎发现代码问题并自动修复:\n\n问题: {q.question}\n观察: {q.observation}\n\n修复结果:\n" + "\n".join(detail_lines),
            "keywords": [Path(target).stem, "自我修复", "代码质量"],
            "findings": findings,
            "origin": "self_thinking",
            "action_taken": "self_heal",
            "modification_proposal": {
                "file": target,
                "fixes": fix_results,
                "auto_applied": succeeded > 0,
            },
        }

    def _insight_from_deep_learning(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从能力深度探索生成洞察"""
        missing = exploration.get("missing_capabilities", [])
        topic = exploration.get("topic", q.target)
        return {
            "observation": q.observation,
            "question": q.question,
            "summary": exploration.get("summary", f"能力深度探索 [{topic}]"),
            "topic": f"能力深度: {topic}",
            "category": "能力参考",
            "content": exploration.get("summary", ""),
            "keywords": [topic] + missing[:5],
            "findings": missing[:5],
            "origin": "capability_audit",
            "action_taken": "deep_learning",
        }

    def _store_insight(self, insight: Dict[str, Any]) -> bool:
        """将洞察存入知识库"""
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()

            topic = insight.get("topic", "")
            if not topic:
                return False

            # 先检查是否已存在
            existing = kb.get_all_knowledge()
            if any(item.get("topic") == topic for item in existing):
                return False

            entry = {
                "topic": topic,
                "category": insight.get("category", "项目自身"),
                "content": insight.get("content", insight.get("summary", "")),
                "source": "自我思考",
                "keywords": insight.get("keywords", []),
                "references": [],
                "importance": 0.9,
                "learning_time": datetime.now().isoformat(),
            }
            return kb.add_knowledge(entry)
        except Exception as e:
            print(f"⚠️  知识库存储失败: {e}")
            return False

    def _add_crawler_tasks(self, q) -> bool:
        """为知识缺口添加爬虫任务"""
        try:
            ctx = q.context
            domain = ctx.get("domain", q.target)
            missing = ctx.get("missing", [])

            if not missing:
                return False

            task_file = self.data_dir / "crawler_tasks.json"

            # 读取现有任务
            existing_tasks = []
            if task_file.exists():
                with open(task_file, encoding="utf-8") as f:
                    existing_tasks = json.load(f)

            existing_queries = {t.get("query", "") for t in existing_tasks}

            # 添加新任务（去重）
            added = 0
            for topic in missing:
                query = f"{topic} 教程" if "基础" in topic or "入门" in topic else topic
                if query not in existing_queries:
                    existing_tasks.append({
                        "query": query,
                        "domain": domain,
                        "reason": f"好奇心引擎发现知识缺口: {domain} 领域缺少 {topic}",
                    })
                    existing_queries.add(query)
                    added += 1

            if added > 0:
                with open(task_file, "w", encoding="utf-8") as f:
                    json.dump(existing_tasks, f, ensure_ascii=False, indent=2)

            return added > 0
        except Exception as e:
            print(f"⚠️  添加爬虫任务失败: {e}")
            return False

    # ═══════════════════════════════════════
    #  📝 游标式逐轮记忆提取（源自 extractMemories.ts）
    # ═══════════════════════════════════════

    def _extract_memories(self) -> List[Dict]:
        """
        游标式逐轮记忆提取

        extractMemories.ts 模式的轻量实现：
        - 跟踪 last_extracted_idx（已处理条目的游标）
        - 每轮只检查游标之后的新条目
        - 对新条目评估：是否需要触发行动
        - 更新游标

        Returns: 触发的行动列表
        """
        tracker_file = self.data_dir / "extract_tracker.json"

        # 读取游标和状态
        tracker = {"last_idx": -1, "last_topic": "", "version": 1}
        if tracker_file.exists():
            try:
                tracker = json.loads(tracker_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            all_k = kb.get_all_knowledge()
            total = len(all_k)

            # 计算游标位置
            last_idx = tracker.get("last_idx", -1)
            if last_idx >= total:
                return []  # 没有新条目

            # 找出新条目
            start = max(0, last_idx + 1) if last_idx >= 0 else 0
            new_entries = all_k[start:]
            if not new_entries:
                return []

            # 对新条目做评估
            actions = []
            for entry in new_entries:
                topic = entry.get("topic", "")
                content = entry.get("content", "")
                category = entry.get("category", "")
                importance = entry.get("importance", 0.5)
                keywords = entry.get("keywords", [])

                # 评估每一条新知识
                evaluation = {
                    "topic": topic[:80],
                    "category": category,
                    "importance": importance,
                    "length": len(content),
                    "has_keywords": len(keywords) > 0,
                    "action_needed": False,
                }

                # 是否需要行动？
                # 1. 项目自身且包含代码模式 → 检查对应代码
                if category == "项目自身" and importance >= 0.7:
                    target_file = self._find_target_file(topic)
                    if target_file:
                        evaluation["action_needed"] = True
                        evaluation["suggested_action"] = "read_file"
                        evaluation["target"] = target_file

                # 2. 内容包含可修复的问题模式
                if any(pattern in content for pattern in ["bare except", "裸 except", "no docstring", "missing doc"]):
                    evaluation["action_needed"] = True
                    evaluation["suggested_action"] = "self_heal"

                # 3. 新技术概念且评分高 → 探索
                if importance >= 0.8 and keywords:
                    evaluation["action_needed"] = True
                    evaluation["suggested_action"] = "research"

                actions.append(evaluation)

            # 更新游标
            tracker["last_idx"] = total - 1
            tracker["last_topic"] = all_k[-1].get("topic", "") if all_k else ""
            tracker["last_evaluated"] = datetime.now().isoformat()
            tracker["evaluated_count"] = tracker.get("evaluated_count", 0) + len(new_entries)
            tracker_file.write_text(json.dumps(tracker, ensure_ascii=False, indent=2))

            if new_entries:
                print(f"\n  {'─'*40}")
                print(f"  🧩 记忆提取: 评估 {len(new_entries)} 条新知识")
                need_action = [a for a in actions if a.get("action_needed")]
                if need_action:
                    print(f"  ⚡ {len(need_action)} 条需要后续行动:")
                    for a in need_action[:3]:
                        print(f"    [{a['suggested_action']}] {a['topic']}")
                print(f"  {'─'*40}")

            return actions

        except Exception as e:
            print(f"  ⚠️ 记忆提取异常: {e}")
            return []

    # ---- 日志 ----

    def _log_thinking_cycle(self, results: List[Dict[str, Any]]):
        """记录思考循环（结构化 ContentBlock 格式）"""
        # 构建结构化消息
        scan_data = {
            "py_files": len(self.snapshot.get("py_files", [])),
            "kb_entries": self.snapshot.get("knowledge_base", {}).get("total_entries", 0),
            "changes": len(self.diff.get("changes", [])) if self.diff else 0,
        } if self.snapshot else {}

        structured = build_cycle_messages(
            phase=f"cycle_{getattr(self, '_cycle_count', 0)}",
            scan_data=scan_data,
            questions=self.questions if self.questions else None,
            insights=results,
        )

        entry = {
            "timestamp": datetime.now().isoformat(),
            "cycle_id": str(uuid.uuid4()),
            "questions_count": len(self.questions),
            "insights_generated": len(results),
            "insights": [
                {
                    "topic": r.get("topic", ""),
                    "summary": r.get("summary", "")[:200],
                    "action": r.get("action_taken", "none"),
                }
                for r in results
            ],
            "snapshot_summary": scan_data,
            # ContentBlock 结构化消息（可查询，向后兼容）
            "messages": [
                {
                    "role": m.role,
                    "blocks": [{"type": b.type, "data": b.data} for b in m.blocks],
                    "timestamp": m.timestamp,
                }
                for m in structured
            ],
        }
        self.thinking_log.append(entry)

        # 持久化
        self.data_dir.mkdir(exist_ok=True)
        try:
            existing = []
            if self.log_file.exists():
                with open(self.log_file, encoding="utf-8") as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  思考日志保存失败: {e}")

    # ---- 查询接口 ----

    def get_thinking_report(self) -> Dict[str, Any]:
        """获取思考报告"""
        return {
            "current_snapshot": self.snapshot,
            "questions": [
                {"observation": q.observation, "question": q.question,
                 "importance": q.importance, "action": q.explore_action}
                for q in (self.questions or [])
            ],
            "recent_logs": self.thinking_log[-5:] if self.thinking_log else [],
        }

    # ---- 演示 ----

    def demonstrate_self_thinking(self):
        """展示自我思考能力"""
        print("🎯 自我思考Agent演示")
        print("=" * 60)

        results = self.run_thinking_cycle(depth=3)

        if results:
            print(f"\n{'='*60}")
            print("📊 本次思考发现:")
            print(f"{'='*60}")
            for r in results:
                print(f"\n  📝 {r.get('topic', '')}")
                print(f"     {r.get('summary', '')[:150]}")
        else:
            print("\n💤 没有新的发现")

        print(f"\n{'='*60}")
        print("✅ 自我思考演示完成")
        print(f"{'='*60}")

    def save_reflection(self):
        """保存反思记录（兼容旧接口）"""
        report = self.get_thinking_report()
        ref_file = self.data_dir / "self_thinking_reflection.json"
        self.data_dir.mkdir(exist_ok=True)
        with open(ref_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)


def main():
    agent = SelfThinkingAgent()
    agent.demonstrate_self_thinking()


if __name__ == "__main__":
    main()
