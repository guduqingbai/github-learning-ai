"""
📔 周期日记 — 记录每轮思考循环的关键事件
受 Phoenix Immortal Diary 系统启发 (memory/diary.py)
轻量级，只记录最近 200 条，自动裁剪
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class CycleDiary:
    """周期日记：记录每轮循环的关键事件"""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.diary_file = self.data_dir / "cycle_diary.json"
        self._entries: List[Dict] = []
        self._load()

    def _load(self):
        if self.diary_file.exists():
            try:
                self._entries = json.loads(self.diary_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, Exception):
                self._entries = []

    def _save(self):
        try:
            trimmed = self._entries[-200:]
            self.diary_file.write_text(
                json.dumps(trimmed, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            self._entries = trimmed
        except Exception:
            pass

    def record(self, event_type: str, detail: str, metadata: Optional[Dict] = None):
        self._entries.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "detail": detail,
            "metadata": metadata or {},
        })
        self._save()

    def recent(self, n: int = 10) -> List[Dict]:
        return self._entries[-n:]

    def events_by_type(self, event_type: str, n: int = 20) -> List[Dict]:
        matched = [e for e in self._entries if e["type"] == event_type]
        return matched[-n:]

    def summary(self) -> Dict[str, Any]:
        total = len(self._entries)
        type_counts: Dict[str, int] = {}
        for e in self._entries:
            t = e["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        return {
            "total_events": total,
            "event_types": type_counts,
            "last_event": self._entries[-1] if self._entries else None,
        }
