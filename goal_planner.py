#!/usr/bin/env python3
"""
目标规划器 — 让星期八有长期目标，不只是 Reactive 好奇心
从持久问题自动生成目标，追踪进度，调整思考优先级
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class Goal:
    id: str
    description: str
    category: str       # knowledge | code_quality | architecture | exploration
    target_value: float
    current_value: float = 0.0
    progress: float = 0.0  # 0.0 ~ 1.0
    created_cycle: int = 0
    deadline_cycle: int = 0  # 0 = 无截止
    status: str = "active"   # active | completed | abandoned
    source: str = ""         # 从哪来的：isolated_entities | docstring | complexity


class GoalPlanner:
    """长期目标规划器"""

    def __init__(self):
        self._file_path = Path("data") / "goals.json"
        self._goals: Dict[str, Goal] = {}
        self._load()

    # ── 目标管理 ────────────────────────────────────

    def add_goal(self, description: str, category: str,
                 target_value: float, source: str = "",
                 deadline_cycle: int = 0) -> str:
        """添加新目标"""
        gid = str(uuid.uuid4())[:8]
        self._goals[gid] = Goal(
            id=gid, description=description, category=category,
            target_value=target_value,
            created_cycle=self._current_cycle(),
            deadline_cycle=deadline_cycle,
            source=source,
        )
        self._save()
        return gid

    def update_progress(self, goal_id: str, current_value: float):
        """更新目标进度"""
        goal = self._goals.get(goal_id)
        if not goal or goal.status != "active":
            return
        goal.current_value = current_value
        goal.progress = min(1.0, current_value / max(1, goal.target_value))
        if goal.progress >= 1.0:
            goal.status = "completed"
        self._save()

    def get_active_goals(self) -> List[Goal]:
        """获取进行中的目标"""
        return [g for g in self._goals.values() if g.status == "active"]

    def get_completed_goals(self) -> List[Goal]:
        return [g for g in self._goals.values() if g.status == "completed"]

    # ── 从系统状态自动生成目标 ────────────────────

    def auto_generate(self, kg_stats: Dict[str, Any] = None,
                      pe_results: Dict[str, Any] = None):
        """根据系统状态自动生成/更新目标"""
        cycle = self._current_cycle()
        existing = {g.source: g for g in self._goals.values()}

        # 知识连接目标
        if kg_stats:
            isolated = kg_stats.get("isolated_count", 0)
            total = kg_stats.get("total_entities", 1)
            if isolated > total * 0.1:  # 超过 10% 孤立
                target = max(1, int(isolated * 0.5))  # 减半
                src = "isolated_entities"
                if src not in existing:
                    self.add_goal(
                        f"减少孤立实体: {isolated} → {target}",
                        "knowledge", float(target), src, cycle + 10)
                else:
                    self.update_progress(existing[src].id, float(isolated))

        # 代码复杂度目标
        if pe_results:
            complex_mods = pe_results.get("complex_modules", [])
            if complex_mods:
                src = "complex_modules"
                count = len(complex_mods)
                if src not in existing:
                    self.add_goal(
                        f"简化 {count} 个复杂模块",
                        "code_quality", float(count), src, cycle + 20)
                else:
                    self.update_progress(existing[src].id, float(count))

            dead_code = pe_results.get("dead_code", [])
            if dead_code:
                total_dead = sum(d.get("unused_count", 0) for d in dead_code)
                src = "dead_code"
                if src not in existing and total_dead > 10:
                    self.add_goal(
                        f"清理 {total_dead} 个未使用定义",
                        "code_quality", float(total_dead), src, cycle + 30)
                else:
                    self.update_progress(existing[src].id, float(total_dead))

        # 归档已完成/过期的
        self._archive_completed()

    def get_goal_priorities(self) -> Dict[str, Dict[str, float]]:
        """
        返回目标优先级详情。
        每类目标包含 priority(紧迫度)、urgency(截止压力)、difficulty(难度)。
        """
        priorities = {}
        for g in self.get_active_goals():
            if g.progress < 0.5:
                base = 1.0 - g.progress
                cat = g.category
                if cat not in priorities or base > priorities[cat]["priority"]:
                    urgency = 0.3
                    if g.deadline_cycle > 0:
                        remaining = g.deadline_cycle - self._current_cycle()
                        urgency = min(1.0, max(0.0, remaining / 20.0))
                    priorities[cat] = {
                        "priority": round(base, 3),
                        "urgency": round(1.0 - urgency, 3),  # 越近越紧迫
                        "difficulty": round(g.progress, 3),   # 进展越少越难
                    }
        return priorities

    def get_summary(self) -> Dict[str, Any]:
        """目标摘要"""
        active = self.get_active_goals()
        completed = self.get_completed_goals()
        return {
            "active_count": len(active),
            "completed_count": len(completed),
            "active": [
                {"id": g.id, "desc": g.description,
                 "progress": round(g.progress, 2),
                 "category": g.category}
                for g in active
            ],
        }

    # ── 内部 ────────────────────────────────────────

    def _archive_completed(self):
        for g in list(self._goals.values()):
            if g.status in ("completed", "abandoned"):
                continue
            if g.deadline_cycle > 0 and self._current_cycle() > g.deadline_cycle:
                if g.progress < 0.5:
                    g.status = "abandoned"
        self._save()

    @staticmethod
    def _current_cycle() -> int:
        try:
            cf = Path("data") / "cycle_counter.json"
            if cf.exists():
                return json.loads(cf.read_text(encoding="utf-8")).get("cycle", 0)
        except Exception:
            pass
        return 0

    def _save(self):
        try:
            data = [
                {"id": g.id, "description": g.description,
                 "category": g.category, "target_value": g.target_value,
                 "current_value": g.current_value, "progress": g.progress,
                 "created_cycle": g.created_cycle,
                 "deadline_cycle": g.deadline_cycle, "status": g.status,
                 "source": g.source}
                for g in self._goals.values()
            ]
            self._file_path.parent.mkdir(exist_ok=True)
            self._file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    def _load(self):
        try:
            if self._file_path.exists():
                data = json.loads(
                    self._file_path.read_text(encoding="utf-8"))
                for item in data:
                    g = Goal(**item)
                    self._goals[g.id] = g
        except Exception:
            pass


if __name__ == "__main__":
    gp = GoalPlanner()

    # 模拟自动生成
    gp.auto_generate(
        kg_stats={"isolated_count": 923, "total_entities": 1405},
        pe_results={
            "complex_modules": [
                {"file": "a.py"}, {"file": "b.py"}, {"file": "c.py"}
            ],
            "dead_code": [{"unused_count": 50}, {"unused_count": 30}],
        }
    )

    summary = gp.get_summary()
    print(f"活跃目标: {summary['active_count']}")
    for g in summary["active"]:
        print(f"  [{g['category']}] {g['desc']} ({g['progress']:.0%})")

    priorities = gp.get_goal_priorities()
    print(f"优先级: {priorities}")
    print("✅ 目标规划器测试完成")
