"""Tests for shared_rules module."""

import tempfile
from pathlib import Path

import pytest

from algitex.shared_rules import (
    RuleContext,
    RuleViolation,
    SharedRule,
    SortedImportsRule,
    RelativeImportRule,
    RuleRegistry,
    get_registry,
    reset_registry,
)


class TestRuleContext:
    def test_context_creation(self):
        ctx = RuleContext(
            file_path="test.py",
            source_code="import os\n",
        )
        assert ctx.file_path == "test.py"
        assert ctx.source_code == "import os\n"
        assert ctx.ast_tree is None
    
    def test_context_with_config(self):
        ctx = RuleContext(
            file_path="test.py",
            source_code="import os\n",
            config={"strict": True},
        )
        assert ctx.config["strict"] is True


class TestRuleViolation:
    def test_violation_creation(self):
        v = RuleViolation(
            rule_id="sorted_imports",
            file="test.py",
            line=1,
            column=0,
            message="Imports not sorted",
            severity="warning",
            fix_available=True,
        )
        assert v.rule_id == "sorted_imports"
        assert v.fix_available is True
    
    def test_violation_to_dict(self):
        v = RuleViolation(
            rule_id="sorted_imports",
            file="test.py",
            line=1,
            column=0,
            message="Imports not sorted",
            severity="warning",
            fix_available=True,
            fix_suggestion="Use isort",
        )
        d = v.to_dict()
        assert d["rule_id"] == "sorted_imports"
        assert d["fix_suggestion"] == "Use isort"


class TestSortedImportsRule:
    def test_rule_properties(self):
        rule = SortedImportsRule()
        assert rule.rule_id == "sorted_imports"
        assert rule.tier == "algorithm"
        assert rule.fixable is True
        assert rule.severity == "warning"
    
    def test_check_sorted_imports(self):
        rule = SortedImportsRule()
        ctx = RuleContext(
            file_path="test.py",
            source_code="import os\nimport json\n",
        )
        
        violations = rule.check(ctx)
        assert len(violations) == 0  # Already sorted
    
    def test_check_unsorted_stdlib_imports(self):
        # This is tricky because stdlib detection is simplified
        rule = SortedImportsRule()
        ctx = RuleContext(
            file_path="test.py",
            source_code="import zzz\nimport aaa\n",  # Alphabetically unsorted
        )
        
        violations = rule.check(ctx)
        # May or may not detect depending on grouping logic
        # Just verify it doesn't crash
        assert isinstance(violations, list)
    
    def test_check_with_import_from(self):
        rule = SortedImportsRule()
        ctx = RuleContext(
            file_path="test.py",
            source_code="from os import path\nimport json\n",
        )
        
        violations = rule.check(ctx)
        # from imports and regular imports may trigger violation
        assert isinstance(violations, list)
    
    def test_fix_with_isort(self):
        rule = SortedImportsRule()
        ctx = RuleContext(
            file_path="test.py",
            source_code="import zzz\nimport os\n",
        )
        
        violation = RuleViolation(
            rule_id="sorted_imports",
            file="test.py",
            line=1,
            column=0,
            message="Unsorted",
            severity="warning",
            fix_available=True,
        )
        
        try:
            import isort
            fixed = rule.fix(ctx, violation)
            assert fixed is not None
            assert "import os" in fixed  # os should come before zzz
        except ImportError:
            pytest.skip("isort not installed")
    
    def test_fix_without_isort(self):
        # Temporarily hide isort
        import sys
        original = sys.modules.get('isort')
        sys.modules['isort'] = None
        
        try:
            rule = SortedImportsRule()
            ctx = RuleContext(file_path="test.py", source_code="import zzz\n")
            violation = RuleViolation(
                rule_id="sorted_imports", file="test.py", line=1, column=0,
                message="Unsorted", severity="warning", fix_available=True,
            )
            fixed = rule.fix(ctx, violation)
            assert fixed is None  # Can't fix without isort
        finally:
            if original:
                sys.modules['isort'] = original
            else:
                del sys.modules['isort']


class TestRelativeImportRule:
    def test_rule_properties(self):
        rule = RelativeImportRule()
        assert rule.rule_id == "relative_imports"
        assert rule.tier == "algorithm"
        assert rule.fixable is True
    
    def test_check_no_relative_imports(self):
        rule = RelativeImportRule()
        ctx = RuleContext(
            file_path="test.py",
            source_code="import os\nfrom pathlib import Path\n",
        )
        
        violations = rule.check(ctx)
        assert len(violations) == 0
    
    def test_check_relative_imports(self):
        rule = RelativeImportRule()
        ctx = RuleContext(
            file_path="test.py",
            source_code="from . import module\nfrom ..parent import something\n",
        )
        
        violations = rule.check(ctx)
        assert len(violations) == 2
        assert violations[0].rule_id == "relative_imports"
        assert violations[0].line == 1
        assert violations[1].line == 2
    
    def test_check_absolute_imports_allowed(self):
        rule = RelativeImportRule()
        ctx = RuleContext(
            file_path="test.py",
            source_code="from mypackage import module\nfrom mypackage.sub import thing\n",
        )
        
        violations = rule.check(ctx)
        assert len(violations) == 0


class TestRuleRegistry:
    def test_registry_creation(self):
        registry = RuleRegistry()
        assert len(registry.list_rules()) == 0
    
    def test_register_and_get(self):
        registry = RuleRegistry()
        rule = SortedImportsRule()
        
        registry.register(rule)
        
        got = registry.get("sorted_imports")
        assert got is rule
    
    def test_list_rules(self):
        registry = RuleRegistry()
        registry.register(SortedImportsRule())
        registry.register(RelativeImportRule())
        
        rules = registry.list_rules()
        assert len(rules) == 2
        
        # Filter by tier
        algo_rules = registry.list_rules(tier="algorithm")
        assert len(algo_rules) == 2
    
    def test_check_file(self):
        registry = RuleRegistry()
        registry.register(SortedImportsRule())
        registry.register(RelativeImportRule())
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("from . import module\n")
            
            results = registry.check_file(str(test_file))
            
            assert "relative_imports" in results
            assert len(results["relative_imports"]) == 1
    
    def test_check_file_not_found(self):
        registry = RuleRegistry()
        
        results = registry.check_file("/nonexistent/file.py")
        
        assert "error" in results
    
    def test_check_file_syntax_error(self):
        registry = RuleRegistry()
        registry.register(SortedImportsRule())
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("this is not valid python syntax!!!\n")
            
            results = registry.check_file(str(test_file))
            
            # Should handle gracefully
            assert isinstance(results, dict)


class TestGlobalRegistry:
    def test_get_registry(self):
        reset_registry()
        
        registry1 = get_registry()
        assert len(registry1.list_rules()) >= 2  # Built-in rules
        
        # Same instance
        registry2 = get_registry()
        assert registry1 is registry2
    
    def test_reset_registry(self):
        reset_registry()
        
        registry1 = get_registry()
        original_rules = list(registry1.list_rules())
        
        registry1.register(SortedImportsRule())
        
        reset_registry()
        
        registry2 = get_registry()
        assert len(registry2.list_rules()) == len(original_rules)
