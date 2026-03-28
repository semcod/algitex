# `cli.parallel`

CLI command for parallel execution of algitex tasks.

## Functions

### `parallel`

```python
def parallel(path: str=typer.Argument('.', help='Path to project'), agents: int=typer.Option(4, '--agents', '-n', help='Number of parallel agents'), tool: str=typer.Option('aider-mcp', '--tool', '-t', help='Docker tool to use'), dry_run: bool=typer.Option(False, '--dry-run', help='Show partition plan without executing'), verbose: bool=typer.Option(False, '--verbose', '-v', help='Verbose output'))
```

Execute tickets in parallel with conflict-free coordination.
