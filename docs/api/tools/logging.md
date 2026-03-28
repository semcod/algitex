# `tools.logging`

Verbose logging utilities with decorators for algitex.

Usage:
    from algitex.tools.logging import log_calls, log_time, verbose
    
    @log_calls
    def my_function():
        pass
    
    @log_time
    def slow_function():
        pass
    
    @verbose
    def debug_function(ctx):
        pass


## Functions

### `set_verbose`

```python
def set_verbose(enabled: bool=True)
```

Enable or disable verbose logging globally.

### `log_calls`

```python
def log_calls(func: Callable) -> Callable
```

Decorator to log function calls with arguments and results.

### `log_time`

```python
def log_time(func: Callable) -> Callable
```

Decorator to log function execution time.

### `verbose`

```python
def verbose(func: Callable) -> Callable
```

Combined decorator: logs calls, time, and results.

### `format_args`

```python
def format_args(args, kwargs) -> str
```

Format arguments for display.

### `format_value`

```python
def format_value(value: Any) -> str
```

Format a value for display.

### `format_result`

```python
def format_result(result: Any) -> str
```

Format a result for display.

### `verbose_print`

```python
def verbose_print(msg: str, level: str='INFO')
```

Print verbose message if verbose mode is enabled.

## Classes

### `VerboseContext`

Context manager for verbose logging in a block.

**Methods:**

#### `__init__`

```python
def __init__(self, name: str)
```
