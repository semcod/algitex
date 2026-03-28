# `tools.feedback`

Feedback loop controller for algitex pipelines.

## Classes

### `FailureStrategy(Enum)`

### `FeedbackPolicy`

Policy configuration for feedback handling.

### `FeedbackController`

Orchestrate retry/replan/escalate decisions.

**Methods:**

#### `__init__`

```python
def __init__(self, policy: Optional[FeedbackPolicy]=None)
```

#### `on_validation_failure`

```python
def on_validation_failure(self, ticket: Dict[str, Any], validation_result: Dict[str, Any], context: Dict[str, Any]) -> Tuple[FailureStrategy, Dict[str, Any]]
```

Decide what to do when vallm validation fails.

        Returns:
            (strategy, params) — what Pipeline should do next.
        

#### `on_success`

```python
def on_success(self, ticket: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]
```

Reset attempt counter on success.

#### `needs_approval`

```python
def needs_approval(self, ticket: Dict[str, Any]) -> bool
```

Check if ticket requires human approval before execution.

### `FeedbackLoop`

Integrates feedback controller into the pipeline execution.

**Methods:**

#### `__init__`

```python
def __init__(self, controller: FeedbackController, tickets_manager, docker_mgr)
```

#### `execute_with_feedback`

```python
def execute_with_feedback(self, ticket: Dict[str, Any], tool: str='aider-mcp') -> Dict[str, Any]
```

Execute a ticket with automatic retry/replan/escalate logic.
