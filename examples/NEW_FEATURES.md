# New Algitex Features

This document describes the new features added to algitex based on patterns found in examples 21 and 26.

## Overview

The following new modules have been added to simplify usage:

1. **Ollama Backend** (`algitex.tools.ollama`) - Native Ollama support
2. **Service Health Checker** (`algitex.tools.services`) - Unified service monitoring
3. **AutoFix** (`algitex.tools.autofix`) - Automated code fixing from TODO items

## New Features in Project Class

### Service Management

```python
from algitex import Project

p = Project(".")

# Check all services
p.print_service_status()  # Pretty-print service status
status = p.check_services()  # Get detailed status

# Wait for service to be ready
p.ensure_service("ollama", timeout_seconds=60)
```

### Ollama Integration

```python
# Check Ollama status
status = p.check_ollama()
print(f"Models: {status['details']['models']}")

# List models
models = p.list_ollama_models()

# Pull a model
p.pull_ollama_model("qwen2.5-coder:7b")

# Generate code
code = p.generate_with_ollama(
    "Write a fibonacci function",
    system="You are a Python expert"
)
```

### AutoFix

```python
# Fix all issues
result = p.fix_issues(limit=5, backend="auto")

# Fix specific issue
p.fix_issue("TASK-001", backend="ollama")

# List TODO tasks
tasks = p.list_todo_tasks()
```

## Simplified Examples

### Example 21 - Aider CLI + Ollama

Original: 289 lines of complex code
Simplified: 50 lines using algitex

```python
from algitex import Project

p = Project(".")
p.print_service_status()
tasks = p.list_todo_tasks()
print(f"Found {len(tasks)} tasks")
```

### Example 26 - LiteLLM Proxy + Ollama

Original: 274 lines with manual HTTP requests
Simplified: 60 lines using algitex

```python
from algitex import Project

p = Project(".")
p.autofix.proxy_url = "http://localhost:4000"
result = p.fix_issues(backend="litellm-proxy")
```

### Example 27 - Unified AutoFix

New example demonstrating all features together:
- Service health checking
- Auto-fixing with multiple backends
- Ollama integration
- TODO management

## AutoFix Backends

The AutoFix module supports multiple backends:

1. **Ollama** - Direct local LLM usage
2. **LiteLLM Proxy** - Via OpenAI-compatible proxy
3. **Aider CLI** - Using aider command-line tool

Auto backend selection:
- Tries Ollama first (most private)
- Falls back to LiteLLM proxy
- Finally tries Aider CLI

## Usage Examples

### Quick Start

```bash
# 1. Create TODO issues
prefact -a

# 2. Fix with algitex (auto-selects best backend)
python -c "
from algitex import Project
p = Project('.')
p.fix_issues(limit=5)
"
```

### Advanced Usage

```python
from algitex import Project

# Initialize with custom TODO file
p = Project(".", todo_file="MY_TODO.md")

# Fix only specific file
p.fix_issues(filter_file="src/main.py", backend="ollama")

# Dry run to see what would be fixed
p.autofix.dry_run = True
p.fix_issues()

# Check services before starting
if not p.check_services()["ollama"]["healthy"]:
    print("Ollama not running!")
    exit(1)
```

## Benefits

1. **Simpler Code** - Examples reduced from ~200-300 lines to ~50-100 lines
2. **Unified Interface** - Single API for multiple backends
3. **Better Error Handling** - Graceful fallbacks and clear error messages
4. **Service Awareness** - Automatic service discovery and health checking
5. **Integration** - Seamless integration with existing algitex features

## Migration Guide

To migrate existing code:

1. Replace manual service checks with `p.check_services()`
2. Replace direct Ollama API calls with `p.ollama` or `p.generate_with_ollama()`
3. Replace TODO parsing with `p.autofix` or `p.list_todo_tasks()`
4. Use `p.fix_issues()` instead of manual fixing logic

See the simplified examples for complete migration examples.
