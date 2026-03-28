# `tools.analysis`

Analysis wrapper — run code2llm, vallm, redup from one place.

Usage:
    from algitex.tools.analysis import Analyzer

    a = Analyzer("./my-project")
    report = a.health()        # quick health check
    report = a.full()          # all tools combined
    print(report.cc_avg)       # 3.5
    print(report.passed)       # True if meets targets


## Classes

### `HealthReport`

Combined analysis result from all tools.

**Methods:**

#### `passed`

```python
def passed(self) -> bool
```

Check if project meets quality targets.

#### `grade`

```python
def grade(self) -> str
```

#### `summary`

```python
def summary(self) -> str
```

### `Analyzer`

Unified interface for code analysis tools.

**Methods:**

#### `__init__`

```python
def __init__(self, project_path: str='.')
```

#### `health`

```python
def health(self) -> HealthReport
```

Quick health check using code2llm.

#### `full`

```python
def full(self) -> HealthReport
```

Full analysis: code2llm + vallm + redup.

### `CLIResult`
