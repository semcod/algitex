# `workflows`

Pipeline — for users who want custom workflows.

Usage:
    from algitex import Pipeline

    result = (
        Pipeline("./my-app")
        .analyze()
        .create_tickets()
        .execute(max_tickets=5)
        .validate()
        .sync("github")
        .report()
    )


## Classes

### `Pipeline`

Composable workflow: chain steps fluently.

**Methods:**

#### `__init__`

```python
def __init__(self, path: str='.', config: Optional[Config]=None)
```

#### `analyze`

```python
def analyze(self, full: bool=True) -> Pipeline
```

Step: analyze project health.

#### `create_tickets`

```python
def create_tickets(self) -> Pipeline
```

Step: auto-create tickets from analysis.

#### `execute`

```python
def execute(self, max_tickets: int=10, tool: str='aider-mcp') -> Pipeline
```

Step: execute open tickets via Docker tool.

#### `validate`

```python
def validate(self) -> Pipeline
```

Step: multi-level validation (static + runtime + security).

#### `sync`

```python
def sync(self, backend: Optional[str]=None) -> Pipeline
```

Step: sync tickets to external system.

#### `report`

```python
def report(self) -> dict
```

Get pipeline results including telemetry.

#### `finish`

```python
def finish(self) -> Pipeline
```

Finalize pipeline run - save telemetry and push to observability.

### `TicketExecutor`

Handles ticket execution with Docker tools, telemetry, context, and feedback.

**Methods:**

#### `__init__`

```python
def __init__(self, docker_mgr: DockerToolManager, project: Project, telemetry: Telemetry, context_builder: ContextBuilder, feedback_controller: FeedbackController)
```

#### `execute_tickets`

```python
def execute_tickets(self, tool: str, max_tickets: int) -> dict
```

Execute tickets using the specified tool.

### `TicketValidator`

Multi-level validation: static analysis, runtime tests, security scanning.

**Methods:**

#### `__init__`

```python
def __init__(self, docker_mgr: DockerToolManager)
```

#### `validate_all`

```python
def validate_all(self) -> dict
```

Run all validation levels.
