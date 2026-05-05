#!/usr/bin/env python3
"""
🎯 思考策略管理 — 基于元认知质量评分切换思考模式

定义四种策略模式，让系统能基于"自己思考得怎么样"自动改变思考方式。
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class ThinkingStrategy:
    """一种思考策略模式——定义系统"该怎么想" """
    name: str                           # 唯一标识 broad_exploration
    display_name: str                   # 中文名：广泛探索
    description: str                    # 说明
    # --- 影响探索阶段 ---
    exploration_depth: int              # 每轮探索问题数（1-5）
    min_importance_threshold: float     # 最小重要性阈值（0.0-1.0）
    question_diversity_bias: float      # 多样性偏好（0.0=喜欢重复主题，1.0=全新领域）
    continuation_boost: float           # 延续问题的重要性加成（0.0-0.5）
    # --- 影响循环节奏 ---
    max_interval: int                   # 最大睡眠间隔（秒）
    min_interval: int                   # 最小睡眠间隔（秒）
    heal_threshold: float               # heal 最小重要值（0.0-1.0）
    # --- 影响认知焦点 ---
    reflection_focus: str               # 反思焦点：loop/quality/goal/balanced
    prefer_continuation: bool           # 是否优先延续已有思考线程


# 四种预定义策略
STRATEGIES: Dict[str, ThinkingStrategy] = {
    "broad_exploration": ThinkingStrategy(
        name="broad_exploration",
        display_name="广泛探索",
        description="浅而广地扫描新领域，适合系统启动或从循环中突破",
        exploration_depth=5,
        min_importance_threshold=0.4,
        question_diversity_bias=0.8,
        continuation_boost=0.0,
        max_interval=1800,
        min_interval=120,
        heal_threshold=0.7,
        reflection_focus="loop",
        prefer_continuation=False,
    ),
    "deep_mining": ThinkingStrategy(
        name="deep_mining",
        display_name="深度挖掘",
        description="专注跟进已有思考线程，适合高质量状态下深挖",
        exploration_depth=3,
        min_importance_threshold=0.6,
        question_diversity_bias=0.2,
        continuation_boost=0.3,
        max_interval=1200,
        min_interval=180,
        heal_threshold=0.6,
        reflection_focus="quality",
        prefer_continuation=True,
    ),
    "goal_driven": ThinkingStrategy(
        name="goal_driven",
        display_name="目标驱动",
        description="仅探索与当前目标最相关的问题，适合从停滞中突破",
        exploration_depth=4,
        min_importance_threshold=0.5,
        question_diversity_bias=0.4,
        continuation_boost=0.2,
        max_interval=900,
        min_interval=60,
        heal_threshold=0.5,
        reflection_focus="goal",
        prefer_continuation=True,
    ),
    "rest_consolidate": ThinkingStrategy(
        name="rest_consolidate",
        display_name="休息巩固",
        description="不探索新问题，专注整理已有知识，适合低质量状态",
        exploration_depth=1,
        min_importance_threshold=0.8,
        question_diversity_bias=0.1,
        continuation_boost=0.0,
        max_interval=3600,
        min_interval=600,
        heal_threshold=0.9,
        reflection_focus="balanced",
        prefer_continuation=False,
    ),
}


class StrategyManager:
    """
    策略管理器——基于元认知质量评分选择策略模式。

    职责：
    1. 根据 ThinkingQualityReport 选择最优策略
    2. 持久化策略切换历史
    3. 提供策略影响参数供 daemon 和 curiosity_engine 使用
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "strategy_history.json"

        self._current_strategy: Optional[ThinkingStrategy] = None
        self._last_switch_cycle: int = 0
        self._consecutive_same_strategy: int = 0
        self._history: List[Dict] = []
        self._load_history()

    @property
    def current_strategy(self) -> Optional[ThinkingStrategy]:
        return self._current_strategy

    def select_strategy(
        self,
        quality: Any,  # ThinkingQualityReport
        cycle_count: int = 0,
        force_switch: Optional[str] = None,
    ) -> ThinkingStrategy:
        """
        核心策略选择逻辑。

        逻辑树：
        1. force_switch 非空 → 直接切换到指定策略
        2. quality < 0.35 → rest_consolidate
        3. stagnation > 0.6 → goal_driven
        4. loop_severity > 0.5 → broad_exploration
        5. quality >= 0.7 → deep_mining
        6. 默认 → broad_exploration
        """
        if force_switch and force_switch in STRATEGIES:
            chosen = STRATEGIES[force_switch]
            self.switch_strategy(chosen, quality.overall_score, cycle_count,
                                 f"强制切换: {force_switch}")
            return chosen

        # 确定目标策略
        if quality.overall_score < 0.35:
            target = "rest_consolidate"
            reason = f"质量偏低 ({quality.overall_score:.2f})"
        elif quality.stagnation > 0.6:
            target = "goal_driven"
            reason = f"停滞严重 ({quality.stagnation:.2f})"
        elif quality.loop_severity > 0.5:
            target = "broad_exploration"
            reason = f"循环显著 ({quality.loop_severity:.2f})"
        elif quality.overall_score >= 0.7:
            target = "deep_mining"
            reason = f"质量良好 ({quality.overall_score:.2f})"
        else:
            target = "broad_exploration"
            reason = f"质量一般 ({quality.overall_score:.2f})，默认模式"

        chosen = STRATEGIES[target]
        self.switch_strategy(chosen, quality.overall_score, cycle_count, reason)
        return chosen

    def apply_to_daemon(self, daemon) -> Dict[str, Any]:
        """将当前策略应用到 daemon 参数，返回变更记录"""
        if not self._current_strategy:
            return {}
        changes = {}
        s = self._current_strategy

        try:
            if hasattr(daemon, 'update_config'):
                kwargs = {}
                if hasattr(daemon, 'max_interval') and daemon.max_interval != s.max_interval:
                    old = daemon.max_interval
                    kwargs["max_interval"] = s.max_interval
                    changes["max_interval"] = (old, s.max_interval)
                if hasattr(daemon, 'min_interval') and daemon.min_interval != s.min_interval:
                    old = daemon.min_interval
                    kwargs["min_interval"] = s.min_interval
                    changes["min_interval"] = (old, s.min_interval)
                if hasattr(daemon, 'heal_threshold') and daemon.heal_threshold != s.heal_threshold:
                    old = daemon.heal_threshold
                    kwargs["heal_threshold"] = s.heal_threshold
                    changes["heal_threshold"] = (old, s.heal_threshold)
                if kwargs:
                    daemon.update_config(**kwargs)
            elif hasattr(daemon, 'heal_threshold'):
                # 直接属性赋值
                daemon.heal_threshold = s.heal_threshold
        except Exception:
            pass

        return changes

    def get_question_filter(self) -> Dict[str, Any]:
        """返回参数字典，传给 curiosity_engine 用于调整问题生成"""
        if not self._current_strategy:
            return {}
        s = self._current_strategy
        return {
            "min_importance": s.min_importance_threshold,
            "diversity_bias": s.question_diversity_bias,
            "prefer_continuation": s.prefer_continuation,
            "continuation_boost": s.continuation_boost,
        }

    def get_exploration_params(self) -> Dict[str, Any]:
        """返回探索阶段的参数"""
        if not self._current_strategy:
            return {}
        s = self._current_strategy
        return {
            "depth": s.exploration_depth,
            "reflection_focus": s.reflection_focus,
        }

    def switch_strategy(
        self,
        new_strategy: ThinkingStrategy,
        quality_score: float,
        cycle_count: int,
        reason: str,
    ) -> bool:
        """
        执行策略切换（记录历史）。
        如果和当前策略相同则不切换（除非连续次数超限）。
        """
        # 相同策略保护
        if self._current_strategy and self._current_strategy.name == new_strategy.name:
            self._consecutive_same_strategy += 1
            if self._consecutive_same_strategy < 3:
                return False
            # 强制轮换到其他策略
            alternatives = [n for n in STRATEGIES if n != new_strategy.name]
            new_name = alternatives[cycle_count % len(alternatives)]
            new_strategy = STRATEGIES[new_name]
            reason += "（连续相同策略超限，强制轮换）"

        old_name = self._current_strategy.display_name if self._current_strategy else "无"
        self._current_strategy = new_strategy
        self._last_switch_cycle = cycle_count
        self._consecutive_same_strategy = 0

        entry = {
            "timestamp": datetime.now().isoformat(),
            "cycle": cycle_count,
            "from": old_name,
            "to": new_strategy.display_name,
            "quality_score": round(quality_score, 3),
            "reason": reason,
        }
        self._history.append(entry)
        self._save_history()

        print(f"\n  🎯 策略切换: {old_name} → {new_strategy.display_name}")
        print(f"     原因: {reason}")
        print(f"     质量评分: {quality_score:.3f}")
        return True

    def get_strategy_history(self) -> List[Dict]:
        """返回策略切换历史"""
        return list(self._history)

    def _save_history(self):
        """持久化策略历史（最近 100 条）"""
        try:
            self.history_file.write_text(
                __import__('json').dumps(self._history[-100:], ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    def _load_history(self):
        """从文件加载策略历史"""
        if not self.history_file.exists():
            return
        try:
            data = __import__('json').loads(self.history_file.read_text(encoding="utf-8"))
            self._history = data if isinstance(data, list) else []
        except Exception:
            pass


def main():
    """测试 StrategyManager 策略选择逻辑"""
    print("=" * 50)
    print("  StrategyManager 测试")
    print("=" * 50)

    from metacognitive_monitor import ThinkingQualityReport

    mgr = StrategyManager()

    scenarios = [
        ("高质量 → 深度挖掘", ThinkingQualityReport(
            overall_score=0.82, loop_severity=0.1, failure_risk=0.05,
            confidence=0.75, stagnation=0.0, stability=0.8, freshness=0.7,
            interpretation="", recommended_mode="", factor_breakdown={},
        )),
        ("一般质量 → 广泛探索", ThinkingQualityReport(
            overall_score=0.55, loop_severity=0.2, failure_risk=0.3,
            confidence=0.5, stagnation=0.2, stability=0.6, freshness=0.5,
            interpretation="", recommended_mode="", factor_breakdown={},
        )),
        ("低质量 → 休息巩固", ThinkingQualityReport(
            overall_score=0.25, loop_severity=0.6, failure_risk=0.7,
            confidence=0.2, stagnation=0.3, stability=0.3, freshness=0.2,
            interpretation="", recommended_mode="", factor_breakdown={},
        )),
        ("循环严重 → 广泛探索", ThinkingQualityReport(
            overall_score=0.60, loop_severity=0.7, failure_risk=0.2,
            confidence=0.5, stagnation=0.1, stability=0.5, freshness=0.3,
            interpretation="", recommended_mode="", factor_breakdown={},
        )),
        ("停滞严重 → 目标驱动", ThinkingQualityReport(
            overall_score=0.50, loop_severity=0.2, failure_risk=0.3,
            confidence=0.5, stagnation=0.8, stability=0.5, freshness=0.4,
            interpretation="", recommended_mode="", factor_breakdown={},
        )),
    ]

    for desc, report in scenarios:
        print(f"\n{desc}:")
        strategy = mgr.select_strategy(report, cycle_count=0)
        print(f"  选择: {strategy.display_name}")
        print(f"  深度: {strategy.exploration_depth}, 阈值: {strategy.min_importance_threshold}")
        print(f"  多样性: {strategy.question_diversity_bias}, 间隔: {strategy.max_interval}s")

    print("\n✅ 策略测试完成")
    return True


if __name__ == "__main__":
    main()
