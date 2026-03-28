# `tools.autofix.batch_backend`

BatchFix backend — grupowanie i optymalizacja podobnych zadań.

Zamiast wykonywać każde zadanie osobno (N API calls),
BatchFix grupuje podobne problemy i wykonuje je za jednym razem (1 API call).

Przykład:
    # 10 zadań "String concatenation" w różnych plikach
    # Normalnie: 10 × 30s = 300s
    # BatchFix: 1 × 60s = 60s (5× szybciej!)


## Classes

### `TaskGroup`

Grupa podobnych zadań do batch fix.

### `BatchFixBackend`

Backend do optymalizacji fixów przez grupowanie.
    
    Args:
        base_url: URL do Ollama (domyślnie localhost:11434)
        model: Nazwa modelu (domyślnie auto-detect)
        dry_run: Jeśli True, tylko symulacja
        timeout: Timeout w sekundach
    

**Methods:**

#### `__init__`

```python
def __init__(self, base_url: str='http://localhost:11434', model: Optional[str]=None, dry_run: bool=True, timeout: float=DEFAULT_TIMEOUT, enable_logging: bool=True)
```

#### `fix_batch`

```python
def fix_batch(self, tasks: list[Task], max_parallel: int=3) -> list[FixResult]
```

Wykonaj wszystkie zadania w batch z równoległym przetwarzaniem.
        
        Args:
            tasks: Lista zadań do wykonania
            max_parallel: Liczba równoległych grup (default: 3)
            
        Returns:
            Lista wyników dla każdego zadania
        
