# `prefact_integration`

Integration between algitex and prefact for shared rule logic.

This module provides adapters to use prefact's rule engine within algitex,
enabling consistent code analysis across both tools.

Usage:
    from algitex.prefact_integration import PrefactRuleAdapter
    
    adapter = PrefactRuleAdapter()
    issues = adapter.check_sorted_imports("src/myfile.py")


## Functions

### `run_prefact_check`

```python
def run_prefact_check(file_path: str) -> bool
```

Quick check if prefact is available and can scan a file.

### `check_file_with_prefact`

```python
def check_file_with_prefact(file_path: str, rule: Optional[str]=None) -> List[Dict[str, Any]]
```

Check a file and return issues as plain dicts for CLI output.

## Classes

### `PrefactIssue`

Issue found by prefact rule.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

### `PrefactRuleAdapter`

Adapter to run prefact rules from algitex.

**Methods:**

#### `__init__`

```python
def __init__(self, prefact_path: Optional[str]=None)
```

#### `is_available`

```python
def is_available(self) -> bool
```

Check if prefact integration is available.

#### `scan_file`

```python
def scan_file(self, file_path: str) -> List[PrefactIssue]
```

Scan a single file using prefact.

#### `scan_directory`

```python
def scan_directory(self, dir_path: str) -> List[PrefactIssue]
```

Scan a directory using prefact.

#### `check_sorted_imports`

```python
def check_sorted_imports(self, file_path: str) -> List[PrefactIssue]
```

Check specifically for sorted imports issues.

#### `check_relative_imports`

```python
def check_relative_imports(self, file_path: str) -> List[PrefactIssue]
```

Check specifically for relative imports issues.

#### `get_rules_info`

```python
def get_rules_info(self) -> Dict[str, Any]
```

Get information about available prefact rules.

### `SharedRuleEngine`

Unified rule engine combining algitex and prefact rules.

**Methods:**

#### `__init__`

```python
def __init__(self)
```

#### `analyze`

```python
def analyze(self, file_path: str) -> Dict[str, List[PrefactIssue]]
```

Run all available analyses on a file.

#### `get_all_issues`

```python
def get_all_issues(self, file_path: str) -> List[PrefactIssue]
```

Get all issues from all sources.
