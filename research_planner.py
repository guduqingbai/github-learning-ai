#!/usr/bin/env python3
"""
Research Planner — 目标分解 + 递归研究

把宽泛的研究目标拆成可执行的子查询，
执行后自动识别知识缺口并生成跟进问题。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


# ══════════════════════════════════════════════════
# 数据结构
# ══════════════════════════════════════════════════

@dataclass
class ResearchFinding:
    """单个子查询的研究发现"""
    sub_query: str
    results_count: int
    summary: str
    key_points: List[str] = field(default_factory=list)
    citations: List[Dict] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)


@dataclass
class ResearchReport:
    """完整研究报告"""
    goal: str
    goal_type: str  # technology | concept | comparison | howto | background
    status: str     # planned | in_progress | completed
    sub_queries: List[str] = field(default_factory=list)
    findings: List[ResearchFinding] = field(default_factory=list)
    overall_summary: str = ""
    gaps: List[str] = field(default_factory=list)
    follow_up_queries: List[str] = field(default_factory=list)
    created: str = ""
    completed: str = ""


# ══════════════════════════════════════════════════
# ResearchPlanner — 目标分解
# ══════════════════════════════════════════════════

class ResearchPlanner:
    """
    把宽泛的研究目标分解为可执行的子查询。
    基于规则（非 LLM），零外部依赖。
    """

    # 类型关键词
    TECHNOLOGY_KW = {"framework", "language", "platform", "protocol", "library",
                     "tool", "database", "api", "sdk", "engine", "runtime",
                     "docker", "container", "kubernetes", "transformer", "compiler", "kernel", "middleware", "神经网络", "框架", "语言", "平台", "协议", "库", "数据库", "引擎", "工具"}
    COMPARISON_KW = {"vs", "vs.", "versus", "compared", "对比", "比较", "区别", "哪个"}
    HOWTO_KW = {"how to", "how do i", "tutorial", "guide", "教程", "如何",
                "怎么", "入门", "指南"}

    def __init__(self):
        pass

    def plan_research(self, goal: str) -> ResearchReport:
        """制定研究计划：分类 → 拆解子查询"""
        goal_type = self._classify_goal(goal)
        sub_queries = self._decompose(goal, goal_type)

        return ResearchReport(
            goal=goal,
            goal_type=goal_type,
            status="planned",
            sub_queries=sub_queries,
            created=datetime.now().isoformat(),
        )

    def _classify_goal(self, goal: str) -> str:
        """对研究目标分类"""
        gl = goal.lower()

        # comparison
        if any(kw in gl for kw in self.COMPARISON_KW):
            return "comparison"

        # howto
        if any(kw in gl for kw in self.HOWTO_KW):
            return "howto"

        # technology
        words = set(gl.split())
        if words & self.TECHNOLOGY_KW:
            return "technology"

        # background
        bg_kw = {"history", "history of", "evolution", "background",
                 "历史", "发展", "背景", "综述"}
        if any(kw in gl for kw in bg_kw):
            return "background"

        return "concept"  # 默认

    def _decompose(self, goal: str, goal_type: str) -> List[str]:
        """按类型拆分子查询（3-5 个），原始目标优先"""
        templates = {
            "technology": [
                goal,
                f"{goal} overview",
                f"{goal} architecture",
                f"{goal} implementation",
            ],
            "concept": [
                goal,
                f"{goal} definition",
                f"{goal} examples",
                f"{goal} applications",
            ],
            "comparison": [
                goal,
                f"{goal} features comparison",
                f"{goal} pros cons",
                f"{goal} performance benchmark",
            ],
            "howto": [
                goal,
                f"{goal} tutorial",
                f"{goal} getting started",
                f"{goal} common pitfalls",
            ],
            "background": [
                goal,
                f"{goal} overview",
                f"{goal} fundamentals",
                f"{goal} current state 2026",
            ],
        }
        queries = templates.get(goal_type, [goal, f"{goal} overview", f"{goal} details"])
        return queries[:4]  # 最多 4 个


# ══════════════════════════════════════════════════
# RecursiveResearcher — 递归缺口分析
# ══════════════════════════════════════════════════

class RecursiveResearcher:
    """
    研究后分析知识缺口，生成跟进查询。

    规则：
    - 子查询结果 < 2 条 → 缺口
    - 内容抓取失败（有结果无 content）→ 缺口
    - 最大 3 个跟进，1 层深度
    """

    MAX_FOLLOW_UPS = 3
    MAX_DEPTH = 1

    def __init__(self):
        self._depth = 0  # 当前递归深度

    def analyze_report(self, report: ResearchReport) -> List[str]:
        """分析研究缺口，生成跟进查询"""
        gaps = []

        # 1. 结果稀疏的查询
        for finding in report.findings:
            if finding.results_count < 2:
                gaps.append(finding.sub_query)

        # 2. 有结果但没抓到正文的
        for finding in report.findings:
            if finding.results_count >= 2:
                has_content = any(
                    c.snippet for c in finding.citations
                ) if finding.citations else False
                if not has_content:
                    gaps.append(f"{finding.sub_query} [需重试]")

        # 3. finding 自身标记的缺口
        for finding in report.findings:
            for g in finding.gaps:
                gap = g.replace("[retry needed]", "").strip()
                if gap and gap not in gaps:
                    gaps.append(gap)

        report.gaps = gaps[:5]  # 最多 5 个缺口

        # 生成跟进查询
        follow_ups = self._generate_follow_ups(report.goal, gaps)
        report.follow_up_queries = follow_ups[:self.MAX_FOLLOW_UPS]

        return report.follow_up_queries

    def _generate_follow_ups(self, goal: str, gaps: List[str]) -> List[str]:
        """从缺口生成跟进查询"""
        follow_ups = []
        for gap in gaps:
            cleaned = gap.replace("[需重试]", "").strip()
            if cleaned:
                follow_ups.append(cleaned)
        # 如果缺口不够，加通用跟进
        while len(follow_ups) < 2:
            follow_ups.append(f"{goal} advanced topics")
            break
        return follow_ups

    def should_deepen(self) -> bool:
        """判断是否允许继续递归"""
        return self._depth < self.MAX_DEPTH

    def deepen(self):
        """进入下一层递归"""
        self._depth += 1

    def reset_depth(self):
        """重置递归深度"""
        self._depth = 0


# ══════════════════════════════════════════════════
# 单测
# ══════════════════════════════════════════════════

def test_goal_classification():
    """测试目标分类"""
    planner = ResearchPlanner()

    assert planner._classify_goal("Python vs Java performance") == "comparison"
    assert planner._classify_goal("How to build a REST API") == "howto"
    assert planner._classify_goal("Transformer architecture") == "technology"
    assert planner._classify_goal("什么是机器学习") == "concept"
    assert planner._classify_goal("History of computing") == "background"

    print("  [OK] 目标分类通过")


def test_decomposition():
    """测试子查询分解"""
    planner = ResearchPlanner()

    # technology
    report = planner.plan_research("Docker container")
    assert report.goal_type == "technology"
    assert len(report.sub_queries) >= 3
    assert any("overview" in q for q in report.sub_queries)

    # comparison
    report = planner.plan_research("AWS vs Azure vs GCP")
    assert report.goal_type == "comparison"
    assert any("pros cons" in q for q in report.sub_queries)

    # howto
    report = planner.plan_research("How to deploy Django")
    assert report.goal_type == "howto"
    assert any("tutorial" in q for q in report.sub_queries)

    print("  [OK] 子查询分解通过")


def test_recursive_analysis():
    """测试递归缺口分析"""
    researcher = RecursiveResearcher()

    # 稀疏结果 → 缺口
    finding1 = ResearchFinding(
        sub_query="rare topic", results_count=0,
        summary="", gaps=["needs retry"],
    )
    from web_researcher import Citation
    finding2 = ResearchFinding(
        sub_query="common topic", results_count=3,
        summary="has results",
        citations=[Citation(source="web", title="t", url="u", snippet="text", fetch_date="", confidence=0.5)],
    )

    report = ResearchReport(
        goal="test", goal_type="concept", status="completed",
        findings=[finding1, finding2],
        created=datetime.now().isoformat(),
    )

    follow_ups = researcher.analyze_report(report)
    assert len(report.gaps) >= 1, f"应有缺口: {report.gaps}"
    assert len(follow_ups) <= 3, f"跟进不能超过3个: {len(follow_ups)}"

    # 深度限制 (MAX_DEPTH=1)
    assert researcher.should_deepen() == True  # depth=0
    researcher.deepen()
    assert researcher.should_deepen() == False  # depth=1 >= MAX

    print("  [OK] 递归缺口分析通过")
    print("  [OK] 深度控制通过")


if __name__ == "__main__":
    print("=" * 50)
    print("  Research Planner 测试")
    print("=" * 50)

    test_goal_classification()
    test_decomposition()
    test_recursive_analysis()

    print("\n  🌐 完整示例:")
    planner = ResearchPlanner()
    report = planner.plan_research("What is reinforcement learning")
    print(f"  目标类型: {report.goal_type}")
    print(f"  子查询 ({len(report.sub_queries)}):")
    for q in report.sub_queries:
        print(f"    - {q}")

    print("\n✅ Research Planner 全部测试完成")
