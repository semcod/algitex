# `microtask.prompts`

Prompt templates for MicroTask execution.

## Public API

```python
__all__ = ['PromptBuilder', 'PROMPT_TEMPLATES', 'SYSTEM_PROMPTS']
```

## Classes

### `PromptBuilder`

Build compact chat prompts for local LLMs.

**Methods:**

#### `__init__`

```python
def __init__(self, model_map: Mapping[int, str] | None=None) -> None
```

#### `build`

```python
def build(self, task: MicroTask, **extra) -> dict[str, object]
```

Return Ollama-compatible chat payload for a task.
