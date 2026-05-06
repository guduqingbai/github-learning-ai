"""测试 constitution.py — 完整性校验"""


class TestConstitutionImports:
    def test_import_works(self):
        from constitution import store_checksums, verify_integrity
        assert callable(store_checksums)
        assert callable(verify_integrity)

    def test_immutable_rules_loaded(self):
        from constitution import IMMUTABLE_RULES
        assert len(IMMUTABLE_RULES) >= 5

    def test_constitution_modules_listed(self):
        from constitution import CONSTITUTION_MODULES
        assert "constitution.py" in CONSTITUTION_MODULES
        assert "CONSTITUTION.md" in CONSTITUTION_MODULES

    def test_keywords_defined(self):
        from constitution import CONSTITUTION_KEYWORDS
        assert len(CONSTITUTION_KEYWORDS) >= 10
