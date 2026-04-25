"""Example 44: Plugin System Architecture

Demonstrates algitex's extensible plugin system for adding
custom tools, backends, and workflow steps.

Run: python examples/44-plugin-system/main.py
"""

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class ToolPlugin(Protocol):
    """Protocol for tool plugins."""
    
    name: str
    version: str
    
    def execute(self, args: dict) -> dict:
        ...


@runtime_checkable
class BackendPlugin(Protocol):
    """Protocol for LLM backend plugins."""
    
    name: str
    supports_streaming: bool
    
    def generate(self, prompt: str, **kwargs) -> str:
        ...


def demo_plugin_architecture():
    """Show the plugin architecture design."""
    print("\n=== Plugin Architecture ===")
    
    architecture = """
    ┌─────────────────────────────────────────┐
    │           algitex Core                  │
    │  - Project, Loop, Workflow              │
    │  - CLI framework                        │
    │  - Event system                         │
    └─────────────────────────────────────────┘
                      │
           ┌──────────┼──────────┬──────────┐
           ▼          ▼          ▼          ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  Tools   │ │ Backends │ │  Hooks   │ │ Commands │
    │ Plugins  │ │ Plugins  │ │ Plugins  │ │ Plugins  │
    └──────────┘ └──────────┘ └──────────┘ └──────────┘
    
    Plugin types:
    • Tool: Add new algitex tools (like code2llm, vallm)
    • Backend: Add new LLM providers (Ollama, OpenAI, etc.)
    • Hook: Intercept and modify workflow execution
    • Command: Add new CLI subcommands
    """
    print(architecture)


def demo_builtin_plugins():
    """Show built-in plugins that come with algitex."""
    print("\n=== Built-in Plugins ===")
    
    plugins = [
        ("tools", "code2llm", "Static analysis", "Builtin"),
        ("tools", "vallm", "4-tier validation", "Builtin"),
        ("tools", "redup", "Duplicate detection", "Builtin"),
        ("tools", "proxym", "LLM proxy gateway", "Optional"),
        ("tools", "planfile", "Ticket management", "Optional"),
        ("backends", "ollama", "Local LLM inference", "Builtin"),
        ("backends", "openrouter", "Multi-provider routing", "Builtin"),
        ("backends", "aider", "Aider integration", "Optional"),
        ("commands", "todo", "TODO processing", "Builtin"),
        ("commands", "microtask", "Atomic tasks", "Builtin"),
        ("commands", "benchmark", "Performance testing", "Builtin"),
        ("commands", "dashboard", "Live monitoring", "Builtin"),
    ]
    
    print(f"\n{'Type':<12} {'Name':<15} {'Purpose':<25} {'Status':<10}")
    print("-" * 65)
    for ptype, name, purpose, status in plugins:
        print(f"{ptype:<12} {name:<15} {purpose:<25} {status:<10}")
    
    print("\n\nPlugin discovery:")
    print("  $ algitex tools          # List all tools")
    print("  $ algitex tools --json   # Export as JSON")


def demo_creating_tool_plugin():
    """Show how to create a custom tool plugin."""
    print("\n=== Creating a Tool Plugin ===")
    
    plugin_code = '''
    # my_tool_plugin.py
    from algitex.plugins import ToolPlugin, register
    
    class MyAnalyzer(ToolPlugin):
        name = "my-analyzer"
        version = "1.0.0"
        
        def execute(self, args: dict) -> dict:
            """Run custom analysis."""
            path = args.get("path", ".")
            
            # Your analysis logic here
            results = self._analyze(path)
            
            return {
                "tool": self.name,
                "files_analyzed": len(results),
                "issues": results
            }
        
        def _analyze(self, path: str) -> list:
            # Implementation
            return []
    
    # Register the plugin
    register(MyAnalyzer)
    '''
    
    print(plugin_code)
    
    print("\n\nInstallation:")
    print("  # Option 1: pip install")
    print("  pip install my-algitex-plugin")
    print("  ")
    print("  # Option 2: Local development")
    print("  mkdir -p ~/.algitex/plugins")
    print("  cp my_tool_plugin.py ~/.algitex/plugins/")
    print("  ")
    print("  # Option 3: Project-local")
    print("  cp my_tool_plugin.py ./.algitex/plugins/")


