#!/usr/bin/env python3
"""
🧠 元认知监控 — 思考质量的自我评估
检测循环模式、评估失败风险、估计置信度、发现停滞
"""

import json
import math
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class MetacognitiveFinding:
    """元认知监控发现"""
    finding_type: str        # loop | failure_risk | confidence | stagnation
    severity: float          # 0-1
    detail: str
    intervention: str = ""
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThinkingQualityReport:
    """综合思考质量报告——聚合四项元认知分析为单一评分"""
    overall_score: float                    # 0.0-1.0 综合质量
    loop_severity: float                    # 0.0-1.0 循环严重度
    failure_risk: float                     # 0.0-1.0 失败风险
    confidence: float                       # 0.0-1.0 置信度（高=好）
    stagnation: float                       # 0.0-1.0 停滞程度
    stability: float                        # 0.0-1.0 近期趋势稳定性
    freshness: float                        # 0.0-1.0 思维新鲜度
    interpretation: str                     # 中文可读解释
    recommended_mode: str                   # 推荐的策略模式名
    factor_breakdown: Dict[str, float]      # 各因子详细得分


class MetacognitiveMonitor:
    """
    纯算法元认知监控，零外部依赖。

    记录思考主题滑动窗口，每次 check() 时执行四项分析：
    - 循环检测：Jaccard 相似度窗口
    - 失败风险评估：从 ExperienceTracker 统计计算
    - 置信度估计：多因子加权
    - 停滞检测：目标进度无变化
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.state_file = self.data_dir / "metacognitive_state.json"

        # 滑动窗口：最近 20 个思考主题
        self._thought_window: deque = deque(maxlen=20)

        # 历史统计
        self._total_checks = 0
        self._findings_history: List[Dict[str, Any]] = []

        # ── 信号去重（从 Evolver 学习） ──
        self._signal_counter: Dict[str, int] = {}   # 信号类型→连续出现次数
        self._signal_dead: Dict[str, bool] = {}      # 信号类型→是否已静默
        self._consecutive_failures = 0                # 连续失败计数
        self._last_strategy_switch = 0                # 上次切换策略的轮次
        self._strategy_history: List[str] = []        # 策略切换历史

        self._load()

    # ── 记录接口 ─────────────────────────────────────

    def record_thought(self, topic: str):
        """记录一个思考主题到滑动窗口"""
        self._thought_window.append(topic)
        self._save()

    # ── 主检查接口 ───────────────────────────────────

    def check(self, experience_tracker=None,
              thinking_stats: Dict[str, Any] = None,
              daemon_stats: Dict[str, Any] = None,
              goal_planner=None) -> List[MetacognitiveFinding]:
        """
        执行完整元认知检查，返回所有发现。

        Args:
            experience_tracker: ExperienceTracker 实例
            thinking_stats: ThinkingEngine 的 stats 字典
            daemon_stats: ThinkingDaemon 的 get_status() 字典
            goal_planner: GoalPlanner 实例
        """
        self._total_checks += 1
        findings: List[MetacognitiveFinding] = []

        findings.extend(self._detect_loops())
        findings.extend(self._estimate_failure_risk(experience_tracker))
        findings.extend(self._estimate_confidence(
            experience_tracker, thinking_stats))
        findings.extend(self._detect_stagnation(goal_planner))

        # 记录 findings
        for f in findings:
            self._findings_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": f.finding_type,
                "severity": f.severity,
                "detail": f.detail,
            })

        # 信号去重：抑制 3+ 次重复的同类信号
        findings = self._dedup_signals(findings)

        # 连续失败检测：5 次后强制切换策略
        self._check_consecutive_failures(findings)

        self._save()
        return findings

    # ── 综合质量评分 ─────────────────────────────────

    def compute_quality_score(self, experience_tracker=None,
                               thinking_stats: Dict[str, Any] = None,
                               daemon_stats: Dict[str, Any] = None,
                               goal_planner=None) -> ThinkingQualityReport:
        """
        聚合四项元认知分析为单一综合质量评分（0.0-1.0）。

        评分公式：
          overall = (1-loop)*0.25 + (1-risk)*0.20 + confidence*0.25
                  + (1-stagnation)*0.15 + stability*0.10 + freshness*0.05
        """
        # 运行四项分析获取 severity
        loops = self._detect_loops()
        risks = self._estimate_failure_risk(experience_tracker)
        confs = self._estimate_confidence(experience_tracker, thinking_stats)
        stags = self._detect_stagnation(goal_planner)

        loop_sev = loops[0].severity if loops else 0.0
        risk_sev = risks[0].severity if risks else 0.0
        stag_sev = stags[0].severity if stags else 0.0
        # confidence: 无finding → 默认0.6，有则反转severity
        if confs:
            conf_val = max(0.0, 1.0 - confs[0].severity)
        else:
            conf_val = 0.6

        # stability: 基于 findings_history 最近趋势
        recent = [h for h in self._findings_history[-20:]
                  if h.get("type") != "empty_cycle"]
        if len(recent) >= 4:
            half = len(recent) // 2
            first_half = sum(1 for h in recent[:half] if h.get("severity", 0) > 0.3)
            second_half = sum(1 for h in recent[half:] if h.get("severity", 0) > 0.3)
            if second_half <= first_half:
                stability = 0.8  # 改善或持平
            elif second_half > first_half + 1:
                stability = 0.3  # 恶化
            else:
                stability = 0.5
        else:
            stability = 0.6

        # freshness: 思考窗口中去重率
        window = list(self._thought_window)
        if len(window) >= 3:
            unique_ratio = len(set(window)) / len(window)
            freshness = min(1.0, unique_ratio * 1.5)
        else:
            freshness = 0.7

        # 综合评分
        overall = (
            (1.0 - loop_sev) * 0.25
            + (1.0 - risk_sev) * 0.20
            + conf_val * 0.25
            + (1.0 - stag_sev) * 0.15
            + stability * 0.10
            + freshness * 0.05
        )
        overall = max(0.0, min(1.0, overall))

        # 策略推荐
        if overall < 0.35:
            recommended = "rest_consolidate"
            interpretation = f"思考质量偏低 ({overall:.2f})，建议休息巩固"
        elif stag_sev > 0.6:
            recommended = "goal_driven"
            interpretation = f"停滞严重 ({stag_sev:.2f})，需要目标驱动突破"
        elif loop_sev > 0.5:
            recommended = "broad_exploration"
            interpretation = f"循环显著 ({loop_sev:.2f})，需要广泛探索打破循环"
        elif overall >= 0.7:
            recommended = "deep_mining"
            interpretation = f"思考质量良好 ({overall:.2f})，适合深度挖掘"
        else:
            recommended = "broad_exploration"
            interpretation = f"思考质量一般 ({overall:.2f})，保持广泛探索"

        return ThinkingQualityReport(
            overall_score=round(overall, 3),
            loop_severity=round(loop_sev, 3),
            failure_risk=round(risk_sev, 3),
            confidence=round(conf_val, 3),
            stagnation=round(stag_sev, 3),
            stability=round(stability, 3),
            freshness=round(freshness, 3),
            interpretation=interpretation,
            recommended_mode=recommended,
            factor_breakdown={
                "loop_penalty": round(1.0 - loop_sev, 3),
                "risk_penalty": round(1.0 - risk_sev, 3),
                "confidence": round(conf_val, 3),
                "stagnation_penalty": round(1.0 - stag_sev, 3),
                "stability": round(stability, 3),
                "freshness": round(freshness, 3),
            },
        )

    # ── 四项分析 ─────────────────────────────────────

    def _detect_loops(self) -> List[MetacognitiveFinding]:
        """Jaccard 相似度滑动窗口：检测 3+ 连续重复主题"""
        findings = []
        window = list(self._thought_window)
        if len(window) < 4:
            return findings

        # 以 3 为步长，检查连续窗口的 Jaccard 相似度
        for i in range(len(window) - 3):
            a = set(self._tokenize(window[i]))
            b = set(self._tokenize(window[i + 1]))
            c = set(self._tokenize(window[i + 2]))
            lab = self._jaccard(a, b)
            lbc = self._jaccard(b, c)
            if lab > 0.8 and lbc > 0.8:
                findings.append(MetacognitiveFinding(
                    finding_type="loop",
                    severity=min(1.0, (lab + lbc) / 2),
                    detail=f"连续 3 轮主题重复: {window[i][:40]} → {window[i+1][:40]} → {window[i+2][:40]}",
                    intervention="调整思考方向，尝试探索新领域",
                ))
                break  # 一轮最多报一个循环

        return findings

    def _estimate_failure_risk(self, et=None) -> List[MetacognitiveFinding]:
        """
        从 ExperienceTracker 统计评估失败风险。

        P_fail = sigmoid(0.4 * R + 0.3 * recency + 0.3 * complexity - 1.0)
          R: 近期失败率 (0-1)
          recency: 最近失败的时间衰减
          complexity: 失败问题的平均复杂度 (0-1)
        """
        findings = []
        risk = 0.0

        if et is not None:
            try:
                summary = et.get_summary()
                total = summary.get("total_experiences", 0)
                failures = summary.get("failed_experiences", 0)

                if total > 0:
                    # 近期失败率 R
                    R = failures / max(1, total)

                    # recency: 从 failure_patterns 看最近是否有失败
                    patterns = et.get_failure_patterns(min_count=1)
                    recent_fail = 1.0 if any(
                        p.get("count", 0) >= 2 for p in patterns
                    ) else 0.0

                    # complexity: 简单估计
                    complexity = min(1.0, len(patterns) / 10.0)

                    # P_fail = sigmoid(0.4*R + 0.3*recency + 0.3*complexity - 1.0)
                    raw = 0.4 * R + 0.3 * recent_fail + 0.3 * complexity - 1.0
                    risk = 1.0 / (1.0 + math.exp(-raw))
            except Exception:
                pass

        if risk > 0.5:
            findings.append(MetacognitiveFinding(
                finding_type="failure_risk",
                severity=min(1.0, risk),
                detail=f"失败风险评估: {risk:.0%} — 建议检查近期修改",
                intervention="回滚失败修改，增加测试覆盖率",
            ))

        return findings

    def _estimate_confidence(self, et=None,
                             thinking_stats=None) -> List[MetacognitiveFinding]:
        """
        5 因子加权置信度估计。

        confidence = 0.25*success_rate + 0.25*knowledge_cohesion
                     + 0.2*cycle_stability + 0.15*empty_ratio
                     + 0.15*heal_efficacy
        """
        factors = {}

        # 1. 成功率 (0.25)
        if et is not None:
            try:
                summary = et.get_summary()
                factors["success_rate"] = summary.get("success_rate", 0) / 100.0
            except Exception:
                factors["success_rate"] = 0.5
        else:
            factors["success_rate"] = 0.5

        # 2. 知识凝聚 (0.25)
        if thinking_stats:
            isolated = thinking_stats.get("isolated_entities", 0)
            total_entities = thinking_stats.get("graph_entities", 1)
            cohesion = 1.0 - (isolated / max(1, total_entities))
            factors["knowledge_cohesion"] = cohesion
        else:
            factors["knowledge_cohesion"] = 0.5

        # 3. 周期稳定性 (0.2)
        if thinking_stats:
            prev_questions = thinking_stats.get("questions_generated", 0)
            prev_insights = thinking_stats.get("insights_generated", 0)
            # 有产出就是稳定
            stability = 0.3 if prev_questions == 0 and prev_insights == 0 else 0.8
            factors["cycle_stability"] = stability
        else:
            factors["cycle_stability"] = 0.5

        # 4. 空循环比 (0.15) — 从窗口判断
        empty_ratio = 0.0
        history = self._findings_history[-20:] if self._findings_history else []
        if history:
            empty_cycles = sum(
                1 for h in history if h.get("type") == "empty_cycle"
            )
            empty_ratio = empty_cycles / max(1, len(history))
        factors["empty_ratio"] = 1.0 - empty_ratio

        # 5. 修复效能 (0.15)
        if et is not None:
            try:
                summary = et.get_summary()
                # 从 critical_patterns 判断修复效果
                patterns = summary.get("critical_patterns", [])
                heal_efficacy = 1.0 - min(1.0, len(patterns) / 5.0)
                factors["heal_efficacy"] = heal_efficacy
            except Exception:
                factors["heal_efficacy"] = 0.5
        else:
            factors["heal_efficacy"] = 0.5

        weights = {
            "success_rate": 0.25,
            "knowledge_cohesion": 0.25,
            "cycle_stability": 0.2,
            "empty_ratio": 0.15,
            "heal_efficacy": 0.15,
        }

        confidence = sum(
            factors.get(k, 0.5) * w for k, w in weights.items()
        )
        confidence = max(0.0, min(1.0, confidence))

        findings = []
        if confidence < 0.4:
            findings.append(MetacognitiveFinding(
                finding_type="confidence",
                severity=1.0 - confidence,
                detail=f"置信度过低: {confidence:.0%} — 系统状态不确定",
                intervention="增加验证，减少高风险操作",
            ))

        return findings

    def _detect_stagnation(self, goal_planner=None) -> List[MetacognitiveFinding]:
        """检测进度为 0 且超过 5 周期的目标"""
        findings = []

        if goal_planner is None:
            return findings

        try:
            summary = goal_planner.get_summary()
            active = summary.get("active", [])

            for g in active:
                progress = g.get("progress", 0)
                cycles_stuck = g.get("cycles_stuck", 0)
                if progress == 0 and cycles_stuck >= 5:
                    findings.append(MetacognitiveFinding(
                        finding_type="stagnation",
                        severity=min(1.0, cycles_stuck / 10.0),
                        detail=f"目标 '{g['desc'][:50]}' 停滞 {cycles_stuck} 周期，进度 0",
                        intervention="重新评估目标可行性，拆分为更小的子目标",
                    ))
        except Exception:
            pass

        return findings

    # ── 信号去重（从 Evolver 学习） ──────────────────

    def _dedup_signals(self, findings: List[MetacognitiveFinding]) -> List[MetacognitiveFinding]:
        """
        信号去重：相同类型的信号连续出现 3+ 次则静默。
        类似 Evolver 的 "3次重复信号抑制" 机制。
        """
        deduped = []
        # 先统一累加本轮所有信号的计数
        for f in findings:
            sig_key = f"{f.finding_type}:{f.detail[:60]}"
            self._signal_counter[sig_key] = self._signal_counter.get(sig_key, 0) + 1

        for f in findings:
            sig_key = f"{f.finding_type}:{f.detail[:60]}"

            if self._signal_dead.get(sig_key):
                continue  # 已永久静默

            # 检查总出现次数（历史记录 + 本轮+之前累计）
            total_count = self._signal_counter[sig_key]

            if total_count >= 3:
                # 检查是否在最近 8 条历史记录中也有这个信号
                recent = [h for h in self._findings_history[-8:]
                          if h.get("type") == f.finding_type
                          and f.detail[:60] in h.get("detail", "")]
                if len(recent) >= 2 or total_count >= 4:
                    # 历史中有记录 或 计数过高 → 静默
                    self._signal_dead[sig_key] = True
                    print(f"  🔇 信号去重: {f.finding_type} 已出现 {total_count} 次，静默")
                    continue

            # 保留第一个出现（最多保留首次 + 一次重复）
            if deduped and any(
                d.finding_type == f.finding_type and d.detail == f.detail
                for d in deduped
            ):
                continue  # 同一批内只保留第一个

            deduped.append(f)

        return deduped

    def _check_consecutive_failures(self, findings: List[MetacognitiveFinding]) -> None:
        """
        连续失败检测：5 次连续检查都发现问题 → 强制切换策略。
        类似 Evolver 的 "5次失败后剥离主导策略"。
        """
        has_finding = len(findings) > 0
        if has_finding:
            self._consecutive_failures += 1
        else:
            self._consecutive_failures = max(0, self._consecutive_failures - 1)

    def force_strategy_switch(self) -> Optional[str]:
        """当连续失败 >=5 时，返回应该切换到的策略名称"""
        if self._consecutive_failures >= 5:
            # 在修复/保守/创新之间轮换
            strategies = ["repair-only", "balanced", "innovate"]
            used = self._strategy_history[-3:]
            for s in strategies:
                if s not in used:
                    self._strategy_history.append(s)
                    self._consecutive_failures = 0
                    return s
            # 都用过了就回到 balanced
            self._strategy_history.append("balanced")
            self._consecutive_failures = 0
            return "balanced"
        return None

    # ── 工具方法 ─────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """简单分词"""
        if not text:
            return []
        return text.lower().replace("_", " ").replace("-", " ").split()

    @staticmethod
    def _jaccard(a: set, b: set) -> float:
        """Jaccard 相似度"""
        if not a and not b:
            return 1.0
        union = a | b
        if not union:
            return 1.0
        return len(a & b) / len(union)

    # ── 持久化 ───────────────────────────────────────

    def _load(self):
        """从文件加载状态"""
        if not self.state_file.exists():
            return
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            self._signal_counter = data.get("signal_counter", {})
            self._signal_dead = {k: bool(v) for k, v in data.get("signal_dead", {}).items()}
            self._consecutive_failures = data.get("consecutive_failures", 0)
            self._last_strategy_switch = data.get("last_strategy_switch", 0)
            self._strategy_history = data.get("strategy_history", [])
            self._thought_window = deque(
                data.get("thought_window", []), maxlen=20
            )
            self._total_checks = data.get("total_checks", 0)
            self._findings_history = data.get("findings_history", [])
        except Exception:
            pass

    def _save(self):
        """持久化到文件"""
        try:
            data = {
                "thought_window": list(self._thought_window),
                "total_checks": self._total_checks,
                "findings_history": self._findings_history[-100:],
                "signal_counter": self._signal_counter,
                "signal_dead": self._signal_dead,
                "consecutive_failures": self._consecutive_failures,
                "last_strategy_switch": self._last_strategy_switch,
                "strategy_history": self._strategy_history,
                "updated_at": datetime.now().isoformat(),
            }
            self.state_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass


def main():
    """测试 MetacognitiveMonitor"""
    print("=" * 50)
    print("  MetacognitiveMonitor 测试")
    print("=" * 50)

    monitor = MetacognitiveMonitor()

    # 1. 测试记录 + 循环检测
    print("\n1. 循环检测测试")
    monitor.record_thought("test_module 模块分析")
    monitor.record_thought("test_module 模块分析")
    monitor.record_thought("test_module 模块分析")
    loops = monitor._detect_loops()
    print(f"   检测到 {len(loops)} 个循环: {[f.detail[:40] for f in loops]}")

    # 2. 失败风险评估（无 ET 时返回空）
    print("\n2. 失败风险评估测试（无 ET）")
    risks = monitor._estimate_failure_risk(None)
    print(f"   风险项: {len(risks)}")

    # 3. 置信度估计（无数据时返回默认）
    print("\n3. 置信度估计测试（无输入）")
    confs = monitor._estimate_confidence(None, None)
    print(f"   置信度发现: {len(confs)}")

    # 4. 停滞检测（无 planner 时返回空）
    print("\n4. 停滞检测测试")
    stags = monitor._detect_stagnation(None)
    print(f"   停滞项: {len(stags)}")

    # 5. 完整检查
    print("\n5. 完整检查（空输入）")
    findings = monitor.check()
    print(f"   共 {len(findings)} 个发现")
    for f in findings:
        print(f"   [{f.finding_type}] severity={f.severity:.2f} — {f.detail[:60]}")

    # 6. Jaccard 工具测试
    print("\n6. Jaccard 工具测试")
    s1 = {"a", "b", "c"}
    s2 = {"a", "b", "d"}
    print(f"   {s1} vs {s2}: {monitor._jaccard(s1, s2):.2f} (期望 0.5)")

    print("\n✅ 元认知监控测试完成")
    return True


if __name__ == "__main__":
    main()
