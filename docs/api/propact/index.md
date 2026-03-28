# `propact`

Propact Workflow Engine — execute Markdown with embedded actions.

Propact treats Markdown as a workflow format. Code blocks tagged with
`propact:rest`, `propact:shell`, `propact:mcp` are executable steps.

Usage:
    from algitex.propact import Workflow

    wf = Workflow("./refactor-v1.md")
    wf.validate()       # check syntax
    wf.execute()         # run all steps
    wf.status()          # step-by-step progress

Workflow format:
    # Fix Imports

    First, analyze the module structure.

    ```propact:shell
    code2llm ./src -f toon --json
    ```

    Then call the fix endpoint:

    ```propact:rest
    POST http://localhost:4000/v1/chat/completions
    {"model": "balanced", "messages": [{"role": "user", "content": "Fix imports"}]}
    ```

    Finally, validate:

    ```propact:shell
    vallm batch ./src --recursive
    ```


## Classes

### `WorkflowStep`

Single executable step in a Propact workflow.

**Methods:**

#### `to_dict`

```python
def to_dict(self) -> dict
```

### `WorkflowResult`

Result of workflow execution.

**Methods:**

#### `success`

```python
def success(self) -> bool
```

### `Workflow`

Parse and execute Propact Markdown workflows.

**Methods:**

#### `__init__`

```python
def __init__(self, path: str)
```

#### `parse`

```python
def parse(self) -> list[WorkflowStep]
```

Parse Markdown into executable steps.

#### `validate`

```python
def validate(self) -> list[str]
```

Check workflow for errors without executing.

#### `execute`

```python
def execute(self) -> WorkflowResult
```

Execute all steps in the workflow.

#### `status`

```python
def status(self) -> dict
```

Current workflow status.