def demo_creating_backend_plugin():
    """Show how to create a custom backend plugin."""
    print("\n=== Creating a Backend Plugin ===")
    
    backend_code = '''
    # custom_backend.py
    from algitex.plugins import BackendPlugin, register
    import requests
    
    class CustomLLM(BackendPlugin):
        name = "custom-llm"
        supports_streaming = True
        
        def __init__(self, api_key: str = None, base_url: str = None):
            self.api_key = api_key
            self.base_url = base_url or "https://api.custom-llm.com"
        
        def generate(self, prompt: str, **kwargs) -> str:
            """Generate completion using custom LLM."""
            response = requests.post(
                f"{self.base_url}/v1/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "prompt": prompt,
                    "max_tokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7)
                }
            )
            return response.json()["text"]
    
    register(CustomLLM)
    '''
    
    print(backend_code)
    
    print("\n\nUsage:")
    print("  # Configure in algitex.yaml")
    print("  llm:")
    print("    backend: custom-llm")
    print("    api_key: ${CUSTOM_LLM_API_KEY}")
    print("    base_url: https://api.custom-llm.com")
    print("  ")
    print("  # Or via CLI")
    print("  algitex ask \"Hello\" --backend custom-llm")


def demo_hook_system():
    """Show the hook system for intercepting events."""
    print("\n=== Hook System ===")
    
    print("\nAvailable hooks:")
    
    hooks = [
        ("pre_analysis", "Before project analysis starts"),
        ("post_analysis", "After analysis completes"),
        ("pre_execute", "Before workflow execution"),
        ("post_execute", "After workflow execution"),
        ("on_ticket_create", "When a new ticket is created"),
        ("on_fix_applied", "When a fix is applied"),
        ("on_error", "When an error occurs"),
    ]
    
    for hook, description in hooks:
        print(f"  • {hook}: {description}")
    
    print("\n\nExample hook implementation:")
    hook_code = '''
    # notification_hook.py
    from algitex.plugins import register_hook
    import requests
    
    @register_hook("on_ticket_create")
    def notify_slack(ticket):
        """Send Slack notification when ticket created."""
        webhook_url = "https://hooks.slack.com/..."
        
        requests.post(webhook_url, json={
            "text": f"New ticket: {ticket.title}"
        })
    
    @register_hook("post_analysis")
    def log_metrics(results):
        """Send metrics to external system."""
        metrics = {
            "avg_cc": results.avg_cc,
            "critical_count": results.critical_count
        }
        # Send to Datadog, Prometheus, etc.
    '''
    print(hook_code)


def demo_plugin_configuration():
    """Show how plugins are configured."""
    print("\n=== Plugin Configuration ===")
    
    config = '''
    # algitex.yaml - Plugin configuration
    
    plugins:
      # Auto-discover from these paths
      search_paths:
        - ~/.algitex/plugins
        - ./.algitex/plugins
        - /usr/share/algitex/plugins
      
      # Explicitly load these plugins
      load:
        - my_analyzer.MyAnalyzer
        - custom_backend.CustomLLM
        - notification_hook
      
      # Plugin-specific settings
      my_analyzer:
        strict_mode: true
        max_files: 1000
      
      custom_backend:
        timeout: 30
        retry_attempts: 3
    
    # Tool-specific config (also plugin-based)
    tools:
      code2llm:
        exclude:
          - "*.test.py"
          - "venv/*"
      
      vallm:
        tiers:
          - syntax
          - types
          - runtime
          - security
    '''
    print(config)


def demo_plugin_marketplace():
    """Show concept of plugin marketplace."""
    print("\n=== Plugin Ecosystem ===")
    
    print("\nFinding plugins:")
    print("  # Search PyPI")
    print("  pip search algitex-plugin")
    print("  ")
    print("  # List community plugins")
    print("  algitex plugins list --community")
    print("  ")
    print("  # Official plugins")
    print("  algitex plugins list --official")
    
    print("\n\nPopular community plugins (example):")
    
    plugins = [
        ("algitex-plugin-github", "GitHub integration", "1.2k ★"),
        ("algitex-plugin-jira", "Jira ticket sync", "890 ★"),
        ("algitex-plugin-slack", "Slack notifications", "650 ★"),
        ("algitex-plugin-prometheus", "Metrics export", "520 ★"),
        ("algitex-plugin-gemini", "Google Gemini backend", "480 ★"),
        ("algitex-plugin-anthropic", "Claude backend", "1.1k ★"),
    ]
    
    print(f"\n{'Package':<30} {'Description':<25} {'Rating':<10}")
    print("-" * 70)
    for pkg, desc, stars in plugins:
        print(f"{pkg:<30} {desc:<25} {stars:<10}")
    
    print("\n\nInstalling a plugin:")
    print("  pip install algitex-plugin-github")
    print("  algitex plugins enable github")


def main():
    """Run all plugin system demos."""
    print("=" * 70)
    print("Example 44: Plugin System Architecture")
    print("=" * 70)
    
    demo_plugin_architecture()
    demo_builtin_plugins()
    demo_creating_tool_plugin()
    demo_creating_backend_plugin()
    demo_hook_system()
    demo_plugin_configuration()
    demo_plugin_marketplace()
    
    print("\n" + "=" * 70)
    print("Key Takeaway:")
    print("  Plugins extend algitex without modifying core.")
    print("  Tools, backends, hooks, and commands are all pluggable.")
    print("=" * 70)


if __name__ == "__main__":
    main()
