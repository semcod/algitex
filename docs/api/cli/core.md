# `cli.core`

Core CLI commands for algitex.

## Functions

### `init`

```python
def init(path: str=typer.Argument('.', help='Project directory')) -> None
```

Initialize algitex for a project.

### `analyze`

```python
def analyze(path: str=typer.Option('.', '--path', '-p'), quick: bool=typer.Option(False, '--quick', '-q'))
```

Analyze project health.

### `plan`

```python
def plan(path: str=typer.Option('.', '--path', '-p'), sprints: int=typer.Option(2, '--sprints', '-s'), focus: str=typer.Option('complexity', '--focus', '-f'))
```

Generate sprint plan with auto-tickets.

### `go`

```python
def go(path: str=typer.Option('.', '--path', '-p'), dry_run: bool=typer.Option(False, '--dry-run'))
```

Full pipeline: analyze → plan → execute → validate.

### `status`

```python
def status(path: str=typer.Option('.', '--path', '-p'))
```

Show project status dashboard.

### `tools`

```python
def tools()
```

Show available tools and their status.

### `ask`

```python
def ask(prompt: str=typer.Argument(...), tier: Optional[str]=typer.Option(None, '--tier', '-t'))
```

Quick LLM query via proxym.

### `sync`

```python
def sync()
```

Sync tickets to external backend.
