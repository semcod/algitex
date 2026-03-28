# `shared_rules`

Shared rule interface for algitex-prefact integration.

This module defines the protocol/interface for rules that can be shared
between algitex and prefact, enabling consistent code analysis.


## Functions

### `get_registry`

```python
def get_registry() -> RuleRegistry
```

Get or create global rule registry.

### `reset_registry`

```python
def reset_registry() -> None
```

Reset the global registry (useful for testing).

## Classes

### `RuleContext`

Context for rule execution.

### `RuleViolation`

Single rule violation.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

### `FixStrategy(Protocol)`

Protocol for auto-fix implementations.

**Methods:**

#### `apply`

```python
def apply(self, source: str, violation: RuleViolation) -> Optional[str]
```

Apply fix to source code, return new source or None if failed.

#### `is_safe`

```python
def is_safe(self, source: str, violation: RuleViolation) -> bool
```

Check if fix can be safely applied without semantic changes.

### `SharedRule(ABC)`

Abstract base class for rules shared between algitex and prefact.

**Methods:**

#### `rule_id`

```python
def rule_id(self) -> str
```

Unique rule identifier (e.g., 'sorted_imports').

#### `description`

```python
def description(self) -> str
```

Human-readable description.

#### `tier`

```python
def tier(self) -> str
```

Execution tier: 'algorithm', 'micro', or 'big'.

#### `fixable`

```python
def fixable(self) -> bool
```

Whether this rule has an auto-fix implementation.

#### `severity`

```python
def severity(self) -> str
```

Default severity level.

#### `check`

```python
def check(self, context: RuleContext) -> List[RuleViolation]
```

Check source code for violations.

#### `fix`

```python
def fix(self, context: RuleContext, violation: RuleViolation) -> Optional[str]
```

Auto-fix a violation. Return new source or None.

### `SortedImportsRule(SharedRule)`

Rule: imports should be sorted (stdlib, third-party, local).

**Methods:**

#### `check`

```python
def check(self, context: RuleContext) -> List[RuleViolation]
```

Check if imports are sorted.

### `RelativeImportRule(SharedRule)`

Rule: prefer absolute imports over relative.

**Methods:**

#### `check`

```python
def check(self, context: RuleContext) -> List[RuleViolation]
```

Check for relative imports.

### `RuleRegistry`

Registry of shared rules.

**Methods:**

#### `__init__`

```python
def __init__(self)
```

#### `register`

```python
def register(self, rule: SharedRule) -> None
```

Register a rule.

#### `get`

```python
def get(self, rule_id: str) -> Optional[SharedRule]
```

Get a rule by ID.

#### `list_rules`

```python
def list_rules(self, tier: Optional[str]=None) -> List[SharedRule]
```

List all rules, optionally filtered by tier.

#### `check_file`

```python
def check_file(self, file_path: str, rule_ids: Optional[List[str]]=None) -> Dict[str, List[RuleViolation]]
```

Run rules against a file.
