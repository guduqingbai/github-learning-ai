"""测试 antibody_library.py — 抗体注册/匹配/策略升级/Buglog"""

from pathlib import Path
from antibody_library import AntibodyLibrary, Antibody, FixStrategy, ProblemTriage


class TestFixStrategy:
    def test_create_and_execute(self):
        def dummy_action(engine, target):
            return {"success": True, "data": target}
        s = FixStrategy("test_strat", "测试策略", dummy_action)
        assert s.name == "test_strat"
        result = s.execute(None, "foo")
        assert result["success"] is True
        assert result["data"] == "foo"


class TestProblemTriage:
    def test_high_importance_allows_many_strategies(self):
        assert ProblemTriage.max_strategies(0.9) == 999

    def test_medium_limits_to_two(self):
        assert ProblemTriage.max_strategies(0.6) == 2

    def test_low_limits_to_one(self):
        assert ProblemTriage.max_strategies(0.3) == 1

    def test_should_defer_high_importance(self):
        # 高重要性 + 策略未用完 → 不应暂缓
        assert ProblemTriage.should_defer(0.9, 2, 5) is False
        # 高重要性 + 策略已用完 → 会暂缓（所有策略都试过了）
        assert ProblemTriage.should_defer(0.9, 10, 3) is True

    def test_should_defer_low_importance(self):
        assert ProblemTriage.should_defer(0.3, 1, 3) is True
        assert ProblemTriage.should_defer(0.3, 0, 3) is False


class TestAntibodyLibrary:
    def test_builtin_antibodies_loaded(self):
        lib = AntibodyLibrary(data_dir=Path("data"))
        assert len(lib._antibodies) >= 2

    def test_match_by_finding_keyword(self):
        lib = AntibodyLibrary(data_dir=Path("data"))
        matched = lib.match(["模块文档缺失"], "")
        names = [ab.name for ab in matched]
        assert "add_docstring" in names

    def test_match_by_summary_keyword(self):
        lib = AntibodyLibrary(data_dir=Path("data"))
        matched = lib.match([], "裸 except 需要修复")
        names = [ab.name for ab in matched]
        assert "fix_bare_except" in names

    def test_no_match_when_no_trigger(self):
        lib = AntibodyLibrary(data_dir=Path("data"))
        matched = lib.match(["无关内容"], "无关总结")
        assert len(matched) == 0

    def test_get_by_name(self):
        lib = AntibodyLibrary(data_dir=Path("data"))
        ab = lib.get_by_name("add_docstring")
        assert ab is not None
        assert ab.name == "add_docstring"

    def test_get_by_name_nonexistent(self):
        lib = AntibodyLibrary(data_dir=Path("data"))
        assert lib.get_by_name("nonexistent") is None

    def test_add_return_types_registered(self):
        lib = AntibodyLibrary(data_dir=Path("data"))
        ab = lib.get_by_name("add_return_types")
        assert ab is not None
        assert len(ab.strategies) >= 1


class TestBuglog:
    def test_record_and_search(self, tmp_path: Path):
        from antibody_library import Buglog
        blog = Buglog(tmp_path)
        blog.record_success("file_a.py", "test_ab", "strategy_1", "测试修复")
        results = blog.search(target="file_a.py")
        assert len(results) == 1
        assert results[0]["antibody"] == "test_ab"
        assert results[0]["fix_count"] == 1

    def test_duplicate_increments_count(self, tmp_path: Path):
        from antibody_library import Buglog
        blog = Buglog(tmp_path)
        blog.record_success("file_a.py", "test_ab", "strategy_1")
        blog.record_success("file_a.py", "test_ab", "strategy_1")
        results = blog.search(target="file_a.py")
        assert len(results) == 1
        assert results[0]["fix_count"] == 2

    def test_has_known_fix(self, tmp_path: Path):
        from antibody_library import Buglog
        blog = Buglog(tmp_path)
        blog.record_success("f.py", "ab", "s1")
        assert blog.has_known_fix("f.py", "ab") is True
        assert blog.has_known_fix("f.py", "other") is False
