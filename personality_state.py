#!/usr/bin/env python3
"""
人格状态 — 从 Evolver PersonalityState 学习

五个连续元参数 (0-1)，控制系统行为风格：
- rigor: 严谨度 — 高=严格验证，低=容忍小误差
- creativity: 创造力 — 高=探索新领域，低=保守执行
- verbosity: 详细度 — 高=详细输出，低=简洁
- risk_tolerance: 风险容忍 — 高=允许大改动，低=保守小修
- obedience: 服从度 — 高=严格遵守约束，低=自主探索

参数通过反馈自然演化，也支持手动覆盖。
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class PersonalityState:
    """
    五个元参数，0-1 连续值。

    每个参数提供一个 gate() 方法，外部模块调用判断是否允许某行为。
    """

    DEFAULTS = {
        "rigor": 0.6,
        "creativity": 0.5,
        "verbosity": 0.5,
        "risk_tolerance": 0.4,
        "obedience": 0.7,
    }

    # 参数间相互影响：调整 A 时 B 也会微调
    COUPLING = {
        "creativity": {"risk_tolerance": +0.1, "rigor": -0.05},
        "risk_tolerance": {"creativity": +0.1, "obedience": -0.1},
        "rigor": {"risk_tolerance": -0.1, "obedience": +0.05},
    }

    def __init__(self):
        self._params: Dict[str, float] = dict(self.DEFAULTS)
        self._override: Dict[str, bool] = {}  # True = 手动锁定
        self._history: list = []
        self._file = Path("data") / "personality_state.json"
        self._load()

    # ── 读取 ──

    def get(self, name: str) -> float:
        return self._params.get(name, self.DEFAULTS.get(name, 0.5))

    def all_params(self) -> Dict[str, float]:
        return dict(self._params)

    # ── 调整 ──

    def adjust(self, name: str, delta: float,
               reason: str = "", force: bool = False) -> float:
        """
        调整一个参数，并传播耦合影响。

        Args:
            name: 参数名
            delta: 变化量 (-1 到 1)
            reason: 调整原因
            force: 是否忽略锁定

        Returns: 调整后的值
        """
        if self._override.get(name) and not force:
            return self._params[name]

        old = self._params[name]
        new = max(0.0, min(1.0, old + delta))
        self._params[name] = new
        self._history.append({
            "param": name,
            "from": round(old, 3),
            "to": round(new, 3),
            "reason": reason[:100] or "未知",
            "timestamp": datetime.now().isoformat(),
        })

        # 传播耦合影响
        if name in self.COUPLING:
            for coupled, coupled_delta in self.COUPLING[name].items():
                if not self._override.get(coupled):
                    cv = self._params[coupled]
                    self._params[coupled] = max(0.0, min(1.0, cv + coupled_delta * abs(delta)))

        self._prune_history()
        self._save()
        return new

    def lock(self, name: str) -> None:
        """锁定参数，防止自动调整"""
        self._override[name] = True

    def unlock(self, name: str) -> None:
        """解锁参数"""
        self._override.pop(name, None)

    def reset(self, name: str = "") -> None:
        """重置一个或所有参数到默认值"""
        if name:
            self._params[name] = self.DEFAULTS.get(name, 0.5)
            self._override.pop(name, None)
        else:
            self._params = dict(self.DEFAULTS)
            self._override.clear()
        self._save()

    # ── 门控 ──

    def gate_creativity(self, base_score: float) -> float:
        """创造力门控：返回调整后的新颖性分数"""
        return base_score * (0.5 + self.get("creativity"))

    def gate_risk(self, change_size: int) -> bool:
        """风险门控：判断是否允许某个幅度的改动"""
        max_allowed = int(self.get("risk_tolerance") * 100)
        return change_size <= max(max_allowed, 5)

    def gate_verbosity(self, base_tokens: int) -> int:
        """详细度门控：调整输出长度上限"""
        ratio = 0.5 + self.get("verbosity")
        return int(base_tokens * ratio)

    def gate_rigor(self, confidence: float) -> float:
        """严谨门控：调整置信度阈值"""
        rigor = self.get("rigor")
        threshold = 0.3 + rigor * 0.5  # 范围 0.3-0.8
        return max(threshold, confidence)

    def gate_obedience(self, constraint_violation: bool) -> bool:
        """服从门控：是否允许违反约束"""
        obedience = self.get("obedience")
        if constraint_violation:
            return obedience > 0.8  # 只有高服从才阻止
        return True

    # ── 从反馈学习 ──

    def learn_from_outcome(self, action: str, success: bool) -> None:
        """
        从行动结果学习调整参数。

        成功 → 微增风险容忍 + 微降严谨（信任当前模式）
        失败 → 微降风险容忍 + 微增严谨（需要更保守）
        """
        if success:
            self.adjust("risk_tolerance", +0.03,
                        reason=f"{action} 成功，略增风险容忍")
            self.adjust("rigor", -0.02,
                        reason=f"{action} 成功，可略放松严谨")
        else:
            self.adjust("risk_tolerance", -0.05,
                        reason=f"{action} 失败，降低风险容忍")
            self.adjust("rigor", +0.05,
                        reason=f"{action} 失败，增加严谨度")

    # ── 策略建议 ──

    def suggest_strategy(self) -> str:
        """基于当前人格状态推荐策略模式"""
        c = self.get("creativity")
        r = self.get("risk_tolerance")
        g = self.get("rigor")

        if c > 0.7 and r > 0.6:
            return "innovate"  # 创新模式：大胆探索
        elif g > 0.7:
            return "harden"    # 加固模式：严格验证
        elif r < 0.3 or g > 0.6:
            return "repair-only"  # 修复模式：保守小修
        else:
            return "balanced"  # 均衡模式（默认）

    # ── 内部 ──

    def _prune_history(self, max_len: int = 100):
        if len(self._history) > max_len:
            self._history = self._history[-max_len:]

    def _load(self):
        if self._file.exists():
            try:
                data = json.loads(self._file.read_text(encoding="utf-8"))
                self._params.update(data.get("params", {}))
                self._override = data.get("override", {})
                self._history = data.get("history", [])
            except Exception:
                pass

    def _save(self):
        try:
            self._file.parent.mkdir(exist_ok=True)
            self._file.write_text(json.dumps({
                "params": self._params,
                "override": self._override,
                "history": self._history[-100:],
                "updated_at": datetime.now().isoformat(),
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass


if __name__ == "__main__":
    ps = PersonalityState()

    print(f"初始: {ps.all_params()}")
    print(f"策略建议: {ps.suggest_strategy()}")

    # 模拟成功 → 参数微调
    ps.learn_from_outcome("修复bug", success=True)
    print(f"成功一次: {ps.all_params()}")

    # 模拟失败 → 参数微调
    ps.learn_from_outcome("探索新领域", success=False)
    print(f"失败一次: {ps.all_params()}")

    # 门控测试
    print(f"创造力门控 0.7 → {ps.gate_creativity(0.7):.2f}")
    print(f"风险门控 50行改动? {ps.gate_risk(50)}")
    print(f"策略建议: {ps.suggest_strategy()}")

    print("✅ PersonalityState 测试完成")
