"""
🔬 探索引擎 — 从 self_thinking_agent.py 抽出
每个探索动作对应一个问题类型，返回结构化探索结果
"""

import ast
import json
import ssl
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional


class ExploreEngine:
    """探索引擎：依赖注入方式引用 agent，执行各类探索动作"""

    def __init__(self, agent):
        self._agent = agent

    # ── 属性代理（避免直接访问 self._agent 内部）──

    @property
    def data_dir(self) -> Path:
        return self._agent.data_dir

    def _check_feature(self, key: str) -> bool:
        return self._agent._check_feature(key)

    def _get_experience_tracker(self):
        return self._agent._get_experience_tracker()

    def _get_personality(self):
        return self._agent._get_personality()

    def _get_research_integration(self):
        return self._agent._get_research_integration()

    def _get_gap_analyzer(self):
        return self._agent._get_gap_analyzer()

    def _get_capability_registry(self):
        return self._agent._get_capability_registry()

    # ── 主入口 ──

    def explore_question(self, q) -> Dict[str, Any]:
        """根据问题类型执行探索"""
        action = q.explore_action
        target = q.target

        et = self._get_experience_tracker()
        problem = target or q.question[:80]
        if et.should_retry(problem, action, max_failures=3):
            alt_strategies = et.get_successful_strategies(problem)
            if alt_strategies:
                print(f"  ⏭️ '{problem[:40]}' 的 '{action}' 已失败多次，尝试替代策略: {alt_strategies[0]}")
                action = alt_strategies[0]
            else:
                print(f"  ⏭️ '{problem[:40]}' 的 '{action}' 已失败多次，跳过")
                return {"note": f"经验记忆跳过: {action} 对 {problem} 已失败 3+ 次"}

        if action == "read_file":
            return self.explore_read_file(target)
        elif action == "compare_files":
            files = target.split(",")
            if len(files) == 2:
                return self.explore_compare_files(files[0], files[1])
            return {"error": "need 2 files for comparison"}
        elif action == "add_crawler_task":
            if not self._check_feature("network_crawler"):
                return {"note": f"network_crawler 已禁用，跳过: {target}"}
            return self.explore_check_gap(q)
        elif action == "check_state":
            return self.explore_check_state(target)
        elif action == "list_new_entries":
            return self.explore_list_new_entries(q)
        elif action == "global_research":
            if not self._check_feature("global_research"):
                return {"note": f"global_research 已禁用，跳过: {target}"}
            return self.explore_global_research(q)
        elif action == "web_research":
            return self.explore_web_research(q)
        elif action in ("self_heal", "code_quality_heal"):
            if not self._check_feature("self_modification"):
                return {"note": f"self_modification 已禁用，跳过修复: {target}"}
            return self.explore_self_heal(q)
        elif action == "deep_learning":
            return self.explore_deep_learning(q)
        elif action == "llm_analysis":
            if not self._check_feature("local_thinking"):
                return {"note": f"local_thinking 已禁用，跳过 LLM 分析: {target}"}
            return self.explore_llm_analysis(q)
        else:
            return {"note": f"未知探索动作: {action}"}

    # ── 各类探索 ──

    def explore_read_file(self, filepath: str) -> Dict[str, Any]:
        """读取文件，提取结构信息"""
        full_path = Path(filepath)
        if not full_path.exists():
            full_path = Path.cwd() / filepath
        if not full_path.exists():
            return {"error": f"文件不存在: {filepath}"}

        try:
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
                    isinstance(n, ast.If)
                    and isinstance(n.test, ast.Compare)
                    and isinstance(n.test.left, ast.Name)
                    and n.test.left.id == "__name__"
                    for n in ast.walk(tree)
                ),
            }
        except SyntaxError as e:
            return {"error": f"语法错误: {e}"}

    def explore_compare_files(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """对比两个文件的结构"""
        info_a = self.explore_read_file(file_a)
        info_b = self.explore_read_file(file_b)

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

    def explore_check_gap(self, q) -> Dict[str, Any]:
        """检查知识缺口详情"""
        ctx = q.context
        domain = ctx.get("domain", q.target)
        missing = ctx.get("missing", [])

        return {
            "domain": domain,
            "missing_topics": missing,
            "gap_count": len(missing),
            "suggested_queries": [
                f"{t} 教程" if "基础" in t or "入门" in t else t
                for t in missing[:5]
            ],
        }

    def explore_check_state(self, target: str) -> Dict[str, Any]:
        """检查系统状态"""
        try:
            from system_state_manager import SystemStateManager
            sm = SystemStateManager()
            return {"state": sm.get_global_state()}
        except Exception as e:
            return {"error": str(e)}

    def explore_list_new_entries(self, q) -> Dict[str, Any]:
        """列出新条目/待探索模块"""
        ctx = q.context
        undocumented = ctx.get("undocumented", [])
        if undocumented:
            return {
                "type": "undocumented_modules",
                "modules": undocumented,
                "count": len(undocumented),
            }
        kb_data = self._agent.snapshot.get("knowledge_base", {})
        return {
            "type": "kb_summary",
            "categories": kb_data.get("category_breakdown", {}),
        }

    # ── 外部研究 ──

    def explore_web_research(self, q) -> Dict[str, Any]:
        """自主多源研究：即时搜索+读内容+综合答案"""
        target = q.target or q.question
        print(f"  🔬 自主研究: \"{target[:80]}\"")
        try:
            ri = self._get_research_integration()
            result = ri.execute_research(target)
            return result
        except Exception as e:
            print(f"  ⚠️ 研究失败: {e}")
            return {
                "observation": getattr(q, 'observation', ''),
                "question": q.question,
                "summary": f"研究执行异常: {e}",
                "action_taken": "web_research_error",
            }

    def explore_global_research(self, q) -> Dict[str, Any]:
        """全球研究：调爬虫和持续学习系统搜索全球资料"""
        ctx = q.context
        queries = ctx.get("research_queries", [])
        results = []

        print(f"   🌐 全球研究: 发起 {len(queries)} 个搜索查询")

        task_file = self.data_dir / "crawler_tasks.json"
        existing_tasks = []
        if task_file.exists():
            with open(task_file, encoding="utf-8") as f:
                existing_tasks = json.load(f)
        existing_queries = {t.get("query", "") for t in existing_tasks}

        added = 0
        for query in queries:
            if query not in existing_queries:
                existing_tasks.append({
                    "query": query,
                    "domain": "自思考架构研究",
                    "reason": f"好奇心引擎全球研究: {q.question[:80]}",
                    "priority": "high",
                })
                existing_queries.add(query)
                added += 1

        if added > 0:
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(existing_tasks, f, ensure_ascii=False, indent=2)

        try:
            from ai_knowledge_crawler import AIKnowledgeCrawler
            for query in queries[:3]:
                try:
                    search_term = query.replace(" ", "+")
                    url = f"https://api.github.com/search/repositories?q={search_term}&sort=stars&per_page=3"
                    req = urllib.request.Request(url, headers={
                        "User-Agent": "Mozilla/5.0 (compatible; SelfThinkingBot/1.0)"
                    })
                    with urllib.request.urlopen(req, timeout=10, context=ssl._create_unverified_context()) as resp:
                        data = json.loads(resp.read().decode())
                        for repo in data.get("items", [])[:3]:
                            results.append({
                                "title": repo["full_name"],
                                "description": (repo.get("description") or "")[:200],
                                "stars": repo.get("stargazers_count", 0),
                                "url": repo["html_url"],
                                "source": "GitHub",
                            })
                    time.sleep(1)
                except Exception as e:
                    print(f"   ⚠️  搜索 '{query}' 失败: {e}")
        except Exception as e:
            print(f"   ⚠️  实时搜索异常: {e}")

        try:
            for query in queries[:2]:
                try:
                    url = f"http://export.arxiv.org/api/query?search_query=all:{query.replace(' ', '+')}&sortBy=relevance&max_results=3"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=15, context=ssl._create_unverified_context()) as resp:
                        xml = resp.read().decode("utf-8")
                        import re as re_mod
                        titles = re_mod.findall(r"<title>(.*?)</title>", xml, re_mod.DOTALL)
                        for i, t in enumerate(titles[1:4], 1):
                            results.append({
                                "title": t.strip().replace("\n", " ")[:150],
                                "description": f"arXiv论文: {query}",
                                "stars": 0,
                                "url": f"https://arxiv.org/search/?query={query}",
                                "source": "arXiv",
                            })
                    time.sleep(3)
                except Exception:
                    pass
        except Exception:
            pass

        return {
            "research_topic": q.target,
            "queries_scheduled": len(queries),
            "crawler_tasks_added": added,
            "real_time_results": len(results),
            "sample_results": results[:5],
            "note": f"已添加 {added} 个爬虫任务，实时获取 {len(results)} 条结果。更多结果将在后台爬取。"
        }

    # ── 自我修复 ──

    def explore_self_heal(self, q) -> Dict[str, Any]:
        """探索并尝试修复代码问题"""
        from self_modification_engine import SelfModificationEngine
        engine = SelfModificationEngine()

        engine.configure_sub_gates(
            allow_bare_except_fix=self._check_feature("modification_bare_except"),
            allow_docstring_add=self._check_feature("modification_docstring"),
            allow_unused_import_remove=self._check_feature("modification_unused_import"),
            allow_destructive_change=self._check_feature("modification_destructive"),
        )

        fix_results = []
        ctx = q.context or {}
        fix_type = ctx.get("type", "bare_except")
        files = [f.strip() for f in q.target.split(",") if f.strip()]

        if fix_type == "bare_except":
            for file in files:
                result = engine.fix_bare_excepts(file)
                fix_results.append({
                    "type": "fix_bare_except",
                    "file": file,
                    "success": result.get("success", False),
                    "detail": result.get("error", "已修复"),
                    "error_kind": result.get("error_kind", ""),
                })

        elif fix_type == "missing_doc":
            for file in files:
                module_name = Path(file).stem
                result = engine.add_module_docstring(file, f"{module_name} module")
                fix_results.append({
                    "type": "add_docstring",
                    "file": file,
                    "success": result.get("success", False),
                    "detail": result.get("error", "已修复"),
                    "error_kind": result.get("error_kind", ""),
                })

        if not fix_results:
            fix_results.append({
                "type": "inspection",
                "file": q.target,
                "success": False,
                "detail": "未找到可自动修复的问题",
            })

        return {
            "target": q.target,
            "fixes_attempted": len(fix_results),
            "fixes_succeeded": sum(1 for r in fix_results if r["success"]),
            "fix_results": fix_results,
        }

    # ── 深度能力学习 ──

    def explore_deep_learning(self, q) -> Dict[str, Any]:
        if not self._check_feature("capability_learning"):
            return {"note": f"capability_learning 已禁用，跳过: {q.target}"}

        target = q.target or q.question[:60]
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        refs = kb.get_knowledge_by_category("能力参考")
        target_refs = [r for r in refs
                       if target.lower() in r.get("topic", "").lower()] if refs else []

        analyzer = self._get_gap_analyzer()
        registry = self._get_capability_registry()
        missing = analyzer.find_missing_capabilities(target_refs or refs)

        return {
            "observation": q.observation,
            "question": q.question,
            "topic": target[:100],
            "summary": f"能力深度探索 [{target[:50]}]: 发现 {len(missing)} 个潜在能力差距",
            "missing_capabilities": [m.topic for m in missing[:5]],
            "action_taken": "deep_learning",
        }

    # ── LLM 分析 ──

    def explore_llm_analysis(self, q) -> Dict[str, Any]:
        """LLM 深度分析：调用本地模型分析代码问题"""
        try:
            from llm_client import get_llm_client
            from llm_prompts import get_prompt
        except ImportError:
            return {"note": "LLM 模块未安装，跳过分析"}

        client = get_llm_client()
        if not client.is_available():
            return {"note": "LLM 不可用，跳过分析"}

        target = getattr(q, 'target', '') or getattr(q, 'filepath', '') or ''
        context = ""
        if target and Path(target).exists():
            lines = Path(target).read_text(encoding="utf-8").split("\n")
            context = "\n".join(lines[:30])

        prompt = get_prompt(
            "llm_analysis",
            question=getattr(q, 'question', '代码分析'),
            target=target or '未知',
            context=context or '无',
        )
        result = client.chat("你是一个代码分析助手。保持简洁。", prompt)

        if not result.success:
            return {"note": f"LLM 分析失败: {result.error}"}

        return {
            "observation": getattr(q, 'observation', ''),
            "question": getattr(q, 'question', ''),
            "summary": result.content[:200],
            "topic": f"LLM 分析: {target or '通用'}",
            "category": "llm_analysis",
            "content": result.content,
            "keywords": ["llm", target.replace('.py', '')] if target else ["llm"],
            "origin": "self_thinking",
        }
