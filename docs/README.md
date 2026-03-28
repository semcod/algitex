<!-- code2docs:start --># algitex

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-652-green)
> **652** functions | **105** classes | **153** files | CC̄ = 3.5

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
        ├── aider_mcp_server        ├── planfile_mcp_server        ├── vallm_server        ├── code2llm_mcp_server        ├── project/        ├── cli/            ├── loop    ├── algitex/            ├── config            ├── cicd        ├── config            ├── proxy            ├── autofix/            ├── docker_transport            ├── todo_parser        ├── algo/            ├── mcp            ├── analysis            ├── docker            ├── parallel/            ├── ollama        ├── tools/            ├── telemetry            ├── ide            ├── workspace            ├── context            ├── tickets            ├── todo_executor            ├── services            ├── todo_actions            ├── todo_local            ├── todo_runner            ├── docker            ├── parallel            ├── ticket            ├── batch            ├── algo            ├── benchmark            ├── feedback            ├── workflow            ├── workflow            ├── todo            ├── config            ├── mcp            ├── autofix            ├── ollama            ├── core            ├── services            ├── ide            ├── batch            ├── pipeline        ├── propact/        ├── todo/            ├── fixer            ├── benchmark            ├── verifier            ├── hybrid                ├── base                ├── aider_backend                ├── proxy_backend                ├── ollama_backend        ├── workflows/                ├── partitioner        ├── main                ├── executor        ├── main        ├── main                ├── extractor        ├── main        ├── workspace_parallel        ├── parallel_multi_tool        ├── parallel_refactoring        ├── main        ├── main        ├── main        ├── file3        ├── main        ├── main        ├── main        ├── file2        ├── file1        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main                ├── models        ├── main        ├── mcp_orchestrator        ├── main        ├── abpr_pipeline                ├── main        ├── main            ├── main            ├── complex_module        ├── main├── project            ├── calculator        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── main        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run            ├── app```

## API Overview

### Classes

- **`VallmServer`** — Validation server with multiple validation levels.
- **`ConfigManager`** — Manages configuration files for various IDEs and tools.
- **`CICDGenerator`** — Generate CI/CD pipelines for algitex projects.
- **`ProxyConfig`** — Proxym gateway settings.
- **`TicketConfig`** — Planfile ticket system settings.
- **`AnalysisConfig`** — Code analysis tool settings.
- **`Config`** — Unified config for the entire algitex stack.
- **`LLMResponse`** — Simplified LLM response.
- **`Proxy`** — Simple wrapper around proxym gateway.
- **`StdioTransport`** — Transport layer for JSON-RPC over stdin/stdout communication.
- **`Task`** — Single todo task extracted from file.
- **`TodoParser`** — Parse todo lists from Markdown and text files.
- **`TraceEntry`** — Single LLM interaction trace.
- **`Pattern`** — Extracted repeating pattern from traces.
- **`Rule`** — Deterministic replacement for an LLM pattern.
- **`LoopState`** — Current state of the progressive algorithmization loop.
- **`Loop`** — The progressive algorithmization engine.
- **`MCPService`** — Definition of an MCP service.
- **`MCPOrchestrator`** — Orchestrates multiple MCP services.
- **`HealthReport`** — Combined analysis result from all tools.
- **`Analyzer`** — Unified interface for code analysis tools.
- **`CLIResult`** — —
- **`DockerTool`** — Single Docker-based tool declaration from docker-tools.yaml.
- **`RunningTool`** — A spawned Docker container with connection info.
- **`DockerToolManager`** — Spawn Docker containers, connect via MCP/REST, call tools, teardown.
- **`OllamaModel`** — Information about an Ollama model.
- **`OllamaResponse`** — Response from Ollama API.
- **`OllamaClient`** — Client for interacting with Ollama API.
- **`OllamaService`** — High-level service for Ollama operations.
- **`ToolStatus`** — —
- **`TraceSpan`** — Single operation span.
- **`Telemetry`** — Track costs, tokens, time across an algitex pipeline run.
- **`IDETool`** — IDE tool configuration.
- **`IDEHelper`** — Base class for IDE integrations.
- **`ClaudeCodeHelper`** — Helper for Claude Code (anthropic-curl) integration.
- **`AiderHelper`** — Helper for Aider integration.
- **`VSCodeHelper`** — Helper for VS Code integration.
- **`EditorIntegration`** — High-level editor integration manager.
- **`RepoConfig`** — Configuration for a single repository in the workspace.
- **`Workspace`** — Manage multiple repos as a single workspace.
- **`CodeContext`** — Assembled context for an LLM coding task.
- **`ContextBuilder`** — Build rich context for LLM coding tasks from .toon files + git + planfile.
- **`SemanticCache`** — Optional semantic caching using Qdrant for context retrieval.
- **`Ticket`** — A single work item.
- **`Tickets`** — Manage project tickets via planfile or local YAML.
- **`TaskResult`** — Result of executing a single task.
- **`TodoExecutor`** — Execute todo tasks using Docker MCP tools.
- **`ServiceStatus`** — Status of a single service.
- **`ServiceChecker`** — Checker for various services used by algitex.
- **`ServiceDependency`** — Manage service dependencies and startup order.
- **`LocalTaskResult`** — Result of executing a single task locally.
- **`LocalExecutor`** — Execute simple code fixes locally without Docker.
- **`TaskResult`** — Result of executing a single task.
- **`TodoRunner`** — Execute todo tasks using Docker MCP tools with local fallback.
- **`BatchResult`** — Result from batch processing.
- **`BatchStats`** — Statistics for batch processing.
- **`BatchProcessor`** — Generic batch processor with rate limiting and retries.
- **`FileBatchProcessor`** — Specialized batch processor for files.
- **`Task`** — Benchmark task definition.
- **`TaskResult`** — Result for a single model on a single task.
- **`BenchmarkResults`** — Complete benchmark results.
- **`ModelBenchmark`** — Benchmark models on standardized tasks.
- **`FailureStrategy`** — —
- **`FeedbackPolicy`** — Policy configuration for feedback handling.
- **`FeedbackController`** — Orchestrate retry/replan/escalate decisions.
- **`FeedbackLoop`** — Integrates feedback controller into the pipeline execution.
- **`ConfigMixin`** — Configuration management functionality for Project.
- **`MCPMixin`** — MCP service orchestration functionality for Project.
- **`AutoFixMixin`** — AutoFix integration functionality for Project.
- **`OllamaMixin`** — Ollama integration functionality for Project.
- **`ServiceMixin`** — Service management functionality for Project.
- **`IDEMixin`** — IDE integration functionality for Project.
- **`BatchMixin`** — Batch processing functionality for Project.
- **`WorkflowStep`** — Single executable step in a Propact workflow.
- **`WorkflowResult`** — Result of workflow execution.
- **`Workflow`** — Parse and execute Propact Markdown workflows.
- **`TodoTask`** — Single TODO task.
- **`FixResult`** — Result of fixing a file.
- **`BenchmarkResult`** — Benchmark results for fix operations.
- **`TodoTask`** — Single TODO task from prefact output.
- **`VerificationResult`** — Result of TODO verification.
- **`TodoVerifier`** — Verify which TODO tasks from prefact are still valid.
- **`HybridResult`** — Result of hybrid fix operation.
- **`RateLimiter`** — Token bucket rate limiter for LLM calls.
- **`LLMTask`** — Task for LLM-based fixing.
- **`HybridAutofix`** — Hybrid autofix: parallel mechanical + rate-limited parallel LLM.
- **`Project`** — One project, all tools, zero boilerplate.
- **`FixResult`** — Result of fixing an issue.
- **`Task`** — Minimal task representation for backends.
- **`AiderBackend`** — Fix issues using Aider CLI.
- **`ProxyBackend`** — Fix issues using LiteLLM proxy.
- **`OllamaBackend`** — Fix issues using Ollama local models.
- **`AutoFix`** — Automated code fixing using various backends.
- **`Pipeline`** — Composable workflow: chain steps fluently.
- **`TicketExecutor`** — Handles ticket execution with Docker tools, telemetry, context, and feedback.
- **`TicketValidator`** — Multi-level validation: static analysis, runtime tests, security scanning.
- **`TaskPartitioner`** — Partition tickets into non-conflicting groups for parallel execution.
- **`ParallelExecutor`** — Execute tickets in parallel using git worktrees + region locking.
- **`RegionExtractor`** — Extract lockable AST regions from Python files using map.toon.
- **`BadClass`** — —
- **`RegionType`** — Types of code regions that can be locked.
- **`CodeRegion`** — An AST-level lockable region within a file.
- **`TaskAssignment`** — A ticket assigned to a specific agent with locked regions.
- **`MergeResult`** — Result of merging agent worktrees back to main.
- **`Handler`** — —

### Functions

- `aider_ai_code(prompt, relative_editable_files, model)` — Edit code using AI via Aider.
- `aider_list_models()` — List available AI models for Aider.
- `aider_chat(message, context)` — Chat with Aider AI about code.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `planfile_create_ticket(title, description, priority, tags)` — Create a new ticket.
- `planfile_list_tickets(status, priority)` — List all tickets with optional filtering.
- `planfile_update_ticket(ticket_id, status, resolution)` — Update ticket status or properties.
- `planfile_create_tickets_bulk(tickets)` — Create multiple tickets at once.
- `planfile_sprint_status()` — Get sprint status overview.
- `planfile_sync()` — Sync tickets with storage.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `analyze_project(path)` — Analyze a Python project and return metrics.
- `generate_toon(path)` — Generate Toon notation report for a project.
- `generate_readme(path)` — Generate README.md content from code analysis.
- `evolution_export(path)` — Export evolution report with modules, dependencies, and hotspots.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `init_ci_cd(project_path, platform)` — Initialize CI/CD for a project.
- `create_quality_gate_config(max_cc, require_tests, security_scan)` — Create a quality gate configuration.
- `spawn_stdio(tool, env, running, save_state)` — docker run -i → persistent subprocess with stdin/stdout MCP.
- `spawn_sse(tool, env, running, save_state)` — docker run -d -p PORT → SSE/HTTP MCP endpoint.
- `spawn_rest(tool, env, running, save_state)` — docker run -d -p PORT → REST/OpenAI-compatible endpoint.
- `spawn_cli(tool, env, running, save_state)` — CLI tool — run on demand via docker exec, no persistent container.
- `call_stdio(rt, tool, args, get_client)` — Send JSON-RPC over stdin, read from stdout with timeout.
- `call_sse(rt, tool, args, get_client)` — POST to SSE/HTTP MCP endpoint.
- `call_rest(rt, tool, args, get_client)` — Call REST endpoint using action name as path.
- `call_cli(rt, cmd, args, get_client)` — docker exec on persistent container.
- `discover_tools()` — Check which tools are available.
- `require_tool(name)` — Raise helpful error if a tool is missing.
- `get_tool_module(name)` — Import and return a tool module, or None if unavailable.
- `create_workspace_template(name, repos)` — Create a workspace configuration template.
- `init_workspace(name, config_path)` — Initialize a new workspace with template.
- `nap_action(task)` — Generate nap action for automated code repair.
- `aider_action(task)` — Generate aider-mcp action for code tasks.
- `ollama_action(task)` — Generate ollama-mcp action for code fixing with local LLM.
- `filesystem_action(task)` — Generate filesystem-mcp action.
- `github_action(task)` — Generate github-mcp action.
- `get_action_handler(tool)` — Get the appropriate action handler for a tool.
- `determine_action(task, tool)` — Determine MCP action and arguments for the task.
- `docker_list()` — List available Docker tools from docker-tools.yaml.
- `docker_spawn(tool_name)` — Start a Docker tool container.
- `docker_call(tool_name, action, input_json)` — Call an MCP tool on a running Docker container.
- `docker_teardown(tool_name)` — Stop Docker tool containers.
- `docker_caps(tool_name)` — List MCP capabilities of a Docker tool.
- `parallel(path, agents, tool, dry_run)` — Execute tickets in parallel with conflict-free coordination.
- `ticket_add(title, priority, type)` — Add a new ticket.
- `ticket_list(status)` — List tickets.
- `ticket_board()` — Kanban board view.
- `algo_discover(path)` — Stage 1: Start trace collection from proxym.
- `algo_extract(path, min_freq)` — Stage 2: Extract repeating patterns from traces.
- `algo_rules(path, no_llm)` — Stage 3: Generate deterministic rules for top patterns.
- `algo_report(path)` — Show algorithmization progress.
- `workflow_run(path, dry_run)` — Execute a Propact Markdown workflow.
- `workflow_validate(path)` — Check a Propact workflow for errors.
- `todo_verify(file)` — Verify which TODO tasks are still valid vs already fixed.
- `todo_fix_parallel(file, workers, dry_run, category)` — Auto-fix mechanical TODO tasks in parallel.
- `todo_list(file)` — Parse and display todo tasks from a file.
- `todo_run(file, tool, dry_run, limit)` — Execute todo tasks via Docker MCP.
- `todo_fix(file, tool, task_id, limit)` — Execute fix tasks (prefact-style) via Docker MCP.
- `todo_benchmark(limit, file, workers, compare)` — Benchmark TODO fix performance.
- `todo_hybrid(file, backend, tool, workers)` — Hybrid autofix: parallel mechanical + rate-limited LLM fixes via proxy/tool.
- `init(path)` — Initialize algitex for a project.
- `analyze(path, quick)` — Analyze project health.
- `plan(path, sprints, focus)` — Generate sprint plan with auto-tickets.
- `go(path, dry_run)` — Full pipeline: analyze → plan → execute → validate.
- `status(path)` — Show project status dashboard.
- `tools()` — Show available tools and their status.
- `ask(prompt, tier)` — Quick LLM query via proxym.
- `sync()` — Sync tickets to external backend.
- `fix_todos(todo_path, workers, dry_run, category)` — Convenience wrapper for parallel_fix.
- `parse_todo(todo_path)` — Parse TODO.md → list of tasks, filtering out worktree duplicates.
- `fix_unused_import(path, task)` — Remove unused import line.
- `fix_fstring(path, task)` — Convert string concatenation to f-string (simple cases only).
- `fix_return_type(path, task)` — Add return type annotation based on suggestion.
- `fix_file(file_path, tasks, dry_run)` — Fix all tasks in a single file. Safe to run in parallel per-file.
- `parallel_fix(todo_path, workers, dry_run, category_filter)` — Fix all TODO tasks in parallel, one worker per file.
- `benchmark_sequential(tasks, dry_run)` — Run sequential benchmark.
- `benchmark_parallel(tasks, workers, dry_run)` — Run parallel benchmark.
- `benchmark_fix(todo_path, limit, workers, dry_run)` — Run benchmark on TODO tasks.
- `compare_modes(todo_path, limit, workers, dry_run)` — Compare parallel vs sequential execution.
- `verify_todos(todo_path)` — Quick verification function.
- `main()` — —
- `main()` — —
- `create_sample_project()` — Create sample project with code to refactor.
- `demo_refactoring()` — Demonstrate real refactoring workflow.
- `check_ollama()` — Check if Ollama is running.
- `list_models()` — List available local models.
- `generate_code(prompt, model)` — Generate code using local Ollama model.
- `analyze_code(code, model)` — Analyze code using local Ollama model.
- `demo_code_generation()` — Demo: Generate a function using local LLM.
- `demo_code_analysis()` — Demo: Analyze code using local LLM.
- `demo_cost_comparison()` — Demo: Compare local vs cloud costs.
- `main()` — —
- `main()` — —
- `main()` — —
- `main()` — —
- `main()` — —
- `main()` — Demonstrate parallel execution with region-based coordination.
- `load_workspace_config()` — Load the workspace configuration.
- `main()` — Demonstrate workspace coordination across multiple repositories.
- `complex_logic(n)` — —
- `main()` — —
- `main()` — —
- `load_env()` — Load .env file if present.
- `check_required_env()` — Check required environment variables.
- `show_workflow()` — Display the 7-step refactoring workflow.
- `demo_with_docker_tools()` — Demonstrate Docker tool usage if available.
- `show_cli_usage()` — Show CLI usage instructions.
- `unused_imports()` — —
- `magic_numbers()` — —
- `no_error_handling()` — —
- `bad_function_1(x, y)` — —
- `bad_function_2(data)` — —
- `bad_function_3(a, b, c, d)` — —
- `main()` — —
- `load_env()` — Load .env file if present.
- `roo_code_config()` — Settings for Roo Code (VS Code extension).
- `cline_config()` — Settings for Cline (VS Code extension).
- `continuedev_config()` — ~/.continue/config.json for Continue.dev.
- `aider_env()` — Environment variables for Aider.
- `cursor_config()` — Settings for Cursor / Windsurf.
- `claude_code_env()` — Environment variables for Claude Code.
- `main()` — —
- `main()` — Main demo function.
- `main()` — —
- `main()` — —
- `create_sample_project()` — Create sample project for GitHub workflow.
- `demo_github_workflow()` — Demonstrate GitHub workflow.
- `main()` — —
- `main()` — —
- `demo_dry_run(todo_file)` — Demo: Dry run to preview what would be fixed.
- `demo_verify_first(todo_file)` — Demo: Verify TODO tasks before fixing.
- `demo_benchmark(todo_file)` — Demo: Benchmark performance.
- `demo_mechanical_only(todo_file)` — Demo: Fix only mechanical issues (fastest).
- `demo_full_hybrid(todo_file, workers, rate_limit)` — Demo: Full hybrid with LLM backend.
- `demo_ollama_local(todo_file)` — Demo: 100% offline with Ollama.
- `main()` — —
- `main()` — —
- `main()` — Demonstrate MCP service orchestration.
- `abpr_pipeline(project_path)` — ABPR loop: Execute → Trace → Conflict → Rule → Validate → Repeat.
- `main()` — —
- `check_services()` — Check if all MCP services are running.
- `main()` — —
- `calculate(x, y)` — Calculate sum.
- `process_data(data)` — Process data with nested logic.
- `calculate(x, y, operation)` — —
- `basic_feedback_example()` — Basic feedback controller example.
- `custom_policy_example()` — Example with custom feedback policy.
- `feedback_extraction_example()` — Example of extracting actionable feedback.
- `feedback_loop_simulation()` — Simulate complete feedback loop with mock execution.
- `escalation_scenarios()` — Different escalation scenarios.
- `cost_optimization_example()` — Example of optimizing costs with feedback policies.
- `calc(a, b, op)` — —
- `main()` — Demonstrate ABPR pipeline: Execute → Trace → Conflict → Rule → Validate → Repeat.


## Project Structure

📄 `docker.aider-mcp.aider_mcp_server` (5 functions)
📄 `docker.code2llm.code2llm_mcp_server` (9 functions)
📄 `docker.planfile-mcp.planfile_mcp_server` (10 functions)
📄 `docker.vallm.vallm_server` (7 functions, 1 classes)
📄 `examples.01-quickstart.main` (1 functions)
📄 `examples.01-quickstart.run`
📄 `examples.02-algo-loop.main` (1 functions)
📄 `examples.02-algo-loop.run`
📄 `examples.03-pipeline.main` (1 functions)
📄 `examples.03-pipeline.run`
📄 `examples.04-ide-integration.main` (8 functions)
📄 `examples.04-ide-integration.run`
📄 `examples.05-cost-tracking.run`
📄 `examples.06-telemetry.run`
📄 `examples.07-context.run`
📄 `examples.08-feedback.main` (6 functions)
📄 `examples.08-feedback.run`
📄 `examples.09-workspace.run`
📄 `examples.10-cicd.run`
📄 `examples.11-aider-mcp.main` (2 functions)
📄 `examples.11-aider-mcp.run`
📄 `examples.11-aider-mcp.sample_project.calculator` (1 functions)
📄 `examples.12-filesystem-mcp.run`
📄 `examples.12-filesystem-mcp.sample_files.src.main` (1 functions)
📄 `examples.13-vallm.run`
📄 `examples.13-vallm.sample_code.complex_module` (2 functions)
📄 `examples.14-docker-mcp.run`
📄 `examples.14-docker-mcp.sample_docker_project.app` (1 functions, 1 classes)
📄 `examples.15-github-mcp.main` (2 functions)
📄 `examples.15-github-mcp.run`
📄 `examples.15-github-mcp.sample_github_project.main` (1 functions)
📄 `examples.17-docker-workflow.main` (5 functions)
📄 `examples.17-docker-workflow.run`
📄 `examples.18-ollama-local.main` (8 functions)
📄 `examples.18-ollama-local.run`
📄 `examples.19-local-mcp-tools.main` (2 functions)
📄 `examples.19-local-mcp-tools.run`
📄 `examples.20-self-hosted-pipeline.main` (1 functions)
📄 `examples.20-self-hosted-pipeline.run`
📄 `examples.21-aider-cli-ollama.main` (1 functions)
📄 `examples.21-aider-cli-ollama.run`
📄 `examples.22-claude-code-ollama.main` (1 functions)
📄 `examples.22-claude-code-ollama.run`
📄 `examples.23-continue-dev-ollama.main` (1 functions)
📄 `examples.23-continue-dev-ollama.run`
📄 `examples.24-ollama-batch.file1` (3 functions)
📄 `examples.24-ollama-batch.file2` (3 functions)
📄 `examples.24-ollama-batch.file3` (3 functions, 1 classes)
📄 `examples.24-ollama-batch.main` (1 functions)
📄 `examples.24-ollama-batch.run`
📄 `examples.25-local-model-comparison.main` (1 functions)
📄 `examples.25-local-model-comparison.run`
📄 `examples.26-litellm-proxy-ollama.main` (1 functions)
📄 `examples.26-litellm-proxy-ollama.run`
📄 `examples.27-unified-autofix.main` (1 functions)
📄 `examples.28-mcp-orchestration.main` (1 functions)
📄 `examples.28-mcp-orchestration.mcp_orchestrator` (1 functions)
📄 `examples.30-parallel-execution.main` (1 functions)
📄 `examples.30-parallel-execution.parallel_multi_tool` (1 functions)
📄 `examples.30-parallel-execution.parallel_refactoring` (1 functions)
📄 `examples.31-abpr-workflow.abpr_pipeline` (1 functions)
📄 `examples.31-abpr-workflow.main` (1 functions)
📄 `examples.32-workspace-coordination.main` (2 functions)
📄 `examples.32-workspace-coordination.workspace_parallel` (1 functions)
📄 `examples.33-hybrid-autofix.main` (7 functions)
📄 `project`
📦 `src.algitex`
📦 `src.algitex.algo` (12 functions, 5 classes)
📄 `src.algitex.algo.loop`
📦 `src.algitex.cli`
📄 `src.algitex.cli.algo` (4 functions)
📄 `src.algitex.cli.core` (8 functions)
📄 `src.algitex.cli.docker` (5 functions)
📄 `src.algitex.cli.parallel` (6 functions)
📄 `src.algitex.cli.ticket` (3 functions)
📄 `src.algitex.cli.todo` (7 functions)
📄 `src.algitex.cli.workflow` (2 functions)
📄 `src.algitex.config` (7 functions, 4 classes)
📦 `src.algitex.project` (16 functions, 1 classes)
📄 `src.algitex.project.autofix` (5 functions, 1 classes)
📄 `src.algitex.project.batch` (3 functions, 1 classes)
📄 `src.algitex.project.config` (5 functions, 1 classes)
📄 `src.algitex.project.ide` (6 functions, 1 classes)
📄 `src.algitex.project.mcp` (8 functions, 1 classes)
📄 `src.algitex.project.ollama` (5 functions, 1 classes)
📄 `src.algitex.project.services` (4 functions, 1 classes)
📦 `src.algitex.propact` (15 functions, 3 classes)
📄 `src.algitex.propact.workflow`
📦 `src.algitex.todo` (1 functions)
📄 `src.algitex.todo.benchmark` (6 functions, 1 classes)
📄 `src.algitex.todo.fixer` (12 functions, 2 classes)
📄 `src.algitex.todo.hybrid` (10 functions, 4 classes)
📄 `src.algitex.todo.verifier` (8 functions, 3 classes)
📦 `src.algitex.tools` (4 functions, 1 classes)
📄 `src.algitex.tools.analysis` (8 functions, 3 classes)
📦 `src.algitex.tools.autofix` (14 functions, 1 classes)
📄 `src.algitex.tools.autofix.aider_backend` (11 functions, 1 classes)
📄 `src.algitex.tools.autofix.base` (1 functions, 2 classes)
📄 `src.algitex.tools.autofix.ollama_backend` (6 functions, 1 classes)
📄 `src.algitex.tools.autofix.proxy_backend` (12 functions, 1 classes)
📄 `src.algitex.tools.batch` (20 functions, 4 classes)
📄 `src.algitex.tools.benchmark` (19 functions, 4 classes)
📄 `src.algitex.tools.cicd` (11 functions, 1 classes)
📄 `src.algitex.tools.config` (12 functions, 1 classes)
📄 `src.algitex.tools.context` (14 functions, 3 classes)
📄 `src.algitex.tools.docker` (15 functions, 3 classes)
📄 `src.algitex.tools.docker_transport` (14 functions, 1 classes)
📄 `src.algitex.tools.feedback` (12 functions, 4 classes)
📄 `src.algitex.tools.ide` (22 functions, 6 classes)
📄 `src.algitex.tools.mcp` (18 functions, 2 classes)
📄 `src.algitex.tools.ollama` (16 functions, 4 classes)
📦 `src.algitex.tools.parallel`
📄 `src.algitex.tools.parallel.executor` (10 functions, 1 classes)
📄 `src.algitex.tools.parallel.extractor` (7 functions, 1 classes)
📄 `src.algitex.tools.parallel.models` (1 functions, 4 classes)
📄 `src.algitex.tools.parallel.partitioner` (7 functions, 1 classes)
📄 `src.algitex.tools.proxy` (9 functions, 2 classes)
📄 `src.algitex.tools.services` (20 functions, 3 classes)
📄 `src.algitex.tools.telemetry` (9 functions, 2 classes)
📄 `src.algitex.tools.tickets` (11 functions, 2 classes)
📄 `src.algitex.tools.todo_actions` (7 functions)
📄 `src.algitex.tools.todo_executor` (12 functions, 2 classes)
📄 `src.algitex.tools.todo_local` (11 functions, 2 classes)
📄 `src.algitex.tools.todo_parser` (8 functions, 2 classes)
📄 `src.algitex.tools.todo_runner` (10 functions, 2 classes)
📄 `src.algitex.tools.workspace` (17 functions, 2 classes)
📦 `src.algitex.workflows` (19 functions, 3 classes)
📄 `src.algitex.workflows.pipeline`

## Requirements

- Python >= >=3.10
- pyyaml >=6.0- httpx >=0.27- rich >=13.0- typer >=0.12- pydantic >=2.0- tabulate >=0.9

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