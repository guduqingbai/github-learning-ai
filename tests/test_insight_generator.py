"""测试 insight_generator.py — 纯函数洞察生成"""

import json
from insight_generator import generate_insight, store_insight, _insight_from_file


class MockQuestion:
    """模拟探索问题对象"""
    def __init__(self, explore_action="read_file", target="test.py",
                 observation="观察", question="问题",
                 importance=0.5, context=None):
        self.explore_action = explore_action
        self.target = target
        self.observation = observation
        self.question = question
        self.importance = importance
        self.context = context or {}


class TestGenerateInsight:
    def test_error_returns_early(self):
        q = MockQuestion()
        result = generate_insight(q, {"error": "出错了"})
        assert result["action_taken"] == "error"
        assert "出错了" in result["summary"]

    def test_read_file_dispatches(self):
        q = MockQuestion(explore_action="read_file", target="test.py")
        result = generate_insight(q, {"file": "test.py", "lines": 50, "docstring": "模块文档"})
        assert result["topic"] == "test 模块分析"
        assert result["category"] == "项目自身"

    def test_compare_dispatches(self):
        q = MockQuestion(explore_action="compare_files")
        exploration = {"file_a": "a.py", "file_b": "b.py", "jaccard_similarity": 0.5, "conclusion": "中等相似"}
        result = generate_insight(q, exploration)
        assert "相似度分析" in result["topic"]

    def test_gap_dispatches(self):
        q = MockQuestion(explore_action="add_crawler_task")
        result = generate_insight(q, {"domain": "test", "missing_topics": ["x"], "crawler_tasks_added": 1})
        assert "知识缺口" in result["summary"]

    def test_global_research_dispatches(self):
        q = MockQuestion(explore_action="global_research", context={"research_queries": ["q1"]})
        result = generate_insight(q, {"research_topic": "AI", "crawler_tasks_added": 2})
        assert "全球研究" in result["summary"]

    def test_self_heal_dispatches(self):
        q = MockQuestion(explore_action="self_heal", question="修复裸 except")
        result = generate_insight(q, {"target": "test.py", "fixes_attempted": 2, "fixes_succeeded": 1, "fix_results": [
            {"success": True, "type": "fix", "file": "test.py", "detail": "已修复"},
            {"success": False, "type": "fix", "file": "test.py", "detail": "失败"},
        ]})
        assert "自我修复" in result["summary"]
        assert "裸 except" in result["findings"]

    def test_deep_learning_dispatches(self):
        q = MockQuestion(explore_action="deep_learning")
        result = generate_insight(q, {"topic": "async", "missing_capabilities": ["asyncio"]})
        assert "能力深度" in result["topic"]

    def test_unknown_action_fallback(self):
        q = MockQuestion(explore_action="unknown_action")
        result = generate_insight(q, {})
        assert "完成" in result["summary"]


class TestStoreInsight:
    def test_no_topic_returns_false(self):
        assert store_insight({"topic": ""}) is False

    def test_returns_bool(self):
        result = store_insight({"topic": "临时测试", "summary": "测试"})
        assert isinstance(result, bool)
