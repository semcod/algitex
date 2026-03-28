# `cli.workflow`

Workflow subcommands for algitex CLI.

## Functions

### `workflow_run`

```python
def workflow_run(path: str=typer.Argument(..., help='Path to .md workflow'), dry_run: bool=typer.Option(False, '--dry-run'))
```

Execute a Propact Markdown workflow.

### `workflow_validate`

```python
def workflow_validate(path: str=typer.Argument(...)) -> None
```

Check a Propact workflow for errors.
