#!/usr/bin/env python3
"""
思考连续性 — 让每一轮思考接着上一轮继续

从 ThoughtGraph 读取活跃线程，注入延续问题（pre-processing），
探索完成后将结果链接为子节点并管理线程生命周期（post-processing）。
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class ThoughtContinuityConfig:
    """可调参数"""
    max_active_threads: int = 3
    max_thread_depth: int = 5
    stale_cycles_threshold: int = 5
    continuation_importance_boost: float = 0.2
    min_continuation_importance: float = 0.4
    max_continuation_questions: int = 5
    reduce_new_questions_ratio: float = 0.5


class ThoughtContinuityManager:
    """主动读取 ThoughtGraph，使思考循环保持连续性"""

    def __init__(self, thought_graph, config: Optional[ThoughtContinuityConfig] = None):
        self._graph = thought_graph
        self._config = config or ThoughtContinuityConfig()
        # thread_id -> 上次触及的 cycle_count，用于陈旧检测
        self._thread_last_touched: Dict[str, int] = {}

    # ── 预处理：注入延续问题 ──

    def inject_continuation_questions(self, current_questions: List,
                                       cycle_count: int,
                                       snapshot: Dict) -> List:
        """
        从 ThoughtGraph 读取活跃线程，生成延续问题。
        返回新的 CuriosityQuestion 列表，调用方应 prepend 到问题队列头部。
        """
        from curiosity_engine import CuriosityQuestion

        active = self._graph.get_active_thoughts(
            max_count=self._config.max_active_threads * 4)
        if not active:
            return []

        # 按根节点分组，每组选最深节点延续
        thread_groups: Dict[str, list] = {}
        for node in active:
            if node.depth >= self._config.max_thread_depth:
                continue
            if node.status == "abandoned":
                continue
            root = self._find_root_thought(node.id)
            root_id = root.id if root else node.id
            thread_groups.setdefault(root_id, []).append(node)

        # 每组选最深 + 计算延续分
        candidates = []
        for root_id, nodes in thread_groups.items():
            deepest = max(nodes, key=lambda n: n.depth)
            node = deepest
            depth_score = 1.0 - (node.depth / max(self._config.max_thread_depth, 1))
            last_touch = self._thread_last_touched.get(node.id, 0)
            freshness = min(1.0, (cycle_count - last_touch) / max(self._config.stale_cycles_threshold, 1))
            score = (node.importance * 0.4) + (depth_score * 0.3) + (freshness * 0.3)
            candidates.append((score, node))

        candidates.sort(key=lambda x: -x[0])

        # 去重：相同主题的只留最高分一个
        seen_topics = set()
        unique_candidates = []
        for score, node in candidates:
            topic_key = node.topic.strip().lower()[:30]
            if topic_key in seen_topics:
                continue
            seen_topics.add(topic_key)
            unique_candidates.append((score, node))
            if len(unique_candidates) >= self._config.max_continuation_questions:
                break

        selected = unique_candidates[:self._config.max_active_threads]

        continuation_qs = []
        for score, node in selected:
            importance = max(
                node.importance + self._config.continuation_importance_boost,
                self._config.min_continuation_importance,
            )
            # 使用根节点的原始主题（而非深层节点的冗余文本）
            root_topic = node.topic
            if node.depth > 0 and node.parent_id:
                parent = self._graph.get_thought(node.parent_id)
                if parent:
                    root_topic = parent.topic
            q = CuriosityQuestion(
                observation=f"已有思考线程: {root_topic} (深度 {node.depth})",
                question=f"继续挖深: {root_topic} — 已探索 {node.depth} 层，继续深挖",
                importance=min(importance, 1.0),
                explore_action="deep_learning",
                target=root_topic,
                context={
                    "parent_thought_id": node.id,
                    "parent_depth": node.depth,
                    "continuation": True,
                },
                reason=f"延续已存在的思考线程 (深度 {node.depth})",
            )
            continuation_qs.append(q)

        if continuation_qs:
            print(f"  🔗 延续 {len(continuation_qs)} 个已有思考线程", flush=True)
            threads_info = " | ".join(
                f"[d{node.depth}] {node.topic[:30]}"
                for _, node in selected
            )
            print(f"     {threads_info}", flush=True)

        return continuation_qs

    def should_reduce_new_questions(self) -> bool:
        """深度优先模式：活跃线程 >= 上限时减少新问题"""
        active = self._graph.get_active_thoughts(
            max_count=self._config.max_active_threads + 1)
        return len(active) >= self._config.max_active_threads

    # ── 后处理：链接结果到父节点 + 管理线程生命周期 ──

    def post_process_results(self, results: List[Dict], cycle_count: int):
        """
        探索完成后处理：
        - 延续的探索结果 → 作为子节点写入 ThoughtGraph
        - 新线程 → 照常写入根节点
        - 更新父节点 metadata（last_cycle_touched）
        - 检测陈旧线程 → 标记 abandoned
        - 检测已达深度上限线程 → 标记 resolved
        """
        had_continuation = False

        for ins in results:
            ctx = ins.get("context", {})
            parent_id = ctx.get("parent_thought_id") if isinstance(ctx, dict) else None

            if parent_id:
                parent_node = self._graph.get_thought(parent_id)
                if parent_node:
                    # 延续线程 → 建立父子链
                    child_id = self._graph.add_thought(
                    topic=(ins.get("topic") or ins.get("question") or ins.get("summary", "延续探索"))[:100],
                    content=ins.get("summary", ins.get("detail", ""))[:500],
                    thought_type="insight",
                    parent_id=parent_id,
                    importance=ins.get("importance", 0.5),
                    source="exploration",
                    metadata={"cycle": cycle_count},
                )
                # 递增 KB learning_depth（用根节点主题）
                root = self._find_root_thought(parent_id)
                if root:
                    self._increment_kb_depth(root.topic)

                self._thread_last_touched[parent_id] = cycle_count
                had_continuation = True
            else:
                # 新线程 → 照常写入根节点
                self._graph.add_thought(
                    topic=(ins.get("topic") or ins.get("question") or ins.get("summary", "未知"))[:100],
                    content=ins.get("summary", ins.get("detail", ""))[:500],
                    thought_type="insight",
                    importance=ins.get("importance", 0.5),
                    source="exploration",
                )

        if not had_continuation:
            return  # 没有延续线程，跳过生命周期管理

        # ── 线程生命周期管理 ──
        for node in self._graph.get_active_thoughts():
            # 已达深度上限 → resolved
            if node.depth >= self._config.max_thread_depth:
                self._graph.resolve_thought(
                    node.id,
                    resolution=f"达到深度上限 {self._config.max_thread_depth}",
                )
                print(f"  ✅ 线程已解决: {node.topic[:40]} (深度 {node.depth})")
                continue

            # 陈旧线程 → abandoned
            last_touch = self._thread_last_touched.get(node.id, cycle_count)
            cycles_since = cycle_count - last_touch
            if cycles_since >= self._config.stale_cycles_threshold:
                self._graph.abandon_thought(
                    node.id,
                    reason=f"{cycles_since} 轮未触及，自动废弃",
                )
                print(f"  ⌛ 线程已废弃: {node.topic[:40]} ({cycles_since} 轮未触及)")

    def _find_root_thought(self, thought_id: str) -> Optional[Any]:
        """沿 parent_id 链回溯到根节点"""
        current = self._graph.get_thought(thought_id)
        while current and current.parent_id:
            parent = self._graph.get_thought(current.parent_id)
            if not parent:
                break
            current = parent
        return current

    # ── KB learning_depth 递增 ──

    def _increment_kb_depth(self, topic: str) -> bool:
        """递增知识库中对应条目的 learning_depth"""
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            all_k = kb.get_all_knowledge()
            # 精确匹配
            for entry in all_k:
                if entry.get("topic", "").lower() == topic.lower():
                    current = entry.get("learning_depth", 0) or 0
                    if current < 2:
                        kb.increment_learning_depth(entry["topic"])
                    return True
            # 模糊匹配
            for entry in all_k:
                if topic.lower() in entry.get("topic", "").lower():
                    current = entry.get("learning_depth", 0) or 0
                    if current < 2:
                        kb.increment_learning_depth(entry["topic"])
                    return True
        except Exception:
            pass
        return False

    # ── 查询接口 ──

    def get_thread_summary(self) -> str:
        """当前活跃线程的可读摘要"""
        active = self._graph.get_active_thoughts(
            max_count=self._config.max_active_threads)
        if not active:
            return "(无活跃线程)"
        parts = []
        for n in active:
            touch = self._thread_last_touched.get(n.id, 0)
            parts.append(f"  [深度{n.depth}] {n.topic[:40]} (imp={n.importance:.2f})")
        return "\n".join(parts)
