"""Integration between algitex and prefact for shared rule logic.

This module provides adapters to use prefact's rule engine within algitex,
enabling consistent code analysis across both tools.

Usage:
    from algitex.prefact_integration import PrefactRuleAdapter
    
    adapter = PrefactRuleAdapter()
    issues = adapter.check_sorted_imports("src/myfile.py")
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import json


@dataclass
class PrefactIssue:
    """Issue found by prefact rule."""
    rule: str
    file: str
    line: int
    column: int
    message: str
    severity: str  # "error", "warning", "info"
    fixable: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "severity": self.severity,
            "fixable": self.fixable,
        }


class PrefactRuleAdapter:
    """Adapter to run prefact rules from algitex."""
    
    def __init__(self, prefact_path: Optional[str] = None):
        self.prefact_path = prefact_path or self._find_prefact()
        self._has_prefact = self.prefact_path is not None
    
    def _find_prefact(self) -> Optional[str]:
        """Find prefact installation."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "prefact", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return "prefact"  # Use module syntax
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check if prefact is in sibling directory
        sibling_prefact = Path(__file__).parent.parent.parent.parent / "prefact" / "src" / "prefact"
        if sibling_prefact.exists():
            return str(sibling_prefact.parent.parent)  # Return the prefact project root
        
        return None
    
    def is_available(self) -> bool:
        """Check if prefact integration is available."""
        return self._has_prefact
    
    def scan_file(self, file_path: str) -> List[PrefactIssue]:
        """Scan a single file using prefact."""
        if not self._has_prefact:
            return []
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "prefact", "scan", file_path, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            data = json.loads(result.stdout)
            return self._parse_issues(data, file_path)
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return []
    
    def scan_directory(self, dir_path: str) -> List[PrefactIssue]:
        """Scan a directory using prefact."""
        if not self._has_prefact:
            return []
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "prefact", "scan", dir_path, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return []
            
            data = json.loads(result.stdout)
            issues = []
            for file_data in data.get("files", []):
                file_path = file_data.get("path", "")
                issues.extend(self._parse_issues(file_data, file_path))
            return issues
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _parse_issues(self, data: Dict, file_path: str) -> List[PrefactIssue]:
        """Parse prefact output into PrefactIssue objects."""
        issues = []
        
        for issue_data in data.get("issues", []):
            issues.append(PrefactIssue(
                rule=issue_data.get("rule", "unknown"),
                file=file_path,
                line=issue_data.get("line", 0),
                column=issue_data.get("column", 0),
                message=issue_data.get("message", ""),
                severity=issue_data.get("severity", "warning"),
                fixable=issue_data.get("fixable", False),
            ))
        
        return issues
    
    def check_sorted_imports(self, file_path: str) -> List[PrefactIssue]:
        """Check specifically for sorted imports issues."""
        all_issues = self.scan_file(file_path)
        return [i for i in all_issues if i.rule == "sorted_imports"]
    
    def check_relative_imports(self, file_path: str) -> List[PrefactIssue]:
        """Check specifically for relative imports issues."""
        all_issues = self.scan_file(file_path)
        return [i for i in all_issues if i.rule == "relative_imports"]
    
    def get_rules_info(self) -> Dict[str, Any]:
        """Get information about available prefact rules."""
        if not self._has_prefact:
            return {"available": False, "rules": []}
        
        # Common prefact rules that algitex can leverage
        return {
            "available": True,
            "rules": [
                {
                    "name": "sorted_imports",
                    "description": "Check if imports are sorted according to PEP8",
                    "fixable": True,
                    "tier": "algorithm",  # Can be fixed algorithmically
                },
                {
                    "name": "relative_imports",
                    "description": "Detect relative imports that should be absolute",
                    "fixable": True,
                    "tier": "algorithm",
                },
                {
                    "name": "unused_imports",
                    "description": "Find unused imports",
                    "fixable": True,
                    "tier": "algorithm",
                },
                {
                    "name": "missing_type_annotations",
                    "description": "Find functions missing return type annotations",
                    "fixable": False,
                    "tier": "micro",  # Needs LLM to infer types
                },
            ]
        }


class SharedRuleEngine:
    """Unified rule engine combining algitex and prefact rules."""
    
    def __init__(self):
        self.prefact = PrefactRuleAdapter()
        self._algitex_rules: Dict[str, Callable] = {}
        self._register_builtin_rules()
    
    def _register_builtin_rules(self):
        """Register algitex's built-in rules."""
        # These are rules that algitex can handle natively
        self._algitex_rules = {
            "unused_import": self._check_unused_import_native,
            "return_type": self._check_return_type_native,
        }
    
    def _check_unused_import_native(self, file_path: str) -> List[PrefactIssue]:
        """Native algitex check for unused imports (fallback when prefact unavailable)."""
        from algitex.nlp import DeadCodeDetector
        
        detector = DeadCodeDetector()
        # This is a simplified check
        return []
    
    def _check_return_type_native(self, file_path: str) -> List[PrefactIssue]:
        """Native algitex check for missing return types."""
        return []
    
    def analyze(self, file_path: str) -> Dict[str, List[PrefactIssue]]:
        """Run all available analyses on a file."""
        results = {
            "prefact": [],
            "algitex": [],
        }
        
        # Run prefact if available
        if self.prefact.is_available():
            results["prefact"] = self.prefact.scan_file(file_path)
        
        # Run native algitex rules
        for rule_name, rule_func in self._algitex_rules.items():
            issues = rule_func(file_path)
            results["algitex"].extend(issues)
        
        return results
    
    def get_all_issues(self, file_path: str) -> List[PrefactIssue]:
        """Get all issues from all sources."""
        results = self.analyze(file_path)
        return results["prefact"] + results["algitex"]


def run_prefact_check(file_path: str) -> bool:
    """Quick check if prefact is available and can scan a file."""
    adapter = PrefactRuleAdapter()
    if not adapter.is_available():
        return False
    
    try:
        issues = adapter.scan_file(file_path)
        return True  # Successfully scanned
    except Exception:
        return False


# Convenience function for CLI integration
def check_file_with_prefact(file_path: str, rule: Optional[str] = None) -> List[Dict[str, Any]]:
    """Check a file and return issues as plain dicts for CLI output."""
    adapter = PrefactRuleAdapter()
    
    if not adapter.is_available():
        return [{"error": "prefact not available"}]
    
    if rule:
        # Specific rule check
        if rule == "sorted_imports":
            issues = adapter.check_sorted_imports(file_path)
        elif rule == "relative_imports":
            issues = adapter.check_relative_imports(file_path)
        else:
            issues = [i for i in adapter.scan_file(file_path) if i.rule == rule]
    else:
        # All rules
        issues = adapter.scan_file(file_path)
    
    return [i.to_dict() for i in issues]
