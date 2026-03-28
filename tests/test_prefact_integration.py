"""Tests for prefact_integration module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from algitex.prefact_integration import (
    PrefactIssue,
    PrefactRuleAdapter,
    SharedRuleEngine,
    run_prefact_check,
    check_file_with_prefact,
)


class TestPrefactIssue:
    def test_issue_creation(self):
        issue = PrefactIssue(
            rule="sorted_imports",
            file="test.py",
            line=10,
            column=0,
            message="Imports should be sorted",
            severity="warning",
            fixable=True,
        )
        assert issue.rule == "sorted_imports"
        assert issue.file == "test.py"
    
    def test_issue_to_dict(self):
        issue = PrefactIssue(
            rule="sorted_imports",
            file="test.py",
            line=10,
            column=0,
            message="Imports should be sorted",
            severity="warning",
            fixable=True,
        )
        d = issue.to_dict()
        assert d["rule"] == "sorted_imports"
        assert d["severity"] == "warning"


class TestPrefactRuleAdapter:
    def test_adapter_creation(self):
        adapter = PrefactRuleAdapter()
        assert adapter is not None
    
    def test_is_available_no_prefact(self):
        adapter = PrefactRuleAdapter(prefact_path=None)
        adapter._has_prefact = False  # Force unavailable
        assert adapter.is_available() is False
    
    @patch("algitex.prefact_integration.subprocess.run")
    def test_find_prefact_success(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="1.0.0")
        
        adapter = PrefactRuleAdapter()
        assert adapter.is_available() is True
    
    @patch("algitex.prefact_integration.subprocess.run")
    def test_scan_file_success(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"issues": [{"rule": "sorted_imports", "line": 5, "column": 0, "message": "Unsorted", "severity": "warning", "fixable": true}]}'
        )
        
        adapter = PrefactRuleAdapter(prefact_path="prefact")
        adapter._has_prefact = True  # Force available
        
        issues = adapter.scan_file("test.py")
        
        assert len(issues) == 1
        assert issues[0].rule == "sorted_imports"
        assert issues[0].line == 5
    
    @patch("algitex.prefact_integration.subprocess.run")
    def test_scan_file_failure(self, mock_run):
        mock_run.return_value = Mock(returncode=1, stderr="error")
        
        adapter = PrefactRuleAdapter(prefact_path="prefact")
        adapter._has_prefact = True
        
        issues = adapter.scan_file("test.py")
        
        assert len(issues) == 0
    
    @patch("algitex.prefact_integration.subprocess.run")
    def test_scan_directory(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"files": [{"path": "a.py", "issues": []}, {"path": "b.py", "issues": [{"rule": "unused", "line": 1, "column": 0, "message": "x", "severity": "warning", "fixable": false}]}]}'
        )
        
        adapter = PrefactRuleAdapter(prefact_path="prefact")
        adapter._has_prefact = True
        
        issues = adapter.scan_directory("./src")
        
        assert len(issues) == 1
        assert issues[0].file == "b.py"
    
    @patch("algitex.prefact_integration.subprocess.run")
    def test_check_sorted_imports(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"issues": [{"rule": "sorted_imports", "line": 1, "column": 0, "message": "Unsorted", "severity": "warning", "fixable": true}]}'
        )
        
        adapter = PrefactRuleAdapter(prefact_path="prefact")
        adapter._has_prefact = True
        
        issues = adapter.check_sorted_imports("test.py")
        
        assert len(issues) == 1
        assert issues[0].rule == "sorted_imports"
    
    @patch("algitex.prefact_integration.subprocess.run")
    def test_check_relative_imports(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"issues": [{"rule": "relative_imports", "line": 1, "column": 0, "message": "Relative", "severity": "warning", "fixable": true}]}'
        )
        
        adapter = PrefactRuleAdapter(prefact_path="prefact")
        adapter._has_prefact = True
        
        issues = adapter.check_relative_imports("test.py")
        
        assert len(issues) == 1
        assert issues[0].rule == "relative_imports"
    
    def test_get_rules_info(self):
        adapter = PrefactRuleAdapter()
        info = adapter.get_rules_info()
        
        assert "available" in info
        assert "rules" in info
        assert len(info["rules"]) >= 4
        
        sorted_rule = next(r for r in info["rules"] if r["name"] == "sorted_imports")
        assert sorted_rule["tier"] == "algorithm"
        assert sorted_rule["fixable"] is True


class TestSharedRuleEngine:
    def test_engine_creation(self):
        engine = SharedRuleEngine()
        assert engine is not None
    
    def test_analyze_without_prefact(self):
        engine = SharedRuleEngine()
        engine.prefact._has_prefact = False  # Disable prefact
        
        results = engine.analyze("/nonexistent.py")
        
        assert "prefact" in results
        assert "algitex" in results
        assert len(results["prefact"]) == 0
    
    def test_get_all_issues(self):
        engine = SharedRuleEngine()
        engine.prefact._has_prefact = False
        
        issues = engine.get_all_issues("/nonexistent.py")
        
        assert isinstance(issues, list)


class TestHelperFunctions:
    @patch("algitex.prefact_integration.subprocess.run")
    def test_run_prefact_check_success(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="{}")
        
        result = run_prefact_check("test.py")
        assert result is True
    
    def test_run_prefact_check_no_prefact(self):
        with patch('algitex.prefact_integration.PrefactRuleAdapter') as mock_adapter:
            mock_instance = MagicMock()
            mock_instance.is_available.return_value = False
            mock_adapter.return_value = mock_instance
            
            result = run_prefact_check("test.py")
            assert result is False
    
    def test_check_file_with_prefact_unavailable(self):
        with patch('algitex.prefact_integration.PrefactRuleAdapter') as mock_adapter:
            mock_instance = MagicMock()
            mock_instance.is_available.return_value = False
            mock_adapter.return_value = mock_instance
            
            result = check_file_with_prefact("test.py")
            assert len(result) == 1
            assert "error" in result[0]
    
    @patch("algitex.prefact_integration.subprocess.run")
    def test_check_file_with_prefact_specific_rule(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"issues": [{"rule": "sorted_imports", "line": 1, "column": 0, "message": "x", "severity": "warning", "fixable": true}]}'
        )
        
        result = check_file_with_prefact("test.py", rule="sorted_imports")
        
        assert len(result) == 1
        assert result[0]["rule"] == "sorted_imports"
    
    @patch("algitex.prefact_integration.subprocess.run")
    def test_check_file_with_prefact_all_rules(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"issues": [{"rule": "a", "line": 1, "column": 0, "message": "x", "severity": "warning", "fixable": true}, {"rule": "b", "line": 2, "column": 0, "message": "y", "severity": "error", "fixable": false}]}'
        )
        
        result = check_file_with_prefact("test.py")
        
        assert len(result) == 2
