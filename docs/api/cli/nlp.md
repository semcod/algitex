# `cli.nlp`

CLI commands for deterministic NLP refactors.

## Public API

```python
__all__ = ['nlp_app', 'nlp_dead_code', 'nlp_docstrings', 'nlp_duplicates', 'nlp_imports']
```

## Functions

### `nlp_docstrings`

```python
def nlp_docstrings(path: str=typer.Option('.', '--path', '-p', help='File or directory to inspect.'), fix: bool=typer.Option(False, '--fix/--dry-run', help='Write the shortened docstrings back.')) -> None
```

Shorten verbose docstrings using pattern-based rewriting.

### `nlp_imports`

```python
def nlp_imports(path: str=typer.Option('.', '--path', '-p', help='File or directory to inspect.'), sort: bool=typer.Option(False, '--sort', help='Write import ordering changes back to disk.')) -> None
```

Sort imports with isort when available, otherwise use a deterministic fallback.

### `nlp_dead_code`

```python
def nlp_dead_code(path: str=typer.Option('.', '--path', '-p', help='Project root to scan.')) -> None
```

Detect top-level functions that are never referenced.

### `nlp_duplicates`

```python
def nlp_duplicates(path: str=typer.Option('.', '--path', '-p', help='Project root to scan.'), min_lines: int=typer.Option(3, '--min-lines', min=2, help='Minimum duplicate block size.')) -> None
```

Detect repeated code blocks with a rolling hash window.
