#!/usr/bin/env python3
"""
📡 自我扫描器 — 读取项目真实状态
纯数据采集，不包含任何随机/模拟值
"""

import ast
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class SelfScanner:
    """读取项目真实状态，返回结构化快照"""

    def __init__(self):
        self.data_dir = Path("data")
        self.project_root = Path.cwd()
        self.snapshot_file = self.data_dir / "self_scanner_snapshot.json"

    def scan_py_files(self) -> List[Dict[str, Any]]:
        """遍历所有 .py 文件，用 ast 解析结构"""
        results = []
        for f in sorted(self.project_root.glob("*.py")):
            try:
                code = f.read_text(encoding="utf-8")
                tree = ast.parse(code)

                classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                imports = []
                for n in ast.walk(tree):
                    if isinstance(n, ast.Import):
                        imports.extend(a.name.split(".")[0] for a in n.names)
                    elif isinstance(n, ast.ImportFrom):
                        if n.module:
                            imports.append(n.module.split(".")[0])

                docstring_count = sum(
                    1 for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                    and isinstance(n.body[0], ast.Expr)
                    and isinstance(n.body[0].value, ast.Constant)
                    and isinstance(n.body[0].value.value, str)
                )
                total_named = len(classes) + len(funcs)
                docstring_ratio = docstring_count / max(1, total_named)

                results.append({
                    "file": f.name,
                    "lines": len(code.splitlines()),
                    "classes": classes,
                    "functions": funcs,
                    "imports": list(set(imports)),
                    "import_count": len(set(imports)),
                    "docstring_ratio": round(docstring_ratio, 2),
                    "has_errors": False,
                })
            except SyntaxError as e:
                results.append({
                    "file": f.name,
                    "lines": 0,
                    "classes": [],
                    "functions": [],
                    "imports": [],
                    "import_count": 0,
                    "docstring_ratio": 0.0,
                    "has_errors": True,
                    "error": str(e),
                })
        return results

    def scan_system_state(self) -> Dict[str, Any]:
        """读 SystemStateManager 全部模块状态"""
        from system_state_manager import SystemStateManager
        sm = SystemStateManager()
        global_state = sm.get_global_state()
        summary = {}
        for module, data in global_state.items():
            summary[module] = {
                "keys": list(data.keys()) if isinstance(data, dict) else [],
                "key_count": len(data) if isinstance(data, dict) else 0,
            }
        return summary

    def scan_knowledge_base(self) -> Dict[str, Any]:
        """读 KnowledgeBase 统计数据"""
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        all_k = kb.get_all_knowledge()
        categories = {}
        for item in all_k:
            cat = item.get("category", "未分类")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_entries": len(all_k),
            "category_breakdown": dict(sorted(categories.items(), key=lambda x: -x[1])),
            "topics": [item.get("topic", "") for item in all_k],
        }

    def scan_self_learning_results(self) -> Dict[str, Any]:
        """调 SelfLearningSystem 获取代码质量分析"""
        try:
            from self_learning_system import SelfLearningSystem
            sls = SelfLearningSystem()
            issues = sls.check_system_vulnerabilities()
            quality = sls.analyze_code_quality()
            return {
                "vulnerabilities": len(issues) if issues else 0,
                "code_quality_issues": quality if isinstance(quality, (int, dict)) else 0,
            }
        except Exception as e:
            return {"vulnerabilities": 0, "code_quality_issues": 0, "error": str(e)}

    def scan_data_directory(self) -> List[Dict[str, Any]]:
        """扫描 data/ 目录"""
        results = []
        if self.data_dir.exists():
            for f in sorted(self.data_dir.glob("*.json")):
                try:
                    stat = f.stat()
                    results.append({
                        "file": f.name,
                        "size_bytes": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
                except OSError:
                    pass
        return results

    def scan_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """复用 SelfDirectedLearner 的 KNOWLEDGE_MAP 对比知识缺口"""
        try:
            from self_directed_learning import KNOWLEDGE_MAP
        except ImportError:
            return []

        kb_data = self.scan_knowledge_base()
        all_topics_lower = {t.lower() for t in kb_data.get("topics", [])}
        for item in self.scan_knowledge_base().get("topics", []):
            all_topics_lower.add(item.lower())

        gaps = []
        for domain, topics in KNOWLEDGE_MAP.items():
            missing = []
            for topic in topics:
                tl = topic.lower()
                found = any(tl in e or e in tl for e in all_topics_lower)
                if not found:
                    missing.append(topic)
            if missing:
                gaps.append({
                    "domain": domain,
                    "missing": missing,
                    "count": len(missing),
                    "total": len(topics),
                })
        return gaps

    def scan_crawler_tasks(self) -> List[Dict[str, Any]]:
        """读爬虫任务队列"""
        task_file = self.data_dir / "crawler_tasks.json"
        if task_file.exists():
            try:
                with open(task_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def scan_modification_history(self) -> Dict[str, Any]:
        """读取自我修改引擎的修改历史"""
        log_file = self.data_dir / "modification_log.json"
        if not log_file.exists():
            return {"total_attempts": 0, "successful": 0, "recent": []}
        try:
            with open(log_file, encoding="utf-8") as f:
                logs = json.load(f)
            total = len(logs)
            succeeded = sum(1 for l in logs if l.get("status") == "success")
            failed = sum(1 for l in logs if l.get("status") == "failed")
            rolled_back = sum(1 for l in logs if l.get("status") == "rolled_back")
            return {
                "total_attempts": total,
                "successful": succeeded,
                "failed": failed,
                "rolled_back": rolled_back,
                "recent": logs[-5:] if logs else [],
            }
        except Exception:
            return {"total_attempts": 0, "successful": 0, "recent": []}

    def get_full_snapshot(self) -> Dict[str, Any]:
        """全量快照"""
        return {
            "timestamp": datetime.now().isoformat(),
            "py_files": self.scan_py_files(),
            "system_state": self.scan_system_state(),
            "knowledge_base": self.scan_knowledge_base(),
            "self_learning": self.scan_self_learning_results(),
            "data_files": self.scan_data_directory(),
            "knowledge_gaps": self.scan_knowledge_gaps(),
            "crawler_tasks": {
                "pending": len(self.scan_crawler_tasks()),
            },
            "modification_history": self.scan_modification_history(),
        }

    def save_snapshot(self, snapshot: Dict[str, Any]):
        """保存快照到磁盘"""
        self.data_dir.mkdir(exist_ok=True)
        with open(self.snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

    def load_previous_snapshot(self) -> Optional[Dict[str, Any]]:
        """加载上次快照"""
        if self.snapshot_file.exists():
            try:
                with open(self.snapshot_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return None

    def diff_from_previous(self, current: Dict[str, Any]) -> Dict[str, Any]:
        """对比当前和上次快照，返回变化"""
        prev = self.load_previous_snapshot()
        if prev is None:
            return {"new_snapshot": True, "changes": ["首次扫描，无历史对比"]}

        changes = []

        # 对比 py_files
        prev_files = {f["file"]: f for f in prev.get("py_files", [])}
        curr_files = {f["file"]: f for f in current.get("py_files", [])}

        for name in curr_files:
            if name not in prev_files:
                changes.append(f"新增文件: {name}")
            elif curr_files[name]["lines"] != prev_files[name]["lines"]:
                changes.append(
                    f"文件变化: {name} "
                    f"({prev_files[name]['lines']}→{curr_files[name]['lines']}行)"
                )

        for name in prev_files:
            if name not in curr_files:
                changes.append(f"删除文件: {name}")

        # 对比 knowledge_base
        prev_kb = prev.get("knowledge_base", {})
        curr_kb = current.get("knowledge_base", {})
        prev_count = prev_kb.get("total_entries", 0)
        curr_count = curr_kb.get("total_entries", 0)
        if curr_count != prev_count:
            changes.append(f"知识库变化: {prev_count}→{curr_count}条")

        # 对比知识缺口
        prev_gaps = {(g["domain"], t) for g in prev.get("knowledge_gaps", []) for t in g.get("missing", [])}
        curr_gaps = {(g["domain"], t) for g in current.get("knowledge_gaps", []) for t in g.get("missing", [])}
        filled = prev_gaps - curr_gaps
        if filled:
            for domain, topic in filled:
                changes.append(f"缺口已补: {domain}/{topic}")

        return {
            "new_snapshot": False,
            "changes": changes,
            "change_count": len(changes),
        }


if __name__ == "__main__":
    scanner = SelfScanner()
    snap = scanner.get_full_snapshot()
    diff = scanner.diff_from_previous(snap)
    print("📡 自我扫描结果:")
    print(f"  Python文件: {len(snap['py_files'])}")
    print(f"  知识库条目: {snap['knowledge_base']['total_entries']}")
    print(f"  知识分类: {list(snap['knowledge_base']['category_breakdown'].keys())}")
    print(f"  知识缺口领域: {len(snap['knowledge_gaps'])}")
    print(f"  爬虫待处理: {snap['crawler_tasks']['pending']}")
    print(f"  变化: {diff.get('change_count', 0)}项")
    for c in diff.get("changes", []):
        print(f"    - {c}")
