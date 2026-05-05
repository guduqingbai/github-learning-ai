#!/usr/bin/env python3
"""
📊 差距分析 — 能力清单 vs 外部参考

正向：已有能力在 KB 中有对应的外部参考吗？
反向：KB 中有没有能力注册表里没有的东西？
"""
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Set


@dataclass
class GapAnalysisResult:
    """单项正向对比：能力 vs KB 条目"""
    capability_name: str
    kb_entry_topic: str
    similarity_score: float     # 0.0-1.0
    reason: str                 # 匹配理由


@dataclass
class RankedGap:
    """反向差距：KB 中有但能力注册表中没有的东西"""
    topic: str
    description: str
    relevance_score: float      # 与项目相关性 0-1
    implementation_cost: float  # 实现成本 0-1
    potential_impact: float     # 潜在影响 0-1
    overall_score: float        # 加权综合
    matched_keywords: List[str] = field(default_factory=list)


# 项目领域关键词——用于评估相关性
DOMAIN_KEYWORDS = {
    "agent", "autonomous", "self", "improving", "learning",
    "metacognition", "reflection", "curiosity", "exploration",
    "cognition", "architecture", "thinking", "reasoning",
    "knowledge", "memory", "planning", "goal", "feedback",
    "adaptation", "evolution", "modification", "code", "scan",
    "monitor", "diagnosis", "heal", "repair", "crawl",
}


class GapAnalyzer:
    """
    差距分析器——交叉对比能力注册表和知识库外部参考。

    两个方向四步走：
    1. 正向：每项已有能力 → KB 有对应记录吗？
    2. 正向得分低 → 该能力需要补充外部知识
    3. 反向：KB 外部参考 → 能力注册表有对应吗？
    4. 反向无对应 → 发现缺失能力
    """

    def __init__(self):
        self._kb = None

    def _get_kb(self):
        """惰性加载 KnowledgeBase"""
        if self._kb is None:
            try:
                from knowledge_base import KnowledgeBase
                self._kb = KnowledgeBase()
            except Exception:
                self._kb = object()
        return self._kb

    # ── 正向对比 ──

    def compare_capability_vs_knowledge(
        self,
        capability: Any,
        kb_entries: List[Dict[str, Any]],
    ) -> List[GapAnalysisResult]:
        """
        一项能力 vs 所有 KB 参考条目。
        返回相似度 < 0.4 的弱匹配项（这些是需要补充的缺口）。
        """
        if not kb_entries:
            return []

        results = []
        cap_name = capability.name if hasattr(capability, 'name') else str(capability)
        cap_module = getattr(capability, 'module', '')

        for entry in kb_entries:
            sim = self._calculate_similarity(cap_name, cap_module, entry)
            if sim < 0.4 and sim > 0.05:
                results.append(GapAnalysisResult(
                    capability_name=cap_name,
                    kb_entry_topic=entry.get("topic", "未知"),
                    similarity_score=round(sim, 3),
                    reason=f"弱匹配 (sim={sim:.2f})",
                ))

        return results

    # ── 反向对比 ──

    def find_missing_capabilities(
        self,
        kb_entries: List[Dict[str, Any]],
    ) -> List[RankedGap]:
        """
        扫描 KB "能力参考" 条目，找出注册表中没有的功能。
        返回排好序的差距列表。
        """
        if not kb_entries:
            return []

        try:
            from capability_registry import CapabilityRegistry
            registry = CapabilityRegistry()
        except Exception:
            return []

        gaps = []
        for entry in kb_entries:
            topic = entry.get("topic", "")
            content = entry.get("content", "")
            keywords = entry.get("keywords", [])

            # 检查注册表中是否有匹配的能力
            matched = False
            for cap in registry.list():
                sim = self._calculate_similarity(cap.name, cap.module, entry)
                if sim >= 0.4:
                    matched = True
                    break

            if not matched:
                relevance = self._estimate_relevance(topic, content, keywords)
                cost = self._estimate_cost(topic, content)
                impact = self._estimate_impact(topic, content, keywords)
                overall = self._compute_overall(relevance, cost, impact)

                gaps.append(RankedGap(
                    topic=topic,
                    description=content[:300],
                    relevance_score=relevance,
                    implementation_cost=cost,
                    potential_impact=impact,
                    overall_score=overall,
                    matched_keywords=keywords if isinstance(keywords, list) else [],
                ))

        return self.rank_gaps_by_value(gaps)

    def rank_gaps_by_value(
        self,
        gaps: List[RankedGap],
    ) -> List[RankedGap]:
        """
        按综合得分排序。
        公式: overall = relevance * 0.40 + impact * 0.35 - cost * 0.15 + 0.10
        """
        for gap in gaps:
            gap.overall_score = self._compute_overall(
                gap.relevance_score, gap.implementation_cost, gap.potential_impact)
        gaps.sort(key=lambda g: -g.overall_score)
        return gaps

    # ── 内部评分方法 ──

    def _calculate_similarity(
        self,
        name: str,
        module: str,
        kb_entry: Dict[str, Any],
    ) -> float:
        """
        计算能力与 KB 条目的相似度。
        基于：名称关键词匹配 + 模块名匹配 + 内容关键词重叠。
        """
        topic = kb_entry.get("topic", "")
        content = kb_entry.get("content", "")
        keywords = kb_entry.get("keywords", [])

        if not topic and not content:
            return 0.0

        # 1. 名称 vs topic 的 Jaccard（权重 0.5）
        name_tokens = set(self._tokenize(name))
        topic_tokens = set(self._tokenize(topic))
        name_jaccard = self._jaccard(name_tokens, topic_tokens)

        # 2. 模块名出现在 topic/content 中（权重 0.2）
        mod_match = 1.0 if module and module.split(".")[0] in topic else 0.0

        # 3. 关键词重叠（权重 0.3）
        name_keywords = set(self._tokenize(name))
        entry_keywords = set(
            k.lower() for k in (keywords if isinstance(keywords, list) else [])
        ) | set(self._tokenize(content[:200]))
        kw_sim = self._jaccard(name_keywords, entry_keywords)

        score = name_jaccard * 0.5 + mod_match * 0.2 + kw_sim * 0.3
        return max(0.0, min(1.0, score))

    def _estimate_relevance(
        self,
        topic: str,
        content: str,
        keywords: Any,
    ) -> float:
        """评估 KB 条目与项目的领域相关性"""
        text = f"{topic} {content}".lower()
        matched = sum(1 for kw in DOMAIN_KEYWORDS if kw in text)
        return min(1.0, matched / max(1, len(DOMAIN_KEYWORDS) * 0.15))

    def _estimate_cost(self, topic: str, content: str) -> float:
        """
        估计实现成本。
        基于内容长度和复杂度做粗略代理估计。
        """
        text = f"{topic} {content}"
        # 更长/更复杂的描述通常意味着更高的实现成本
        length_factor = min(1.0, len(text) / 2000)
        # 关键词"complex/sophisticated/large"增加成本
        complexity_indicators = ["complex", "sophisticated", "large", "multi", "distributed"]
        comp_score = sum(1 for w in complexity_indicators if w in text.lower())
        complexity = min(1.0, comp_score / 3.0)
        return round((length_factor * 0.5 + complexity * 0.5), 2)

    def _estimate_impact(self, topic: str, content: str, keywords: Any) -> float:
        """评估潜在影响——关键词匹配程度"""
        impact_kw = {
            "self": 0.3, "learning": 0.3, "autonomous": 0.3,
            "improve": 0.25, "optimize": 0.2, "automatic": 0.2,
            "analyze": 0.15, "detect": 0.15, "knowledge": 0.2,
            "reasoning": 0.25, "planning": 0.2, "reflection": 0.3,
        }
        text = f"{topic} {content}".lower()
        score = 0.3  # 基础分
        for kw, boost in impact_kw.items():
            if kw in text:
                score += boost
        return min(1.0, score)

    def _compute_overall(
        self,
        relevance: float,
        cost: float,
        impact: float,
    ) -> float:
        """综合评分：越高越值得实现"""
        return max(0.0, min(1.0,
            relevance * 0.40 + impact * 0.35 - cost * 0.15 + 0.10
        ))

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """分词"""
        if not text:
            return []
        text = text.lower().replace("_", " ").replace("-", " ").replace("/", " ")
        return [w for w in re.findall(r'\w+', text) if len(w) > 1]

    @staticmethod
    def _jaccard(a: Set[str], b: Set[str]) -> float:
        """Jaccard 相似度"""
        if not a and not b:
            return 1.0
        union = a | b
        if not union:
            return 1.0
        return len(a & b) / len(union)


