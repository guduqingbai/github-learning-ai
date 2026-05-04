#!/usr/bin/env python3
"""
自模型 — 基于 AST 深度分析系统自身代码
提取能力清单、依赖关系、对外接口
"""

import ast
from pathlib import Path
from typing import Dict, Any, List, Optional, Set


class SelfModel:
    """基于 AST 分析系统自身的代码结构"""

    def __init__(self, knowledge_graph=None):
        self.project_root = Path.cwd()
        self._kg = knowledge_graph

    def scan_capabilities(self) -> List[Dict[str, Any]]:
        """从所有 .py 文件的类/函数签名提取能力清单"""
        capabilities = []
        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body
                               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    decorators = [self._decorator_name(d) for d in node.decorator_list]
                    docstring = ast.get_docstring(node) or ""
                    capabilities.append({
                        "type": "class",
                        "module": f.name,
                        "name": node.name,
                        "methods": methods,
                        "method_count": len(methods),
                        "decorators": decorators,
                        "docstring_preview": docstring[:80],
                    })
                elif isinstance(node, ast.FunctionDef):
                    # 顶层函数（不在类里面）
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            if node in ast.walk(parent):
                                break
                    else:
                        decorators = [self._decorator_name(d)
                                      for d in node.decorator_list]
                        docstring = ast.get_docstring(node) or ""
                        capabilities.append({
                            "type": "function",
                            "module": f.name,
                            "name": node.name,
                            "args": [a.arg for a in node.args.args],
                            "arg_count": len(node.args.args),
                            "decorators": decorators,
                            "docstring_preview": docstring[:80],
                        })
        return capabilities

    def scan_dependencies(self) -> Dict[str, List[str]]:
        """模块间依赖关系矩阵（import 图）"""
        deps: Dict[str, List[str]] = {}
        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue

            module_name = f.name
            deps[module_name] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        base = alias.name.split(".")[0]
                        if base != module_name.replace(".py", ""):
                            deps[module_name].append(base)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        base = node.module.split(".")[0]
                        if base != module_name.replace(".py", ""):
                            deps[module_name].append(base)

            deps[module_name] = list(set(deps[module_name]))
        return deps

    def scan_interfaces(self) -> List[Dict[str, Any]]:
        """每个模块对外暴露的 API（非私有顶层函数和类）"""
        interfaces = []
        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue

            public_items = []
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        docstring = ast.get_docstring(node) or ""
                        public_items.append({
                            "type": "function",
                            "name": node.name,
                            "args": [a.arg for a in node.args.args],
                            "docstring_preview": docstring[:80],
                        })
                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith("_"):
                        docstring = ast.get_docstring(node) or ""
                        methods = [n.name for n in node.body
                                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        public_methods = [m for m in methods if not m.startswith("_")]
                        public_items.append({
                            "type": "class",
                            "name": node.name,
                            "public_methods": public_methods,
                            "public_method_count": len(public_methods),
                            "docstring_preview": docstring[:80],
                        })

            if public_items:
                interfaces.append({
                    "module": f.name,
                    "public_items": public_items,
                    "exposure_count": len(public_items),
                })
        return interfaces

    def find_entry_points(self) -> List[str]:
        """找到模块入口点（有 if __name__ == __main__ 的模块）"""
        entries = []
        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if (isinstance(node, ast.If)
                        and isinstance(node.test, ast.Compare)
                        and isinstance(node.test.left, ast.Name)
                        and node.test.left.id == "__name__"
                        and any(isinstance(c, ast.Constant)
                                and c.value == "__main__"
                                for c in node.test.comparators)):
                    entries.append(f.name)
                    break
        return entries

    def build_self_graph(self):
        """将自身结构写入 knowledge_graph"""
        if not self._kg:
            return {"error": "No knowledge graph provided"}

        results = {
            "modules_added": 0,
            "classes_added": 0,
            "functions_added": 0,
            "relations_added": 0,
        }

        # 每个 .py 文件 → module 实体
        deps = self.scan_dependencies()
        for f_name in deps:
            existing = self._kg.find_entity(f_name)
            if not existing:
                self._kg.add_entity(f_name, "module", {"file": f_name})
                results["modules_added"] += 1

        # 类 → class 实体，连接到所属模块
        capabilities = self.scan_capabilities()
        for cap in capabilities:
            if cap["type"] == "class":
                existing = self._kg.find_entity(cap["name"])
                if not existing:
                    eid = self._kg.add_entity(cap["name"], "class", {
                        "module": cap["module"],
                        "methods": cap["methods"],
                        "method_count": cap["method_count"],
                    })
                    results["classes_added"] += 1
                    # 连接到模块
                    mod_entity = self._kg.find_entity(cap["module"])
                    if mod_entity:
                        self._kg.add_relation(eid, mod_entity.id,
                                              "defined_in")
                        results["relations_added"] += 1

            elif cap["type"] == "function":
                existing = self._kg.find_entity(cap["name"])
                if not existing:
                    eid = self._kg.add_entity(cap["name"], "function", {
                        "module": cap["module"],
                        "args": cap["args"],
                        "arg_count": cap["arg_count"],
                    })
                    results["functions_added"] += 1
                    mod_entity = self._kg.find_entity(cap["module"])
                    if mod_entity:
                        self._kg.add_relation(eid, mod_entity.id,
                                              "defined_in")
                        results["relations_added"] += 1

        # import 依赖关系
        for module_name, imports in deps.items():
            mod_entity = self._kg.find_entity(module_name)
            if not mod_entity:
                continue
            for imp in imports:
                imp_file = f"{imp}.py"
                imp_entity = self._kg.find_entity(imp_file)
                if not imp_entity:
                    imp_entity = self._kg.find_entity(imp)
                if imp_entity:
                    self._kg.add_relation(mod_entity.id, imp_entity.id,
                                          "depends_on", 0.7)
                    results["relations_added"] += 1

        return results

    def generate_report(self) -> Dict[str, Any]:
        """生成自模型报告"""
        capabilities = self.scan_capabilities()
        deps = self.scan_dependencies()
        interfaces = self.scan_interfaces()
        entries = self.find_entry_points()

        classes = [c for c in capabilities if c["type"] == "class"]
        functions = [f for f in capabilities if f["type"] == "function"]

        # 依赖分析：使用最多/最少的模块
        dep_counts = {m: len(ims) for m, ims in deps.items()}
        most_depended = sorted(dep_counts.items(), key=lambda x: -x[1])[:5]

        # 被依赖最多的模块
        reverse_deps: Dict[str, int] = {}
        for m, ims in deps.items():
            for im in ims:
                reverse_deps[im] = reverse_deps.get(im, 0) + 1
        most_referenced = sorted(reverse_deps.items(),
                                 key=lambda x: -x[1])[:5]

        return {
            "total_modules": len(deps),
            "total_classes": len(classes),
            "total_functions": len(functions),
            "total_interfaces": sum(i["exposure_count"] for i in interfaces),
            "entry_points": entries,
            "most_dependent_modules": most_depended,
            "most_referenced_modules": most_referenced,
            "classes_by_module": {
                c["module"]: c["name"] for c in classes
            },
        }

    def generate_self_profile(self, data_sources: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        从多个运行时来源构建集成自我画像。

        Args:
            data_sources: 可选来源字典，包含:
                - experience_tracker: ExperienceTracker 实例
                - metacognitive_monitor: MetacognitiveMonitor 实例
                - knowledge_base: KnowledgeBase 实例
                - daemon_stats: ThinkingDaemon.get_status() 字典

        Returns:
            包含以下键的字典:
            - knowledge_domains: {category: strength}
            - strategy_effectiveness: {strategy: success_rate}
            - recent_trends: {direction: trend}
            - health: 0-1 复合健康值
            - confidence: 0-1 置信度
        """
        profile = {
            "knowledge_domains": {},
            "strategy_effectiveness": {},
            "recent_trends": {},
            "health": 0.5,
            "confidence": 0.5,
        }

        if not data_sources:
            return profile

        # 1. 知识领域分布
        kb = data_sources.get("knowledge_base")
        if kb is not None:
            try:
                all_k = kb.get_all_knowledge()
                cat_counts = {}
                for e in all_k:
                    c = e.get("category", "未分类")
                    cat_counts[c] = cat_counts.get(c, 0) + 1
                if cat_counts:
                    max_count = max(cat_counts.values())
                    profile["knowledge_domains"] = {
                        c: round(n / max_count, 3)
                        for c, n in sorted(cat_counts.items(),
                                           key=lambda x: -x[1])
                    }
            except Exception:
                pass

        # 2. 策略有效性
        et = data_sources.get("experience_tracker")
        if et is not None:
            try:
                summary = et.get_summary()
                profile["strategy_effectiveness"] = summary.get(
                    "strategy_success_rates", {})
            except Exception:
                pass

        # 3. 近期趋势（从元认知发现历史对比）
        mm = data_sources.get("metacognitive_monitor")
        if mm is not None:
            try:
                state_file = Path("data") / "metacognitive_state.json"
                if state_file.exists():
                    import json
                    mc_data = json.loads(
                        state_file.read_text(encoding="utf-8"))
                    history = mc_data.get("findings_history", [])
                    if len(history) >= 4:
                        mid = len(history) // 2
                        first_half = history[:mid]
                        second_half = history[mid:]
                        for ftype in ("confidence", "loop",
                                       "failure_risk", "stagnation"):
                            before = sum(
                                1 for h in first_half if h.get("type") == ftype)
                            after = sum(
                                1 for h in second_half if h.get("type") == ftype)
                            if after < before:
                                profile["recent_trends"][ftype] = "improving"
                            elif after > before:
                                profile["recent_trends"][ftype] = "worsening"
                            else:
                                profile["recent_trends"][ftype] = "stable"
                # 置信度
                profile["confidence"] = 0.5
                for h in mc_data.get("findings_history", []):
                    if h.get("type") == "confidence":
                        profile["confidence"] = max(
                            0, 1.0 - h.get("severity", 0.5))
            except Exception:
                pass

        # 4. 复合健康
        confidence = profile["confidence"]
        error_rate = 0.0
        heal_rate = 0.0
        d_stats = data_sources.get("daemon_stats")
        if d_stats:
            total = d_stats.get("total_heal_attempts", 0)
            errors = d_stats.get("error_count", 0)
            succ = d_stats.get("total_heal_successes", 0)
            error_rate = min(1.0, errors / max(1, total + errors))
            heal_rate = succ / max(1, total)
        profile["health"] = round(
            0.4 * confidence
            + 0.3 * (1.0 - error_rate)
            + 0.3 * heal_rate,
            3,
        )

        return profile

    @staticmethod
    def _decorator_name(node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return node.func.id
        return str(node)


if __name__ == "__main__":
    sm = SelfModel()

    report = sm.generate_report()
    print("=== 自模型报告 ===")
    print(f"模块数: {report['total_modules']}")
    print(f"类数: {report['total_classes']}")
    print(f"函数数: {report['total_functions']}")
    print(f"公开接口数: {report['total_interfaces']}")
    print(f"入口点: {report['entry_points']}")
    print(f"最多依赖的模块: {report['most_dependent_modules']}")
    print(f"被引用最多的模块: {report['most_referenced_modules']}")

    # 测试写入知识图
    from knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    sm._kg = kg
    result = sm.build_self_graph()
    print(f"\n写入图: {result}")
    stats = kg.get_statistics()
    print(f"图统计: {stats}")
    print("✅ 自模型测试完成")
