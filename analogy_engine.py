#!/usr/bin/env python3
"""
类比引擎 — 结构相似度检测
发现不同模块/概念之间的结构类比关系
"""

from typing import Dict, Any, List, Optional, Tuple
from collections import Counter


class AnalogyEngine:
    """结构类比引擎"""

    def __init__(self, knowledge_graph=None):
        self._kg = knowledge_graph

    def structural_fingerprint(self, eid: str) -> Dict[str, float]:
        """
        计算实体的结构特征向量。
        用于比较两个实体在图中位置的相似性。
        """
        entity = self._kg.get_entity(eid) if self._kg else None
        if not entity:
            return {}

        relations = self._kg.get_relations(eid)

        # 节点度：出度、入度、总度
        out_degree = sum(1 for r in relations if r.source == eid)
        in_degree = sum(1 for r in relations if r.target == eid)

        # 关系类型分布
        type_counts: Dict[str, int] = Counter(r.rel_type for r in relations)
        total = len(relations) or 1

        # 连接实体类型分布
        connected_types: Dict[str, int] = Counter()
        for r in relations:
            neighbor_id = r.target if r.source == eid else r.source
            neighbor = self._kg.get_entity(neighbor_id) if self._kg else None
            if neighbor:
                connected_types[neighbor.type] += 1

        # 位置中心性：连接的不同群落数
        # 简化：用连接的不同实体类型数表示
        type_diversity = len(connected_types)

        fingerprint = {
            "out_degree": out_degree,
            "in_degree": in_degree,
            "total_degree": out_degree + in_degree,
            "type_diversity": type_diversity,
            "rel_depends_on": type_counts.get("depends_on", 0) / total,
            "rel_related_to": type_counts.get("related_to", 0) / total,
            "rel_defined_in": type_counts.get("defined_in", 0) / total,
            "rel_prerequisite": type_counts.get("prerequisite", 0) / total,
            "connected_modules": connected_types.get("module", 0),
            "connected_concepts": connected_types.get("concept", 0),
            "connected_classes": connected_types.get("class", 0),
            "connected_functions": connected_types.get("function", 0),
        }
        return fingerprint

    def cosine_similarity(self, fp_a: Dict[str, float],
                          fp_b: Dict[str, float]) -> float:
        """余弦相似度"""
        all_keys = set(fp_a.keys()) & set(fp_b.keys())
        if not all_keys:
            return 0.0

        dot = sum(fp_a[k] * fp_b[k] for k in all_keys)
        mag_a = sum(v ** 2 for v in fp_a.values()) ** 0.5 or 1
        mag_b = sum(v ** 2 for v in fp_b.values()) ** 0.5 or 1
        return dot / (mag_a * mag_b)

    def find_analogies(self, target_eid: str, candidate_type: str = None,
                       threshold: float = 0.5,
                       max_results: int = 10) -> List[Dict[str, Any]]:
        """
        找到与目标实体结构类似的实体。

        Args:
            target_eid: 目标实体 ID
            candidate_type: 候选实体类型过滤（None = 全部）
            threshold: 相似度阈值
            max_results: 返回数量上限
        """
        if not self._kg:
            return []

        target = self._kg.get_entity(target_eid)
        if not target:
            return []

        target_fp = self.structural_fingerprint(target_eid)
        if not target_fp:
            return []

        results = []
        candidates = self._kg.find_entities(candidate_type) if candidate_type else self._kg.find_entities()

        for candidate in candidates:
            if candidate.id == target_eid:
                continue
            cfp = self.structural_fingerprint(candidate.id)
            if not cfp:
                continue
            sim = self.cosine_similarity(target_fp, cfp)
            if sim >= threshold:
                results.append({
                    "entity_a": target.name,
                    "entity_a_id": target_eid,
                    "entity_a_type": target.type,
                    "entity_b": candidate.name,
                    "entity_b_id": candidate.id,
                    "entity_b_type": candidate.type,
                    "similarity": round(sim, 3),
                })

        results.sort(key=lambda x: -x["similarity"])
        return results[:max_results]

    def cross_domain_analogies(self, threshold: float = 0.5,
                                max_results: int = 10) -> List[Dict[str, Any]]:
        """
        发现跨域类比：不同类型的实体但有相似结构。
        例如：一个模块的结构和一个概念的结构相似。
        """
        if not self._kg:
            return []

        # 按类型分组
        by_type: Dict[str, List[str]] = {}
        for e in self._kg.find_entities():
            by_type.setdefault(e.type, []).append(e.id)

        types = list(by_type.keys())
        analogies = []

        for i in range(len(types)):
            for j in range(i + 1, len(types)):
                type_a, type_b = types[i], types[j]
                for eid_a in by_type[type_a][:20]:  # 限制防止组合爆炸
                    fp_a = self.structural_fingerprint(eid_a)
                    if not fp_a:
                        continue
                    for eid_b in by_type[type_b][:20]:
                        fp_b = self.structural_fingerprint(eid_b)
                        if not fp_b:
                            continue
                        sim = self.cosine_similarity(fp_a, fp_b)
                        if sim >= threshold:
                            a_name = self._kg.get_entity(eid_a).name
                            b_name = self._kg.get_entity(eid_b).name
                            analogies.append({
                                "entity_a": a_name,
                                "entity_a_type": type_a,
                                "entity_b": b_name,
                                "entity_b_type": type_b,
                                "similarity": round(sim, 3),
                            })

        analogies.sort(key=lambda x: -x["similarity"])
        return analogies[:max_results]

    def generate_analogy_insight(self, entity_a: str, entity_b: str,
                                  similarity: float) -> str:
        """生成类比洞察文本"""
        if similarity >= 0.9:
            template = "极高相似度: '{a}' 和 '{b}' 结构几乎相同，可能功能重复"
        elif similarity >= 0.7:
            template = "较强相似: '{a}' 和 '{b}' 在图中的位置类型很像，可能存在跨域模式"
        elif similarity >= 0.5:
            template = "结构相似: '{a}' 和 '{b}' 具有相似的关系模式，值得进一步比较"
        else:
            template = "轻微相似: '{a}' 和 '{b}' 有少量结构共同点"

        return template.format(a=entity_a, b=entity_b)


