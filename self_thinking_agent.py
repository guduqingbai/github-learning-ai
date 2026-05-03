#!/usr/bin/env python3
"""
🧠 自我思考Agent - 真正的自我思考核心能力
好奇心驱动的自我扫描→发现→探索→学习循环
所有输出基于真实项目数据，无随机模拟
"""

import json
import uuid
import os
import time
import ssl
import urllib.request
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
        self._skills = self._init_skills()

    # ---- 模块化思考技能系统 ----

    def _init_skills(self) -> Dict[str, Dict[str, Any]]:
        """注册可用思考技能（元数据+执行体，类似SKILL.md模式）"""
        return {
            "gap_analysis": {
                "name": "知识缺口分析",
                "description": "对比知识库与 KNOWLEDGE_MAP，发现缺失领域并生成爬虫任务",
                "trigger": "knowledge_gaps > 0",
                "default_depth": 5,
                "icon": "🔍",
            },
            "global_research": {
                "name": "全球架构研究",
                "description": "搜索GitHub/arXiv获取自思考AI架构和最佳实践",
                "trigger": "self_architecture_kb_missing",
                "default_depth": 3,
                "icon": "🌐",
            },
            "code_quality": {
                "name": "代码质量审查",
                "description": "扫描代码漏洞、质量问题和异常模式",
                "trigger": "vulnerabilities > 0 or quality_issues > 0",
                "default_depth": 3,
                "icon": "🔧",
            },
            "self_scan": {
                "name": "自身扫描",
                "description": "扫描项目结构和自知识别覆盖情况",
                "trigger": "self_kb_coverage < 50%",
                "default_depth": 3,
                "icon": "📡",
            },
            "full_cycle": {
                "name": "完整思考循环",
                "description": "运行所有思考技能（默认模式）",
                "trigger": "manual / scheduled",
                "default_depth": 4,
                "icon": "🧠",
            },
        }

    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有可用思考技能"""
        return [
            {
                "name": s["name"],
                "description": s["description"],
                "trigger": s["trigger"],
                "icon": s["icon"],
                "key": key,
            }
            for key, s in self._skills.items()
        ]

    def run_skill(self, skill_name: str, depth: Optional[int] = None) -> List[Dict]:
        """执行指定的思考技能"""
        skill = self._skills.get(skill_name)
        if not skill:
            print(f"⚠️  未知技能: {skill_name}")
            return []

        effective_depth = depth if depth is not None else skill["default_depth"]
        icon = skill["icon"]

        print(f"\n{icon} 执行思考技能: {skill['name']}")
        print(f"   描述: {skill['description']}")

        # 所有技能共享扫描阶段
        self._scan_project()

        if skill_name == "gap_analysis":
            return self._run_gap_skill(effective_depth)
        elif skill_name == "global_research":
            return self._run_research_skill(effective_depth)
        elif skill_name == "code_quality":
            return self._run_quality_skill(effective_depth)
        elif skill_name == "self_scan":
            return self._run_self_scan_skill(effective_depth)
        else:
            # full_cycle → 所有问题类型一起跑（原逻辑）
            return self._run_full_cycle(effective_depth)

    def _run_gap_skill(self, depth: int) -> List[Dict]:
        """知识缺口分析技能：只关注 gap 类问题"""
        self._generate_questions()
        gap_qs = [q for q in self.questions if q.explore_action == "add_crawler_task"]
        if not gap_qs:
            print("✅ 没有发现新的知识缺口")
            return []
        print(f"🔍 发现 {len(gap_qs)} 个知识缺口，探索 top {min(depth, len(gap_qs))}")
        return self._explore_and_store(gap_qs[:depth])

    def _run_research_skill(self, depth: int) -> List[Dict]:
        """全球研究技能：只关注 global_research 类问题"""
        self._generate_questions()
        research_qs = [q for q in self.questions if q.explore_action == "global_research"]
        if not research_qs:
            print("✅ 当前无需全球研究")
            return []
        print(f"🌐 发起 {len(research_qs)} 项全球研究，探索 top {min(depth, len(research_qs))}")
        return self._explore_and_store(research_qs[:depth])

    def _run_quality_skill(self, depth: int) -> List[Dict]:
        """代码质量技能：分析代码问题"""
        self._generate_questions()
        quality_qs = [q for q in self.questions if q.explore_action in ("check_state", "read_file")]
        if not quality_qs:
            print("✅ 未发现新的代码质量问题")
            return []
        print(f"🔧 发现 {len(quality_qs)} 个代码相关问题，探索 top {min(depth, len(quality_qs))}")
        return self._explore_and_store(quality_qs[:depth])

    def _run_self_scan_skill(self, depth: int) -> List[Dict]:
        """自身扫描技能：分析自知识覆盖"""
        self._generate_questions()
        self_qs = [q for q in self.questions if q.target == "project_self"]
        if not self_qs:
            print("✅ 项目自知识覆盖良好")
            return []
        return self._explore_and_store(self_qs[:depth])

    def _explore_and_store(self, questions: List) -> List[Dict]:
        """通用探索+存储流程（被各个技能复用）"""
        results = []
        for q in questions:
            print(f"\n  {'─'*30}")
            print(f"  ❓ {q.question[:90]}")
            exploration = self._explore_question(q)
            insight = self._generate_insight(q, exploration)
            stored = self._store_insight(insight)
            results.append(insight)

            action = q.explore_action
            if action == "add_crawler_task":
                added = self._add_crawler_tasks(q)
                print(f"  🎯 爬虫任务{'已添加' if added else '已存在'}")
            elif action == "global_research":
                print(f"  🌐 研究任务已调度")

        self._log_thinking_cycle(results)
        return results

    def _run_full_cycle(self, depth: int) -> List[Dict]:
        """完整思考循环：所有问题类型一起探索（原默认逻辑）"""
        self._generate_questions()
        if not self.questions:
            print("💤 当前没有特别的好奇心触发")
            return []

        print(f"❓ 生成了 {len(self.questions)} 个好奇心问题")
        return self._explore_and_store(self.questions[:depth])

    # ---- 核心循环 ----

    def run_thinking_cycle(self, depth: int = 3,
                            skill: Optional[str] = None) -> List[Dict]:
        """
        执行一轮思考循环

        Args:
            depth: 探索问题数量
            skill: 指定思考技能（None=full_cycle, 或技能名称）
        """
        print(f"\n{'='*60}")
        print(f"🧠 自我思考循环启动 [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"{'='*60}")

        # 所有路径都需要先扫描
        if skill and skill in self._skills:
            self._scan_project()
            self._study_knowledge()
            return self.run_skill(skill, depth)

        # 默认路径：学习 → 生成问题(好奇心+学习反馈) → 探索
        self._scan_project()
        learned = self._study_knowledge()

        # 好奇心引擎生成问题（基于扫描数据）
        self._generate_questions()

        # 学习触发的行动和问题（优先级高于好奇心引擎的问题）
        action_questions = []
        study_questions = []
        if learned:
            action_questions = self._apply_study_actions(learned)
            study_questions = self._generate_questions_from_study(learned)
            self.questions = action_questions + study_questions + self.questions
            if action_questions or study_questions:
                print(f"  💡 学习触发了 {len(action_questions) + len(study_questions)} 个新问题")

        # 始终记录学习行动（即使 0 个行动）
        self._log_study_actions(learned,
                                action_questions + study_questions)

        if not self.questions:
            print("💤 当前没有特别的好奇心触发")
            return []

        print(f"❓ 共 {len(self.questions)} 个好奇心问题")
        return self._explore_and_store(self.questions[:depth])

    def _scan_project(self):
        """扫描项目当前状态"""
        self.snapshot = self.scanner.get_full_snapshot()
        self.diff = self.scanner.diff_from_previous(self.snapshot)
        self.scanner.save_snapshot(self.snapshot)

    def _study_knowledge(self) -> List[Dict]:
        """
        在思考之前先"学习"知识库中的新资料
        三级优先级：P0=项目自身, P1=系统相关概念, P2=其他按重要性
        P0 条目每 5 周期重新学习一次，避免学完就忘
        返回本轮学习的条目列表（可用于后续行动触发）
        """
        study_tracker = self.data_dir / "study_tracker.json"
        studied_topics = set()
        if study_tracker.exists():
            try:
                studied_topics = set(json.loads(study_tracker.read_text(encoding="utf-8")))
            except Exception:
                studied_topics = set()

        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            all_k = kb.get_all_knowledge()

            # 找没学过的
            unstudied = [k for k in all_k if k.get("topic", "") not in studied_topics]

            # 所有已学过的 P0 条目，每 5 周期重新学一次
            # 用 counter 文件追踪周期数
            cycle_counter = self.data_dir / "cycle_counter.json"
            counter_data = {"cycle": 0}
            if cycle_counter.exists():
                try:
                    counter_data = json.loads(cycle_counter.read_text(encoding="utf-8"))
                except Exception:
                    pass
            counter_data["cycle"] = counter_data.get("cycle", 0) + 1
            cycle_counter.write_text(json.dumps(counter_data))

            restudy = []
            if counter_data["cycle"] % 5 == 0:
                for k in all_k:
                    if k.get("category") == "项目自身" and k.get("topic", "") in studied_topics:
                        restudy.append(k)

            # 三级优先级排序
            project_keywords = ["self", "thinking", "cognition", "modification", "scanner", "curiosity"]

            def priority(entry):
                cat = entry.get("category", "")
                topic = entry.get("topic", "")
                imp = entry.get("importance", 0.5)
                if cat == "项目自身":
                    return (0, -imp)  # P0: 项目自身知识优先
                if any(kw in cat.lower() for kw in project_keywords) or \
                   any(kw in topic.lower() for kw in project_keywords):
                    return (1, -imp)  # P1: 系统相关概念
                return (2, -imp)  # P2: 其他

            unstudied.sort(key=priority)

            # 优先未学过的，不足时补充重新学习的 P0
            batch = unstudied[:5]
            if len(batch) < 5 and restudy:
                batch.extend(restudy[:5 - len(batch)])
            if not batch:
                return []

            # 构建学习条目
            learned = []
            for entry in batch:
                studied_topics.add(entry.get("topic", ""))
                learned.append({
                    "topic": entry.get("topic", ""),
                    "source": entry.get("source", ""),
                    "importance": entry.get("importance", 0),
                    "category": entry.get("category", ""),
                    "content": entry.get("content", ""),
                    "key_concepts": entry.get("keywords", [])[:5],
                    "summary": (entry.get("content", "") or "")[:100],
                })

            # 保存学习追踪
            study_tracker.write_text(json.dumps(list(studied_topics), ensure_ascii=False), encoding="utf-8")

            # 记录学习日志
            study_log = self.data_dir / "study_log.json"
            study_entries = []
            if study_log.exists():
                try:
                    study_entries = json.loads(study_log.read_text(encoding="utf-8"))
                except Exception:
                    pass
            study_entries.append({
                "time": datetime.now().isoformat(),
                "batch_size": len(learned),
                "total_studied": len(studied_topics),
                "total_kb": len(all_k),
                "entries": [{
                    "topic": l["topic"],
                    "source": l["source"],
                    "importance": l["importance"],
                    "category": l["category"],
                    "key_concepts": l["key_concepts"],
                    "summary": l["summary"],
                } for l in learned],
            })
            study_log.write_text(json.dumps(study_entries, ensure_ascii=False, indent=2), encoding="utf-8")

            # 打印学习摘要
            print(f"\n  {'─'*40}")
            print(f"  📖 学习新知识 ({len(learned)}/{len(all_k)}):")
            for l in learned:
                tag = "🔬" if "[深度]" in l["topic"] else "📄"
                pri = "⭐ " if l.get("category") == "项目自身" else ""
                concepts = ", ".join(l["key_concepts"][:3])
                print(f"  {tag}{pri}{l['topic'][:60]}")
                if concepts:
                    print(f"     概念: {concepts}")
            print(f"  {'─'*40}")

            return learned

        except Exception as e:
            print(f"  ⚠️ 学习阶段异常: {e}")
            return []

    def _apply_study_actions(self, learned: List[Dict]) -> List:
        """
        对学习的内容生成行动：扫描实际代码找问题，触发修复或探索
        返回好奇心问题列表
        """
        from curiosity_engine import CuriosityQuestion
        questions = []
        import ast

        # 扫描实际项目代码找常见问题
        code_issues = {"bare_excepts": [], "no_docstrings": [], "long_functions": []}
        for py_file in Path.cwd().glob("*.py"):
            try:
                code = py_file.read_text(encoding="utf-8")
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        for handler in node.handlers:
                            if handler.type is None:
                                code_issues["bare_excepts"].append(py_file.name)
                    if isinstance(node, ast.FunctionDef):
                        if not ast.get_docstring(node):
                            if len(node.body) > 5:
                                code_issues["no_docstrings"].append(
                                    f"{py_file.name}:{node.name}"
                                )
            except Exception:
                continue

        # 将发现的代码问题转为好奇行动
        if code_issues["bare_excepts"]:
            unique_files = sorted(set(code_issues["bare_excepts"]))[:3]
            questions.append(CuriosityQuestion(
                observation=f"发现 {len(code_issues['bare_excepts'])} 处裸 except",
                question=f"有文件用了裸 except: {', '.join(unique_files)}，要不要修复？",
                importance=0.9,
                explore_action="self_heal",
                target=",".join(unique_files),
                context={"source": "code_scan", "type": "bare_except"}
            ))

        if code_issues["no_docstrings"]:
            files_with_issues = sorted(set(f.split(":")[0] for f in code_issues["no_docstrings"]))[:3]
            questions.append(CuriosityQuestion(
                observation=f"发现 {len(code_issues['no_docstrings'])} 个函数缺少文档",
                question=f"函数缺少文档: {', '.join(code_issues['no_docstrings'][:3])}，要补充吗？",
                importance=0.7,
                explore_action="self_heal",
                target=",".join(files_with_issues),
                context={
                    "source": "code_scan",
                    "type": "missing_doc",
                    "functions": code_issues["no_docstrings"][:5]
                }
            ))

        # 每轮至少生成一个探索问题（基于学习内容）
        if not questions and learned:
            entries_with_content = [l for l in learned if l.get("content")]
            if entries_with_content:
                entry = entries_with_content[0]
                questions.append(CuriosityQuestion(
                    observation=f"学习了新内容: {entry['topic'][:60]}",
                    question=f"刚学了 '{entry['topic'][:60]}'，对项目代码有启发吗？",
                    importance=entry.get("importance", 0.5),
                    explore_action="read_file",
                    target=self._find_target_file(entry["topic"]),
                    context={"source": "study_action", "topic": entry["topic"]}
                ))

        return questions

    def _generate_questions_from_study(self, learned: List[Dict]) -> List:
        """
        从学习的内容生成新的好奇心问题，让学到的知识驱动进一步探索
        """
        from curiosity_engine import CuriosityQuestion
        questions = []

        for entry in learned:
            topic = entry.get("topic", "")
            content = entry.get("content", "")
            importance = entry.get("importance", 0.5)
            key_concepts = entry.get("key_concepts", [])[:3]
            category = entry.get("category", "")

            # 1. 学到项目自身相关内容 → 代码质量/改进问题
            if category == "项目自身":
                questions.append(CuriosityQuestion(
                    observation=f"学习了项目自身知识: {topic[:60]}",
                    question=f"学习了 '{topic[:60]}'，检查这部分代码还有优化空间吗？",
                    importance=round(importance, 2),
                    explore_action="read_file",
                    target=self._find_target_file(topic),
                    context={"source": "study_question", "category": category}
                ))

            # 2. 学到新技术概念且重要性较高 → 深入搜索
            elif key_concepts and importance >= 0.6:
                domain = key_concepts[0]
                questions.append(CuriosityQuestion(
                    observation=f"学到新概念: {topic[:50]}",
                    question=f"'{topic[:60]}' 评分 {importance}，搜索更多关于 {domain} 的资料？",
                    importance=round(importance, 2),
                    explore_action="add_crawler_task",
                    target=topic[:60],
                    context={
                        "domain": domain,
                        "missing": [topic[:60]],
                        "source": "study_question",
                    }
                ))

            # 3. 条目内容较长/较重要 → 全球研究
            if len(content) > 300 and importance >= 0.7:
                questions.append(CuriosityQuestion(
                    observation=f"发现高质量知识: {topic[:50]}",
                    question=f"'{topic[:60]}' 内容质量很高，做全球深度研究？",
                    importance=round(importance + 0.1, 2),
                    explore_action="global_research",
                    target=topic[:60],
                    context={
                        "research_queries": [topic[:80], f"{topic[:60]} tutorial", f"{topic[:60]} best practices"],
                        "source": "study_question",
                    }
                ))

        return questions

    def _find_target_file(self, topic: str) -> str:
        """从学习 topic 推断对应的项目文件"""
        for py_file in Path.cwd().glob("*.py"):
            if py_file.stem in topic:
                return str(py_file)
        return topic

    def _log_study_actions(self, learned: List[Dict], questions: List):
        """记录学习触发的行动到 thinking_log"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "study_actions",
            "learned_count": len(learned),
            "actions_generated": len(questions),
            "actions": [
                {"observation": q.observation[:100], "action": q.explore_action, "target": q.target}
                for q in questions
            ] if questions else [],
            "learned_topics": [l["topic"][:60] for l in learned] if learned else [],
        }
        self.data_dir.mkdir(exist_ok=True)
        log_file = self.data_dir / "self_thinking_log.json"
        try:
            existing = []
            if log_file.exists():
                with open(log_file, encoding="utf-8") as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _generate_questions(self):
        """从扫描数据生成好奇心问题，跳过已发现的知识缺口"""
        # 加载缺口追踪器
        gap_tracker = self.data_dir / "gap_tracker.json"
        known_gaps = set()
        if gap_tracker.exists():
            try:
                data = json.loads(gap_tracker.read_text(encoding="utf-8"))
                known_gaps = set(data.get("gaps", []))
            except Exception:
                pass

        all_questions = self.curiosity.generate_questions(self.snapshot, self.diff)

        # 过滤已发现的缺口
        filtered = []
        for q in all_questions:
            if q.explore_action == "add_crawler_task":
                gap_key = q.target
                if gap_key in known_gaps:
                    continue
                known_gaps.add(gap_key)
            filtered.append(q)

        self.questions = filtered

        # 保存缺口追踪
        gap_tracker.write_text(json.dumps({
            "gaps": list(known_gaps),
            "updated": datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2))

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
        elif action == "global_research":
            return self._explore_global_research(q)
        elif action == "self_heal":
            return self._explore_self_heal(q)
        elif action == "code_quality_heal":
            return self._explore_self_heal(q)
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

    def _explore_global_research(self, q) -> Dict[str, Any]:
        """全球研究：调爬虫和持续学习系统搜索全球资料"""
        ctx = q.context
        queries = ctx.get("research_queries", [])
        results = []

        print(f"   🌐 全球研究: 发起 {len(queries)} 个搜索查询")

        # 1. 添加爬虫任务到队列
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

        # 2. 同时尝试直接调爬虫实时获取
        try:
            from ai_knowledge_crawler import AIKnowledgeCrawler
            crawler = AIKnowledgeCrawler()
            # 用前3个查询搜索GitHub（最重要的）
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

        # 3. 尝试arXiv搜索
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

    # ---- 自我修复探索 ----

    def _explore_self_heal(self, q) -> Dict[str, Any]:
        """探索并尝试修复代码问题"""
        from self_modification_engine import SelfModificationEngine
        engine = SelfModificationEngine()

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
        elif q.explore_action == "global_research":
            return self._insight_from_global_research(q, exploration)
        elif q.explore_action in ("self_heal", "code_quality_heal"):
            return self._insight_from_self_heal(q, exploration)
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

    def _insight_from_global_research(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从全球研究生成洞察"""
        topic = exploration.get("research_topic", "global")
        results = exploration.get("sample_results", [])
        tasks = exploration.get("crawler_tasks_added", 0)
        realtime = exploration.get("real_time_results", 0)

        # 从实时结果提炼要点
        top_results = ""
        for r in results[:3]:
            top_results += f"- [{r['source']}] {r['title']} ({r.get('stars', 0)}⭐) {r.get('description', '')[:80]}\n"

        summary = f"全球研究 [{topic}]: 已调度 {tasks} 个爬虫任务"
        if results:
            summary += f"，实时获取 {len(results)} 条结果\n{top_results[:200]}"

        content = (
            f"好奇心驱动全球研究: {q.question}\n\n"
            f"搜索查询:\n"
            + "\n".join(f"- {qq}" for qq in q.context.get("research_queries", []))
            + f"\n\n实时结果:\n{top_results}"
            + f"\n爬虫将持续在后台上获取更多资料。"
        )

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"全球研究: {topic}",
            "category": "项目自身",
            "content": content,
            "keywords": [topic, "全球研究", "架构探索"],
            "findings": [f"调度了 {tasks} 个爬虫任务", f"实时获取 {realtime} 条结果"],
            "origin": "self_thinking",
            "action_taken": "global_research",
        }

    def _insight_from_self_heal(self, q, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """从自我修复探索生成洞察"""
        target = exploration.get("target", q.target)
        attempted = exploration.get("fixes_attempted", 0)
        succeeded = exploration.get("fixes_succeeded", 0)
        fix_results = exploration.get("fix_results", [])

        detail_lines = []
        for fix in fix_results:
            status = "✅" if fix["success"] else "❌"
            detail_lines.append(f"  {status} [{fix['type']}] {fix['file']}: {fix['detail']}")

        summary = f"自我修复 [{target}]: 尝试 {attempted} 项修复，成功 {succeeded} 项\n" + "\n".join(detail_lines)

        return {
            "observation": q.observation,
            "question": q.question,
            "summary": summary,
            "topic": f"{Path(target).stem} 自我修复",
            "category": "项目自身",
            "content": f"好奇心引擎发现代码问题并自动修复:\n\n问题: {q.question}\n观察: {q.observation}\n\n修复结果:\n" + "\n".join(detail_lines),
            "keywords": [Path(target).stem, "自我修复", "代码质量"],
            "findings": [f"修复 {succeeded}/{attempted} 项" if attempted > 0 else "无需修复"],
            "origin": "self_thinking",
            "action_taken": "self_heal",
            "modification_proposal": {
                "file": target,
                "fixes": fix_results,
                "auto_applied": succeeded > 0,
            },
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
