#!/usr/bin/env python3
"""
内在思考器 — 系统主动思考自己已有的知识

不依赖外部扫描或爬虫，直接从知识库、思维图、知识图中挖掘：
- 散落知识点间的潜在连接
- 知识枢纽（连接多个领域的核心实体）
- 值得深入的高价值知识

每次输出少量高质量洞察，加入常规问题优先级排序。
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class InternalInsight:
    """内在思考产生的洞察"""
    content: str
    category: str       # connection | pattern | self_question
    importance: float
    related_entities: List[str] = field(default_factory=list)
    source: str = "internal_thinker"


class InternalThinker:
    """
    纯本地内在思考器，零外部依赖。
    每轮运行 3 项分析：
    1. 知识交叉连接 — 跨类别但有共同关键词的知识对
    2. 枢纽实体分析 — 知识图中的 hubs
    3. 自我提问 — 高重要性低深度知识 + 孤立思维节点
    """

    def __init__(self):
        self._kb = None
        self._kg = None
        self._tg = None
        self._processed_pairs: set = set()  # 已处理的连接对
        self._processed_bridges: set = set()  # 已分析的枢纽
        self._processed_orphans: set = set()  # 已处理的孤立节点

    def _lazy_init(self):
        if self._kb is None:
            from knowledge_base import KnowledgeBase
            self._kb = KnowledgeBase()
        if self._kg is None:
            from knowledge_graph import KnowledgeGraph
            self._kg = KnowledgeGraph()
        if self._tg is None:
            from thought_buffer import ThoughtGraph
            self._tg = ThoughtGraph()

    def think(self) -> Dict[str, Any]:
        """
        执行一轮内在思考。

        Returns:
            {"insights": List[InternalInsight], "questions": List[Dict]}
        """
        self._lazy_init()
        insights: List[InternalInsight] = []
        questions: List[Dict] = []

        insights.extend(self._find_cross_connections())
        insights.extend(self._analyze_hubs())
        qs = self._self_question()
        questions.extend(qs)

        return {"insights": insights, "questions": questions}

    # ── Pass 1: 知识交叉连接 ─────────────────────────

    def _find_cross_connections(self) -> List[InternalInsight]:
        """
        在知识库中发现跨类别但共享关键词的知识对。

        方法：按关键词建索引，找共享相同关键词但来自不同类别的条目对。
        """
        results = []
        all_k = self._kb.get_all_knowledge()
        if len(all_k) < 2:
            return results

        keyword_idx: Dict[str, List[dict]] = {}
        for entry in all_k:
            topic = entry.get("topic", "")
            keywords = entry.get("keywords", [])
            words = set(topic.lower().split())
            for kw in keywords:
                words.add(str(kw).lower())
            words.add(entry.get("category", "").lower())
            for w in words:
                if len(w) > 2:
                    keyword_idx.setdefault(w, []).append(entry)

        seen = set()
        for word, entries in keyword_idx.items():
            if len(entries) < 2:
                continue
            for i, a in enumerate(entries):
                cat_a = a.get("category", "")
                for b in entries[i + 1:]:
                    cat_b = b.get("category", "")
                    if cat_a == cat_b or not cat_a or not cat_b:
                        continue
                    topic_a = a.get("topic", "")
                    topic_b = b.get("topic", "")
                    pair = tuple(sorted([topic_a, topic_b]))
                    if pair in seen or pair in self._processed_pairs:
                        continue
                    seen.add(pair)
                    self._processed_pairs.add(pair)
                    imp = round(min(0.75, 0.4 + len(entries) * 0.02), 2)
                    results.append(InternalInsight(
                        content=f"跨域连接: 「{topic_a[:50]}」↔「{topic_b[:50]}」通过共有关键词「{word}」",
                        category="connection",
                        importance=imp,
                        related_entities=[topic_a[:60], topic_b[:60]],
                    ))
                    if len(results) >= 3:
                        return results
        return results

    # ── Pass 2: 枢纽实体分析 ─────────────────────────

    def _analyze_hubs(self) -> List[InternalInsight]:
        """
        分析知识图中的枢纽实体（连接多个社区的节点）。

        这些实体通常是架构核心或关键概念，
        理解它们有助于系统认识自己的知识骨架。
        """
        results = []
        try:
            bridges = self._kg.find_bridges()
            for b in bridges:
                name = b.get("entity_name", "")
                if name in self._processed_bridges:
                    continue
                self._processed_bridges.add(name)
                deg = b.get("degree", 0)
                types = b.get("connects_types", [])
                results.append(InternalInsight(
                    content=f"知识枢纽: 「{name}」连接 {types}（度={deg}）— 这是知识骨架的关键节点",
                    category="pattern",
                    importance=0.7,
                    related_entities=[name],
                ))
                if len(results) >= 2:
                    break
        except Exception:
            pass
        return results

    # ── Pass 3: 自我提问 ────────────────────────────

    def _self_question(self) -> List[Dict]:
        """
        从已有知识生成自我提问。

        两类来源：
        1. 高重要性但低学习深度的知识条目 → 值得深挖
        2. 孤立思维节点 → 为什么没有连接？
        """
        questions = []
        all_k = self._kb.get_all_knowledge()

        # 高重要性 + 低深度
        candidates = [
            e for e in all_k
            if e.get("importance", 0) >= 0.7
            and (e.get("learning_depth", 0) or 0) < 2
            and len(e.get("topic", "")) > 5
        ]
        candidates.sort(key=lambda e: -e.get("importance", 0))
        for entry in candidates[:2]:
            topic = entry.get("topic", "")
            imp = entry.get("importance", 0.7)
            questions.append({
                "question": f"「{topic[:60]}」很重要(评分{imp})但了解还不够深，它的核心原理是什么？",
                "importance": round(imp, 2),
                "explore_action": "deep_learning",
                "target": topic[:60],
                "source": "internal_thinker",
            })

        # 孤立思维节点
        try:
            orphans = self._tg.get_orphaned_thoughts()
            for o in orphans:
                if o.id in self._processed_orphans:
                    continue
                self._processed_orphans.add(o.id)
                if o.importance >= 0.5:
                    questions.append({
                        "question": f"孤立想法: 「{o.topic[:50]}」没有任何连接，它和哪些知识相关？",
                        "importance": round(o.importance, 2),
                        "explore_action": "explore",
                        "target": o.topic[:60],
                        "source": "internal_thinker",
                    })
                    break
        except Exception:
            pass

        return questions


if __name__ == "__main__":
    it = InternalThinker()
    result = it.think()
    print(f"内在思考结果:")
    print(f"  洞察: {len(result['insights'])} 条")
    for ins in result["insights"]:
        print(f"    [{ins.category}] {ins.content[:80]}")
    print(f"  问题: {len(result['questions'])} 个")
    for q in result["questions"]:
        print(f"    [{q['importance']}] {q['question'][:80]}")
