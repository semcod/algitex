<!-- code2docs:start --># algitex

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-302-green)
> **302** functions | **45** classes | **56** files | CC̄ = 3.4

> Auto-generated project documentation from source code analysis.

**Author:** Tom Sapletta  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/semcod/algitex](https://github.com/semcod/algitex)

## Installation

### From PyPI

```bash
pip install algitex
```

### From Source

```bash
git clone https://github.com/semcod/algitex
cd algitex
pip install -e .
```

### Optional Extras

```bash
pip install algitex[all]    # all optional features
pip install algitex[proxy]    # proxy features
pip install algitex[tickets]    # tickets features
pip install algitex[analysis]    # analysis features
pip install algitex[routing]    # routing features
pip install algitex[dev]    # development tools
```

## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
algitex ./my-project

# Only regenerate README
algitex ./my-project --readme-only

# Preview what would be generated (no file writes)
algitex ./my-project --dry-run

# Check documentation health
algitex check ./my-project

# Sync — regenerate only changed modules
algitex sync ./my-project
```

### Python API

```python
from algitex import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```

## Generated Output

When you run `algitex`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `algitex.yaml` in your project root (or run `algitex init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

algitex can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- algitex:start -->
# Project Title
... auto-generated content ...
<!-- algitex:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

```
algitex/
    ├── algitex/            ├── loop        ├── config        ├── cli            ├── cicd        ├── project            ├── proxy        ├── algo/            ├── analysis            ├── todo_parser        ├── tools/            ├── workspace            ├── telemetry            ├── context            ├── tickets            ├── docker            ├── todo_executor            ├── workflow            ├── todo_runner            ├── pipeline        ├── main        ├── propact/        ├── main        ├── main        ├── main        ├── workflows/        ├── main        ├── main        ├── main        ├── main            ├── feedback        ├── main        ├── main        ├── main        ├── main        ├── main├── project        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── main        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── main        ├── main```

## API Overview

### Classes

- **`ProxyConfig`** — Proxym gateway settings.
- **`TicketConfig`** — Planfile ticket system settings.
- **`AnalysisConfig`** — Code analysis tool settings.
- **`Config`** — Unified config for the entire algitex stack.
- **`CICDGenerator`** — Generate CI/CD pipelines for algitex projects.
- **`Project`** — One project, all tools, zero boilerplate.
- **`LLMResponse`** — Simplified LLM response.
- **`Proxy`** — Simple wrapper around proxym gateway.
- **`TraceEntry`** — Single LLM interaction trace.
- **`Pattern`** — Extracted repeating pattern from traces.
- **`Rule`** — Deterministic replacement for an LLM pattern.
- **`LoopState`** — Current state of the progressive algorithmization loop.
- **`Loop`** — The progressive algorithmization engine.
- **`HealthReport`** — Combined analysis result from all tools.
- **`Analyzer`** — Unified interface for code analysis tools.
- **`CLIResult`** — —
- **`Task`** — Single todo task extracted from file.
- **`TodoParser`** — Parse todo lists from Markdown and text files.
- **`ToolStatus`** — —
- **`RepoConfig`** — Configuration for a single repository in the workspace.
- **`Workspace`** — Manage multiple repos as a single workspace.
- **`TraceSpan`** — Single operation span.
- **`Telemetry`** — Track costs, tokens, time across an algitex pipeline run.
- **`CodeContext`** — Assembled context for an LLM coding task.
- **`ContextBuilder`** — Build rich context for LLM coding tasks from .toon files + git + planfile.
- **`SemanticCache`** — Optional semantic caching using Qdrant for context retrieval.
- **`Ticket`** — A single work item.
- **`Tickets`** — Manage project tickets via planfile or local YAML.
- **`DockerTool`** — Single Docker-based tool declaration from docker-tools.yaml.
- **`RunningTool`** — A spawned Docker container with connection info.
- **`DockerToolManager`** — Spawn Docker containers, connect via MCP/REST, call tools, teardown.
- **`TaskResult`** — Result of executing a single task.
- **`TodoExecutor`** — Execute todo tasks using Docker MCP tools.
- **`TaskResult`** — Result of executing a single task.
- **`TodoRunner`** — Execute todo tasks using Docker MCP tools.
- **`WorkflowStep`** — Single executable step in a Propact workflow.
- **`WorkflowResult`** — Result of workflow execution.
- **`Workflow`** — Parse and execute Propact Markdown workflows.
- **`Pipeline`** — Composable workflow: chain steps fluently.
- **`TicketExecutor`** — Handles ticket execution with Docker tools, telemetry, context, and feedback.
- **`TicketValidator`** — Multi-level validation: static analysis, runtime tests, security scanning.
- **`FailureStrategy`** — —
- **`FeedbackPolicy`** — Policy configuration for feedback handling.
- **`FeedbackController`** — Orchestrate retry/replan/escalate decisions.
- **`FeedbackLoop`** — Integrates feedback controller into the pipeline execution.

### Functions

- `init(path)` — Initialize algitex for a project.
- `analyze(path, quick)` — Analyze project health.
- `plan(path, sprints, focus)` — Generate sprint plan with auto-tickets.
- `go(path, dry_run)` — Full pipeline: analyze → plan → execute → validate.
- `status(path)` — Show project status dashboard.
- `tools()` — Show available tools and their status.
- `ask(prompt, tier)` — Quick LLM query via proxym.
- `sync()` — Sync tickets to external backend.
- `ticket_add(title, priority, type)` — Add a new ticket.
- `ticket_list(status)` — List tickets.
- `ticket_board()` — Kanban board view.
- `algo_discover(path)` — Stage 1: Start trace collection from proxym.
- `algo_extract(path, min_freq)` — Stage 2: Extract repeating patterns from traces.
- `algo_rules(path, no_llm)` — Stage 3: Generate deterministic rules for top patterns.
- `algo_report(path)` — Show algorithmization progress.
- `workflow_run(path, dry_run)` — Execute a Propact Markdown workflow.
- `workflow_validate(path)` — Check a Propact workflow for errors.
- `docker_list()` — List available Docker tools from docker-tools.yaml.
- `docker_spawn(tool_name)` — Start a Docker tool container.
- `docker_call(tool_name, action, input_json)` — Call an MCP tool on a running Docker container.
- `docker_teardown(tool_name)` — Stop Docker tool containers.
- `docker_caps(tool_name)` — List MCP capabilities of a Docker tool.
- `todo_list(file)` — Parse and display todo tasks from a file.
- `todo_run(file, tool, dry_run, limit)` — Execute todo tasks via Docker MCP.
- `todo_fix(file, tool, task_id)` — Execute fix tasks (prefact-style) via Docker MCP.
- `init_ci_cd(project_path, platform)` — Initialize CI/CD for a project.
- `create_quality_gate_config(max_cc, require_tests, security_scan)` — Create a quality gate configuration.
- `discover_tools()` — Check which tools are available.
- `require_tool(name)` — Raise helpful error if a tool is missing.
- `get_tool_module(name)` — Import and return a tool module, or None if unavailable.
- `create_workspace_template(name, repos)` — Create a workspace configuration template.
- `init_workspace(name, config_path)` — Initialize a new workspace with template.
- `main()` — —
- `load_env()` — Load .env file if present.
- `check_api_keys()` — Check if required API keys are set.
- `demo_refactoring_examples()` — Show example refactoring operations that aider-mcp can perform.
- `demo_with_docker_tools()` — Demonstrate actual Docker tool usage if available.
- `main()` — —
- `basic_github_actions_example()` — Generate basic GitHub Actions workflow.
- `gitlab_ci_example()` — Generate GitLab CI configuration.
- `quality_gates_example()` — Example of configuring quality gates.
- `dockerfile_example()` — Generate Dockerfile for algitex project.
- `precommit_hooks_example()` — Generate pre-commit configuration.
- `complete_ci_cd_setup()` — Example of complete CI/CD setup.
- `multi_platform_ci_example()` — Example of multi-platform CI/CD.
- `cleanup_ci_projects()` — Clean up all sample CI projects.
- `load_env()` — Load .env file if present.
- `demo_docker_operations()` — Show example Docker operations.
- `demo_with_docker_tools()` — Demonstrate Docker tool usage if available.
- `load_env()` — Load .env file if present.
- `demo_validation_examples()` — Show example vallm validation operations.
- `demo_with_docker_tools()` — Demonstrate Docker tool usage if available.
- `load_env()` — Load .env file if present.
- `check_required_env()` — Check required environment variables.
- `show_workflow()` — Display the 7-step refactoring workflow.
- `demo_with_docker_tools()` — Demonstrate Docker tool usage if available.
- `show_cli_usage()` — Show CLI usage instructions.
- `main()` — —
- `main()` — —
- `load_env()` — Load .env file if present.
- `roo_code_config()` — Settings for Roo Code (VS Code extension).
- `cline_config()` — Settings for Cline (VS Code extension).
- `continuedev_config()` — ~/.continue/config.json for Continue.dev.
- `aider_env()` — Environment variables for Aider.
- `cursor_config()` — Settings for Cursor / Windsurf.
- `claude_code_env()` — Environment variables for Claude Code.
- `main()` — —
- `load_env()` — Load .env file if present.
- `check_github_token()` — Check if GitHub PAT is set.
- `demo_github_operations()` — Show example GitHub operations.
- `demo_with_docker_tools()` — Demonstrate Docker tool usage if available.
- `basic_telemetry_example()` — Basic telemetry tracking example.
- `context_manager_example()` — Using telemetry as a context manager.
- `multi_model_comparison()` — Compare costs across different models.
- `budget_tracking_example()` — Track spending against a budget.
- `basic_context_example()` — Basic context building example.
- `context_optimization_example()` — Example of optimizing context for different use cases.
- `semantic_search_example()` — Example of semantic search for related code (placeholder).
- `prompt_engineering_example()` — Example of how context improves prompt engineering.
- `cleanup_example_projects()` — Clean up example projects.
- `basic_feedback_example()` — Basic feedback controller example.
- `custom_policy_example()` — Example with custom feedback policy.
- `feedback_extraction_example()` — Example of extracting actionable feedback.
- `feedback_loop_simulation()` — Simulate complete feedback loop with mock execution.
- `escalation_scenarios()` — Different escalation scenarios.
- `cost_optimization_example()` — Example of optimizing costs with feedback policies.
- `load_env()` — Load .env file if present.
- `demo_filesystem_operations()` — Show example filesystem operations.
- `demo_with_docker_tools()` — Demonstrate Docker tool usage if available.
- `create_sample_workspace()` — Create a sample workspace configuration.
- `workspace_management_example()` — Example of workspace management operations.
- `cross_repo_analysis_example()` — Example of analyzing multiple repositories.
- `cross_repo_planning_example()` — Example of planning across repositories.
- `workspace_execution_example()` — Example of executing across the workspace.
- `advanced_workspace_features()` — Example of advanced workspace features.
- `cleanup_sample_workspace()` — Clean up the sample workspace.


## Project Structure

📄 `examples.01-quickstart.main` (1 functions)
📄 `examples.01-quickstart.run`
📄 `examples.02-algo-loop.main` (1 functions)
📄 `examples.02-algo-loop.run`
📄 `examples.03-pipeline.main` (1 functions)
📄 `examples.03-pipeline.run`
📄 `examples.04-ide-integration.main` (8 functions)
📄 `examples.04-ide-integration.run`
📄 `examples.05-cost-tracking.main` (1 functions)
📄 `examples.05-cost-tracking.run`
📄 `examples.06-telemetry.main` (4 functions)
📄 `examples.06-telemetry.run`
📄 `examples.07-context.main` (5 functions)
📄 `examples.07-context.run`
📄 `examples.08-feedback.main` (6 functions)
📄 `examples.08-feedback.run`
📄 `examples.09-workspace.main` (7 functions)
📄 `examples.09-workspace.run`
📄 `examples.10-cicd.main` (8 functions)
📄 `examples.10-cicd.run`
📄 `examples.11-aider-mcp.main` (4 functions)
📄 `examples.11-aider-mcp.run`
📄 `examples.12-filesystem-mcp.main` (3 functions)
📄 `examples.12-filesystem-mcp.run`
📄 `examples.13-vallm.main` (3 functions)
📄 `examples.13-vallm.run`
📄 `examples.14-docker-mcp.main` (3 functions)
📄 `examples.14-docker-mcp.run`
📄 `examples.15-github-mcp.main` (4 functions)
📄 `examples.15-github-mcp.run`
📄 `examples.17-docker-workflow.main` (5 functions)
📄 `examples.17-docker-workflow.run`
📄 `project`
📦 `src.algitex`
📦 `src.algitex.algo` (12 functions, 5 classes)
📄 `src.algitex.algo.loop`
📄 `src.algitex.cli` (25 functions)
📄 `src.algitex.config` (7 functions, 4 classes)
📄 `src.algitex.project` (12 functions, 1 classes)
📦 `src.algitex.propact` (12 functions, 3 classes)
📄 `src.algitex.propact.workflow`
📦 `src.algitex.tools` (4 functions, 1 classes)
📄 `src.algitex.tools.analysis` (8 functions, 3 classes)
📄 `src.algitex.tools.cicd` (11 functions, 1 classes)
📄 `src.algitex.tools.context` (14 functions, 3 classes)
📄 `src.algitex.tools.docker` (23 functions, 3 classes)
📄 `src.algitex.tools.feedback` (12 functions, 4 classes)
📄 `src.algitex.tools.proxy` (9 functions, 2 classes)
📄 `src.algitex.tools.telemetry` (9 functions, 2 classes)
📄 `src.algitex.tools.tickets` (11 functions, 2 classes)
📄 `src.algitex.tools.todo_executor` (12 functions, 2 classes)
📄 `src.algitex.tools.todo_parser` (8 functions, 2 classes)
📄 `src.algitex.tools.todo_runner` (13 functions, 2 classes)
📄 `src.algitex.tools.workspace` (17 functions, 2 classes)
📦 `src.algitex.workflows` (19 functions, 3 classes)
📄 `src.algitex.workflows.pipeline`

## Requirements

- Python >= >=3.10
- pyyaml >=6.0- httpx >=0.27- rich >=13.0- typer >=0.12- pydantic >=2.0

## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/semcod/algitex
cd algitex

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 📖 [Full Documentation](https://github.com/semcod/algitex/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/semcod/algitex/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/semcod/algitex/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/semcod/algitex/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](./docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](./docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](./docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](./docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](./docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](./docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](./docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](./docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](./CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->