#!/usr/bin/env python3
"""
Research Integration — 研究系统的思考循环集成

通过 Hook 系统把多源研究和现有思考循环对接：
- POST_QUESTIONS: 拦截 global_research 问题，执行即时搜索
- POST_SCAN: 发现知识贫瘠领域，发起研究
- CYCLE_END: 分析研究缺口，生成跟进问题
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# ── 只有在实际使用时才导入（延迟导入避免循环依赖） ──


class ResearchIntegration:
    """
    研究集成器：连接 Web Researcher 和思考循环。

    不直接依赖 self_thinking_agent，通过 Hook 系统交互。
    """

    def __init__(self):
        self._searcher = None
        self._synthesizer = None
        self._planner = None
        self._recursive = None
        self._kb = None

        # 已执行过的研究查询缓存（避免重复）
        self._executed_queries: set = set()
        self._recent_reports: List[Dict] = []  # 最近的研究报告
        self._initial_research_triggered = False  # 是否已触发过初始研究

    def _lazy_init(self):
        """延迟初始化所有子模块"""
        if self._searcher is None:
            from web_researcher import MultiSourceSearcher, AnswerSynthesizer
            self._searcher = MultiSourceSearcher()
            self._synthesizer = AnswerSynthesizer()
        if self._planner is None:
            from research_planner import ResearchPlanner, RecursiveResearcher
            self._planner = ResearchPlanner()
            self._recursive = RecursiveResearcher()

    def register_hooks(self, agent) -> None:
        """注册到 SelfThinkingAgent 的 Hook 系统"""
        self._lazy_init()

        agent.register_hook("post_questions", self._on_post_questions,
                            name="research_on_questions", priority=5)
        agent.register_hook("post_scan", self._on_post_scan,
                            name="research_on_scan", priority=10)
        agent.register_hook("cycle_end", self._on_cycle_end,
                            name="research_on_cycle_end", priority=5)

        print("  🔬 研究集成已注册 (POST_QUESTIONS/POST_SCAN/CYCLE_END)")

    def _on_post_questions(self, agent, **kw) -> None:
        """
        在好奇心问题生成后触发。

        对 global_research 类型的问题，执行即时多源搜索，
        而不是排入爬虫队列等待。
        """
        questions = getattr(agent, 'questions', [])
        if not questions:
            return

        new_questions = []
        for q in questions:
            action = getattr(q, 'explore_action', '') or getattr(q, 'explore_action', '')
            target = getattr(q, 'target', '') or getattr(q, 'question', '')

            if action == "global_research" and target:
                # 检查是否已执行过
                cache_key = f"global:{target[:80]}"
                if cache_key not in self._executed_queries:
                    # 转化为 web_research 类型
                    if hasattr(q, 'explore_action'):
                        q.explore_action = "web_research"
                    self._executed_queries.add(cache_key)
                    new_questions.append(q)

        if new_questions:
            print(f"  🔄 升级 {len(new_questions)} 个 global_research → web_research")

    def _on_post_scan(self, agent, **kw) -> None:
        """
        在扫描完成后触发。

        检查知识库各分类条目数，若某分类 < 3 条且该分类有价值，
        自动发起基础研究。首次运行时触发一轮架构研究。
        """
        # ── 检查知识贫瘠分类 ──
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            breakdown = kb.get_category_breakdown()

            thin_categories = [
                (cat, count) for cat, count in breakdown.items()
                if count < 3 and cat not in ("网络研究", "未分类")
            ]

            for cat, count in thin_categories[:2]:
                query = f"{cat} 基础知识"
                cache_key = f"scan:{query[:60]}"
                if cache_key in self._executed_queries:
                    continue

                print(f"  📚 发现「{cat}」仅 {count} 条，自动发起研究")
                self._executed_queries.add(cache_key)

                try:
                    from curiosity_engine import CuriosityQuestion
                    new_q = CuriosityQuestion(
                        observation=f"知识分类「{cat}」仅有 {count} 条，需要补充基础信息",
                        question=f"研究「{cat}」的基础概念",
                        importance=0.6,
                        explore_action="web_research",
                        target=cat,
                        context={"auto_triggered": True},
                        reason=f"知识缺口: {cat} 领域知识不足",
                    )
                    if hasattr(agent, 'questions'):
                        agent.questions.append(new_q)
                        print(f"    → 已添加研究问题: {cat}")
                except Exception:
                    pass
        except Exception:
            pass

        # ── 初始研究触发器 ──
        self._trigger_initial_research(agent)

    def _trigger_initial_research(self, agent) -> None:
        """首次运行时发起一轮架构级联网研究"""
        if self._initial_research_triggered:
            return
        has_real_research = any(
            q.startswith("global:") or q.startswith("scan:")
            for q in self._executed_queries
        )
        if has_real_research or len(self._recent_reports) > 0:
            return
        self._initial_research_triggered = True
        print("  🌐 首次运行，自动发起架构级研究")
        try:
            from curiosity_engine import CuriosityQuestion
            init_q = CuriosityQuestion(
                observation="系统首次运行，尚未进行任何联网研究",
                question="研究自主思考AI系统的核心架构模式和最佳实践",
                importance=0.9,
                explore_action="web_research",
                target="autonomous thinking AI architecture best practices 2026",
                context={"initial_research": True, "depth": "comprehensive"},
                reason="初始研究：为系统建立基础知识",
            )
            if hasattr(agent, 'questions'):
                agent.questions.append(init_q)
                print(f"    → 已添加初始架构研究问题")
        except Exception:
            pass

    def _on_cycle_end(self, agent, **kw) -> None:
        """
        在思考循环结束后触发。

        检查已完成的研究报告，识别缺口，
        生成跟进问题到下一轮。
        """
        if not self._recent_reports:
            return

        for report in self._recent_reports:
            if report.get("status") != "completed":
                continue

            gaps = report.get("gaps", [])
            follow_ups = report.get("follow_up_queries", [])

            if gaps and follow_ups and self._recursive and self._recursive.should_deepen():
                self._recursive.deepen()
                print(f"  🔍 研究「{report.get('goal', '?')}」有 {len(gaps)} 个缺口")
                print(f"    跟进: {follow_ups[0][:80]}")

                # 添加跟进问题到 agent
                try:
                    from curiosity_engine import CuriosityQuestion
                    for fq in follow_ups[:2]:
                        cache_key = f"followup:{fq[:60]}"
                        if cache_key in self._executed_queries:
                            continue
                        self._executed_queries.add(cache_key)

                        new_q = CuriosityQuestion(
                            observation=f"研究缺口: {fq}",
                            question=f"进一步研究: {fq}",
                            importance=0.65,
                            explore_action="web_research",
                            target=fq,
                            context={"follow_up": True, "parent_goal": report.get("goal")},
                            reason="递归研究发现知识缺口",
                        )
                        if hasattr(agent, 'questions'):
                            agent.questions.append(new_q)
                except Exception:
                    pass

    def _cross_synthesize_findings(self, query: str, findings) -> Dict[str, Any]:
        """
        跨子查询综合：提取主题、生成洞察、统计来源性能。

        纯规则驱动（无 LLM），从 findings 中做频率分析、共现检测。
        """
        # 1. 收集所有 key_points 和 citations
        all_points: List[str] = []
        all_citations: List[Dict] = []
        source_counts: Dict[str, int] = {}

        for f in findings:
            all_points.extend(f.key_points)
            all_citations.extend(f.citations)

            for c in f.citations:
                if isinstance(c, dict):
                    src = c.get("source", "unknown")
                else:
                    src = getattr(c, "source", "unknown")
                source_counts[src] = source_counts.get(src, 0) + 1

        # 2. 简单主题检测：从 key_points 中提取高频词（长度 >= 2 的中文/英文词）
        word_freq: Dict[str, int] = {}
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                      "have", "has", "had", "do", "does", "did", "will", "would",
                      "could", "should", "may", "might", "can", "shall", "to", "of",
                      "in", "for", "on", "with", "at", "by", "from", "as", "into",
                      "through", "during", "before", "after", "above", "below",
                      "between", "out", "off", "over", "under", "again", "further",
                      "then", "once", "here", "there", "when", "where", "why",
                      "how", "all", "each", "every", "both", "few", "more", "most",
                      "other", "some", "such", "no", "nor", "not", "only", "own",
                      "same", "so", "than", "too", "very", "just", "because", "and",
                      "but", "or", "if", "while", "that", "this", "it", "its",
                      "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
                      "都", "一", "一个", "上", "也", "很", "到", "说", "要",
                      "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}

        for point in all_points:
            # 英文词
            for word in point.split():
                word_clean = word.strip(".,;:!?\"'()[]{}").lower()
                if len(word_clean) >= 3 and word_clean not in stop_words:
                    word_freq[word_clean] = word_freq.get(word_clean, 0) + 1
            # 中文二元组
            point_stripped = point.strip()
            for i in range(len(point_stripped) - 1):
                pair = point_stripped[i:i+2]
                if any('一' <= c <= '鿿' for c in pair):
                    word_freq[pair] = word_freq.get(pair, 0) + 1

        # 排序高频词作为主题
        sorted_words = sorted(word_freq.items(), key=lambda x: -x[1])
        themes = [w for w, c in sorted_words[:8] if c >= 2]

        # 3. 生成洞察：从 key_points 中找包含高频词的句子
        insights = []
        scored_points = []
        for pt in all_points:
            score = sum(1 for w in themes if w.lower() in pt.lower())
            if score > 0:
                scored_points.append((score, pt))

        scored_points.sort(key=lambda x: -x[0])
        seen_insights = set()
        for score, pt in scored_points[:5]:
            key = pt[:60]
            if key not in seen_insights:
                seen_insights.add(key)
                insights.append(pt)

        # 4. 生成综合摘要（如 findings 中有多条摘要则拼接）
        summaries = []
        for f in findings:
            if f.summary and len(f.summary) > 20:
                summaries.append(f.summary)

        if summaries:
            combined = "；".join(summaries[:3])
            summary_text = f"综合 {len(findings)} 个子查询结果：{combined}"
        else:
            summary_text = f"对「{query}」的研究完成，共 {len(findings)} 个子查询"

        # 5. 收集缺口和跟进
        all_gaps = []
        all_follow_ups = []
        for f in findings:
            all_gaps.extend(f.gaps)
        # 用 RecursiveResearcher 做正式缺口分析
        if self._recursive:
            from research_planner import ResearchReport
            temp_report = ResearchReport(
                goal=query, goal_type="concept", status="completed",
                findings=list(findings), created=datetime.now().isoformat(),
            )
            all_follow_ups = self._recursive.analyze_report(temp_report)
            all_gaps = temp_report.gaps

        return {
            "summary": summary_text,
            "insights": insights,
            "themes": themes,
            "gaps": all_gaps,
            "follow_ups": all_follow_ups,
            "source_performance": source_counts,
        }

    def execute_research(self, query: str, goal_type: str = "concept") -> Dict[str, Any]:
        """
        执行完整研究流程：规划 → 搜索 → 综合 → 识别缺口。

        Args:
            query: 研究查询
            goal_type: 目标类型

        Returns:
            研究结果 dict，包含 summary / citations / gaps 等
        """
        self._lazy_init()
        print(f"\n  🔬 执行研究: \"{query}\"")

        # 1. 如果查询较宽泛，先做计划
        from research_planner import ResearchReport
        report: ResearchReport = self._planner.plan_research(query)
        report.status = "in_progress"

        # 2. 逐一执行子查询
        all_results = []
        for sub_q in report.sub_queries:
            print(f"\n  📝 子查询: \"{sub_q}\"")
            results = self._searcher.search_all(sub_q)
            all_results.extend(results)

            # 综合
            answer = self._synthesizer.synthesize(sub_q, results)
            from research_planner import ResearchFinding
            finding = ResearchFinding(
                sub_query=sub_q,
                results_count=len(results),
                summary=answer.get("summary", "")[:200],
                key_points=answer.get("key_points", [])[:3],
                citations=answer.get("citations", []),
                gaps=[] if len(results) >= 2 else [f"{sub_q} 结果不足"],
            )

            report.findings.append(finding)

        # 3. 综合整体结果
        if all_results:
            overall = self._synthesizer.synthesize(query, all_results)
            report.overall_summary = overall.get("summary", "")
            report.completed = datetime.now().isoformat()
            report.status = "completed"

            # 4. 跨查询综合分析（提取主题、生成洞察）
            cross = self._cross_synthesize_findings(query, report.findings)
            report.overall_summary = cross["summary"]
            report.gaps = cross["gaps"]
            report.follow_up_queries = cross["follow_ups"]

            # 5. 存储到知识库（含综合洞察）
            kb_entry = self._synthesizer.make_kb_entry(query, overall)
            kb_entry["insights"] = cross.get("insights", [])
            kb_entry["gaps"] = cross.get("gaps", [])
            kb_entry["follow_up_queries"] = cross.get("follow_ups", [])
            kb_entry["themes"] = cross.get("themes", [])
            kb_entry["source_performance"] = cross.get("source_performance", {})
            success = self._store_to_kb(kb_entry)
            print(f"  💾 研究结果存储到知识库: {'成功' if success else '失败'}")

        # 6. 构造返回
        result = {
            "topic": f"研究: {query}",
            "summary": report.overall_summary or f"对「{query}」的研究完成",
            "insights": cross.get("insights", []) if all_results else [],
            "themes": cross.get("themes", []) if all_results else [],
            "key_points": [],
            "citations": [],
            "gaps": report.gaps,
            "follow_up_queries": report.follow_up_queries,
            "source_performance": cross.get("source_performance", {}) if all_results else {},
            "total_results": len(all_results),
            "sub_queries_count": len(report.sub_queries),
            "findings_count": len(report.findings),
            "action_taken": "web_research",
            "research_date": datetime.now().isoformat(),
        }

        # 收集 key_points 和 citations
        for f in report.findings:
            result["key_points"].extend(f.key_points)
            result["citations"].extend(f.citations)

        # 保存报告到缓存 + 写入研究日志
        self._recent_reports.append({
            "goal": query, "status": report.status,
            "gaps": report.gaps, "follow_up_queries": report.follow_up_queries,
            "findings_count": len(report.findings),
        })
        if len(self._recent_reports) > 20:
            self._recent_reports = self._recent_reports[-20:]

        # 7. 写入研究日志（实用价值：留下可读的记录）
        if all_results:
            self._write_research_journal(result)

        return result

    def _store_to_kb(self, kb_entry: Dict) -> bool:
        """存储知识条目到知识库"""
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            return kb.add_knowledge(kb_entry)
        except Exception:
            pass
        # 二次尝试：用 learn_from_experience 兜底
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            return kb.learn_from_experience(kb_entry)
        except Exception:
            return False

    def _write_research_journal(self, result: Dict[str, Any]):
        """将研究结果写入日志文件，留下可读的记录"""
        try:
            journal_dir = Path("data")
            journal_dir.mkdir(parents=True, exist_ok=True)
            journal_file = journal_dir / "research_journal.md"

            topic = result.get("topic", "未知主题")
            summary = result.get("summary", "")
            insights = result.get("insights", [])
            themes = result.get("themes", [])
            key_points = result.get("key_points", [])
            gaps = result.get("gaps", [])
            follow_ups = result.get("follow_up_queries", [])
            total = result.get("total_results", 0)
            sub_count = result.get("sub_queries_count", 0)
            src_perf = result.get("source_performance", {})
            date = result.get("research_date", datetime.now().isoformat())[:19]

            # 构建日志条目
            lines = [f"\n## {topic}", f"**时间**: {date}", f"**结果数**: {total} 条（{sub_count} 个子查询）"]

            if src_perf:
                src_str = " | ".join(f"{s}: {c}" for s, c in sorted(src_perf.items(), key=lambda x: -x[1]))
                lines.append(f"**来源**: {src_str}")

            if summary:
                lines.append(f"\n**摘要**: {summary[:500]}")

            if themes:
                lines.append(f"\n**主题词**: {'、'.join(themes)}")

            if insights:
                lines.append("\n**洞察**:")
                for ins in insights[:5]:
                    lines.append(f"- {ins[:150]}")

            if key_points:
                lines.append("\n**关键要点**:")
                for kp in key_points[:8]:
                    lines.append(f"- {kp[:150]}")

            if gaps:
                lines.append(f"\n**未填补缺口**: {len(gaps)}")
                for g in gaps[:3]:
                    lines.append(f"- {g[:100]}")

            if follow_ups:
                lines.append(f"\n**跟进问题**:")
                for fu in follow_ups[:3]:
                    lines.append(f"- {fu[:100]}")

            lines.append("---")

            # 追加写入
            with open(journal_file, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

            print(f"  📖 研究日志已写入: {journal_file}")
        except Exception:
            pass

    def get_research_stats(self) -> Dict[str, Any]:
        """研究统计"""
        return {
            "executed_queries": len(self._executed_queries),
            "recent_reports": len(self._recent_reports),
            "pending_follow_ups": sum(
                1 for r in self._recent_reports
                if r.get("follow_up_queries")
            ),
        }


if __name__ == "__main__":
    print("=" * 50)
    print("  Research Integration 测试")
    print("=" * 50)

    # 模拟 Agent
    class MockAgent:
        def __init__(self):
            self.questions = []
        def register_hook(self, event, handler, **kw):
            print(f"  注册钩子: {event}")

    agent = MockAgent()
    ri = ResearchIntegration()
    ri.register_hooks(agent)

    # 测试研究执行
    print("\n  🌐 真实研究测试:")
    result = ri.execute_research("Python list comprehension", goal_type="concept")
    print(f"  主题: {result['topic']}")
    print(f"  总结果: {result['total_results']}")
    print(f"  子查询: {result['sub_queries_count']}")
    print(f"  缺口: {result['gaps'][:3]}")
    print(f"  摘要: {result['summary'][:200]}...")

    # 测试钩子
    print("\n  🔌 Hook 测试:")
    ri._on_post_scan(agent)
    print(f"  POST_SCAN 后问题数: {len(agent.questions)}")

    print("\n  📊 统计:", ri.get_research_stats())

    print("\n✅ Research Integration 测试完成")
