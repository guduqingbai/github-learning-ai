#!/usr/bin/env python3
"""
🧠 自我思考Agent - 真正的自我思考核心能力
好奇心驱动的自我扫描→发现→探索→学习循环
所有输出基于真实项目数据，无随机模拟
"""

import json
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class SelfThinkingAgent:
    """自我思考Agent - 好奇心驱动的真实思考引擎"""

    def __init__(self):
        from self_scanner import SelfScanner
        from curiosity_engine import CuriosityEngine
        self.scanner = SelfScanner()
        self.curiosity = CuriosityEngine()
        self.snapshot = None
        self.diff = None
        self.questions: List = []
        self.thinking_log: List[Dict] = []
        self.data_dir = Path("data")
        self.log_file = self.data_dir / "self_thinking_log.json"

    # ---- 核心循环 ----

    def run_thinking_cycle(self, depth: int = 3) -> List[Dict]:
        """
        执行一轮完整思考循环

        1. 扫描项目当前状态
        2. 从数据中生成好奇心问题
        3. 对 top N 问题分别探索并生成洞察
        4. 将洞察存入知识库
        5. 记录思考日志
        """
        print(f"\n{'='*60}")
        print(f"🧠 自我思考循环启动 [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"{'='*60}")

        # 1. 扫描
        self._scan_project()
        print(f"📡 扫描完成: {len(self.snapshot.get('py_files', []))} 文件, "
              f"{self.snapshot.get('knowledge_base', {}).get('total_entries', 0)} 知识条目")

        # 2. 生成好奇心问题
        self._generate_questions()
        if not self.questions:
            print("💤 当前没有特别的好奇心触发")
            return []

        print(f"❓ 生成了 {len(self.questions)} 个好奇心问题")
        for q in self.questions[:depth]:
            print(f"   [{q.importance:.2f}] {q.question[:80]}...")

        # 3. 探索 top N 问题
        cycle_results = []
        for i, q in enumerate(self.questions[:depth]):
            print(f"\n{'─'*40}")
            print(f"🔍 探索问题 {i+1}/{depth}: {q.question[:80]}")
            print(f"{'─'*40}")

            exploration = self._explore_question(q)
            insight = self._generate_insight(q, exploration)
            stored = self._store_insight(insight)
            cycle_results.append(insight)

            print(f"   ✅ 洞察已{'存入' if stored else '生成'}: {insight.get('summary', '')[:100]}")

            # 如果是知识缺口，添加爬虫任务
            if q.explore_action == "add_crawler_task":
                added = self._add_crawler_tasks(q)
                print(f"   🎯 爬虫任务已{'添加' if added else '存在'}: {q.target}")

        # 4. 记录思考日志
        self._log_thinking_cycle(cycle_results)
        print(f"\n✅ 思考循环完成，生成 {len(cycle_results)} 个洞察")

        return cycle_results

    def _scan_project(self):
        """扫描项目当前状态"""
        self.snapshot = self.scanner.get_full_snapshot()
        self.diff = self.scanner.diff_from_previous(self.snapshot)
        self.scanner.save_snapshot(self.snapshot)

    def _generate_questions(self):
        """从扫描数据生成好奇心问题"""
        self.questions = self.curiosity.generate_questions(self.snapshot, self.diff)

    # ---- 探索方法 ----

    def _explore_question(self, q) -> Dict[str, Any]:
        """根据问题类型执行探索"""
        action = q.explore_action
        target = q.target

        if action == "read_file":
            return self._explore_read_file(target)
        elif action == "compare_files":
            files = target.split(",")
            if len(files) == 2:
                return self._explore_compare_files(files[0], files[1])
            return {"error": "need 2 files for comparison"}
        elif action == "add_crawler_task":
            return self._explore_check_gap(q)
        elif action == "check_state":
            return self._explore_check_state(target)
        elif action == "list_new_entries":
            return self._explore_list_new_entries(q)
        else:
            return {"note": f"未知探索动作: {action}"}

    def _explore_read_file(self, filepath: str) -> Dict[str, Any]:
        """读取文件，提取结构信息"""
        full_path = Path(filepath)
        if not full_path.exists():
            full_path = Path.cwd() / filepath
        if not full_path.exists():
            return {"error": f"文件不存在: {filepath}"}

        try:
            import ast
            code = full_path.read_text(encoding="utf-8")
            tree = ast.parse(code)

            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({"name": node.name, "methods": methods})

            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            imports = []
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    imports.extend(a.name for a in n.names)
                elif isinstance(n, ast.ImportFrom):
                    if n.module:
                        imports.append(n.module)

            # 提取模块文档
            docstring = ast.get_docstring(tree) or ""

            top_imports = sorted(set(i.split(".")[0] for i in imports))
            return {
                "file": filepath,
                "lines": len(code.splitlines()),
                "classes": classes,
                "top_functions": funcs[:10],
                "function_count": len(funcs),
                "imports": top_imports,
                "import_count": len(top_imports),
                "docstring": docstring[:200] if docstring else "(无模块文档)",
                "has_main": any(
                    isinstance(n, ast.If) and
                    isinstance(n.test, ast.Compare) and
                    isinstance(n.test.left, ast.Name) and
                    n.test.left.id == "__name__"
                    for n in ast.walk(tree)
                ),
            }
        except SyntaxError as e:
            return {"error": f"语法错误: {e}"}

    def _explore_compare_files(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """对比两个文件的结构"""
        info_a = self._explore_read_file(file_a)
        info_b = self._explore_read_file(file_b)

        if "error" in info_a or "error" in info_b:
            return {"error": "无法比较"}

        imports_a = set(info_a.get("imports", []))
        imports_b = set(info_b.get("imports", []))

        overlap = imports_a & imports_b
        jaccard = len(overlap) / max(1, len(imports_a | imports_b))

        return {
            "file_a": file_a,
            "file_b": file_b,
            "import_overlap": list(overlap),
            "jaccard_similarity": round(jaccard, 2),
            "classes_a": len(info_a.get("classes", [])),
            "classes_b": len(info_b.get("classes", [])),
            "conclusion": "可能重复" if jaccard > 0.6 else "不太可能重复",
        }

    def _explore_check_gap(self, q) -> Dict[str, Any]:
        """检查知识缺口详情"""
        ctx = q.context
        domain = ctx.get("domain", q.target)
        missing = ctx.get("missing", [])

        return {
            "domain": domain,
            "missing_topics": missing,
            "gap_count": len(missing),
            "suggested_queries": [f"{t} 教程" if "基础" in t or "入门" in t else t
                                  for t in missing[:5]],
        }

    def _explore_check_state(self, target: str) -> Dict[str, Any]:
        """检查系统状态"""
        try:
            from system_state_manager import SystemStateManager
            sm = SystemStateManager()
            return {"state": sm.get_global_state()}
        except Exception as e:
            return {"error": str(e)}

    def _explore_list_new_entries(self, q) -> Dict[str, Any]:
        """列出新条目/待探索模块"""
        ctx = q.context
        undocumented = ctx.get("undocumented", [])
        if undocumented:
            return {
                "type": "undocumented_modules",
                "modules": undocumented,
                "count": len(undocumented),
            }
        kb_data = self.snapshot.get("knowledge_base", {})
        return {
            "type": "kb_summary",
            "categories": kb_data.get("category_breakdown", {}),
        }

    # ---- 洞察生成与存储 ----

    def _generate_insight(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从探索结果生成洞察"""
        if "error" in exploration:
            return {
                "observation": q.observation,
                "question": q.question,
                "summary": f"探索失败: {exploration['error']}",
                "exploration": exploration,
            }

        if q.explore_action == "read_file":
            return self._insight_from_file(q, exploration)
        elif q.explore_action == "compare_files":
            return self._insight_from_comparison(q, exploration)
        elif q.explore_action == "add_crawler_task":
            return self._insight_from_gap(q, exploration)
        else:
            return {
                "observation": q.observation,
                "question": q.question,
                "summary": f"探索 {q.target} 完成",
                "exploration": exploration,
            }

    def _insight_from_file(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从文件探索生成洞察"""
        file = exploration.get("file", q.target)
        classes = exploration.get("classes", [])
        funcs = exploration.get("top_functions", [])
        imports = exploration.get("imports", [])
        doc = exploration.get("docstring", "")
        lines = exploration.get("lines", 0)

        # 根据代码结构自动生成摘要
        parts = []
        if classes:
            class_desc = ", ".join(f"{c['name']}({len(c['methods'])}方法)" for c in classes[:5])
            parts.append(f"定义了 {len(classes)} 个类: {class_desc}")
        if funcs:
            parts.append(f"包含 {exploration.get('function_count', 0)} 个函数")
        if imports:
            parts.append(f"依赖 {exploration.get('import_count', 0)} 个外部模块")

        primary_purpose = doc[:100] if doc and doc != "(无模块文档)" else "模块文档缺失"
        summary = f"{file} ({lines}行): {primary_purpose}。{'; '.join(parts)}。"

        # 模块文档缺失本身也是一个发现
        findings = []
        if doc == "(无模块文档)":
            findings.append("模块级文档缺失")

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"{file.replace('.py', '')} 模块分析",
            "category": "项目自身",
            "content": f"{summary}\n\n结构:\n- 类: {json.dumps(classes, ensure_ascii=False)}\n- 主要函数: {funcs}\n- imports: {imports}",
            "keywords": [file.replace(".py", ""), "模块分析"] + \
                        ([c["name"] for c in classes[:3]] if classes else []),
            "findings": findings,
            "origin": "self_thinking",
        }

    def _insight_from_comparison(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        s = exploration.get("jaccard_similarity", 0)
        a = exploration.get("file_a", "")
        b = exploration.get("file_b", "")
        conclusion = exploration.get("conclusion", "")

        summary = f"对比 {a} 和 {b}: import 相似度 {s:.0%}，{conclusion}。"

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"{a} vs {b} 相似度分析",
            "category": "项目自身",
            "content": summary,
            "keywords": [a.replace(".py", ""), b.replace(".py", ""), "相似度分析"],
            "findings": [],
            "origin": "self_thinking",
        }

    def _insight_from_gap(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        domain = exploration.get("domain", q.target)
        missing = exploration.get("missing_topics", [])

        summary = f"发现知识缺口: {domain} 领域缺 {len(missing)} 个子话题，已生成爬虫任务。"

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"知识缺口: {domain}",
            "category": "项目自身",
            "content": f"领域 {domain} 缺少以下知识: {', '.join(missing)}。已生成定向爬虫任务。",
            "keywords": [domain, "知识缺口"],
            "findings": [f"缺失 {len(missing)} 个话题"],
            "origin": "self_thinking",
            "action_taken": "add_crawler_tasks",
        }

    def _store_insight(self, insight: Dict[str, Any]) -> bool:
        """将洞察存入知识库"""
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()

            topic = insight.get("topic", "")
            if not topic:
                return False

            # 先检查是否已存在
            existing = kb.get_all_knowledge()
            if any(item.get("topic") == topic for item in existing):
                return False

            entry = {
                "topic": topic,
                "category": insight.get("category", "项目自身"),
                "content": insight.get("content", insight.get("summary", "")),
                "source": "自我思考",
                "keywords": insight.get("keywords", []),
                "references": [],
                "importance": 0.9,
                "learning_time": datetime.now().isoformat(),
            }
            return kb.add_knowledge(entry)
        except Exception as e:
            print(f"⚠️  知识库存储失败: {e}")
            return False

    def _add_crawler_tasks(self, q) -> bool:
        """为知识缺口添加爬虫任务"""
        try:
            ctx = q.context
            domain = ctx.get("domain", q.target)
            missing = ctx.get("missing", [])

            if not missing:
                return False

            task_file = self.data_dir / "crawler_tasks.json"

            # 读取现有任务
            existing_tasks = []
            if task_file.exists():
                with open(task_file, encoding="utf-8") as f:
                    existing_tasks = json.load(f)

            existing_queries = {t.get("query", "") for t in existing_tasks}

            # 添加新任务（去重）
            added = 0
            for topic in missing:
                query = f"{topic} 教程" if "基础" in topic or "入门" in topic else topic
                if query not in existing_queries:
                    existing_tasks.append({
                        "query": query,
                        "domain": domain,
                        "reason": f"好奇心引擎发现知识缺口: {domain} 领域缺少 {topic}",
                    })
                    existing_queries.add(query)
                    added += 1

            if added > 0:
                with open(task_file, "w", encoding="utf-8") as f:
                    json.dump(existing_tasks, f, ensure_ascii=False, indent=2)

            return added > 0
        except Exception as e:
            print(f"⚠️  添加爬虫任务失败: {e}")
            return False

    # ---- 日志 ----

    def _log_thinking_cycle(self, results: List[Dict[str, Any]]):
        """记录思考循环"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "cycle_id": str(uuid.uuid4()),
            "questions_count": len(self.questions),
            "insights_generated": len(results),
            "insights": [
                {
                    "topic": r.get("topic", ""),
                    "summary": r.get("summary", "")[:200],
                    "action": r.get("action_taken", "none"),
                }
                for r in results
            ],
            "snapshot_summary": {
                "py_files": len(self.snapshot.get("py_files", [])),
                "kb_entries": self.snapshot.get("knowledge_base", {}).get("total_entries", 0),
                "knowledge_gaps": len(self.snapshot.get("knowledge_gaps", [])),
                "changes": self.diff.get("changes", []) if self.diff else [],
            },
        }
        self.thinking_log.append(entry)

        # 持久化
        self.data_dir.mkdir(exist_ok=True)
        try:
            existing = []
            if self.log_file.exists():
                with open(self.log_file, encoding="utf-8") as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  思考日志保存失败: {e}")

    # ---- 查询接口 ----

    def get_thinking_report(self) -> Dict[str, Any]:
        """获取思考报告"""
        return {
            "current_snapshot": self.snapshot,
            "questions": [
                {"observation": q.observation, "question": q.question,
                 "importance": q.importance, "action": q.explore_action}
                for q in (self.questions or [])
            ],
            "recent_logs": self.thinking_log[-5:] if self.thinking_log else [],
        }

    # ---- 演示 ----

    def demonstrate_self_thinking(self):
        """展示自我思考能力"""
        print("🎯 自我思考Agent演示")
        print("=" * 60)

        results = self.run_thinking_cycle(depth=3)

        if results:
            print(f"\n{'='*60}")
            print("📊 本次思考发现:")
            print(f"{'='*60}")
            for r in results:
                print(f"\n  📝 {r.get('topic', '')}")
                print(f"     {r.get('summary', '')[:150]}")
        else:
            print("\n💤 没有新的发现")

        print(f"\n{'='*60}")
        print("✅ 自我思考演示完成")
        print(f"{'='*60}")

    def save_reflection(self):
        """保存反思记录（兼容旧接口）"""
        report = self.get_thinking_report()
        ref_file = self.data_dir / "self_thinking_reflection.json"
        self.data_dir.mkdir(exist_ok=True)
        with open(ref_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)


def main():
    agent = SelfThinkingAgent()
    agent.demonstrate_self_thinking()


if __name__ == "__main__":
    main()
