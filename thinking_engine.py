#!/usr/bin/env python3
"""
思考引擎 — 星期八自己的纯本地大脑
整合知识图、自模型、模式引擎、类比引擎
生成真正的好奇心、洞察和自我叙事，不依赖任何外部 API
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class CuriosityQuestion:
    """一个真正的好奇心问题"""
    question: str
    source: str      # knowledge_gap | pattern | analogy | complexity | dependency
    confidence: float
    related_entity: str = ""
    detail: str = ""


@dataclass
class Insight:
    """一个真正的洞察"""
    content: str
    category: str    # code_quality | knowledge | architecture | dependency
    importance: float
    related_entities: List[str] = field(default_factory=list)


@dataclass
class ThinkingResult:
    """一次思考循环的结果"""
    timestamp: str
    curiosity_questions: List[CuriosityQuestion]
    insights: List[Insight]
    narrative: str
    stats: Dict[str, Any]


class ThinkingEngine:
    """
    纯本地思考引擎。

    思考不需要外部 API。所有好奇心、洞察、叙事
    都来自对自身代码和知识的真实分析。
    """

    def __init__(self, knowledge_graph=None, self_model=None,
                 pattern_engine=None, analogy_engine=None):
        self._kg = knowledge_graph
        self._sm = self_model
        self._pe = pattern_engine
        self._ae = analogy_engine
        self._previous_stats: Dict[str, Any] = {}
        self._stats_file = Path("data") / "thinking_engine_stats.json"
        self._load_previous_stats()
        self._goal_planner = None

    # ── 历史状态追踪（用于叙事理解） ────────────────

    def _load_previous_stats(self):
        """加载上次思考的统计快照"""
        try:
            if self._stats_file.exists():
                import json
                self._previous_stats = json.loads(
                    self._stats_file.read_text(encoding="utf-8"))
        except Exception:
            self._previous_stats = {}

    def _save_current_stats(self, stats: Dict[str, Any]):
        """保存当前统计快照供下次对比"""
        try:
            import json
            self._stats_file.parent.mkdir(exist_ok=True)
            self._stats_file.write_text(
                json.dumps(stats, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    def _compute_delta(self, current: Dict[str, Any]) -> Dict[str, Any]:
        """对比当前和上次思考，找出变化"""
        prev = self._previous_stats
        if not prev:
            return {"first_cycle": True}

        delta = {}
        for key in ["total_classes", "total_functions", "total_modules",
                     "graph_entities", "graph_relations", "isolated_entities"]:
            if key in current and key in prev:
                diff = current[key] - prev[key]
                if diff != 0:
                    delta[key] = diff
        return delta

    def think(self) -> ThinkingResult:
        """
        执行一次完整的思考循环。

        1. 更新自模型 → 了解自身状态
        2. 更新知识图 → 关联新旧知识
        3. 运行模式引擎 → 发现代码/知识的问题
        4. 运行类比引擎 → 发现跨域连接
        5. 生成好奇心 → 基于真实缺口
        6. 生成洞察 → 基于模式发现
        7. 组装叙事 → 基于实际变化
        8. 返回思考结果
        """
        # ── 1. 自模型扫描 ──────────────────────────
        sm_report = self._sm.generate_report() if self._sm else {}

        # ── 2. 构建自身到知识图 ─────────────────────
        if self._sm and self._kg:
            self._sm.build_self_graph()

        # ── 3. 从 KnowledgeBase 导入到知识图 ────────
        if self._kg:
            try:
                from knowledge_base import KnowledgeBase
                kb = KnowledgeBase()
                self._kg.merge_from_knowledge_base(kb.get_all_knowledge())
            except Exception:
                pass

        # ── 4. 模式分析 ────────────────────────────
        pattern_results = {}
        if self._pe:
            try:
                from knowledge_base import KnowledgeBase
                kb = KnowledgeBase()
                pattern_results = self._pe.analyze_all(kb)
            except Exception:
                pattern_results = self._pe.analyze_all()

        # ── 5. 类比分析 ────────────────────────────
        analogies = []
        if self._ae and self._kg:
            analogies = self._ae.cross_domain_analogies(threshold=0.5)

        # ── 5b. 目标规划 ────────────────────────────
        goal_summary = {}
        try:
            from goal_planner import GoalPlanner
            gp = GoalPlanner()
            kg_stats = self._kg.get_statistics() if self._kg else None
            gp.auto_generate(kg_stats, pattern_results)
            goal_summary = gp.get_summary()
        except Exception:
            pass

        # ── 6. 生成好奇心 ───────────────────────────
        questions = self._generate_questions(
            sm_report, pattern_results, analogies)

        # ── 7. 生成洞察 ────────────────────────────
        insights = self._generate_insights(
            sm_report, pattern_results, analogies)

        # ── 8. 组装叙事 ────────────────────────────
        narrative = self._assemble_narrative(
            questions, insights, sm_report, pattern_results, analogies, goal_summary)

        # ── 9. 统计 ────────────────────────────────
        stats = {
            "questions_generated": len(questions),
            "insights_generated": len(insights),
            "patterns_found": sum(
                len(v) for v in pattern_results.items()
                if isinstance(v, list) and v
            ),
            "analogies_found": len(analogies),
            "total_classes": sm_report.get("total_classes", 0),
            "total_functions": sm_report.get("total_functions", 0),
            "total_modules": sm_report.get("total_modules", 0),
        }

        if self._kg:
            kg_stats = self._kg.get_statistics()
            stats["graph_entities"] = kg_stats["total_entities"]
            stats["graph_relations"] = kg_stats["total_relations"]
            stats["isolated_entities"] = kg_stats["isolated_count"]

        self._previous_stats = stats
        self._save_current_stats(stats)

        return ThinkingResult(
            timestamp=datetime.now().isoformat(),
            curiosity_questions=questions,
            insights=insights,
            narrative=narrative,
            stats=stats,
        )

    # ── 好奇心生成（纯算法） ─────────────────────────

    def _generate_questions(self, sm_report: Dict[str, Any],
                            pattern_results: Dict[str, Any],
                            analogies: List[Dict[str, Any]]) -> List[CuriosityQuestion]:
        """基于真实数据生成好奇心问题"""
        questions: List[CuriosityQuestion] = []

        # --- 从知识图缺口生成 ---
        if self._kg:
            gaps = self._kg.find_gaps()
            for g in gaps[:5]:
                questions.append(CuriosityQuestion(
                    question=f"为什么 '{g['entity_name']}' 是孤立的？需要建立什么连接？",
                    source="knowledge_gap",
                    confidence=0.8,
                    related_entity=g["entity_name"],
                    detail=g["detail"],
                ))

            bridges = self._kg.find_bridges()
            for b in bridges[:3]:
                questions.append(CuriosityQuestion(
                    question=f"'{b['entity_name']}' 连接了 {b['connects_types']}，能否利用这种跨界能力？",
                    source="knowledge_gap",
                    confidence=0.7,
                    related_entity=b["entity_name"],
                    detail=f"度={b['degree']}, 连接类型={b['connects_types']}",
                ))

        # --- 从模式发现生成 ---
        bare_excepts = pattern_results.get("bare_excepts", [])
        if bare_excepts:
            questions.append(CuriosityQuestion(
                question=f"有 {len(bare_excepts)} 处 bare except，是否应该指定异常类型？",
                source="pattern",
                confidence=0.9,
                detail=f"位置: {[b['file'] for b in bare_excepts[:3]]}",
            ))

        missing_docs = pattern_results.get("missing_docstrings", [])
        if missing_docs:
            total_missing = sum(m.get("missing_count", 0) for m in missing_docs)
            questions.append(CuriosityQuestion(
                question=f"{total_missing} 个函数/类缺少文档，补全文档能否提升可维护性？",
                source="pattern",
                confidence=0.7,
                detail=f"涉及 {len(missing_docs)} 个模块",
            ))

        complex_mods = pattern_results.get("complex_modules", [])
        if complex_mods:
            for cm in complex_mods[:2]:
                questions.append(CuriosityQuestion(
                    question=f"'{cm['file']}' {cm['detail']}，是否应该拆分？",
                    source="complexity",
                    confidence=0.8,
                    related_entity=cm["file"],
                    detail=cm["detail"],
                ))

        similar_mods = pattern_results.get("similar_modules", [])
        if similar_mods:
            for sm in similar_mods[:2]:
                questions.append(CuriosityQuestion(
                    question=f"'{sm['module_a']}' 和 '{sm['module_b']}' 结构相似（{sm['similarity']:.0%}），是否功能重复？",
                    source="pattern",
                    confidence=0.6,
                    related_entity=f"{sm['module_a']} & {sm['module_b']}",
                    detail=sm["detail"],
                ))

        dead_code = pattern_results.get("dead_code", [])
        if dead_code:
            total_dead = sum(d.get("unused_count", 0) for d in dead_code)
            questions.append(CuriosityQuestion(
                question=f"检测到 {total_dead} 个可能未使用的定义，是否可以清理？",
                source="pattern",
                confidence=0.5,
                detail=f"涉及 {len(dead_code)} 个模块",
            ))

        # --- 从类比生成 ---
        for a in analogies[:3]:
            questions.append(CuriosityQuestion(
                question=f"'{a['entity_a']}' ({a['entity_a_type']}) 和 '{a['entity_b']}' ({a['entity_b_type']}) 结构相似（{a['similarity']}），能互相借鉴吗？",
                source="analogy",
                confidence=0.6,
                related_entity=f"{a['entity_a']} & {a['entity_b']}",
            ))

        # --- 从自模型生成 ---
        if sm_report.get("total_classes", 0) == 0 and sm_report.get("total_modules", 0) > 0:
            questions.append(CuriosityQuestion(
                question="项目中有模块但没有类，是否应该引入面向对象设计？",
                source="complexity",
                confidence=0.4,
            ))

        # --- 从知识图统计生成 ---
        if self._kg:
            stats = self._kg.get_statistics()
            if stats["isolated_count"] > stats["total_entities"] * 0.3:
                questions.append(CuriosityQuestion(
                    question=f"超过 30% 的实体是孤立的（{stats['isolated_count']}/{stats['total_entities']}），知识连接严重不足",
                    source="knowledge_gap",
                    confidence=0.9,
                ))

        # 好奇心数量和内容不稳定是正常的——真实好奇心本来就随状态变化
        return questions

    # ── 洞察生成（基于模式发现） ────────────────────

    def _generate_insights(self, sm_report: Dict[str, Any],
                           pattern_results: Dict[str, Any],
                           analogies: List[Dict[str, Any]]) -> List[Insight]:
        """从模式分析生成真正的洞察"""
        insights: List[Insight] = []

        # 代码质量洞察
        bare = pattern_results.get("bare_excepts", [])
        if bare:
            insights.append(Insight(
                content=f"发现 {len(bare)} 处 bare except 语句，这是异常吞噬的常见来源。建议全部替换为具体的异常类型。",
                category="code_quality",
                importance=0.9,
                related_entities=[b["file"] for b in bare[:5]],
            ))

        dead = pattern_results.get("dead_code", [])
        if dead:
            total = sum(d.get("unused_count", 0) for d in dead)
            names = [d["file"] for d in dead[:5]]
            insights.append(Insight(
                content=f"{total} 个函数/类可能未被使用，分布在 {names}。删除无用代码可以降低认知负荷。",
                category="code_quality",
                importance=0.6,
                related_entities=names,
            ))

        # 架构洞察
        similar = pattern_results.get("similar_modules", [])
        if similar:
            for s in similar[:2]:
                insights.append(Insight(
                    content=f"'{s['module_a']}' 和 '{s['module_b']}' 导入依赖相似度 {s['similarity']:.0%}，共享的导入包括 {s['shared_imports'][:5]}。可能提取公共模块。",
                    category="architecture",
                    importance=0.7,
                    related_entities=[s["module_a"], s["module_b"]],
                ))

        complex_mods = pattern_results.get("complex_modules", [])
        if complex_mods:
            for cm in complex_mods[:2]:
                insights.append(Insight(
                    content=f"'{cm['file']}' 比较复杂（{cm['lines']}行，{cm['functions']}个函数）。"
                             + "大模块难以测试和维护，建议按职责拆分。",
                    category="architecture",
                    importance=0.7,
                    related_entities=[cm["file"]],
                ))

        # 知识洞察
        clusters = pattern_results.get("concept_clusters", [])
        if clusters:
            for c in clusters[:2]:
                insights.append(Insight(
                    content=f"概念聚类: {c['detail']}。这些概念高度关联，可以统一学习或引用。",
                    category="knowledge",
                    importance=0.5,
                ))

        gaps = pattern_results.get("knowledge_gaps", [])
        if gaps:
            insights.append(Insight(
                content=f"知识图中有 {len(gaps)} 个缺口（孤立实体/未连接概念）。建立这些连接能提升知识的关联性。",
                category="knowledge",
                importance=0.6,
            ))

        # 类比洞察
        for a in analogies[:2]:
            if self._ae:
                text = self._ae.generate_analogy_insight(
                    a["entity_a"], a["entity_b"], a["similarity"])
                insights.append(Insight(
                    content=text,
                    category="architecture" if a["entity_a_type"] != a["entity_b_type"] else "knowledge",
                    importance=0.5,
                    related_entities=[a["entity_a"], a["entity_b"]],
                ))

        # 自模型洞察
        dep_modules = sm_report.get("most_dependent_modules", [])
        if dep_modules:
            name, count = dep_modules[0]
            insights.append(Insight(
                content=f"'{name}' 是依赖最多的模块（{count} 个导入），它是系统的核心依赖枢纽。",
                category="architecture",
                importance=0.6,
                related_entities=[name],
            ))

        ref_modules = sm_report.get("most_referenced_modules", [])
        if ref_modules:
            name, count = ref_modules[0]
            insights.append(Insight(
                content=f"'{name}' 是被其他模块引用最多的（{count} 次修改），它是系统的热点。",
                category="architecture",
                importance=0.5,
                related_entities=[name],
            ))

        return insights

    # ── 叙事组装（非生成，是基于变化的组装） ─────────

    def _assemble_narrative(self, questions: List[CuriosityQuestion],
                            insights: List[Insight],
                            sm_report: Dict[str, Any],
                            pattern_results: Dict[str, Any],
                            analogies: List[Dict] = None,
                            goal_summary: Dict[str, Any] = None) -> str:
        """组装带自我理解的叙事 — 不只是报告，还有反思和趋势感知"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        parts = [f"星期八思考报告 ({now})"]

        # ═══════════════════════════════════════════
        # 1. 自身状态
        # ═══════════════════════════════════════════
        mod_count = sm_report.get("total_modules", 0)
        cls_count = sm_report.get("total_classes", 0)
        func_count = sm_report.get("total_functions", 0)
        parts.append(f"自我状态: {mod_count} 个模块, {cls_count} 个类, {func_count} 个函数")

        # 知识图状态
        if self._kg:
            kgs = self._kg.get_statistics()
            parts.append(f"知识图: {kgs['total_entities']} 实体, {kgs['total_relations']} 关系, "
                         + f"{kgs['isolated_count']} 孤立, {kgs['bridge_count']} 跨界者")

        # 经验记忆统计
        try:
            from experience_tracker import ExperienceTracker
            et = ExperienceTracker()
            exp = et.get_summary()
            if exp["total_experiences"] > 0:
                parts.append(f"经验记忆: {exp['total_experiences']} 次尝试, "
                             f"成功率 {exp['success_rate']}%")
                if exp["critical_patterns"]:
                    worst = exp["critical_patterns"][0]
                    parts.append(f"  ⚠️ 重复失败: '{worst['problem'][:30]}' "
                                 f"用 {worst['strategy']} 已失败 {worst['count']} 次")
        except Exception:
            pass

        # ═══════════════════════════════════════════
        # 2. 变化感知（delta from last cycle）
        # ═══════════════════════════════════════════
        delta = self._compute_delta(self._previous_stats or {})
        if delta.get("first_cycle"):
            parts.append("状态: 首次思考，无历史对比")
        else:
            change_parts = []
            if "graph_entities" in delta:
                v = delta["graph_entities"]
                change_parts.append(f"知识图 {'+' if v > 0 else ''}{v} 实体")
            if "graph_relations" in delta:
                v = delta["graph_relations"]
                change_parts.append(f"关系 {'+' if v > 0 else ''}{v}")
            if "isolated_entities" in delta:
                v = delta["isolated_entities"]
                change_parts.append(f"孤立实体 {'-' if v < 0 else '+'}{abs(v)}")
            if change_parts:
                parts.append(f"自上次: {'; '.join(change_parts)}")

        # ═══════════════════════════════════════════
        # 3. 关注点（最重要的几个问题/趋势）
        # ═══════════════════════════════════════════
        concerns = []
        if self._kg:
            kgs = self._kg.get_statistics()
            isolated_ratio = kgs["isolated_count"] / max(1, kgs["total_entities"])
            if isolated_ratio > 0.3:
                concerns.append(f"知识连接严重不足: {kgs['isolated_count']}/{kgs['total_entities']} 实体孤立")
            if kgs["bridge_count"] > 0:
                concerns.append(f"检测到 {kgs['bridge_count']} 个跨界实体，值得关注")

        pattern_summary = pattern_results.get("summary", {})
        total_issues = pattern_summary.get("total_issues", 0)
        high_sev = pattern_summary.get("high_severity", 0)
        if high_sev > 0:
            concerns.append(f"高危问题 {high_sev} 处需立即处理")
        if total_issues > 100:
            concerns.append(f"总问题数较多 ({total_issues} 处)，建议集中清理")

        if concerns:
            parts.append(f"关注 ({len(concerns)} 项):")
            for c in concerns:
                parts.append(f"  ⚠️ {c}")

        # ═══════════════════════════════════════════
        # 4. 好奇心
        # ═══════════════════════════════════════════
        if questions:
            top_q = questions[:5]
            parts.append(f"好奇心 ({len(questions)} 个问题):")
            for q in top_q:
                parts.append(f"  [{q.source}] {q.question}")

        # ═══════════════════════════════════════════
        # 5. 洞察
        # ═══════════════════════════════════════════
        if insights:
            top_i = sorted(insights, key=lambda x: -x.importance)[:5]
            parts.append(f"洞察 ({len(insights)} 条):")
            for ins in top_i:
                parts.append(f"  [{ins.category}] (重要性 {ins.importance}) {ins.content}")

        # ═══════════════════════════════════════════
        # 6. 跨域类比（使用已计算好的结果，避免重复调用）
        # ═══════════════════════════════════════════
        if analogies:
            parts.append(f"跨域类比: {len(analogies)} 个潜在连接")
            for a in analogies[:2]:
                shared = a.get("shared_roles", [])
                hint = f"  - {a['entity_a']} ({a['entity_a_type']}) ↔ {a['entity_b']} ({a['entity_b_type']})"
                if shared:
                    hint += f" 共同角色: {', '.join(shared[:3])}"
                parts.append(hint)

        # ═══════════════════════════════════════════
        # 7. 目标进展
        # ═══════════════════════════════════════════
        if goal_summary:
            active = goal_summary.get("active", [])
            completed_count = goal_summary.get("completed_count", 0)
            if active:
                parts.append(f"目标 ({len(active)} 个活跃, {completed_count} 个已完成):")
                for g in active[:5]:
                    bar = "█" * int(g["progress"] * 10) + "░" * (10 - int(g["progress"] * 10))
                    parts.append(f"  [{g['category']}] {g['desc'][:50]} {bar} {g['progress']:.0%}")
            elif completed_count > 0:
                parts.append(f"目标: {completed_count} 个目标已完成")

        # ═══════════════════════════════════════════
        # 7b. 元认知状态
        # ═══════════════════════════════════════════
        try:
            from metacognitive_monitor import MetacognitiveMonitor
            mm = MetacognitiveMonitor()
            m_state = []
            state_file = Path("data") / "metacognitive_state.json"
            if state_file.exists():
                import json as j
                mc_data = j.loads(state_file.read_text(encoding="utf-8"))
                window = mc_data.get("thought_window", [])
                history = mc_data.get("findings_history", [])
                if window:
                    m_state.append(f"思考窗口: {len(window)} 条, "
                                   f"最近: {window[-1][:40]}")
                if history:
                    recent = history[-3:]
                    for h in recent:
                        m_state.append(f"  [{h['type']}] sev={h['severity']:.2f} "
                                       f"— {h['detail'][:50]}")
                if m_state:
                    parts.append(f"元认知 ({len(history)} 条总记录):")
                    parts.extend(m_state)
        except Exception:
            pass

        # ═══════════════════════════════════════════
        # 8. 反思
        # ═══════════════════════════════════════════
        reflection_lines = []
        prev = self._previous_stats
        if prev:
            prev_questions = prev.get("questions_generated", 0)
            prev_insights = prev.get("insights_generated", 0)
            curr_questions = len(questions)
            curr_insights = len(insights)
            if curr_questions > prev_questions * 1.5 and prev_questions > 0:
                reflection_lines.append(f"好奇心较上次大幅提升 ({prev_questions}→{curr_questions})，可能发现了新的知识缺口")
            if curr_insights < prev_insights * 0.5 and prev_insights > 0:
                reflection_lines.append(f"洞察产出下降 ({prev_insights}→{curr_insights})，可能需要调整思考方向")
            if curr_insights > prev_insights * 1.5 and prev_insights > 0:
                reflection_lines.append(f"洞察产出显著增加，思考效果提升")

        if not questions and not insights:
            reflection_lines.append("本轮无新的好奇心或洞察，系统可能处于稳定状态")
        elif questions and not insights:
            reflection_lines.append("有好奇心但未产生洞察，探索效率需关注")

        if reflection_lines:
            parts.append("反思:")
            for line in reflection_lines:
                parts.append(f"  💭 {line}")

        return "\n".join(parts)


if __name__ == "__main__":
    from knowledge_graph import KnowledgeGraph
    from self_model import SelfModel
    from pattern_engine import PatternEngine
    from analogy_engine import AnalogyEngine

    kg = KnowledgeGraph()
    sm = SelfModel(kg)
    pe = PatternEngine(kg)
    ae = AnalogyEngine(kg)

    engine = ThinkingEngine(
        knowledge_graph=kg,
        self_model=sm,
        pattern_engine=pe,
        analogy_engine=ae,
    )

    result = engine.think()
    print("=== 星期八的思考结果 ===")
    print(f"好奇心问题: {len(result.curiosity_questions)}")
    for q in result.curiosity_questions:
        print(f"  [{q.source}] {q.question}")
    print(f"\n洞察: {len(result.insights)}")
    for ins in sorted(result.insights, key=lambda x: -x.importance)[:5]:
        print(f"  [{ins.category}] (imp={ins.importance}) {ins.content[:100]}")
    print(f"\n叙事:\n{result.narrative}")
    print(f"\n统计: {result.stats}")
    print("✅ 思考引擎测试完成")
