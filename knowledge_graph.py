#!/usr/bin/env python3
"""
知识图 — 实体-关系知识图，替换扁平 KB
纯 dict + list，不依赖任何外部库
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple


@dataclass
class GraphEntity:
    id: str
    name: str
    type: str  # concept | module | function | pattern
    properties: Dict[str, Any] = field(default_factory=dict)
    created: str = ""
    updated: str = ""


@dataclass
class Relation:
    source: str
    target: str
    rel_type: str   # depends_on | implements | related_to | prerequisite | similar_to
    weight: float = 1.0


class KnowledgeGraph:
    """实体-关系知识图"""

    def __init__(self):
        self._entities: Dict[str, GraphEntity] = {}
        self._relations: List[Relation] = []
        self._file_path = Path("data") / "knowledge_graph.json"
        self._batch_mode: bool = False
        self._pending_save: bool = False
        self._load()

    # ── 实体操作 ────────────────────────────────────

    def add_entity(self, name: str, type: str,
                   properties: Dict[str, Any] = None) -> str:
        """添加实体，返回 id"""
        now = datetime.now().isoformat()
        eid = str(uuid.uuid4())
        self._entities[eid] = GraphEntity(
            id=eid, name=name, type=type,
            properties=properties or {},
            created=now, updated=now,
        )
        self._save()
        return eid

    def get_entity(self, eid: str) -> Optional[GraphEntity]:
        return self._entities.get(eid)

    def find_entity(self, name: str) -> Optional[GraphEntity]:
        for e in self._entities.values():
            if e.name == name:
                return e
        return None

    def find_entities(self, type: str = None) -> List[GraphEntity]:
        if type:
            return [e for e in self._entities.values() if e.type == type]
        return list(self._entities.values())

    def remove_entity(self, eid: str) -> bool:
        if eid not in self._entities:
            return False
        self._entities.pop(eid)
        self._relations = [r for r in self._relations
                          if r.source != eid and r.target != eid]
        self._save()
        return True

    def update_entity(self, eid: str, properties: Dict[str, Any]) -> bool:
        entity = self._entities.get(eid)
        if not entity:
            return False
        entity.properties.update(properties)
        entity.updated = datetime.now().isoformat()
        self._save()
        return True

    # ── 关系操作 ────────────────────────────────────

    def add_relation(self, source: str, target: str,
                     rel_type: str, weight: float = 1.0) -> bool:
        source_ok = source in self._entities
        target_ok = target in self._entities
        if not source_ok or not target_ok:
            return False
        self._relations.append(Relation(source, target, rel_type, weight))
        self._save()
        return True

    def get_relations(self, eid: str = None,
                      rel_type: str = None) -> List[Relation]:
        results = self._relations
        if eid:
            results = [r for r in results
                      if r.source == eid or r.target == eid]
        if rel_type:
            results = [r for r in results if r.rel_type == rel_type]
        return results

    def remove_relations(self, source: str = None,
                         target: str = None, rel_type: str = None):
        before = len(self._relations)
        self._relations = [
            r for r in self._relations
            if not (
                (source is None or r.source == source) and
                (target is None or r.target == target) and
                (rel_type is None or r.rel_type == rel_type)
            )
        ]
        if len(self._relations) != before:
            self._save()

    # ── 图分析 ──────────────────────────────────────

    def find_gaps(self) -> List[Dict[str, Any]]:
        """找到知识图中的缺口：孤立实体、未连接的实体"""
        gaps = []
        all_ids = set(self._entities.keys())
        connected_ids: Set[str] = set()
        for r in self._relations:
            connected_ids.add(r.source)
            connected_ids.add(r.target)

        # 孤立实体（没有关系的实体）
        for eid in all_ids:
            if eid not in connected_ids:
                entity = self._entities[eid]
                gaps.append({
                    "type": "isolated",
                    "entity_id": eid,
                    "entity_name": entity.name,
                    "entity_type": entity.type,
                    "detail": f"实体 '{entity.name}' 没有建立任何关系"
                })

        # 单向依赖（只依赖别人但没人依赖它，且不是顶层概念）
        for eid in all_ids:
            entity = self._entities[eid]
            if entity.type == "concept":
                is_source = any(r.source == eid for r in self._relations)
                is_target = any(r.target == eid for r in self._relations)
                if is_source and not is_target:
                    gaps.append({
                        "type": "unreferenced_concept",
                        "entity_id": eid,
                        "entity_name": entity.name,
                        "entity_type": entity.type,
                        "detail": f"概念 '{entity.name}' 没有被任何其他实体引用"
                    })

        return gaps

    def find_bridges(self) -> List[Dict[str, Any]]:
        """找到桥接不同实体群的实体"""
        from collections import defaultdict, deque

        # 构建邻接表
        adj: Dict[str, Set[str]] = defaultdict(set)
        for r in self._relations:
            adj[r.source].add(r.target)
            adj[r.target].add(r.source)

        # 计算群落（BFS）
        visited: Set[str] = set()
        communities: List[Set[str]] = []
        for eid in self._entities:
            if eid in visited:
                continue
            queue = deque([eid])
            group: Set[str] = set()
            while queue:
                node = queue.popleft()
                if node in visited:
                    continue
                visited.add(node)
                group.add(node)
                for neighbor in adj.get(node, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)
            communities.append(group)

        # 桥接者：属于多个群？不可能，只能属于一个群。
        # 跨界者：连接度 > 平均连接度 2x，且连接不同类型的实体
        degree = {e: len(adj[e]) for e in self._entities}
        avg_deg = sum(degree.values()) / max(1, len(degree))
        bridges = []
        for eid, deg in degree.items():
            if deg >= avg_deg * 2 and deg >= 3:
                entity = self._entities[eid]
                # 检查连接类型多样性
                connected_types = set()
                for r in self.get_relations(eid):
                    neighbor = r.target if r.source == eid else r.source
                    neighbor_e = self._entities.get(neighbor)
                    if neighbor_e:
                        connected_types.add(neighbor_e.type)
                if len(connected_types) >= 2:
                    bridges.append({
                        "entity_id": eid,
                        "entity_name": entity.name,
                        "entity_type": entity.type,
                        "degree": deg,
                        "connects_types": list(connected_types),
                        "communities": len(communities),
                    })
        return sorted(bridges, key=lambda x: -x["degree"])

    def get_subgraph(self, eid: str, max_depth: int = 2) -> Dict[str, Any]:
        """提取以 eid 为中心的局部子图"""
        result = {"center": eid, "entities": {}, "relations": []}
        visited: Set[str] = set()

        def walk(node: str, depth: int):
            if depth > max_depth or node in visited:
                return
            visited.add(node)
            entity = self._entities.get(node)
            if entity:
                result["entities"][node] = {
                    "name": entity.name,
                    "type": entity.type,
                }
            for r in self._relations:
                if r.source == node:
                    result["relations"].append({
                        "source": r.source, "target": r.target,
                        "type": r.rel_type, "weight": r.weight,
                    })
                    walk(r.target, depth + 1)
                elif r.target == node:
                    result["relations"].append({
                        "source": r.source, "target": r.target,
                        "type": r.rel_type, "weight": r.weight,
                    })
                    walk(r.source, depth + 1)

        walk(eid, 0)
        return result

    def traverse(self, start_id: str, rel_types: List[str] = None,
                 max_depth: int = 5) -> List[Dict[str, Any]]:
        """图遍历，返回路径"""
        from collections import deque

        paths = []
        queue = deque([(start_id, [start_id], 0)])

        while queue:
            node, path, depth = queue.popleft()
            if depth > max_depth:
                continue

            entity = self._entities.get(node)
            if depth > 0:
                paths.append({
                    "entity_id": node,
                    "entity_name": entity.name if entity else "?",
                    "depth": depth,
                    "path": path.copy(),
                })

            for r in self._relations:
                if rel_types and r.rel_type not in rel_types:
                    continue
                if r.source == node and r.target not in path:
                    queue.append((r.target, path + [r.target], depth + 1))
                elif r.target == node and r.source not in path:
                    queue.append((r.source, path + [r.source], depth + 1))

        return paths

    def merge_from_knowledge_base(self, kb_data: List[Dict[str, Any]]):
        """从 KnowledgeBase 导入已有知识条目为概念实体（批量写入，仅末尾一次保存）"""
        self._batch_mode = True
        self._pending_save = False
        try:
            for item in kb_data:
                topic = item.get("topic", "")
                if not topic:
                    continue
                existing = self.find_entity(topic)
                if existing:
                    continue
                eid = self.add_entity(topic, "concept", {
                    "category": item.get("category", ""),
                    "source": item.get("source", ""),
                    "keywords": item.get("keywords", []),
                })
                # 分类关系
                category = item.get("category", "")
                cat_entity = self.find_entity(category)
                if not cat_entity:
                    cat_id = self.add_entity(category, "concept",
                                             {"category": "meta"})
                else:
                    cat_id = cat_entity.id
                self.add_relation(eid, cat_id, "belongs_to")

                # 关键词关系
                keywords = item.get("keywords", [])
                for kw in keywords[:5]:
                    kw_entity = self.find_entity(kw)
                    if not kw_entity:
                        kw_id = self.add_entity(kw, "concept",
                                                {"keyword": True})
                    else:
                        kw_id = kw_entity.id
                    self.add_relation(eid, kw_id, "related_to", 0.5)
        finally:
            self.flush()

    def get_statistics(self) -> Dict[str, Any]:
        """图统计"""
        types: Dict[str, int] = {}
        for e in self._entities.values():
            types[e.type] = types.get(e.type, 0) + 1

        rel_types: Dict[str, int] = {}
        for r in self._relations:
            rel_types[r.rel_type] = rel_types.get(r.rel_type, 0) + 1

        gaps = self.find_gaps()
        bridges = self.find_bridges()

        return {
            "total_entities": len(self._entities),
            "total_relations": len(self._relations),
            "entity_types": types,
            "relation_types": rel_types,
            "isolated_count": len(gaps),
            "bridge_count": len(bridges),
        }

    # ── 持久化 ────────────────────────────────────────

    def _save(self):
        if self._batch_mode:
            self._pending_save = True
            return
        try:
            data = {
                "entities": {eid: {
                    "id": e.id, "name": e.name, "type": e.type,
                    "properties": e.properties,
                    "created": e.created, "updated": e.updated,
                } for eid, e in self._entities.items()},
                "relations": [
                    {"source": r.source, "target": r.target,
                     "rel_type": r.rel_type, "weight": r.weight}
                    for r in self._relations
                ],
            }
            self._file_path.parent.mkdir(exist_ok=True)
            self._file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception as e:
            print(f"⚠️  知识图保存失败: {e}")

    def flush(self):
        """批处理模式下强制写入磁盘并退出批处理模式"""
        if self._pending_save:
            self._pending_save = False
            self._batch_mode = False
            self._save()
        self._batch_mode = False

    def _load(self):
        try:
            if self._file_path.exists():
                data = json.loads(
                    self._file_path.read_text(encoding="utf-8"))
                for eid, e in data.get("entities", {}).items():
                    self._entities[eid] = GraphEntity(**e)
                for r in data.get("relations", []):
                    self._relations.append(Relation(**r))
        except Exception as e:
            print(f"⚠️  知识图加载失败: {e}")


if __name__ == "__main__":
    kg = KnowledgeGraph()

    # 测试基础操作
    e1 = kg.add_entity("机器学习", "concept",
                       {"category": "数据科学"})
    e2 = kg.add_entity("监督学习", "concept",
                       {"category": "数据科学"})
    e3 = kg.add_entity("Python", "concept",
                       {"category": "工程"})
    e4 = kg.add_entity("感知系统", "module",
                       {"file": "cognitive_architecture.py"})
    kg.add_relation(e1, e2, "prerequisite", 0.8)
    kg.add_relation(e3, e1, "related_to", 0.3)

    stats = kg.get_statistics()
    print(f"实体: {stats['total_entities']}, 关系: {stats['total_relations']}")
    gaps = kg.find_gaps()
    print(f"孤立实体: {len(gaps)}")
    for g in gaps:
        print(f"  - {g['entity_name']} ({g['type']})")
    bridges = kg.find_bridges()
    print(f"桥接实体: {len(bridges)}")

    sub = kg.get_subgraph(e1, max_depth=1)
    print(f"子图: 中心={sub['center']}, 实体={len(sub['entities'])}, 关系={len(sub['relations'])}")
    print("✅ 知识图测试完成")
