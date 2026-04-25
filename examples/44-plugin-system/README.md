# Example 44: Plugin System Architecture

Demonstrates algitex's extensible plugin system for adding custom tools, backends, and workflow steps.

## Running

```bash
cd examples/44-plugin-system
make run
```

## Plugin Types

| Type | Purpose | Example |
|------|---------|---------|
| Tool | Add analysis tools | code2llm, vallm |
| Backend | Add LLM providers | ollama, openrouter |
| Hook | Intercept events | Slack notifications |
| Command | Add CLI commands | todo, benchmark |

## Creating a Tool Plugin

```python
# my_plugin.py
from algitex.plugins import ToolPlugin, register

class MyAnalyzer(ToolPlugin):
    name = "my-analyzer"
    version = "1.0.0"
    
    def execute(self, args: dict) -> dict:
        path = args.get("path", ".")
        results = self._analyze(path)
        return {"tool": self.name, "issues": results}

register(MyAnalyzer)
```

## Creating a Backend Plugin

```python
from algitex.plugins import BackendPlugin, register

class CustomLLM(BackendPlugin):
    name = "custom-llm"
    supports_streaming = True
    
    def generate(self, prompt: str, **kwargs) -> str:
        # Call your LLM API
        return response

register(CustomLLM)
```

## Hook System

```python
from algitex.plugins import register_hook

@register_hook("on_ticket_create")
def notify_slack(ticket):
    # Send notification
    pass
```

## Available Hooks

- `pre_analysis` - Before analysis starts
- `post_analysis` - After analysis completes
- `pre_execute` - Before workflow execution
- `post_execute` - After workflow execution
- `on_ticket_create` - When ticket created
- `on_fix_applied` - When fix applied

## Configuration

```yaml
# algitex.yaml
plugins:
  search_paths:
    - ~/.algitex/plugins
  load:
    - my_analyzer.MyAnalyzer
  
  my_analyzer:
    strict_mode: true
```

## Built-in Plugins

```bash
# List all tools
algitex tools

# List community plugins
algitex plugins list --community
```

## Files

- `main.py` - Demonstration of plugin system
- `Makefile` - Standard run/test/clean targets
