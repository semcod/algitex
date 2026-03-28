# `tools.proxy`

Proxy wrapper — talk to proxym without learning its API.

Usage:
    from algitex.tools.proxy import Proxy

    proxy = Proxy()                          # auto-config from env
    reply = proxy.ask("Explain this code")   # routes to best model
    reply = proxy.ask("Fix typo", tier="cheap")
    print(proxy.budget())                    # remaining budget


## Classes

### `LLMResponse`

Simplified LLM response.

### `Proxy`

Simple wrapper around proxym gateway.

**Methods:**

#### `__init__`

```python
def __init__(self, config: Optional[ProxyConfig]=None)
```

#### `ask`

```python
def ask(self, prompt: str) -> LLMResponse
```

Send a prompt to the LLM via proxym.

        Args:
            prompt: Your question or instruction.
            tier: Force a tier (trivial/operational/standard/complex/deep).
            model: Force a specific model alias (cheap/balanced/premium/free/local).
            system: Optional system prompt.
            context: Inject code2llm delta context (X-Inject-Context).
            planfile_ref: Planfile ticket ref (X-Planfile-Ref: project/sprint/ticket).
            workflow_ref: Propact workflow ref (X-Workflow-Ref: workflow-id).
        

#### `budget`

```python
def budget(self) -> dict[str, Any]
```

Check remaining budget.

#### `models`

```python
def models(self) -> list[dict]
```

List available models.

#### `health`

```python
def health(self) -> bool
```

Check if proxym is running.

#### `close`

```python
def close(self) -> None
```
