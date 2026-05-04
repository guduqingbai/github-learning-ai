#!/usr/bin/env python3
"""
模式引擎 — 纯 Python 模式发现
代码模式 + 知识模式，不依赖任何外部 API
"""

import ast
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from collections import Counter


class PatternEngine:
    """纯算法模式发现"""

    def __init__(self, knowledge_graph=None):
        self.project_root = Path.cwd()
        self._kg = knowledge_graph

    # ═══════════════════════════════════════════════
    # 代码模式
    # ═══════════════════════════════════════════════

    def find_bare_excepts(self) -> List[Dict[str, Any]]:
        """找到所有 bare except: 语句"""
        findings = []
        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        findings.append({
                            "file": f.name,
                            "lineno": node.lineno,
                            "detail": f"{f.name}:{node.lineno} - bare except",
                            "severity": "high",
                        })
        return findings

    def find_missing_docstrings(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """找到 docstring 覆盖率低于阈值的模块"""
        findings = []
        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue

            named_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    has_doc = (isinstance(node.body[0], ast.Expr)
                               and isinstance(node.body[0].value, ast.Constant)
                               and isinstance(node.body[0].value.value, str))
                    named_nodes.append((node.name, has_doc))

            if not named_nodes:
                continue

            doc_ratio = sum(1 for _, has in named_nodes if has) / len(named_nodes)
            if doc_ratio < threshold:
                missing = [name for name, has in named_nodes if not has]
                findings.append({
                    "file": f.name,
                    "ratio": round(doc_ratio, 2),
                    "missing": missing[:10],
                    "missing_count": len(missing),
                    "total": len(named_nodes),
                    "detail": f"{f.name}: docstring {doc_ratio:.0%} ({len(missing)}/{len(named_nodes)} 缺文档)",
                    "severity": "medium",
                })
        return sorted(findings, key=lambda x: x["ratio"])

    def find_dead_code(self) -> List[Dict[str, Any]]:
        """找到定义但可能未使用的函数和变量（同一模块内）"""
        findings = []

        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue

            defined: Set[str] = set()
            used: Set[str] = set()
            skip_names = {"main", "run", "test_*", "__name__", "__main__",
                          "__init__", "__new__", "__str__", "__repr__"}

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 忽略特殊方法和 test_ 函数
                    if node.name.startswith("test_") or node.name.startswith("__"):
                        continue
                    defined.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    defined.add(node.name)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used.add(node.id)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    used.add(node.func.id)

            potential_dead = defined - used - skip_names
            if potential_dead:
                findings.append({
                    "file": f.name,
                    "unused": sorted(potential_dead),
                    "unused_count": len(potential_dead),
                    "detail": f"{f.name}: {len(potential_dead)} 个可能未使用的定义",
                    "severity": "low",
                })

        return findings

    def find_complex_modules(self, max_lines: int = 400,
                              max_functions: int = 20) -> List[Dict[str, Any]]:
        """找到复杂度过高的模块（行数过多、函数过多）"""
        findings = []
        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue

            lines = len(code.splitlines())
            func_count = sum(1 for n in ast.walk(tree)
                             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
            class_count = sum(1 for n in ast.walk(tree)
                              if isinstance(n, ast.ClassDef))

            reasons = []
            if lines > max_lines:
                reasons.append(f"{lines} 行 (上限 {max_lines})")
            if func_count > max_functions:
                reasons.append(f"{func_count} 个函数 (上限 {max_functions})")

            if reasons:
                findings.append({
                    "file": f.name,
                    "lines": lines,
                    "functions": func_count,
                    "classes": class_count,
                    "reasons": reasons,
                    "detail": f"{f.name}: {'; '.join(reasons)}",
                    "severity": "medium",
                })
        return sorted(findings, key=lambda x: -x["lines"])

    def find_similar_modules(self, similarity_threshold: float = 0.6) -> List[Dict[str, Any]]:
        """找到结构相似的模块（基于 import Jaccard 相似度）"""
        module_imports: Dict[str, Set[str]] = {}

        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue

            imports: Set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])
            module_imports[f.name] = imports

        similar_pairs = []
        names = list(module_imports.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = module_imports[names[i]], module_imports[names[j]]
                if not a and not b:
                    continue
                intersection = a & b
                union = a | b
                jaccard = len(intersection) / len(union) if union else 0

                if jaccard >= similarity_threshold:
                    similar_pairs.append({
                        "module_a": names[i],
                        "module_b": names[j],
                        "similarity": round(jaccard, 2),
                        "shared_imports": sorted(intersection),
                        "detail": f"{names[i]} ↔ {names[j]}: import 相似度 {jaccard:.0%}",
                        "severity": "info",
                    })

        return similar_pairs

    # ═══════════════════════════════════════════════
    # 知识模式
    # ═══════════════════════════════════════════════

    def find_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """基于知识图的缺口发现（孤立实体、未分类实体）"""
        if not self._kg:
            return []
        return self._kg.find_gaps()

    def find_concept_clusters(self) -> List[Dict[str, Any]]:
        """概念聚类：找到紧密关联的实体群"""
        if not self._kg:
            return []
        from collections import defaultdict, deque

        # 获取所有概念实体
        concepts = self._kg.find_entities("concept")
        concept_ids = {e.id for e in concepts}
        if not concept_ids:
            return []

        # 邻近表
        adj: Dict[str, Set[str]] = defaultdict(set)
        for r in self._kg._relations:
            if r.source in concept_ids and r.target in concept_ids:
                adj[r.source].add(r.target)
                adj[r.target].add(r.source)

        # BFS 聚类
        visited: Set[str] = set()
        clusters: List[Dict[str, Any]] = []
        for cid in concept_ids:
            if cid in visited:
                continue
            queue = deque([cid])
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

            if len(group) >= 2:
                names = [self._kg.get_entity(e).name
                         for e in group if self._kg.get_entity(e)]
                clusters.append({
                    "size": len(group),
                    "entities": names,
                    "detail": f"聚类: {', '.join(names[:5])}{'...' if len(names) > 5 else ''}",
                })

        return sorted(clusters, key=lambda x: -x["size"])

    def find_redundant_entries(self, knowledge_base) -> List[Dict[str, Any]]:
        """找到知识库中可能冗余的条目（基于关键词重叠）"""
        all_kb = knowledge_base.get_all_knowledge()
        redundant = []

        for i in range(len(all_kb)):
            for j in range(i + 1, len(all_kb)):
                a, b = all_kb[i], all_kb[j]
                kw_a = set(a.get("keywords", []))
                kw_b = set(b.get("keywords", []))
                if not kw_a or not kw_b:
                    continue

                overlap = kw_a & kw_b
                overlap_ratio = len(overlap) / max(len(kw_a), len(kw_b))
                if overlap_ratio >= 0.7:
                    redundant.append({
                        "topic_a": a.get("topic", ""),
                        "topic_b": b.get("topic", ""),
                        "overlap_keywords": sorted(overlap),
                        "overlap_ratio": round(overlap_ratio, 2),
                        "detail": f"'{a.get('topic')}' ↔ '{b.get('topic')}': 关键词重叠 {overlap_ratio:.0%}",
                        "severity": "low",
                    })

        return redundant

    def analyze_all(self, knowledge_base=None) -> Dict[str, Any]:
        """运行所有模式分析，返回完整报告"""
        results = {
            "bare_excepts": self.find_bare_excepts(),
            "missing_docstrings": self.find_missing_docstrings(),
            "dead_code": self.find_dead_code(),
            "complex_modules": self.find_complex_modules(),
            "similar_modules": self.find_similar_modules(),
            "knowledge_gaps": self.find_knowledge_gaps(),
            "concept_clusters": self.find_concept_clusters(),
        }

        if knowledge_base:
            results["redundant_entries"] = self.find_redundant_entries(knowledge_base)

        # 全局统计
        total_issues = sum(len(v) for v in results.values() if isinstance(v, list))
        high = sum(1 for items in results.values()
                   if isinstance(items, list)
                   for item in items if item.get("severity") == "high")

        results["summary"] = {
            "total_issues": total_issues,
            "high_severity": high,
        }
        return results


if __name__ == "__main__":
    pe = PatternEngine()

    # 代码模式
    bare = pe.find_bare_excepts()
    print(f"Bare excepts: {len(bare)} 处")

    doc = pe.find_missing_docstrings()
    print(f"低文档覆盖率: {len(doc)} 个模块")

    dead = pe.find_dead_code()
    print(f"可能未使用的代码: {sum(d['unused_count'] for d in dead)} 处")

    complex_mods = pe.find_complex_modules()
    print(f"复杂模块: {len(complex_mods)} 个")

    similar = pe.find_similar_modules()
    print(f"相似模块对: {len(similar)} 对")

    # 知识模式（需要知识图）
    from knowledge_graph import KnowledgeGraph
    from knowledge_base import KnowledgeBase
    kg = KnowledgeGraph()
    pe._kg = kg

    gaps = pe.find_knowledge_gaps()
    print(f"知识缺口: {len(gaps)} 处")

    kb = KnowledgeBase()
    redundant = pe.find_redundant_entries(kb)
    print(f"冗余条目: {len(redundant)} 对")

    print("✅ 模式引擎测试完成")
