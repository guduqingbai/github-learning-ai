#!/usr/bin/env python3
"""
经验追踪器 — 让星期八记住什么方法有效、什么方法无效
跨周期记录策略 + 结果，避免重复踩坑
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import Counter


@dataclass
class ExperienceRecord:
    problem: str       # 问题标识（文件名/主题/操作类型）
    strategy: str      # 尝试的策略
    outcome: str       # success | failure | error
    error_type: str    # gate_blocked | not_found | syntax_error | empty_result
    cycle: int = 0
    timestamp: str = ""
    detail: str = ""


class ExperienceTracker:
    """跨周期经验记忆，记录什么策略对什么问题有效/无效"""

    def __init__(self):
        self._file_path = Path("data") / "experience_tracker.json"
        self._records: List[ExperienceRecord] = []
        self._load()

    # ── 记录 ────────────────────────────────────────

    def record(self, problem: str, strategy: str, outcome: str,
               error_type: str = "", cycle: int = 0,
               detail: str = ""):
        """记录一次经验"""
        self._records.append(ExperienceRecord(
            problem=problem[:100],
            strategy=strategy[:50],
            outcome=outcome,
            error_type=error_type[:30],
            cycle=cycle,
            timestamp=datetime.now().isoformat(),
            detail=detail[:200],
        ))
        # 控制内存，最多 1000 条
        if len(self._records) > 1000:
            self._records = self._records[-500:]
        self._save()

    # ── 查询 ────────────────────────────────────────

    def should_retry(self, problem: str, strategy: str,
                     max_failures: int = 3, window: int = 20) -> bool:
        """
        检查同一问题+策略是否已经失败太多次。
        window 限制只查最近 N 条记录。
        Returns True = 不应该重试（失败太多）
        """
        recent = self._records[-window:] if window > 0 else self._records
        failures = sum(
            1 for r in recent
            if r.problem == problem and r.strategy == strategy
            and r.outcome in ("failure", "error")
        )
        return failures >= max_failures

    def get_successful_strategies(self, problem: str) -> List[str]:
        """找到对某个问题曾经成功过的策略"""
        strategies = set()
        for r in self._records:
            if r.problem == problem and r.outcome == "success":
                strategies.add(r.strategy)
        return list(strategies)

    def get_failure_patterns(self, min_count: int = 2) -> List[Dict[str, Any]]:
        """跨周期统计重复失败模式"""
        pairs: Dict[str, int] = Counter()
        details: Dict[str, str] = {}

        for r in self._records:
            if r.outcome in ("failure", "error"):
                key = f"{r.problem}|{r.strategy}|{r.error_type}"
                pairs[key] += 1
                if r.detail:
                    details[key] = r.detail

        patterns = []
        for key, count in pairs.most_common():
            if count < min_count:
                break
            problem, strategy, err_type = key.split("|", 2)
            patterns.append({
                "problem": problem,
                "strategy": strategy,
                "error_type": err_type,
                "count": count,
                "detail": details.get(key, ""),
            })
        return patterns

    def get_summary(self) -> Dict[str, Any]:
        """给叙事用的经验摘要"""
        total = len(self._records)
        successes = sum(1 for r in self._records if r.outcome == "success")
        failures = sum(1 for r in self._records if r.outcome in ("failure", "error"))
        patterns = self.get_failure_patterns(min_count=3)

        # 每种策略的成功率
        strategy_stats = Counter(r.strategy for r in self._records)
        strategy_success = Counter(
            r.strategy for r in self._records if r.outcome == "success")
        strategy_rates = {
            s: round(strategy_success[s] / strategy_stats[s] * 100)
            if strategy_stats[s] > 0 else 0
            for s in strategy_stats
        }

        return {
            "total_experiences": total,
            "successes": successes,
            "failures": failures,
            "success_rate": round(successes / max(1, total) * 100),
            "critical_patterns": patterns[:5],
            "strategy_success_rates": strategy_rates,
        }

    def clear(self):
        """清空所有记录（测试用）"""
        self._records.clear()
        self._save()

    # ── 持久化 ──────────────────────────────────────

    def _save(self):
        try:
            data = [{
                "problem": r.problem,
                "strategy": r.strategy,
                "outcome": r.outcome,
                "error_type": r.error_type,
                "cycle": r.cycle,
                "timestamp": r.timestamp,
                "detail": r.detail,
            } for r in self._records]
            self._file_path.parent.mkdir(exist_ok=True)
            self._file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception as e:
            print(f"⚠️  经验保存失败: {e}")

    def _load(self):
        try:
            if self._file_path.exists():
                data = json.loads(
                    self._file_path.read_text(encoding="utf-8"))
                for item in data:
                    self._records.append(ExperienceRecord(**item))
        except Exception:
            pass


if __name__ == "__main__":
    et = ExperienceTracker()

    # 模拟记录
    et.record("fix_bare_except", "self_heal", "success", cycle=1)
    et.record("read_knowledge_base.py", "read_file", "success", cycle=1)
    et.record("fix_dead_code", "self_heal", "failure",
              "syntax_error", cycle=2, detail="AST解析失败")
    et.record("fix_dead_code", "self_heal", "failure",
              "syntax_error", cycle=3, detail="再次失败")

    # 测试查重
    print(f"应重试 fix_dead_code+self_heal? {et.should_retry('fix_dead_code', 'self_heal', 3)}")
    print(f"应重试 fix_bare_except+self_heal? {et.should_retry('fix_bare_except', 'self_heal', 3)}")

    # 测试成功策略
    print(f"fix_bare_except 的有效策略: {et.get_successful_strategies('fix_bare_except')}")

    # 测试摘要
    stats = et.get_summary()
    print(f"经验摘要: 总计{stats['total_experiences']}, 成功率{stats['success_rate']}%")
    print(f"失败模式: {stats['critical_patterns']}")
    print("✅ 经验追踪器测试完成")
