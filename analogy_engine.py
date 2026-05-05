#!/usr/bin/env python3
"""
类比引擎 — 结构映射 + 关系模式匹配
从余弦相似度升级到子图结构映射，能说明"为什么像"
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from collections import Counter, defaultdict


class AnalogyEngine:
    """结构类比引擎 v2 — 关系模式匹配"""

    def __init__(self, knowledge_graph=None):
        self._kg = knowledge_graph
        self._sig_cache: Dict[str, Dict[str, Any]] = {}

    # ═══════════════════════════════════════════════
    # v1 兼容：特征向量指纹
    # ═══════════════════════════════════════════════

    def structural_fingerprint(self, eid: str) -> Dict[str, float]:
        """计算实体的特征向量（v1 兼容）"""
        entity = self._kg.get_entity(eid) if self._kg else None
        if not entity:
            return {}

        relations = self._kg.get_relations(eid)
        out_degree = sum(1 for r in relations if r.source == eid)
        in_degree = sum(1 for r in relations if r.target == eid)
        type_counts: Dict[str, int] = Counter(r.rel_type for r in relations)
        total = len(relations) or 1

        connected_types: Dict[str, int] = Counter()
        for r in relations:
            neighbor_id = r.target if r.source == eid else r.source
            neighbor = self._kg.get_entity(neighbor_id) if self._kg else None
            if neighbor:
                connected_types[neighbor.type] += 1

        return {
            "out_degree": out_degree,
            "in_degree": in_degree,
            "total_degree": out_degree + in_degree,
            "type_diversity": len(connected_types),
            "rel_depends_on": type_counts.get("depends_on", 0) / total,
            "rel_related_to": type_counts.get("related_to", 0) / total,
            "rel_defined_in": type_counts.get("defined_in", 0) / total,
            "rel_prerequisite": type_counts.get("prerequisite", 0) / total,
            "connected_modules": connected_types.get("module", 0),
            "connected_concepts": connected_types.get("concept", 0),
            "connected_classes": connected_types.get("class", 0),
            "connected_functions": connected_types.get("function", 0),
        }

    def cosine_similarity(self, fp_a: Dict[str, float],
                          fp_b: Dict[str, float]) -> float:
        """余弦相似度（v1 兼容）"""
        all_keys = set(fp_a.keys()) & set(fp_b.keys())
        if not all_keys:
            return 0.0
        dot = sum(fp_a[k] * fp_b[k] for k in all_keys)
        mag_a = sum(v ** 2 for v in fp_a.values()) ** 0.5 or 1
        mag_b = sum(v ** 2 for v in fp_b.values()) ** 0.5 or 1
        return dot / (mag_a * mag_b)

    # ═══════════════════════════════════════════════
    # v2 核心：关系结构映射
    # ═══════════════════════════════════════════════

    def relational_signature(self, eid: str, depth: int = 2) -> Dict[str, Any]:
        """
        提取实体的关系结构签名（比特征向量更深）。
        捕获实体在其 neighborhood 中的角色模式。

        Returns:
            {
                "role_patterns": ["source:depends_on->module", "target:defined_in<-class", ...],
                "neighborhood_hash": "...",
                "relay_count": N,  # 作为桥接的次数
            }
        """
        if eid in self._sig_cache:
            return self._sig_cache[eid]

        entity = self._kg.get_entity(eid) if self._kg else None
        if not entity:
            return {}

        relations = self._kg.get_relations(eid)
        patterns: List[str] = []
        relay_count = 0

        for r in relations:
            if r.source == eid:
                target_entity = self._kg.get_entity(r.target) if self._kg else None
                target_type = target_entity.type if target_entity else "unknown"
                patterns.append(f"source:{r.rel_type}->{target_type}")
                relay_count += 1
            if r.target == eid:
                source_entity = self._kg.get_entity(r.source) if self._kg else None
                source_type = source_entity.type if source_entity else "unknown"
                patterns.append(f"target:{r.rel_type}<-{source_type}")
                relay_count += 1

        patterns.sort()
        # 生成子图哈希（2 跳）
        neighborhood = self._get_neighborhood_pattern(eid, depth)

        result = {
            "role_patterns": patterns,
            "neighborhood": neighborhood,
            "relay_count": relay_count,
            "pattern_count": len(patterns),
        }
        self._sig_cache[eid] = result
        return result

    def _get_neighborhood_pattern(self, eid: str, depth: int) -> str:
        """生成实体的 2 跳邻域拓扑模式字符串"""
        if not self._kg:
            return ""
        visited: Set[str] = set()
        edges: List[str] = []

        def walk(node: str, d: int):
            if d > depth or node in visited:
                return
            visited.add(node)
            n_entity = self._kg.get_entity(node)
            n_type = n_entity.type if n_entity else "?"
            for r in self._kg.get_relations(node):
                other = r.target if r.source == node else r.source
                o_entity = self._kg.get_entity(other)
                o_type = o_entity.type if o_entity else "?"
                edges.append(f"{n_type}-{r.rel_type}-{o_type}")
                if other not in visited:
                    walk(other, d + 1)

        walk(eid, 0)
        edges.sort()
        return "|".join(edges[:50])  # 截断防止过长

    def relational_similarity(self, sig_a: Dict[str, Any],
                              sig_b: Dict[str, Any]) -> float:
        """
        基于关系模式计算相似度（比余弦更深层）。

        比较：
        1. 角色模式重叠度（Jaccard）
        2. 中继角色相似度
        3. 邻域拓扑重叠度
        """
        patterns_a = set(sig_a.get("role_patterns", []))
        patterns_b = set(sig_b.get("role_patterns", []))

        if not patterns_a and not patterns_b:
            return 0.0

        # Jaccard 相似度
        intersection = patterns_a & patterns_b
        union = patterns_a | patterns_b
        pattern_jaccard = len(intersection) / len(union) if union else 0

        # 中继角色相似度
        relay_a = sig_a.get("relay_count", 0)
        relay_b = sig_b.get("relay_count", 0)
        max_relay = max(relay_a, relay_b) or 1
        relay_sim = 1 - abs(relay_a - relay_b) / max_relay

        # 邻域拓扑重叠
        hood_a = sig_a.get("neighborhood", "")
        hood_b = sig_b.get("neighborhood", "")
        hood_sim = 0.0
        if hood_a and hood_b:
            set_a = set(hood_a.split("|"))
            set_b = set(hood_b.split("|"))
            h_intersection = set_a & set_b
            h_union = set_a | set_b
            hood_sim = len(h_intersection) / len(h_union) if h_union else 0

        # 加权综合
        return pattern_jaccard * 0.5 + relay_sim * 0.2 + hood_sim * 0.3

    def find_analogies(self, target_eid: str, candidate_type: str = None,
                       threshold: float = 0.3, use_deep: bool = True,
                       max_results: int = 10) -> List[Dict[str, Any]]:
        """
        找到与目标实体结构类似的实体。

        use_deep=True 时使用关系签名匹配（v2），
        否则使用余弦相似度（v1 兼容）。
        """
        if not self._kg:
            return []

        target = self._kg.get_entity(target_eid)
        if not target:
            return []

        if use_deep:
            sig_a = self.relational_signature(target_eid)
            if not sig_a.get("role_patterns"):
                return []
        else:
            fp_a = self.structural_fingerprint(target_eid)
            if not fp_a:
                return []

        results = []
        candidates = self._kg.find_entities(candidate_type) if candidate_type else self._kg.find_entities()

        for candidate in candidates:
            if candidate.id == target_eid:
                continue

            if use_deep:
                sig_b = self.relational_signature(candidate.id)
                if not sig_b.get("role_patterns"):
                    continue
                sim = self.relational_similarity(sig_a, sig_b)
            else:
                fp_b = self.structural_fingerprint(candidate.id)
                if not fp_b:
                    continue
                sim = self.cosine_similarity(fp_a, fp_b)

            if sim >= threshold:
                mapping = self._describe_mapping(target_eid, candidate.id) if use_deep else {}
                results.append({
                    "entity_a": target.name,
                    "entity_a_id": target_eid,
                    "entity_a_type": target.type,
                    "entity_b": candidate.name,
                    "entity_b_id": candidate.id,
                    "entity_b_type": candidate.type,
                    "similarity": round(sim, 3),
                    **mapping,
                })

        results.sort(key=lambda x: -x["similarity"])
        return results[:max_results]

    def cross_domain_analogies(self, threshold: float = 0.3,
                                use_deep: bool = True,
                                max_results: int = 10) -> List[Dict[str, Any]]:
        """跨域类比发现（使用 v2 映射）"""
        if not self._kg:
            return []

        by_type: Dict[str, List[str]] = {}
        for e in self._kg.find_entities():
            by_type.setdefault(e.type, []).append(e.id)

        types = list(by_type.keys())
        analogies = []

        self._sig_cache.clear()  # 新鲜缓存，避免跨调用污染

        for i in range(len(types)):
            for j in range(i + 1, len(types)):
                type_a, type_b = types[i], types[j]
                for eid_a in by_type[type_a][:10]:
                    if use_deep:
                        sig_a = self.relational_signature(eid_a)
                        if not sig_a.get("role_patterns"):
                            continue
                    else:
                        fp_a = self.structural_fingerprint(eid_a)
                        if not fp_a:
                            continue

                    for eid_b in by_type[type_b][:10]:
                        if use_deep:
                            sig_b = self.relational_signature(eid_b)
                            if not sig_b.get("role_patterns"):
                                continue
                            sim = self.relational_similarity(sig_a, sig_b)
                        else:
                            fp_b = self.structural_fingerprint(eid_b)
                            if not fp_b:
                                continue
                            sim = self.cosine_similarity(fp_a, fp_b)

                        if sim >= threshold:
                            a_name = self._kg.get_entity(eid_a).name
                            b_name = self._kg.get_entity(eid_b).name
                            mapping = self._describe_mapping(eid_a, eid_b) if use_deep else {}
                            analogies.append({
                                "entity_a": a_name,
                                "entity_a_type": type_a,
                                "entity_b": b_name,
                                "entity_b_type": type_b,
                                "similarity": round(sim, 3),
                                **mapping,
                            })

        analogies.sort(key=lambda x: -x["similarity"])
        return analogies[:max_results]

    # ═══════════════════════════════════════════════
    # 映射描述
    # ═══════════════════════════════════════════════

    def _describe_mapping(self, eid_a: str, eid_b: str) -> Dict[str, Any]:
        """找出两个实体之间共享的具体角色模式"""
        if not self._kg:
            return {}

        sig_a = self.relational_signature(eid_a)
        sig_b = self.relational_signature(eid_b)

        patterns_a = set(sig_a.get("role_patterns", []))
        patterns_b = set(sig_b.get("role_patterns", []))

        shared = patterns_a & patterns_b
        only_a = patterns_a - patterns_b
        only_b = patterns_b - patterns_a

        return {
            "shared_roles": sorted(shared)[:10],
            "a_unique_roles": sorted(only_a)[:5],
            "b_unique_roles": sorted(only_b)[:5],
        }

    def generate_analogy_insight(self, entity_a: str, entity_b: str,
                                  similarity: float,
                                  shared_roles: List[str] = None) -> str:
        """生成带解释的类比洞察"""
        if shared_roles:
            role_hint = ", ".join(shared_roles[:4])
            core = (f"'{entity_a}' 和 '{entity_b}' 结构相似（{similarity:.0%}），"
                    f"共同模式: {role_hint}")
        else:
            core = (f"'{entity_a}' 和 '{entity_b}' 结构相似（{similarity:.0%}）")

        if similarity >= 0.7:
            return f"强烈类比: {core}。可能共享相同的架构角色。"
        elif similarity >= 0.5:
            return f"类比: {core}。值得进一步比较。"
        else:
            return f"弱类比: {core}。有少量结构共同点。"

    def classify_analogy(self, sim_a: float, type_a: str, type_b: str) -> str:
        """给类比分类"""
        if type_a == type_b and sim_a >= 0.7:
            return "direct_duplicate"  # 可能重复
        elif type_a == type_b:
            return "peer_similar"       # 同类相似
        else:
            return "cross_domain"       # 跨域

    # ═══════════════════════════════════════════════
    # v1 兼容接口
    # ═══════════════════════════════════════════════

    def find_analogies_v1(self, target_eid: str, candidate_type: str = None,
                           threshold: float = 0.5, max_results: int = 10) -> List[Dict[str, Any]]:
        """v1 兼容：余弦相似度"""
        return self.find_analogies(target_eid, candidate_type,
                                   threshold, use_deep=False,
                                   max_results=max_results)

    def cross_domain_analogies_v1(self, threshold: float = 0.5,
                                    max_results: int = 10) -> List[Dict[str, Any]]:
        """v1 兼容：余弦相似度跨域"""
        return self.cross_domain_analogies(threshold, use_deep=False,
                                            max_results=max_results)


if __name__ == "__main__":
    from knowledge_graph import KnowledgeGraph

    kg = KnowledgeGraph()
    ae = AnalogyEngine(kg)

    # 测试实体
    e1 = kg.add_entity("机器学习", "concept")
    e2 = kg.add_entity("深度学习", "concept")
    e3 = kg.add_entity("监督学习", "concept")
    e4 = kg.add_entity("Python", "concept")
    m1 = kg.add_entity("scanner.py", "module")
    f1 = kg.add_entity("scan_func", "function")
    m2 = kg.add_entity("thinker.py", "module")
    f2 = kg.add_entity("think_func", "function")

    kg.add_relation(e1, e2, "related_to", 0.8)
    kg.add_relation(e1, e3, "prerequisite", 0.7)
    kg.add_relation(e2, e3, "related_to", 0.6)
    kg.add_relation(e4, e1, "related_to", 0.3)
    kg.add_relation(f1, m1, "defined_in")
    kg.add_relation(f2, m2, "defined_in")

    # 测试关系签名
    sig = ae.relational_signature(e1)
    print(f"关系签名 (机器学习): {sig['pattern_count']} 个模式")
    print(f"  角色: {sig['role_patterns']}")

    # 测试关系相似度
    sim_ee = ae.relational_similarity(
        ae.relational_signature(e1), ae.relational_signature(e2))
    print(f"机器学习 ↔ 深度学习 (关系相似度): {sim_ee:.3f}")

    sim_ef = ae.relational_similarity(
        ae.relational_signature(e1), ae.relational_signature(f1))
    print(f"机器学习 ↔ scan_func (关系相似度): {sim_ef:.3f}")

    # 测试 v2 类比发现
    analogies = ae.find_analogies(e1, threshold=0.1, use_deep=True)
    print(f"v2 类比 (机器学习, threshold=0.1): {len(analogies)} 个")
    for a in analogies[:5]:
        insight = ae.generate_analogy_insight(
            a["entity_a"], a["entity_b"], a["similarity"],
            a.get("shared_roles", []))
        print(f"  {a['entity_b']} ({a['entity_b_type']}): {a['similarity']:.3f}")
        print(f"    共享角色: {a.get('shared_roles', [])}")
        print(f"    洞察: {insight}")

    print("✅ 类比引擎 v2 测试完成")