def main():
    """测试 GapAnalyzer"""
    print("=" * 50)
    print("  GapAnalyzer 测试")
    print("=" * 50)

    from capability_registry import Capability, CapabilityRegistry

    analyzer = GapAnalyzer()

    # 1. 相似度计算测试
    print("\n1. 相似度计算测试")
    sim = analyzer._calculate_similarity(
        "代码扫描", "self_scanner.py",
        {"topic": "Self-Improving Code Scanner for Automated Refactoring",
         "content": "An automated code scanner that analyzes Python code quality.",
         "keywords": ["code", "scan", "refactoring"]},
    )
    print(f"   代码扫描 vs 论文: {sim:.3f}")

    # 2. 正向对比
    print("\n2. 正向对比测试（无 KB 条目时）")
    cap = Capability("测试能力", "test.py")
    results = analyzer.compare_capability_vs_knowledge(cap, [])
    assert len(results) == 0, "空 KB 应返回空"
    print(f"   弱匹配项: {len(results)}")

    # 3. 反向差距检测
    print("\n3. 反向差距检测")
    sample_entries = [
        {"topic": "Tool-Using Agent Architecture with External APIs",
         "content": "An agent that learns to use external tools via reinforcement learning.",
         "keywords": ["tool", "api", "agent", "reinforcement"]},
    ]
    missing = analyzer.find_missing_capabilities(sample_entries)
    print(f"   发现缺失能力: {len(missing)}")
    for g in missing:
        print(f"   [{g.overall_score:.2f}] {g.topic[:60]}")

    # 4. 排序测试
    print("\n4. 排序测试")
    gaps = [
        RankedGap("Low Impact Feature", "a small utility", 0.3, 0.8, 0.2, 0.0),
        RankedGap("High Impact Feature", "major new capability", 0.8, 0.3, 0.9, 0.0),
    ]
    ranked = analyzer.rank_gaps_by_value(gaps)
    assert ranked[0].topic == "High Impact Feature"
    print(f"   排序正确: {ranked[0].topic} > {ranked[1].topic}")

    print("\n✅ GapAnalyzer 测试完成")
    return True


if __name__ == "__main__":
    main()
