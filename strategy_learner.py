#!/usr/bin/env python3
"""
🧠 策略学习引擎 — 从行为记录中提炼策略

当前阶段：数据采集模式。只记录特征、不决策。
当行为记录积累到 200+ 条后自动启动聚类分析。

闭环：行为 → 特征标记 → 模式发现 → 策略提炼 → 指导方向
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class StrategyLearner:
    """
    策略学习引擎。

    职责：
    1. 读取 BehaviorFeedback 的行为记录
    2. 为每条记录标记上下文特征（action_type, target_area, 时间特征等）
    3. 当数据量达到阈值时，自动运行模式分析
    4. 输出的策略权重供 _prioritize_questions 参考（非强制）

    当前状态：只分析、不干预。
    """

    # 聚类需要的记录数阈值
    MIN_RECORDS_FOR_CLUSTERING = 200

    # 策略有效期（轮次），到期后逐步降权
    STRATEGY_TTL = 50

    # 已知的操作类型 → 所属领域
    ACTION_DOMAINS = {
        "read_file": "code_analysis",
        "check_state": "code_analysis",
        "compare_files": "code_analysis",
        "self_heal": "self_modification",
        "modify_code": "self_modification",
        "add_crawler_task": "knowledge_acquisition",
        "global_research": "knowledge_acquisition",
        "deep_learning": "knowledge_acquisition",
        "study_knowledge": "knowledge_acquisition",
        "explore_module": "code_analysis",
    }

    # 目标路径匹配 → 领域（按前缀匹配）
    TARGET_DOMAIN_PATTERNS = [
        ("knowledge_graph", "knowledge_infrastructure"),
        ("curiosity_engine", "curiosity_system"),
        ("thinking_engine", "thinking_system"),
        ("self_thinking_agent", "agent_orchestration"),
        ("self_modification", "modification_system"),
        ("thinking_daemon", "daemon_system"),
        ("self_scanner", "scanning_system"),
        ("pattern_engine", "pattern_system"),
        ("analogy_engine", "analogy_system"),
        ("crawler", "crawler_system"),
        ("knowledge_base", "knowledge_infrastructure"),
        ("behavior_feedback", "feedback_system"),
    ]

    def __init__(self, behavior_feedback):
        self.bf = behavior_feedback
        # 当前生效的策略列表（初始为空，数据积累后自动填充）
        self._strategies: List[Dict] = []
        self._last_analysis_cycle: int = 0
        self._analysis_interval = 10  # 每 10 轮分析一次

    # ── 特征标记 ──────────────────────────────────────────

    def _tag_features(self, record: Dict) -> Dict[str, Any]:
        """
        给一条行为记录打上上下文特征。

        这些特征将来用于聚类，找出"什么条件下什么策略有效"。
        """
        features = {}
        action = record.get("action_type", "")
        target = record.get("target", "")
        result = record.get("result", "")

        # 所属领域
        features["action_domain"] = self.ACTION_DOMAINS.get(action, "other")
        features["target_domain"] = self._infer_target_domain(target)

        # 时段特征（用于分析：白天 vs 深夜的行为模式是否不同）
        ts = record.get("timestamp", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                features["hour"] = dt.hour
                features["is_night"] = dt.hour < 6 or dt.hour > 22
                features["day_of_week"] = dt.weekday()
            except Exception:
                pass

        # 序列特征
        features["cycle"] = record.get("cycle", 0)
        features["result"] = result

        # 成功/失败的前置序列（未来扩展）
        return features

    def _infer_target_domain(self, target: str) -> str:
        """从目标路径推断所属领域"""
        if not target:
            return "unknown"
        t_lower = target.lower()
        for pattern, domain in self.TARGET_DOMAIN_PATTERNS:
            if pattern in t_lower:
                return domain
        return "other"

    # ── 分析 ──────────────────────────────────────────────

    def analyze(self, current_cycle: int) -> Dict[str, Any]:
        """
        分析行为记录（数据量不足时仅返回统计）。

        Returns:
            {
                "status": "insufficient_data" | "analyzed",
                "record_count": int,
                "strategies": [...],  # 仅 status=="analyzed" 时有值
                "summary": str,
            }
        """
        records = self.bf.records
        count = len(records)

        if count < self.MIN_RECORDS_FOR_CLUSTERING:
            return {
                "status": "insufficient_data",
                "record_count": count,
                "needed": self.MIN_RECORDS_FOR_CLUSTERING,
                "strategies": [],
                "summary": f"数据不足 ({count}/{self.MIN_RECORDS_FOR_CLUSTERING})，"
                           f"暂不进行策略聚类",
            }

        # ── 数据量充足：执行模式分析（当前为占位，后续实现聚类） ──
        if current_cycle - self._last_analysis_cycle < self._analysis_interval:
            return {
                "status": "skipped",
                "record_count": count,
                "strategies": self._strategies,
                "summary": f"未到分析周期 (上次: {self._last_analysis_cycle}, 当前: {current_cycle})",
            }

        self._last_analysis_cycle = current_cycle
        # TODO: 聚类分析（v2，数据量 200+ 后激活）
        # 1. 按 action_domain + target_domain 分组
        # 2. 计算每组成功率
        # 3. 提取有效/无效模式
        # 4. 更新 self._strategies

        analysis = self._simple_pattern_analysis(records)
        return analysis

    def _simple_pattern_analysis(self, records: List[Dict]) -> Dict[str, Any]:
        """
        简单模式分析（非聚类，纯统计）。
        在聚类实现之前提供基础的方向指导。
        """
        # 按 (action_domain, target_domain) 分组统计
        groups: Dict[Tuple[str, str], Dict] = {}
        for r in records:
            features = self._tag_features(r)
            key = (features["action_domain"], features["target_domain"])
            if key not in groups:
                groups[key] = {"total": 0, "success": 0, "failure": 0, "partial": 0}
            g = groups[key]
            g["total"] += 1
            result = r.get("result", "")
            if result in g:
                g[result] += 1

        patterns = []
        for (ad, td), s in sorted(groups.items(), key=lambda x: -x[1]["total"]):
            if s["total"] < 3:
                continue  # 样本太少，不提炼策略
            success_rate = s["success"] / s["total"] if s["total"] else 0
            patterns.append({
                "action_domain": ad,
                "target_domain": td,
                "samples": s["total"],
                "success_rate": round(success_rate, 2),
                "label": f"[{ad}] → [{td}]",
            })

        # 提取有效策略（成功率 >= 70%）
        effective = [p for p in patterns if p["success_rate"] >= 0.7]
        # 提取无效策略（成功率 <= 30%）
        ineffective = [p for p in patterns if p["success_rate"] <= 0.3]

        strategies = []
        for p in effective:
            strategies.append({
                "type": "effective",
                "action_domain": p["action_domain"],
                "target_domain": p["target_domain"],
                "confidence": p["success_rate"],
                "samples": p["samples"],
                "rule": f"在 {p['target_domain']} 领域使用 {p['action_domain']} 操作往往有效",
                "ttl": self.STRATEGY_TTL,
                "created_at_cycle": self._last_analysis_cycle,
            })
        for p in ineffective:
            strategies.append({
                "type": "ineffective",
                "action_domain": p["action_domain"],
                "target_domain": p["target_domain"],
                "confidence": 1.0 - p["success_rate"],
                "samples": p["samples"],
                "rule": f"在 {p['target_domain']} 领域使用 {p['action_domain']} 操作效果不佳",
                "ttl": self.STRATEGY_TTL,
                "created_at_cycle": self._last_analysis_cycle,
            })

        self._strategies = self._expire_strategies(strategies, current_cycle)

        return {
            "status": "analyzed",
            "record_count": len(records),
            "strategies": self._strategies,
            "summary": f"{len(records)} 条记录分析完成，"
                       f"{len(effective)} 条有效策略, "
                       f"{len(ineffective)} 条无效策略",
        }

    def _expire_strategies(self, strategies: List[Dict],
                           current_cycle: int) -> List[Dict]:
        """策略过期机制：超过 TTL 的策略逐步降权"""
        valid = []
        for s in strategies:
            age = current_cycle - s.get("created_at_cycle", current_cycle)
            if age >= s.get("ttl", self.STRATEGY_TTL):
                # 策略过期：降权 50%
                s["confidence"] *= 0.5
                s["expired"] = True
                if s["confidence"] < 0.1:
                    continue  # 太低就丢弃
            valid.append(s)
        return valid

    # ── 对外接口 ──────────────────────────────────────────

    def get_strategy_weight(self, action_type: str,
                            target: str = "",
                            current_cycle: int = 0) -> float:
        """
        给某个方向返回策略参考权重。

        Returns -0.2 ~ +0.2:
          +0.2 → 有明确证据表明该方向有效
          -0.2 → 有明确证据表明该方向无效
           0.0 → 无数据或数据不足

        注意：当前策略只是参考权重，不覆盖 behavior_bias。
        等数据量充足后再考虑融合。
        """
        if len(self.bf.records) < self.MIN_RECORDS_FOR_CLUSTERING:
            return 0.0

        action_domain = self.ACTION_DOMAINS.get(action_type, "other")
        target_domain = self._infer_target_domain(target)

        # 检查有效策略
        for s in self._strategies:
            if (s.get("action_domain") == action_domain
                    and s.get("target_domain") == target_domain):
                if s.get("type") == "effective":
                    return 0.15 + 0.05 * s.get("confidence", 0.5)
                elif s.get("type") == "ineffective":
                    return -0.15 - 0.05 * (1.0 - s.get("confidence", 0.5))

        return 0.0

    def get_strategy_summary(self) -> str:
        """返回当前策略清单文本"""
        if not self._strategies:
            return "暂无策略（数据积累中）"

        lines = [f"策略 ({len(self._strategies)} 条):"]
        for s in sorted(self._strategies, key=lambda x: -x.get("confidence", 0)):
            label = "✅" if s.get("type") == "effective" else "❌"
            expired = " (已过期)" if s.get("expired") else ""
            lines.append(
                f"   {label} {s.get('rule', '')} "
                f"(信度: {s.get('confidence', 0):.0%}, "
                f"样本: {s.get('samples', 0)}){expired}")
        return "\n".join(lines)
