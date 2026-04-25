# `project`

Project — the single object you need to know.

Refactored: split into functional mixins to reduce complexity.

Expanded from wronai with:
- Progressive algorithmization (Loop)
- Propact workflow execution
- Planfile-aware proxy headers (X-Planfile-Ref, X-Workflow-Ref)
- Per-ticket cost ledger
- DSL rule extraction

Usage:
    from algitex import Project

    p = Project("./my-app")
    p.analyze()                     # code2llm + vallm + redup
    p.plan(sprints=2)               # generate strategy → tickets
    p.execute()                     # llx picks model, proxym routes
    p.run_workflow("refactor.md")   # execute Propact workflow
    p.algo.discover()               # start progressive algorithmization
    p.status()                      # health + tickets + budget + algo progress


## Public API

```python
__all__ = ['Project']
```

### `Project(ServiceMixin, AutoFixMixin, OllamaMixin, BatchMixin, BenchmarkMixin, IDEMixin, ConfigMixin, MCPMixin)`

One project, all tools, zero boilerplate.

**Methods:**

#### `__init__`

```python
def __init__(self, path: str='.', config: Optional[Config]=None)
```

#### `analyze`

```python
def analyze(self, full: bool=True) -> HealthReport
```

Analyze project health.

#### `plan`

```python
def plan(self, sprints: int=2, focus: str='complexity', auto_tickets: bool=True) -> dict
```

Generate a sprint plan from analysis results.

#### `execute`

```python
def execute(self, ticket_id: Optional[str]=None) -> dict
```

Execute work with planfile-aware headers and cost tracking.

#### `status`

```python
def status(self) -> dict
```

Full project status: health + tickets + budget + algo progress.

#### `run_workflow`

```python
def run_workflow(self, workflow_path: str) -> dict
```

Execute a Propact Markdown workflow.

#### `ask`

```python
def ask(self, prompt: str, **kwargs) -> str
```

Quick LLM query with planfile-aware routing.

#### `add_ticket`

```python
def add_ticket(self, title: str, **kwargs) -> Ticket
```

#### `generate_todo`

```python
def generate_todo(self, filename: str='TODO.md') -> dict
```

Generate TODO.md from analysis results.
        
        Creates a TODO.md file with code issues found during analysis.
        Uses the last analysis report if available, otherwise runs a new analysis.
        
        Args:
            filename: Name of the TODO file to create (default: TODO.md)
            
        Returns:
            dict with count of issues created and the filename
        