if __name__ == "__main__":
    from knowledge_graph import KnowledgeGraph

    kg = KnowledgeGraph()
    ae = AnalogyEngine(kg)

    # 创建测试实体
    e1 = kg.add_entity("机器学习", "concept", {"category": "数据科学"})
    e2 = kg.add_entity("深度学习", "concept", {"category": "数据科学"})
    e3 = kg.add_entity("监督学习", "concept", {"category": "数据科学"})
    e4 = kg.add_entity("Python", "concept", {"category": "工程"})
    e5 = kg.add_entity("self_scanner.py", "module", {"file": "self_scanner.py"})
    e6 = kg.add_entity("scanner_scan_py_files", "function", {})

    kg.add_relation(e1, e2, "related_to", 0.8)
    kg.add_relation(e1, e3, "prerequisite", 0.7)
    kg.add_relation(e2, e3, "related_to", 0.6)
    kg.add_relation(e4, e1, "related_to", 0.3)
    kg.add_relation(e6, e5, "defined_in")

    # 测试指纹
    fp = ae.structural_fingerprint(e1)
    print(f"指纹 (机器学习): {fp}")

    # 测试类比
    analogies = ae.find_analogies(e1, threshold=0.1)
    print(f"类比结果: {len(analogies)} 个")
    for a in analogies:
        print(f"  {a['entity_b']} ({a['entity_b_type']}): 相似度 {a['similarity']}")
        print(f"    洞察: {ae.generate_analogy_insight(a['entity_a'], a['entity_b'], a['similarity'])}")

    cross = ae.cross_domain_analogies(threshold=0.1)
    print(f"跨域类比: {len(cross)} 个")

    print("✅ 类比引擎测试完成")
