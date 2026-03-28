# New Algitex Features

This document describes the new features added to algitex based on patterns found in examples 18, 21, 22, 23, 24, 25, and 26.

## Overview

The following new modules have been added to simplify usage:

1. **Ollama Backend** (`algitex.tools.ollama`) - Native Ollama support
2. **Service Health Checker** (`algitex.tools.services`) - Unified service monitoring
3. **AutoFix** (`algitex.tools.autofix`) - Automated code fixing from TODO items
4. **Batch Processing** (`algitex.tools.batch`) - Parallel file processing with rate limiting
5. **Model Benchmarking** (`algitex.tools.benchmark`) - Compare models on standardized tasks
6. **IDE Integration** (`algitex.tools.ide`) - Support for Claude Code, Aider, VS Code, etc.
7. **Configuration Management** (`algitex.tools.config`) - Generate and manage IDE/tool configs
8. **MCP Orchestration** (`algitex.tools.mcp`) - Manage multiple MCP services
9. **MicroTask** (`algitex.cli.microtask`) - Atomic micro-tasks pipeline for small LLMs
10. **NLP** (`algitex.cli.nlp`) - Deterministic NLP refactor helpers

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

# Generate TODO.md from analysis
result = p.generate_todo()  # Creates TODO.md with issues from analysis
print(f"Created {result['filename']} with {result['count']} issues")
```

### Batch Processing

```python
# Batch analyze files
result = p.batch_analyze(
    directory="src/",
    pattern="*.py",
    parallelism=8,
    rate_limit=5.0
)

# Create custom batch processor
def my_worker(item):
    # Process item
    return result

processor = p.create_batch_processor(
    worker_func=my_worker,
    parallelism=4,
    rate_limit=2.0
)
results = processor.process(items)
```

### Model Benchmarking

```python
# Benchmark models
results = p.benchmark_models(
    models=["qwen2.5-coder:7b", "llama3:8b"],
    tasks=["code_completion", "bug_fix"]
)

# Print results
p.print_benchmark_results(results, format="table")

# Add custom benchmark task
p.add_benchmark_task(
    "optimization",
    "Code Optimization",
    "Optimize this code...",
    ["faster", "efficient", "improved"]
)
```

### IDE Integration

```python
# Setup IDE tool
p.setup_ide("claude-code")  # or "aider", "vscode"

# Fix file with Claude Code
p.fix_with_claude("main.py", "Add type hints", model="qwen2.5-coder:7b")

# Fix file with Aider
p.fix_with_aider("utils.py", "Add error handling")

# Detect available editor
editor = p.detect_editor()

# Get IDE tool status
status = p.get_ide_status()
```

### Configuration Management

```python
# Setup all project configurations
p.setup_configs(tools=["vscode", "env", "docker"])

# Install Continue.dev config
p.install_continue_config(models=["qwen2.5-coder:7b"])

# Install VS Code settings
p.install_vscode_settings()

# Generate .env file
p.generate_env_file({
    "ollama": "http://localhost:11434",
    "litellm": "http://localhost:4000"
})
```

### MCP Service Orchestration

```python
# Start all MCP services
p.start_mcp_services()

# Wait for services to be ready
p.wait_for_mcp_ready(timeout=60)

# Check service status
p.print_mcp_status()

# Restart specific service
p.restart_mcp_service("aider")

# Generate MCP client config
p.generate_mcp_config()

# Stop all services
p.stop_mcp_services()
```

## Simplified Examples

### Example 21 - Aider CLI + Ollama

Original: 289 lines of complex code
Simplified: 15 lines using algitex

```python
from algitex import Project

p = Project(".")
p.print_service_status()
result = p.generate_todo()  # Creates TODO.md
p.fix_issues()  # Auto-fix all issues
```

### Example 22 - Claude Code + Ollama

Original: 181 lines with manual setup
Simplified: 60 lines using algitex

```python
from algitex import Project

p = Project(".")
p.setup_ide("claude-code")
p.fix_with_claude("file.py", "Add documentation")
```

### Example 24 - Batch Processing

Original: 289 lines with ThreadPoolExecutor
Simplified: 80 lines using algitex

```python
from algitex import Project

p = Project(".")
result = p.batch_analyze(".", "*.py", parallelism=8)
print(f"Processed {result['total']} files")
```

### Example 25 - Model Benchmarking

Original: 278 lines with manual scoring
Simplified: 90 lines using algitex

```python
from algitex import Project

p = Project(".")
results = p.benchmark_models(["model1", "model2"])
p.print_benchmark_results(results)
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

### Example 23 - Continue.dev + Ollama

Original: 177 lines with manual JSON generation
Simplified: 50 lines using algitex

