#!/usr/bin/env python3
"""
🔄 行为反馈层 — 从「观察代码」到「观察行为」

系统不再只看自己长什么样，而是看自己做得怎么样。
每次探索/修改/学习后记录结果，用历史表现调整下一轮的好奇心方向。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class BehaviorFeedback:
    """
    行为反馈记录与聚合。

    record() → 存行为+结果
    get_bias() → 给某个方向打出偏好分（±0.3）
    get_report() → 本轮总结文本（供反思审计用）
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path("data")
        self.file = self.data_dir / "behavior_feedback.json"
        self._max_records = 1000
        self.records: List[Dict] = self._load()

    # ── 持久化 ────────────────────────────────────────────

    def _load(self) -> List[Dict]:
        try:
            if self.file.exists():
                data = json.loads(self.file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data[-self._max_records:]
        except Exception:
            pass
        return []

    def _save(self):
        try:
            self.data_dir.mkdir(exist_ok=True)
            self.file.write_text(
                json.dumps(self.records[-self._max_records:],
                           ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    # ── 记录 ──────────────────────────────────────────────

    def record(self, cycle: int, action_type: str, target: str,
               question: str, result: str, detail: str = ""):
        """
        记录一次行为结果。

        Args:
            cycle: 思考循环编号
            action_type: 操作类型 (explore|modify|research|study|heal)
            target: 作用目标（文件/模块/主题）
            question: 驱动此行为的好奇心问题
            result: success | failure | partial
            detail: 补充信息
        """
        record = {
            "cycle": cycle,
            "action_type": action_type,
            "target": target[:100],
            "question": question[:200],
            "result": result,
            "detail": detail[:300],
            "timestamp": datetime.now().isoformat(),
        }
        self.records.append(record)
        self._save()

    # ── 查询 ──────────────────────────────────────────────

    def get_recent(self, n: int = 20) -> List[Dict]:
        """最近 n 条记录"""
        return self.records[-n:]

    def get_action_stats(self) -> Dict[str, Dict[str, float]]:
        """
        各操作类型的聚合统计。

        Returns:
            {action_type: {total, success, failure, partial, success_rate}}
        """
        stats: Dict[str, Dict] = {}
        for r in self.records:
            at = r.get("action_type", "unknown")
            if at not in stats:
                stats[at] = {"total": 0, "success": 0,
                             "failure": 0, "partial": 0}
            stats[at]["total"] += 1
            res = r.get("result", "unknown")
            if res in stats[at]:
                stats[at][res] += 1

        for at, s in stats.items():
            total = s["total"]
            s["success_rate"] = round(s["success"] / total, 2) if total else 0.0
        return stats

    def get_target_stats(self, min_attempts: int = 2) -> Dict[str, Dict]:
        """
        按目标聚合统计，找出反复失败的方向。
        """
        target_map: Dict[str, Dict] = {}
        for r in self.records:
            t = r.get("target", "") or r.get("question", "")[:60]
            if not t:
                continue
            if t not in target_map:
                target_map[t] = {"total": 0, "success": 0,
                                 "failure": 0, "recent_cycle": 0}
            target_map[t]["total"] += 1
            res = r.get("result", "")
            if res == "success":
                target_map[t]["success"] += 1
            elif res == "failure":
                target_map[t]["failure"] += 1
            target_map[t]["recent_cycle"] = max(
                target_map[t]["recent_cycle"], r.get("cycle", 0))

        # 只返回达到最少尝试次数的
        return {t: s for t, s in target_map.items()
                if s["total"] >= min_attempts}

    def get_failing_targets(self) -> List[Dict]:
        """反复失败的目标列表（失败率 > 50% 且尝试 >= 2）"""
        result = []
        for target, stats in self.get_target_stats(min_attempts=2).items():
            if stats["total"] >= 2 and stats["failure"] / stats["total"] > 0.5:
                result.append({
                    "target": target[:60],
                    "attempts": stats["total"],
                    "failures": stats["failure"],
                    "fail_rate": round(stats["failure"] / stats["total"], 2),
                })
        result.sort(key=lambda x: -x["fail_rate"])
        return result

    def get_successful_targets(self) -> List[Dict]:
        """成功目标列表（成功率 >= 70% 且尝试 >= 2）"""
        result = []
        for target, stats in self.get_target_stats(min_attempts=2).items():
            success_rate = stats["success"] / stats["total"]
            if success_rate >= 0.7:
                result.append({
                    "target": target[:60],
                    "attempts": stats["total"],
                    "successes": stats["success"],
                    "success_rate": round(success_rate, 2),
                })
        result.sort(key=lambda x: -x["success_rate"])
        return result

    def get_recent_successful_directions(self, n_cycles: int = 5) -> List[str]:
        """最近 n 轮中成功的方向列表"""
        current_cycle = max((r.get("cycle", 0) for r in self.records), default=0)
        threshold = max(0, current_cycle - n_cycles)

        targets = set()
        for r in self.records:
            if (r.get("cycle", 0) >= threshold
                    and r.get("result") == "success"
                    and r.get("target")):
                targets.add(r["target"][:60])
        return list(targets)

    # ── 方向偏好 ──────────────────────────────────────────

    def get_bias(self, action_type: str, target: str = "") -> float:
        """
        基于历史行为给出方向偏好分。

        Returns -0.3 ~ +0.3:
          +0.3 → 该方向历史成功率很高，鼓励
          -0.3 → 该方向反复失败，抑制
           0.0 → 无历史数据，中性
        """
        if not self.records:
            return 0.0

        # 1. 同操作类型的整体成功率
        stats = self.get_action_stats()
        at_stats = stats.get(action_type)
        if not at_stats or at_stats["total"] < 2:
            return 0.0

        base_rate = at_stats["success_rate"]

        # 2. 如果该方向反复失败 → 惩罚
        if target:
            target_stats = self.get_target_stats(min_attempts=1)
            ts = target_stats.get(target[:60])
            if ts and ts["total"] >= 2:
                fail_rate = ts["failure"] / ts["total"]
                if fail_rate > 0.5:
                    return -0.3  # 反复失败，强烈抑制
                if fail_rate > 0.3:
                    return -0.1  # 偶有失败，轻微抑制

        # 3. 根据历史成功率给分
        if base_rate >= 0.8:
            return 0.3   # 该类型操作一直很成功 → 鼓励
        elif base_rate >= 0.6:
            return 0.1   # 还行 → 轻微鼓励
        elif base_rate <= 0.3:
            return -0.25  # 经常失败 → 强烈抑制，直接跳过问题生成
        return 0.0

    # ── 报告 ──────────────────────────────────────────────

    def get_report(self, cycle: int) -> str:
        """为反思审计生成行为反馈报告"""
        lines = []

        stats = self.get_action_stats()
        lines.append(f"📊 行为统计 ({len(self.records)} 条记录):")
        for at, s in sorted(stats.items()):
            lines.append(f"   {at}: {s['total']} 次尝试, "
                         f"成功率 {s['success_rate']:.0%}")

        failing = self.get_failing_targets()
        if failing:
            lines.append(f"\n⚠️ 反复失败的方向 ({len(failing)} 个):")
            for f in failing[:3]:
                lines.append(f"   {f['target']}: "
                             f"失败 {f['failures']}/{f['attempts']} 次")

        successful = self.get_successful_targets()
        if successful:
            lines.append(f"\n✅ 成功方向 ({len(successful)} 个):")
            for s in successful[:3]:
                lines.append(f"   {s['target']}: "
                             f"成功 {s['successes']}/{s['attempts']} 次")

        recent = self.get_recent_successful_directions()
        if recent:
            lines.append(f"\n🔥 近期成功方向:")
            for t in recent[:5]:
                lines.append(f"   {t}")

        return "\n".join(lines)
