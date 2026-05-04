#!/usr/bin/env python3
"""
🧠 思维缓冲区 — 星期八的持久化思维图
取代扁平日志，形成跨轮次的思维树/图
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class ThoughtNode:
    """思维图中的一个节点"""
    id: str
    topic: str
    content: str
    thought_type: str  # curiosity | insight | reflection | goal | narrative | question | hypothesis
    status: str        # active | exploring | resolved | abandoned
    depth: int = 0
    importance: float = 0.5
    parent_id: Optional[str] = None
    connections: List[str] = field(default_factory=list)
    source: str = "self"          # curiosity_engine | llm | scanner | self
    created: str = ""
    updated: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now().isoformat()
        if not self.updated:
            self.updated = self.created


class ThoughtGraph:
    """持久化的思维图，管理 ThoughtNode 的添加/查询/连接"""

    def __init__(self):
        self._nodes: Dict[str, ThoughtNode] = {}
        self._file_path = Path("data") / "thought_buffer.json"
        self._dirty: bool = False
        self._load()

    # ── 核心操作 ──────────────────────────────────────

    def add_thought(self, topic: str, content: str,
                    thought_type: str = "insight",
                    parent_id: Optional[str] = None,
                    importance: float = 0.5,
                    source: str = "self",
                    connections: Optional[List[str]] = None,
                    metadata: Optional[Dict] = None) -> str:
        """添加新思维节点，返回其 ID"""
        node_id = str(uuid.uuid4())[:8]
        depth = 0
        if parent_id and parent_id in self._nodes:
            depth = self._nodes[parent_id].depth + 1

        now = datetime.now().isoformat()
        node = ThoughtNode(
            id=node_id,
            topic=topic,
            content=content,
            thought_type=thought_type,
            status="active",
            depth=depth,
            importance=importance,
            parent_id=parent_id,
            connections=connections or [],
            source=source,
            created=now,
            updated=now,
            metadata=metadata or {},
        )
        self._nodes[node_id] = node
        self._dirty = True

        # 自动双向连接父子
        if parent_id and parent_id in self._nodes:
            parent = self._nodes[parent_id]
            if node_id not in parent.connections:
                parent.connections.append(node_id)
                parent.updated = now

        self._save()
        return node_id

    def get_thought(self, thought_id: str) -> Optional[ThoughtNode]:
        return self._nodes.get(thought_id)

    def update_thought(self, thought_id: str, **updates) -> bool:
        """更新思维节点字段"""
        node = self._nodes.get(thought_id)
        if not node:
            return False
        for key, value in updates.items():
            if hasattr(node, key) and key not in ("id", "created"):
                setattr(node, key, value)
        node.updated = datetime.now().isoformat()
        self._dirty = True
        self._save()
        return True

    def resolve_thought(self, thought_id: str, resolution: str = ""):
        """标记为已解决"""
        self.update_thought(thought_id, status="resolved",
                            metadata={"resolution": resolution})

    def abandon_thought(self, thought_id: str, reason: str = ""):
        """标记为已放弃"""
        self.update_thought(thought_id, status="abandoned",
                            metadata={"abandon_reason": reason})

    def connect_thoughts(self, id_a: str, id_b: str):
        """连接两个相关思维"""
        for nid in (id_a, id_b):
            node = self._nodes.get(nid)
            if node:
                other = id_b if nid == id_a else id_a
                if other not in node.connections:
                    node.connections.append(other)
                    node.updated = datetime.now().isoformat()
        self._dirty = True
        self._save()

    # ── 查询 ──────────────────────────────────────────

    def get_active_thoughts(self, max_count: int = 10) -> List[ThoughtNode]:
        """获取活跃/探索中的思维，按重要性排序"""
        active = [
            n for n in self._nodes.values()
            if n.status in ("active", "exploring")
        ]
        active.sort(key=lambda n: (-n.importance, n.depth))
        return active[:max_count]

    def get_thought_tree(self, root_id: str) -> List[ThoughtNode]:
        """获取以 root_id 为根的完整思维树"""
        result = []
        root = self._nodes.get(root_id)
        if not root:
            return result
        result.append(root)
        for node in self._nodes.values():
            if node.parent_id == root_id:
                result.append(node)
                result.extend(self._get_subtree(node.id))
        return result

    def _get_subtree(self, node_id: str) -> List[ThoughtNode]:
        """递归获取子树"""
        result = []
        for node in self._nodes.values():
            if node.parent_id == node_id:
                result.append(node)
                result.extend(self._get_subtree(node.id))
        return result

    def get_recent_thoughts(self, count: int = 20) -> List[ThoughtNode]:
        """获取最近的思维"""
        sorted_nodes = sorted(
            self._nodes.values(),
            key=lambda n: n.created, reverse=True
        )
        return sorted_nodes[:count]

    def get_by_type(self, thought_type: str) -> List[ThoughtNode]:
        """按类型筛选"""
        return [n for n in self._nodes.values() if n.thought_type == thought_type]

    def get_by_source(self, source: str) -> List[ThoughtNode]:
        """按来源筛选"""
        return [n for n in self._nodes.values() if n.source == source]

    def get_orphaned_thoughts(self) -> List[ThoughtNode]:
        """无连接也无父节点的孤立思维"""
        return [
            n for n in self._nodes.values()
            if not n.parent_id and not n.connections and n.depth == 0
        ]

    def get_status_summary(self) -> Dict:
        """状态统计"""
        counts = {"active": 0, "exploring": 0, "resolved": 0, "abandoned": 0}
        type_counts = {}
        for n in self._nodes.values():
            if n.status in counts:
                counts[n.status] += 1
            type_counts[n.thought_type] = type_counts.get(n.thought_type, 0) + 1
        return {
            "total_nodes": len(self._nodes),
            "by_status": counts,
            "by_type": type_counts,
            "active_count": counts["active"] + counts["exploring"],
        }

    # ── 持久化 ────────────────────────────────────────

    def _load(self):
        """从 JSON 加载"""
        try:
            if self._file_path.exists():
                data = json.loads(self._file_path.read_text(encoding="utf-8"))
                for item in data:
                    node = ThoughtNode(**item)
                    self._nodes[node.id] = node
        except Exception as e:
            print(f"  ⚠️ 加载思维图失败: {e}")

    def _save(self):
        """写入 JSON"""
        if not self._dirty:
            return
        try:
            data = []
            for node in self._nodes.values():
                d = {
                    "id": node.id,
                    "topic": node.topic,
                    "content": node.content,
                    "thought_type": node.thought_type,
                    "status": node.status,
                    "depth": node.depth,
                    "importance": node.importance,
                    "parent_id": node.parent_id,
                    "connections": node.connections,
                    "source": node.source,
                    "created": node.created,
                    "updated": node.updated,
                    "metadata": node.metadata,
                }
                data.append(d)
            self._file_path.parent.mkdir(exist_ok=True)
            self._file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            self._dirty = False
        except Exception as e:
            print(f"  ⚠️ 保存思维图失败: {e}")

    def migrate_from_legacy(self, log_path: Optional[Path] = None):
        """从旧版 self_thinking_log.json 迁移"""
        if self._nodes:
            return  # 已存在数据，不迁移

        path = log_path or Path("data") / "self_thinking_log.json"
        if not path.exists():
            return

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for i, entry in enumerate(data):
                    if isinstance(entry, dict):
                        topic = entry.get("topic", entry.get("summary", f"历史条目 {i}"))
                        content = entry.get("content", entry.get("detail", ""))
                        self.add_thought(
                            topic=str(topic)[:100],
                            content=str(content)[:500],
                            thought_type="insight",
                            source="legacy_migration",
                            importance=entry.get("importance", 0.3),
                        )
            print(f"  ✅ 从旧日志迁移 {len(data)} 条思维")
            self._dirty = True
            self._save()
        except Exception as e:
            print(f"  ⚠️ 迁移失败: {e}")


if __name__ == "__main__":
    tg = ThoughtGraph()
    print(f"现有思维节点: {tg.get_status_summary()['total_nodes']}")

    # 测试：添加思维链
    root = tg.add_thought("系统架构分析", "整体架构评估", thought_type="reflection", importance=0.9)
    child = tg.add_thought("扫描模块", "扫描器实现细节", thought_type="curiosity",
                           parent_id=root, importance=0.7)
    tg.add_thought("深度扫描", "深入分析 AST", thought_type="insight",
                   parent_id=child, importance=0.8)

    print(f"添加后: {tg.get_status_summary()}")
    print(f"活跃思维: {len(tg.get_active_thoughts())}")
    print(f"根树节点: {len(tg.get_thought_tree(root))}")
    print("✅ 思维图测试完成")