```python
from algitex import Project

p = Project(".")
p.install_continue_config(models=["qwen2.5-coder:7b"])
```

### Example 28 - MCP Orchestration

New example demonstrating MCP service management:
- Start/stop multiple MCP services
- Dependency-aware startup
- Health checking and monitoring

```python
from algitex import Project

p = Project(".")
p.start_mcp_services()
p.wait_for_mcp_ready()
p.print_mcp_status()
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
4. **Claude Code** - Using anthropic-curl

Auto backend selection:
- Tries Ollama first (most private)
- Falls back to LiteLLM proxy
- Tries Claude Code if available
- Finally tries Aider CLI

## Batch Processing Features

- **Parallel execution** with configurable workers
- **Rate limiting** to avoid overwhelming services
- **Retry logic** with exponential backoff
- **Progress tracking** (tqdm optional)
- **Result persistence** to JSON files
- **Generic interface** works with any callable

## Benchmarking Features

- **Standardized tasks** for fair comparison
- **Quality scoring** based on expected keywords
- **Performance metrics** (time, tokens, throughput)
- **Multiple output formats** (table, summary, detailed)
- **Custom tasks** support
- **Results persistence** and loading

## IDE Integration Features

- **Multiple editors** supported (Claude Code, Aider, VS Code, Cursor)
- **Auto-configuration** of environment variables
- **Detection** of available editors
- **Quick fix commands** generation
- **Batch processing** integration

## Usage Examples

### Quick Start

```bash
# 1. Generate TODO from analysis
python -c "from algitex import Project; p = Project('.'); p.generate_todo()"

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

# Batch analyze with custom processor
def analyze_code(file_path):
    # Custom analysis logic
    return p.generate_with_ollama(f"Analyze: {file_path}")

processor = p.create_batch_processor(analyze_code, parallelism=8)
results = processor.process(file_list)

# Benchmark custom models
p.add_benchmark_task("my_task", "My Task", prompt, keywords)
results = p.benchmark_models(["model1", "model2"], ["my_task"])

# IDE integration
if p.detect_editor() == "claude-code":
    p.fix_with_claude("file.py", "Fix bug")
```

## Configuration Management Features

- **Continue.dev** - Automatic config generation with Ollama models
- **VS Code** - Settings, extensions, and workspace configuration
- **Environment files** - Generate .env with service URLs
- **Docker Compose** - Generate docker-compose.yml for services
- **Backup handling** - Automatic backup of existing configs

## MCP Orchestration Features

- **Service lifecycle** - Start, stop, restart services
- **Dependency management** - Services wait for dependencies
- **Health checking** - Monitor service health via endpoints
- **Graceful shutdown** - SIGTERM handling with timeout
- **Log collection** - Capture service logs
- **Config generation** - Generate MCP client configs

## Code Quality Improvements

The algitex library has been refactored for better maintainability:

### AutoFix Module Refactoring
- Large methods broken into focused helper functions
- `fix_with_aider()` split into: `_ensure_git_repo()`, `_build_aider_prompt()`, `_build_aider_command()`, `_run_aider_subprocess()`
- `fix_with_proxy()` split into: `_read_file_content()`, `_build_proxy_prompt()`, `_call_proxy_api()`, `_extract_code_from_response()`, `_write_fixed_file()`
- Improved error handling and code organization
- Better separation of concerns for easier testing

### Benefits
- **Testability** - Individual components can be unit tested
- **Maintainability** - Each function has a single responsibility
- **Readability** - Clear workflow and structure
- **Extensibility** - Easy to add new backends or features

## Benefits

1. **Simpler Code** - Examples reduced from ~200-300 lines to ~50-100 lines
2. **Unified Interface** - Single API for multiple backends
3. **Better Error Handling** - Graceful fallbacks and clear error messages
4. **Service Awareness** - Automatic service discovery and health checking
5. **Integration** - Seamless integration with existing algitex features
6. **Extensibility** - Easy to add new backends, tasks, and IDE tools
7. **Performance** - Optimized batch processing with rate limiting
8. **Flexibility** - Generic interfaces work with any LLM backend

## Migration Guide

To migrate existing code:

1. Replace manual service checks with `p.check_services()`
2. Replace direct Ollama API calls with `p.ollama` or `p.generate_with_ollama()`
3. Replace TODO parsing with `p.autofix` or `p.list_todo_tasks()`
4. Use `p.fix_issues()` instead of manual fixing logic
5. Replace ThreadPoolExecutor with `p.create_batch_processor()`
6. Use `p.benchmark_models()` for model comparison
7. Use IDE helpers instead of manual subprocess calls

See the simplified examples for complete migration examples.
