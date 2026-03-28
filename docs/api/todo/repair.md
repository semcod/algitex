# `todo.repair`

Per-type repair functions — each handles exactly one fix category.

Implements Strategy pattern: REPAIRERS dict maps category → repair function.


## Public API

```python
__all__ = ['REPAIRERS', 'repair_unused_import', 'repair_return_type', 'repair_fstring', 'repair_magic_number', 'repair_module_block']
```

## Functions

### `repair_unused_import`

```python
def repair_unused_import(path: Path, name: str, line_idx: int) -> bool
```

Remove unused import from file.
    
    Args:
        path: File to modify
        name: Import name to remove
        line_idx: 0-based line index
    
    Returns:
        True if fixed, False otherwise
    

### `repair_return_type`

```python
def repair_return_type(path: Path, suggested: str, line_idx: int) -> bool
```

Add return type annotation to function.
    
    Args:
        path: File to modify
        suggested: Return type annotation (e.g., "-> None")
        line_idx: 0-based line index
    
    Returns:
        True if fixed, False otherwise
    

### `repair_fstring`

```python
def repair_fstring(path: Path, _unused: str='', _unused2: int=0) -> bool
```

Convert string concatenations to f-strings using flynt or simple rewrite.
    
    Args:
        path: File to modify
        _unused: Unused parameter for API consistency
        _unused2: Unused parameter for API consistency
    
    Returns:
        True if any changes were made
    

### `repair_magic_number`

```python
def repair_magic_number(path: Path, number: int, line_idx: int, const_name: str | None=None) -> bool
```

Replace magic number with named constant.
    
    Args:
        path: File to modify
        number: Magic number to replace
        line_idx: 0-based line index
        const_name: Constant name (auto-detected if None)
    
    Returns:
        True if fixed, False otherwise
    

### `repair_module_block`

```python
def repair_module_block(path: Path, _unused: str='', _unused2: int=0) -> bool
```

Add standard module execution block.
    
    Args:
        path: File to modify
        _unused: Unused parameter for API consistency
        _unused2: Unused parameter for API consistency
    
    Returns:
        True if block was added
    
