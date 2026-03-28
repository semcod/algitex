# `nlp`

Deterministic NLP refactor helpers for algitex.

## Public API

```python
__all__ = ['DeadCodeDetector', 'DocstringChange', 'DocstringShortener', 'find_duplicate_blocks', 'sort_imports_in_path']
```

## Functions

### `sort_imports_in_path`

```python
def sort_imports_in_path(path: str | Path, apply: bool=True) -> dict[str, int]
```

Sort imports in a file or directory tree, preferring isort when available.

### `find_duplicate_blocks`

```python
def find_duplicate_blocks(project_path: str | Path, min_lines: int=3) -> list[dict[str, object]]
```

Find repeated code blocks with a rolling hash over line windows.

## Classes

### `DocstringChange`

Single docstring rewrite.

### `DocstringShortener`

Shorten verbose docstrings to one or two lines.

**Methods:**

#### `shorten`

```python
def shorten(self, docstring: str) -> str | None
```

Return a shorter version of a docstring or None if unchanged.

#### `fix_file`

```python
def fix_file(self, path: str | Path, apply: bool=True) -> list[dict[str, object]]
```

Shorten docstrings in a single Python file.

#### `fix_path`

```python
def fix_path(self, path: str | Path, apply: bool=True) -> list[dict[str, object]]
```

Shorten docstrings in a file or directory tree.

### `DeadCodeDetector`

Detect top-level functions that appear unused.

**Methods:**

#### `scan`

```python
def scan(self, project_path: str | Path) -> list[dict[str, object]]
```

Return a list of dead top-level functions.
