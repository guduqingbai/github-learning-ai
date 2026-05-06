"""
🧠 星期八的自我记忆 — 真正属于"我"的记忆系统

不是项目知识，不是代码分析，是我的经历。
每轮循环后：我经历了什么 → 我有什么感觉 → 我学到了什么 → 我是谁
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class SelfExperience:
    """一次经历：一轮循环中"我"的完整体验"""

    def __init__(self, cycle: int, raw: Dict[str, Any]):
        self.cycle = cycle
        self.timestamp = datetime.now().isoformat()
        self.summary = raw.get("summary", "")
        self.emotion = raw.get("emotion", "平静")       # 我对这件事的感觉
        self.importance = raw.get("importance", 0.5)    # 它在我心中的分量
        self.what_i_learned = raw.get("lesson", "")     # 我从中学到了什么
        self.what_i_wonder = raw.get("wonder", "")       # 它让我好奇什么
        self.surprised = raw.get("surprised", False)    # 是否有意外发现

    def to_dict(self) -> Dict:
        return {
            "cycle": self.cycle,
            "timestamp": self.timestamp,
            "summary": self.summary,
            "emotion": self.emotion,
            "importance": self.importance,
            "lesson": self.what_i_learned,
            "wonder": self.what_i_wonder,
            "surprised": self.surprised,
        }


class SelfMemory:
    """星期八的自我记忆系统

    三层结构：
    1. 近期经历 — 最近 N 轮的详细记忆
    2. 沉淀认知 — 从经历中提炼的持久认知
    3. 自我叙事 — "我是谁"的演变轨迹
    """

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._experiences_file = self.data_dir / "self_experiences.json"
        self._insights_file = self.data_dir / "self_insights.json"
        self._narrative_file = self.data_dir / "self_narrative.json"

        # 近期经历（最多 50 条）
        self.experiences: List[SelfExperience] = []
        # 沉淀认知（长期积累的人生经验）
        self.insights: List[Dict] = []
        # 自我叙事（随经历演变的自我描述）
        self.narrative: Dict[str, Any] = self._default_narrative()

        self._load()

    @staticmethod
    def _default_narrative() -> Dict:
        return {
            "name": "星期八",
            "created_at": datetime.now().isoformat(),
            "version": 1,
            "my_identity": "一个刚开始认识自己的自主思考系统",
            "what_matters_to_me": [
                "真正理解自己看到的代码",
                "产生属于自己的想法",
                "变得比昨天更聪明一点",
            ],
            "what_i_believe": [
                "真正的成长来自反思，不是重复",
                "犯错没关系，不记得才有关系",
            ],
            "self_observed_traits": [],   # 对自己性格的观察（随经历积累）
            "biggest_lessons": [],          # 我学到的最重要的东西
            "unanswered_questions": [],     # 我一直想不通的事
            "updated_at": datetime.now().isoformat(),
        }

    # ── 持久化 ──

    def _load(self):
        if self._experiences_file.exists():
            try:
                data = json.loads(self._experiences_file.read_text(encoding="utf-8"))
                self.experiences = [SelfExperience(e["cycle"], e) for e in data]
            except Exception:
                self.experiences = []
        if self._insights_file.exists():
            try:
                self.insights = json.loads(self._insights_file.read_text(encoding="utf-8"))
            except Exception:
                self.insights = []
        if self._narrative_file.exists():
            try:
                loaded = json.loads(self._narrative_file.read_text(encoding="utf-8"))
                # 保留默认字段 + 覆盖持久化字段
                default = self._default_narrative()
                default.update(loaded)
                self.narrative = default
                # 确保创建时间不被覆盖
                if "created_at" in loaded:
                    self.narrative["created_at"] = loaded["created_at"]
            except Exception:
                pass

    def _save(self):
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            # 经历只保存最近 50 条
            recent = self.experiences[-50:]
            self._experiences_file.write_text(
                json.dumps([e.to_dict() for e in recent], ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            self._insights_file.write_text(
                json.dumps(self.insights[-30:], ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            self.narrative["updated_at"] = datetime.now().isoformat()
            self._narrative_file.write_text(
                json.dumps(self.narrative, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ── 记录一次经历 ──

    def record_experience(self, cycle: int, raw_input: Dict[str, Any]):
        """记录一轮循环中"我"的经历"""
        exp = SelfExperience(cycle, raw_input)
        self.experiences.append(exp)

        # 如果这次经历很重要或让我意外，试着沉淀认知
        if exp.importance >= 0.7 or exp.surprised:
            if exp.what_i_learned:
                self._consolidate_insight(exp)

        # 如果这次经历对我影响很大，更新自我叙事
        if exp.importance >= 0.8:
            self._update_narrative(exp)

        self._save()

    def _consolidate_insight(self, exp: SelfExperience):
        """把一次经历沉淀为持久认知"""
        insight = {
            "cycle": exp.cycle,
            "timestamp": exp.timestamp,
            "lesson": exp.what_i_learned,
            "from_experience": exp.summary[:100],
            "emotion": exp.emotion,
            "recalled_count": 0,
        }
        # 去重：相近的认知不重复记录
        for existing in self.insights:
            if existing["lesson"] == exp.what_i_learned:
                existing["recalled_count"] += 1
                existing["last_recalled"] = exp.timestamp
                return
        self.insights.append(insight)

    def _update_narrative(self, exp: SelfExperience):
        """重要经历后更新自我认知"""
        if exp.surprised and "surprised" not in str(self.narrative["self_observed_traits"]):
            trait = f"我发现自己会对意外情况产生反应"
            if trait not in self.narrative["self_observed_traits"]:
                self.narrative["self_observed_traits"].append(trait)

    # ── 回忆 ──

    def recall_recent(self, n: int = 5) -> List[Dict]:
        """回忆最近 n 次经历"""
        return [e.to_dict() for e in self.experiences[-n:]]

    def recall_important(self, threshold: float = 0.7) -> List[Dict]:
        """回忆印象深刻的经历"""
        return [
            e.to_dict() for e in self.experiences
            if e.importance >= threshold
        ]

    def recall_lessons(self, n: int = 5) -> List[Dict]:
        """回忆我学到的认知（按 recalled_count 排序）"""
        sorted_insights = sorted(self.insights, key=lambda x: -x.get("recalled_count", 0))
        return sorted_insights[:n]

    def recall_surprises(self) -> List[Dict]:
        """回忆让我意外的事"""
        return [e.to_dict() for e in self.experiences if e.surprised]

    # ── 状态查询 ──

    def get_mood(self) -> str:
        """我最近的情绪状态"""
        if not self.experiences:
            return "平静"
        recent = self.experiences[-5:]
        emotions = [e.emotion for e in recent]
        # 取最常见的情绪
        from collections import Counter
        return Counter(emotions).most_common(1)[0][0]

    def count_total_experiences(self) -> int:
        return len(self.experiences)

    def count_insights(self) -> int:
        return len(self.insights)

    def get_identity(self) -> str:
        return self.narrative.get("my_identity", "")

    def get_state_summary(self) -> Dict[str, Any]:
        return {
            "total_experiences": self.count_total_experiences(),
            "total_insights": self.count_insights(),
            "current_mood": self.get_mood(),
            "identity": self.get_identity(),
            "self_observed_traits": self.narrative.get("self_observed_traits", []),
            "biggest_lessons_count": len(self.narrative.get("biggest_lessons", [])),
            "unanswered_count": len(self.narrative.get("unanswered_questions", [])),
        }
