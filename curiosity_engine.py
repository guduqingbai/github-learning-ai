#!/usr/bin/env python3
"""
❓ 好奇心引擎 — 从 Scanner 数据生成真实好奇心信号
每个问题都基于可观察的项目事实，没有任何随机值
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class CuriosityQuestion:
    """一个由真实观察产生的好奇心问题"""
    observation: str          # 观察到的现象
    question: str             # 由此产生的问题
    importance: float         # 0.0-1.0 重要性
    explore_action: str       # 探索方式
    target: str               # 目标文件/模块
    context: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""          # 为什么生成这个问题


class CuriosityEngine:
    """从 Scanner 快照生成好奇心信号"""

    def __init__(self):
        self._recent_observations: set = set()
        from knowledge_base import KnowledgeBase
        self.kb = KnowledgeBase()

    def generate_questions(self, snapshot: Dict[str, Any],
                           diff: Optional[Dict[str, Any]] = None) -> List[CuriosityQuestion]:
        """运行所有好奇心触发器，按重要性排序（完整模式）"""
        questions: List[CuriosityQuestion] = []

        questions.extend(self._curiosity_new_files(snapshot, diff))
        questions.extend(self._curiosity_module_size(snapshot))
        questions.extend(self._curiosity_self_knowledge_gap(snapshot))
        questions.extend(self._curiosity_code_quality(snapshot))
        questions.extend(self._curiosity_kb_gaps(snapshot))
        questions.extend(self._curiosity_similar_modules(snapshot))
        questions.extend(self._curiosity_kb_growth(snapshot, diff))
        questions.extend(self._curiosity_import_anomalies(snapshot))
        questions.extend(self._curiosity_empty_modules(snapshot))
        questions.extend(self._curiosity_global_research(snapshot))
        questions.extend(self._curiosity_deep_learning(snapshot))

        # 去重：同样的问题不重复生成
        seen = set()
        unique = []
        for q in questions:
            key = q.question[:60]
            if key not in seen:
                seen.add(key)
                unique.append(q)

        unique.sort(key=lambda x: -x.importance)
        return unique

    def generate_metadata(self, snapshot: Dict[str, Any],
                           diff: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """仅生成问题元数据（轻量模式），节省上下文"""
        full = self.generate_questions(snapshot, diff)
        return [
            {
                "id": i,
                "question": q.question[:120],
                "importance": q.importance,
                "action": q.explore_action,
                "target": q.target,
            }
            for i, q in enumerate(full)
        ]

    def get_question_detail(self, question_id: int, snapshot: Dict[str, Any],
                             diff: Optional[Dict[str, Any]] = None) -> Optional[CuriosityQuestion]:
        """按 ID 加载单个问题的完整详情（懒加载）"""
        full = self.generate_questions(snapshot, diff)
        if 0 <= question_id < len(full):
            return full[question_id]
        return None

    def _has_self_kb_entry(self, module_name: str) -> bool:
        """检查某个模块是否有项目自身知识条目"""
        all_k = self.kb.get_all_knowledge()
        for item in all_k:
            if item.get("category") == "项目自身":
                name = item.get("topic", "")
                if module_name.replace(".py", "") in name:
                    return True
        return False

    # ---- 好奇心触发器 ----

    def _curiosity_new_files(self, snapshot: Dict[str, Any],
                              diff: Optional[Dict[str, Any]]) -> List[CuriosityQuestion]:
        """新文件出现 → 好奇"""
        qs = []
        if diff and not diff.get("new_snapshot", True):
            for change in diff.get("changes", []):
                if change.startswith("新增文件:"):
                    name = change.replace("新增文件: ", "").strip()
                    qs.append(CuriosityQuestion(
                        observation=f"检测到新文件 {name}",
                        question=f"新文件 {name} 的作用是什么？它是怎么被创建出来的？",
                        importance=0.8,
                        explore_action="read_file",
                        target=name,
                        context={"file": name, "reason": "new_file"}
                    ))
        return qs

    def _curiosity_module_size(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """模块超过200行但无自知识条目 → 好奇"""
        qs = []
        for f in snapshot.get("py_files", []):
            if f["lines"] > 200 and not self._has_self_kb_entry(f["file"]):
                qs.append(CuriosityQuestion(
                    observation=f"{f['file']} 有 {f['lines']} 行但没有项目自身知识条目",
                    question=f"{f['file']} 有 {f['lines']} 行，{len(f['classes'])} 个类，{len(f['functions'])} 个函数——这个模块是做什么的？",
                    importance=0.7,
                    explore_action="read_file",
                    target=f["file"],
                    context={"file": f["file"], "lines": f["lines"],
                             "classes": f["classes"], "functions": f["functions"]}
                ))
        return qs

    def _curiosity_self_knowledge_gap(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """自知识别条目数远少于模块数 → 好奇"""
        py_files = snapshot.get("py_files", [])
        kb_data = snapshot.get("knowledge_base", {})
        cat_breakdown = kb_data.get("category_breakdown", {})
        self_entries = cat_breakdown.get("项目自身", 0)
        total_modules = len(py_files)

        if self_entries < total_modules * 0.5 and total_modules > 0:
            qs = [CuriosityQuestion(
                observation=f"项目有 {total_modules} 个模块但'项目自身'分类只有 {self_entries} 条知识",
                question=f"还有 {total_modules - self_entries} 个模块没有自知识条目，它们各自是什么？",
                importance=0.7,
                explore_action="list_new_entries",
                target="project_self",
                context={"total_modules": total_modules, "self_entries": self_entries}
            )]
            # 找出具体哪些模块没有条目
            undocumented = []
            for f in py_files:
                if f["lines"] > 0 and not self._has_self_kb_entry(f["file"]):
                    undocumented.append(f["file"])
            if undocumented:
                qs[0].context["undocumented"] = undocumented[:10]
                qs[0].observation += f"，例如 {', '.join(undocumented[:5])}"
            return qs
        return []

    def _curiosity_code_quality(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """SelfLearningSystem 发现代码问题 → 好奇"""
        sl = snapshot.get("self_learning", {})
        vulns = sl.get("vulnerabilities", 0)
        quality = sl.get("code_quality_issues", 0)
        total_issues = (vulns if isinstance(vulns, (int, float)) else 0) + \
                       (quality if isinstance(quality, (int, float)) else 0)

        if total_issues > 0:
            return [CuriosityQuestion(
                observation=f"代码分析发现 {total_issues} 个问题（漏洞:{vulns}, 质量:{quality}）",
                question=f"这些代码问题是什么原因导致的？哪些模块的问题最多？",
                importance=min(0.9, 0.5 + total_issues * 0.05),
                explore_action="check_state",
                target="code_quality",
                context={"vulnerabilities": vulns, "code_quality_issues": quality}
            )]
        return []

    def _curiosity_kb_gaps(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """知识缺口 → 好奇"""
        qs = []
        for gap in snapshot.get("knowledge_gaps", []):
            ratio = gap["count"] / max(1, gap["total"])
            importance = 0.5 + ratio * 0.3
            if ratio > 0.5:
                qs.append(CuriosityQuestion(
                    observation=f"领域 '{gap['domain']}' 缺 {gap['count']}/{gap['total']} 个子话题",
                    question=f"{gap['domain']} 领域知识缺口很大（{gap['count']}个未学），要不要让爬虫去查？",
                    importance=round(importance, 2),
                    explore_action="add_crawler_task",
                    target=gap["domain"],
                    context={"domain": gap["domain"], "missing": gap["missing"]}
                ))
        return qs

    def _curiosity_similar_modules(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """import 相似度高的模块 → 好奇是否重复"""
        qs = []
        files = [f for f in snapshot.get("py_files", []) if f["import_count"] > 0]
        for i, a in enumerate(files):
            for b in files[i + 1:]:
                set_a = set(a["imports"])
                set_b = set(b["imports"])
                if len(set_a) > 0 and len(set_b) > 0:
                    jaccard = len(set_a & set_b) / len(set_a | set_b)
                    if jaccard > 0.5:
                        qs.append(CuriosityQuestion(
                            observation=f"{a['file']} 和 {b['file']} 的 import 相似度 {jaccard:.0%}",
                            question=f"{a['file']} 和 {b['file']} 功能是否重复？imports 重叠度 {jaccard:.0%}",
                            importance=0.5,
                            explore_action="compare_files",
                            target=f"{a['file']},{b['file']}",
                            context={"file_a": a["file"], "file_b": b["file"],
                                     "similarity": round(jaccard, 2)}
                        ))
        return qs

    def _curiosity_kb_growth(self, snapshot: Dict[str, Any],
                              diff: Optional[Dict[str, Any]]) -> List[CuriosityQuestion]:
        """知识库增长 → 好奇"""
        if diff and not diff.get("new_snapshot", True):
            kb_changes = [c for c in diff.get("changes", []) if c.startswith("知识库变化")]
            if kb_changes:
                return [CuriosityQuestion(
                    observation=kb_changes[0],
                    question="新增了哪些知识？它们和已有知识有什么关联？",
                    importance=0.5,
                    explore_action="list_new_entries",
                    target="knowledge_base",
                    context={"change_desc": kb_changes[0]}
                )]
        return []

    def _curiosity_import_anomalies(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """import 数量异常的模块 → 好奇"""
        qs = []
        for f in snapshot.get("py_files", []):
            if f["import_count"] > 15:
                qs.append(CuriosityQuestion(
                    observation=f"{f['file']} 导入了 {f['import_count']} 个模块",
                    question=f"{f['file']} 为什么需要 {f['import_count']} 个 import？依赖是否过多？",
                    importance=0.55,
                    explore_action="read_file",
                    target=f["file"],
                    context={"file": f["file"], "import_count": f["import_count"],
                             "imports": f["imports"]}
                ))
        return qs

    def _curiosity_empty_modules(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """docstring 覆盖率极低的模块 → 好奇"""
        qs = []
        for f in snapshot.get("py_files", []):
            if f["docstring_ratio"] < 0.1 and f["functions"] and f["lines"] > 50:
                qs.append(CuriosityQuestion(
                    observation=f"{f['file']} 的 docstring 覆盖率仅 {f['docstring_ratio']:.0%}",
                    question=f"{f['file']} 有 {len(f['functions'])} 个函数但几乎没文档，为什么？",
                    importance=0.4,
                    explore_action="read_file",
                    target=f["file"],
                    context={"file": f["file"], "docstring_ratio": f["docstring_ratio"],
                             "function_count": len(f["functions"])}
                ))
        return qs

    def _curiosity_deep_learning(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """检查知识库中深度不足但值得深挖的条目"""
        qs = []
        try:
            all_k = self.kb.get_all_knowledge()
            for entry in all_k:
                depth = entry.get("learning_depth", 0)
                importance = entry.get("importance", 0)
                score = entry.get("content_score", importance)
                topic = entry.get("topic", "")

                # 条件：深度不足(0或无标记) 但 内容质量不错 且 有学习价值
                if depth is None:
                    depth = 0
                if depth < 2 and score >= 0.5 and len(topic) > 3:
                    qs.append(CuriosityQuestion(
                        observation=f"知识 '{topic[:50]}' 质量评分 {score} 但学习深度仅 {depth}",
                        question=f"'{topic[:50]}' 资料不错（评分{score}），要不要深入挖掘更多相关内容？",
                        importance=round(0.5 + score * 0.3, 2),
                        explore_action="deep_learning",
                        target=topic[:60],
                        context={
                            "topic": topic,
                            "current_depth": depth,
                            "score": score,
                        }
                    ))
        except Exception:
            pass

        # 只保留最重要的2条，避免问题太多
        qs.sort(key=lambda x: -x.importance)
        return qs[:2]

    def _curiosity_global_research(self, snapshot: Dict[str, Any]) -> List[CuriosityQuestion]:
        """项目核心架构本身 → 搜全球资料学习更好方案"""
        qs = []

        # 检查是否有"自我思考AI架构"相关知识
        all_k = self.kb.get_all_knowledge()
        has_self_thinking_kb = any(
            "自我思考" in item.get("topic", "") or "自主Agent" in item.get("topic", "")
            for item in all_k
        )

        if not has_self_thinking_kb:
            qs.append(CuriosityQuestion(
                observation="知识库中没有'自我思考AI架构'或'自主Agent系统'相关条目",
                question="全球最好的自我思考AI架构是怎么设计的？其他项目如何实现自主Agent？",
                importance=0.85,
                explore_action="global_research",
                target="self_thinking_architecture",
                context={
                    "research_queries": [
                        "self thinking AI architecture",
                        "autonomous agent system design",
                        "cognitive architecture patterns",
                        "metacognition AI implementation",
                        "curiosity driven exploration system",
                    ]
                }
            ))

        # 检查当前项目架构的知识覆盖
        py_files = snapshot.get("py_files", [])
        total_modules = len(py_files)
        cat_breakdown = snapshot.get("knowledge_base", {}).get("category_breakdown", {})
        self_entries = cat_breakdown.get("项目自身", 0)

        if self_entries < total_modules:
            # 有模块还没分析，但更重要的是：当前的架构设计是否最优？
            qs.append(CuriosityQuestion(
                observation=f"项目有 {total_modules} 个模块，仅 {self_entries} 条自知识，架构仍有优化空间",
                question="当前的多层架构（认知层→学习层→数据层→采集层）是否最优？业界有没有更好的分层方案？",
                importance=0.8,
                explore_action="global_research",
                target="architecture_comparison",
                context={
                    "research_queries": [
                        "AI learning system layered architecture",
                        "self-improving system design patterns",
                        "cognitive architecture best practices",
                    ]
                }
            ))

        return qs


if __name__ == "__main__":
    from self_scanner import SelfScanner
    scanner = SelfScanner()
    snap = scanner.get_full_snapshot()
    engine = CuriosityEngine()
    questions = engine.generate_questions(snap)
    print(f"❓ 好奇心引擎生成了 {len(questions)} 个问题:\n")
    for q in questions[:10]:
        print(f"  [{q.importance:.2f}] {q.question}")
        print(f"       观察: {q.observation}")
        print(f"       动作: {q.explore_action} → {q.target}")
        print()
