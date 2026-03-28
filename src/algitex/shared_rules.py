"""Shared rule interface for algitex-prefact integration.

This module defines the protocol/interface for rules that can be shared
between algitex and prefact, enabling consistent code analysis.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, Any
from pathlib import Path


@dataclass(frozen=True)
class RuleContext:
    """Context for rule execution."""
    file_path: str
    source_code: str
    ast_tree: Optional[Any] = None  # AST if available
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            object.__setattr__(self, 'config', {})


@dataclass(frozen=True)
class RuleViolation:
    """Single rule violation."""
    rule_id: str
    file: str
    line: int
    column: int
    message: str
    severity: str  # "error", "warning", "info"
    fix_available: bool
    fix_suggestion: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "severity": self.severity,
            "fix_available": self.fix_available,
            "fix_suggestion": self.fix_suggestion,
        }


class FixStrategy(Protocol):
    """Protocol for auto-fix implementations."""
    
    def apply(self, source: str, violation: RuleViolation) -> Optional[str]:
        """Apply fix to source code, return new source or None if failed."""
        ...
    
    def is_safe(self, source: str, violation: RuleViolation) -> bool:
        """Check if fix can be safely applied without semantic changes."""
        ...


class SharedRule(ABC):
    """Abstract base class for rules shared between algitex and prefact."""
    
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique rule identifier (e.g., 'sorted_imports')."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def tier(self) -> str:
        """Execution tier: 'algorithm', 'micro', or 'big'."""
        raise NotImplementedError
    
    @property
    def fixable(self) -> bool:
        """Whether this rule has an auto-fix implementation."""
        return False
    
    @property
    def severity(self) -> str:
        """Default severity level."""
        return "warning"
    
    @abstractmethod
    def check(self, context: RuleContext) -> List[RuleViolation]:
        """Check source code for violations."""
        raise NotImplementedError
    
    def fix(self, context: RuleContext, violation: RuleViolation) -> Optional[str]:
        """Auto-fix a violation. Return new source or None."""
        if not self.fixable:
            return None
        return self._apply_fix(context, violation)
    
    def _apply_fix(self, context: RuleContext, violation: RuleViolation) -> Optional[str]:
        """Override to implement auto-fix."""
        return None


class SortedImportsRule(SharedRule):
    """Rule: imports should be sorted (stdlib, third-party, local)."""
    
    rule_id = "sorted_imports"
    description = "Imports should be sorted according to PEP8"
    tier = "algorithm"
    fixable = True
    severity = "warning"
    
    def check(self, context: RuleContext) -> List[RuleViolation]:
        """Check if imports are sorted."""
        from ast import parse, Import, ImportFrom
        
        violations = []
        try:
            tree = parse(context.source_code)
        except SyntaxError:
            return violations
        
        imports = []
        for node in tree.body:
            if isinstance(node, (Import, ImportFrom)):
                imports.append((node.lineno, node))
        
        if len(imports) < 2:
            return violations
        
        # Check sorting
        prev_group = None
        for lineno, node in imports:
            if isinstance(node, Import):
                group = "stdlib"  # Simplified
            else:
                module = node.module or ""
                if module.startswith("."):
                    group = "local"
                elif module in ("os", "sys", "json", "pathlib", "typing"):
                    group = "stdlib"
                else:
                    group = "third_party"
            
            if prev_group and group < prev_group:
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    file=context.file_path,
                    line=lineno,
                    column=0,
                    message=f"Import group '{group}' should come before '{prev_group}'",
                    severity=self.severity,
                    fix_available=self.fixable,
                ))
            
            prev_group = group
        
        return violations
    
    def _apply_fix(self, context: RuleContext, violation: RuleViolation) -> Optional[str]:
        """Use isort to fix imports."""
        try:
            import isort
            return isort.code(context.source_code)
        except ImportError:
            return None


class RelativeImportRule(SharedRule):
    """Rule: prefer absolute imports over relative."""
    
    rule_id = "relative_imports"
    description = "Relative imports should be converted to absolute"
    tier = "algorithm"
    fixable = True
    severity = "warning"
    
    def check(self, context: RuleContext) -> List[RuleViolation]:
        """Check for relative imports."""
        from ast import parse, ImportFrom
        
        violations = []
        try:
            tree = parse(context.source_code)
        except SyntaxError:
            return violations
        
        for node in tree.body:
            if isinstance(node, ImportFrom) and node.level > 0:
                violations.append(RuleViolation(
                    rule_id=self.rule_id,
                    file=context.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Relative import 'from {'.' * node.level}{node.module or ''} ...' should be absolute",
                    severity=self.severity,
                    fix_available=self.fixable,
                ))
        
        return violations


class RuleRegistry:
    """Registry of shared rules."""
    
    def __init__(self):
        self._rules: Dict[str, SharedRule] = {}
    
    def register(self, rule: SharedRule) -> None:
        """Register a rule."""
        self._rules[rule.rule_id] = rule
    
    def get(self, rule_id: str) -> Optional[SharedRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)
    
    def list_rules(self, tier: Optional[str] = None) -> List[SharedRule]:
        """List all rules, optionally filtered by tier."""
        rules = list(self._rules.values())
        if tier:
            rules = [r for r in rules if r.tier == tier]
        return rules
    
    def check_file(self, file_path: str, rule_ids: Optional[List[str]] = None) -> Dict[str, List[RuleViolation]]:
        """Run rules against a file."""
        path = Path(file_path)
        if not path.exists():
            return {"error": [RuleViolation("file_not_found", file_path, 0, 0, "File not found", "error", False)]}
        
        source = path.read_text()
        context = RuleContext(file_path=str(path), source_code=source)
        
        results = {}
        rules_to_run = [self._rules[r] for r in rule_ids] if rule_ids else list(self._rules.values())
        
        for rule in rules_to_run:
            violations = rule.check(context)
            if violations:
                results[rule.rule_id] = violations
        
        return results


# Global registry instance
_registry: Optional[RuleRegistry] = None


def get_registry() -> RuleRegistry:
    """Get or create global rule registry."""
    global _registry
    if _registry is None:
        _registry = RuleRegistry()
        # Register built-in rules
        _registry.register(SortedImportsRule())
        _registry.register(RelativeImportRule())
    return _registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _registry
    _registry = None
