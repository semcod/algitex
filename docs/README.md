<!-- code2docs:start --># algitex

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-1207-green)
> **1207** functions | **174** classes | **192** files | CC̄ = 3.5

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
    ├── fix_readme        ├── vallm_server        ├── vallm_mcp_server        ├── proxym_server    ├── generate_lib_docs        ├── planfile_mcp_server        ├── proxym_mcp_server        ├── code2llm_server        ├── code2llm_mcp_server        ├── aider_mcp_server        ├── project/        ├── cli/    ├── algitex/        ├── config        ├── metrics        ├── dashboard        ├── prefact_integration            ├── loop        ├── shared_rules        ├── nlp/        ├── benchmark            ├── ollama_cache            ├── config            ├── cicd            ├── proxy            ├── autofix/            ├── mcp        ├── algo/            ├── todo_parser            ├── docker_transport            ├── ollama            ├── parallel/            ├── workspace        ├── tools/            ├── docker            ├── telemetry            ├── ide            ├── context            ├── tickets            ├── todo_executor            ├── services            ├── logging            ├── todo_runner            ├── todo_actions            ├── todo_local            ├── feedback            ├── dashboard            ├── benchmark            ├── batch            ├── docker            ├── ticket            ├── microtask            ├── parallel            ├── metrics            ├── algo            ├── core            ├── benchmark            ├── workflow            ├── nlp            ├── workflow            ├── config            ├── mcp            ├── autofix            ├── ollama        ├── propact/            ├── ide            ├── services            ├── benchmark            ├── batch            ├── todo            ├── pipeline            ├── analysis        ├── todo/            ├── micro        ├── workflows/            ├── classify            ├── fixer            ├── tiering            ├── repair            ├── benchmark            ├── verify            ├── prompts            ├── verifier            ├── audit            ├── classifier        ├── microtask/            ├── slicer                ├── base            ├── hybrid                ├── aider_backend                ├── fallback_backend                ├── proxy_backend            ├── executor                ├── ollama_backend                ├── partitioner                ├── batch_logger                ├── executor                ├── batch_backend        ├── buggy_code        ├── main        ├── buggy_code        ├── main        ├── main                ├── extractor                ├── models        ├── main        ├── main        ├── parallel_multi_tool        ├── workspace_parallel        ├── parallel_refactoring        ├── parallel_real_world        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── file3        ├── main        ├── file2        ├── main        ├── file1        ├── buggy_code        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── main        ├── buggy_code        ├── main        ├── buggy_code        ├── main        ├── main        ├── buggy_code        ├── main        ├── main        ├── main        ├── main        ├── mcp_orchestrator        ├── main        ├── main        ├── main        ├── abpr_pipeline        ├── main        ├── main        ├── main                ├── main            ├── main            ├── calculator            ├── complex_module            ├── file3            ├── file2├── project        ├── run            ├── file1        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── main        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run            ├── app```

## API Overview

### Classes

- **`VallmServer`** — Validation server with multiple validation levels.
- **`ProxymServer`** — LLM proxy with budget tracking.
- **`Code2LLMServer`** — Code analysis server for LLM context generation.
- **`ProxyConfig`** — Proxym gateway settings.
- **`TicketConfig`** — Planfile ticket system settings.
- **`AnalysisConfig`** — Code analysis tool settings.
- **`Config`** — Unified config for the entire algitex stack.
- **`LLMCall`** — Single LLM call record.
- **`FixResult`** — Single fix execution record.
- **`MetricsCollector`** — Collect metrics during algitex operations.
- **`MetricsReporter`** — Generate reports and dashboards from metrics.
- **`TierState`** — State tracking for a single tier.
- **`CacheState`** — State tracking for cache metrics.
- **`LiveDashboard`** — Live Rich dashboard for monitoring algitex operations.
- **`SimpleProgressTracker`** — Simplified progress tracking without full dashboard.
- **`PrefactIssue`** — Issue found by prefact rule.
- **`PrefactRuleAdapter`** — Adapter to run prefact rules from algitex.
- **`SharedRuleEngine`** — Unified rule engine combining algitex and prefact rules.
- **`RuleContext`** — Context for rule execution.
- **`RuleViolation`** — Single rule violation.
- **`FixStrategy`** — Protocol for auto-fix implementations.
- **`SharedRule`** — Abstract base class for rules shared between algitex and prefact.
- **`SortedImportsRule`** — Rule: imports should be sorted (stdlib, third-party, local).
- **`RelativeImportRule`** — Rule: prefer absolute imports over relative.
- **`RuleRegistry`** — Registry of shared rules.
- **`DocstringChange`** — Single docstring rewrite.
- **`DocstringShortener`** — Shorten verbose docstrings to one or two lines.
- **`DeadCodeDetector`** — Detect top-level functions that appear unused.
- **`BenchmarkResult`** — Single benchmark run result.
- **`BenchmarkSuite`** — Collection of benchmark results.
- **`BenchmarkRunner`** — Main benchmark runner with memory tracking.
- **`CacheBenchmark`** — Benchmarks for LLM cache performance.
- **`TierBenchmark`** — Benchmarks for three-tier performance comparison.
- **`MemoryBenchmark`** — Memory profiling benchmarks.
- **`CacheEntry`** — Single cache entry with metadata.
- **`LLMCache`** — Disk-based cache for LLM responses.
- **`CachedOllamaClient`** — OllamaClient with automatic response caching.
- **`ConfigManager`** — Manages configuration files for various IDEs and tools.
- **`CICDGenerator`** — Generate CI/CD pipelines for algitex projects.
- **`LLMResponse`** — Simplified LLM response.
- **`Proxy`** — Simple wrapper around proxym gateway.
- **`MCPService`** — Definition of an MCP service.
- **`MCPOrchestrator`** — Orchestrates multiple MCP services.
- **`TraceEntry`** — Single LLM interaction trace.
- **`Pattern`** — Extracted repeating pattern from traces.
- **`Rule`** — Deterministic replacement for an LLM pattern.
- **`LoopState`** — Current state of the progressive algorithmization loop.
- **`Loop`** — The progressive algorithmization engine.
- **`Task`** — Single todo task extracted from file.
- **`TodoParser`** — Parse todo lists from Markdown and text files.
- **`StdioTransport`** — Transport layer for JSON-RPC over stdin/stdout communication.
- **`OllamaModel`** — Information about an Ollama model.
- **`OllamaResponse`** — Response from Ollama API.
- **`OllamaClient`** — Client for interacting with Ollama API.
- **`OllamaService`** — High-level service for Ollama operations.
- **`RepoConfig`** — Configuration for a single repository in the workspace.
- **`Workspace`** — Manage multiple repos as a single workspace.
- **`ToolStatus`** — —
- **`DockerTool`** — Single Docker-based tool declaration from docker-tools.yaml.
- **`RunningTool`** — A spawned Docker container with connection info.
- **`DockerToolManager`** — Spawn Docker containers, connect via MCP/REST, call tools, teardown.
- **`TraceSpan`** — Single operation span.
- **`Telemetry`** — Track costs, tokens, time across an algitex pipeline run.
- **`IDETool`** — IDE tool configuration.
- **`IDEHelper`** — Base class for IDE integrations.
- **`ClaudeCodeHelper`** — Helper for Claude Code (anthropic-curl) integration.
- **`AiderHelper`** — Helper for Aider integration.
- **`VSCodeHelper`** — Helper for VS Code integration.
- **`EditorIntegration`** — High-level editor integration manager.
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
- **`VerboseContext`** — Context manager for verbose logging in a block.
- **`TaskResult`** — Result of executing a single task.
- **`TodoRunner`** — Execute todo tasks using Docker MCP tools with local fallback.
- **`LocalTaskResult`** — Result of executing a single task locally.
- **`LocalExecutor`** — Execute simple code fixes locally without Docker.
- **`FailureStrategy`** — —
- **`FeedbackPolicy`** — Policy configuration for feedback handling.
- **`FeedbackController`** — Orchestrate retry/replan/escalate decisions.
- **`FeedbackLoop`** — Integrates feedback controller into the pipeline execution.
- **`Task`** — Benchmark task definition.
- **`TaskResult`** — Result for a single model on a single task.
- **`BenchmarkResults`** — Complete benchmark results.
- **`ModelBenchmark`** — Benchmark models on standardized tasks.
- **`BatchResult`** — Result from batch processing.
- **`BatchStats`** — Statistics for batch processing.
- **`BatchProcessor`** — Generic batch processor with rate limiting and retries.
- **`FileBatchProcessor`** — Specialized batch processor for files.
- **`ConfigMixin`** — Configuration management functionality for Project.
- **`MCPMixin`** — MCP service orchestration functionality for Project.
- **`AutoFixMixin`** — AutoFix integration functionality for Project.
- **`OllamaMixin`** — Ollama integration functionality for Project.
- **`WorkflowStep`** — Single executable step in a Propact workflow.
- **`WorkflowResult`** — Result of workflow execution.
- **`Workflow`** — Parse and execute Propact Markdown workflows.
- **`IDEMixin`** — IDE integration functionality for Project.
- **`ServiceMixin`** — Service management functionality for Project.
- **`BenchmarkMixin`** — Model benchmarking functionality for Project.
- **`BatchMixin`** — Batch processing functionality for Project.
- **`Project`** — One project, all tools, zero boilerplate.
- **`HealthReport`** — Combined analysis result from all tools.
- **`Analyzer`** — Unified interface for code analysis tools.
- **`CLIResult`** — —
- **`FunctionSnippet`** — Minimal source slice around a function or method.
- **`MicroFixResult`** — Result of a micro-LLM fix.
- **`FunctionExtractor`** — Extract a single function or method around a task line.
- **`MicroPromptBuilder`** — Build narrow prompts for micro-LLM fixes.
- **`MicroFixer`** — Execute micro-LLM fixes on a TODO file.
- **`Pipeline`** — Composable workflow: chain steps fluently.
- **`TicketExecutor`** — Handles ticket execution with Docker tools, telemetry, context, and feedback.
- **`TicketValidator`** — Multi-level validation: static analysis, runtime tests, security scanning.
- **`TaskTriage`** — Classification result for a single TODO task.
- **`TodoTask`** — Single TODO task.
- **`FixResult`** — Result of fixing a file.
- **`TierSummary`** — Aggregated classification summary for a TODO list.
- **`BenchmarkResult`** — Benchmark results for fix operations.
- **`VerifyResult`** — Result of TODO verification.
- **`TodoTask`** — Single TODO task entry.
- **`PromptBuilder`** — Build compact chat prompts for local LLMs.
- **`TodoTask`** — Single TODO task from prefact output.
- **`VerificationResult`** — Result of TODO verification.
- **`TodoVerifier`** — Verify which TODO tasks from prefact are still valid.
- **`AuditEntry`** — Single audit entry for an operation.
- **`ChangeRecord`** — Record of a single file change for rollback.
- **`AuditLogger`** — Comprehensive audit logging with rollback support.
- **`TaskType`** — Classification tiers for micro tasks.
- **`MicroTask`** — Atomic unit of work for a single file change.
- **`MicroTaskBatch`** — Tasks grouped by file for execution.
- **`ContextSlicer`** — Extract the smallest useful context for a micro task.
- **`FixResult`** — Result of fixing an issue.
- **`Task`** — Minimal task representation for backends.
- **`AutoFixBackend`** — Base class for autofix backends.
- **`HybridResult`** — Result of hybrid fix operation.
- **`RateLimiter`** — Token bucket rate limiter for LLM calls.
- **`LLMTask`** — Task for LLM-based fixing.
- **`HybridAutofix`** — Hybrid autofix: parallel mechanical + rate-limited parallel LLM.
- **`AiderBackend`** — Fix issues using Aider CLI.
- **`BackendStatus`** — Status of a backend.
- **`FallbackBackend`** — Backend with automatic failover to alternative LLM services.
- **`AutoFix`** — Automated code fixing using various backends.
- **`ProxyBackend`** — Fix issues using LiteLLM proxy.
- **`PhaseResult`** — Summary for a single execution phase.
- **`MicroTaskExecutor`** — Execute micro tasks in three tiers: algorithmic, small LLM, big LLM.
- **`OllamaBackend`** — Fix issues using Ollama local models.
- **`TaskPartitioner`** — Partition tickets into non-conflicting groups for parallel execution.
- **`BatchLogEntry`** — Single entry in batch log.
- **`BatchSessionLog`** — Complete log of batch session.
- **`BatchLogger`** — Logger for batch operations with markdown output.
- **`ParallelExecutor`** — Execute tickets in parallel using git worktrees + region locking.
- **`TaskGroup`** — Grupa podobnych zadań do batch fix.
- **`BatchFixBackend`** — Backend do optymalizacji fixów przez grupowanie.
- **`Manager`** — —
- **`RegionExtractor`** — Extract lockable AST regions from Python files using map.toon.
- **`RegionType`** — Types of code regions that can be locked.
- **`CodeRegion`** — An AST-level lockable region within a file.
- **`TaskAssignment`** — A ticket assigned to a specific agent with locked regions.
- **`MergeResult`** — Result of merging agent worktrees back to main.
- **`BadClass`** — —
- **`DataManager`** — —
- **`UserManager`** — Manages user operations.
- **`DataManager`** — —
- **`UserManager`** — Manage users.
- **`Handler`** — —

### Functions

- `fix_readme(path)` — Collapse repeated license and author lines in the project README.
- `validate_static(path)` — Run static analysis with ruff, mypy on the project.
- `validate_runtime(path)` — Run runtime tests with pytest.
- `validate_security(path)` — Run security scan with bandit.
- `validate_all(path)` — Run all validation levels: static, runtime, and security.
- `analyze_complexity(path)` — Analyze code complexity with radon.
- `calculate_quality_score(path)` — Calculate overall quality score combining validation and complexity.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `extract_docstring(node)` — Extract docstring from AST node.
- `get_function_signature(node)` — Build function signature string from AST node.
- `parse_file(filepath)` — Parse Python file and extract documentation.
- `generate_module_doc(module_name, module_path, parsed)` — Generate markdown documentation for a module.
- `scan_package(src_dir, output_dir)` — Scan package and generate markdown documentation.
- `generate_index(output_dir, modules)` — Generate index.md with module overview.
- `main()` — —
- `planfile_create_ticket(title, description, priority, tags)` — Create a new ticket.
- `planfile_list_tickets(status, priority)` — List all tickets with optional filtering.
- `planfile_update_ticket(ticket_id, status, resolution)` — Update ticket status or properties.
- `planfile_create_tickets_bulk(tickets)` — Create multiple tickets at once.
- `planfile_sprint_status()` — Get sprint status overview.
- `planfile_sync()` — Sync tickets with storage.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `count_tokens(text)` — Count tokens in text.
- `list_models()` — List available LLM models and their capabilities.
- `chat_completion(messages, model, temperature, max_tokens)` — Send chat completion request to LLM provider.
- `simple_prompt(prompt, model)` — Simple single-prompt completion.
- `get_budget_status()` — Get current budget/usage status (placeholder for budget tracking).
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `analyze_project(path)` — Analyze a Python project and return metrics.
- `generate_toon(path)` — Generate Toon notation report for a project.
- `generate_readme(path)` — Generate README.md content from code analysis.
- `evolution_export(path)` — Export evolution report with modules, dependencies, and hotspots.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `aider_ai_code(prompt, relative_editable_files, model)` — Edit code using AI via Aider.
- `aider_list_models()` — List available AI models for Aider.
- `aider_chat(message, context)` — Chat with Aider AI about code.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `get_metrics()` — Get or create global metrics collector.
- `reset_metrics()` — Reset global metrics.
- `show_quick_dashboard(duration)` — Show a quick demo dashboard for a specified duration.
- `run_prefact_check(file_path)` — Quick check if prefact is available and can scan a file.
- `check_file_with_prefact(file_path, rule)` — Check a file and return issues as plain dicts for CLI output.
- `get_registry()` — Get or create global rule registry.
- `reset_registry()` — Reset the global registry (useful for testing).
- `sort_imports_in_path(path, apply)` — Sort imports in a file or directory tree, preferring isort when available.
- `find_duplicate_blocks(project_path, min_lines)` — Find repeated code blocks with a rolling hash over line windows.
- `run_quick_benchmark()` — Run quick benchmark suite.
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
- `create_workspace_template(name, repos)` — Create a workspace configuration template.
- `init_workspace(name, config_path)` — Initialize a new workspace with template.
- `discover_tools()` — Check which tools are available.
- `require_tool(name)` — Raise helpful error if a tool is missing.
- `get_tool_module(name)` — Import and return a tool module, or None if unavailable.
- `set_verbose(enabled)` — Enable or disable verbose logging globally.
- `log_calls(func)` — Decorator to log function calls with arguments and results.
- `log_time(func)` — Decorator to log function execution time.
- `verbose(func)` — Combined decorator: logs calls, time, and results.
- `format_args(args, kwargs)` — Format arguments for display.
- `format_value(value)` — Format a value for display.
- `format_result(result)` — Format a result for display.
- `verbose_print(msg, level)` — Print verbose message if verbose mode is enabled.
- `nap_action(task)` — Generate nap action for automated code repair.
- `aider_action(task)` — Generate aider-mcp action for code tasks.
- `ollama_action(task)` — Generate ollama-mcp action for code fixing with local LLM.
- `filesystem_action(task)` — Generate filesystem-mcp action.
- `github_action(task)` — Generate github-mcp action.
- `get_action_handler(tool)` — Get the appropriate action handler for a tool.
- `determine_action(task, tool)` — Determine MCP action and arguments for the task.
- `dashboard_live(duration, refresh, demo)` — Launch live TUI dashboard for real-time monitoring.
- `dashboard_monitor(cache_dir, metrics_file)` — Monitor existing cache and metrics files.
- `dashboard_export(format, output, duration)` — Export dashboard data to file (JSON or Prometheus format).
- `docker_list()` — List available Docker tools from docker-tools.yaml.
- `docker_spawn(tool_name)` — Start a Docker tool container.
- `docker_call(tool_name, action, input_json)` — Call an MCP tool on a running Docker container.
- `docker_teardown(tool_name)` — Stop Docker tool containers.
- `docker_caps(tool_name)` — List MCP capabilities of a Docker tool.
- `ticket_add(title, priority, type)` — Add a new ticket.
- `ticket_list(status)` — List tickets.
- `ticket_board()` — Kanban board view.
- `microtask_classify(todo_path)` — Classify TODO items into atomic MicroTasks.
- `microtask_plan(todo_path)` — Show execution plan, tiers, and model hints.
- `microtask_run(todo_path, algo_only, tier, dry_run)` — Execute the three-phase microtask pipeline.
- `parallel(path, agents, tool, dry_run)` — Execute tickets in parallel with conflict-free coordination.
- `init_cmd(path)` — Initialize with markdown help.
- `metrics_show(storage, export)` — Show metrics dashboard.
- `metrics_clear(storage, cache_dir)` — Clear all metrics and cache.
- `metrics_cache(cache_dir, list_entries, clear)` — Manage LLM response cache.
- `metrics_compare(storage)` — Compare tier performance (algorithm vs micro vs big LLM).
- `algo_discover(path)` — Stage 1: Start trace collection from proxym.
- `algo_extract(path, min_freq)` — Stage 2: Extract repeating patterns from traces.
- `algo_rules(path, no_llm)` — Stage 3: Generate deterministic rules for top patterns.
- `algo_report(path)` — Show algorithmization progress.
- `init(path)` — Initialize algitex for a project.
- `analyze(path, quick)` — Analyze project health.
- `plan(path, sprints, focus)` — Generate sprint plan with auto-tickets.
- `go(path, dry_run)` — Full pipeline: analyze → plan → execute → validate.
- `status(path)` — Show project status dashboard.
- `tools()` — Show available tools and their status.
- `ask(prompt, tier)` — Quick LLM query via proxym.
- `sync()` — Sync tickets to external backend.
- `benchmark_cache(entries, lookups)` — Benchmark LLM cache performance.
- `benchmark_tiers()` — Benchmark all three tiers (algorithm, micro, big).
- `benchmark_memory(lines)` — Benchmark memory usage for large file processing.
- `benchmark_full(export, quick)` — Run full benchmark suite.
- `benchmark_quick()` — Quick benchmark (30 seconds).
- `workflow_run(path, dry_run)` — Execute a Propact Markdown workflow.
- `workflow_validate(path)` — Check a Propact workflow for errors.
- `nlp_docstrings(path, fix)` — Shorten verbose docstrings using pattern-based rewriting.
- `nlp_imports(path, sort)` — Sort imports with isort when available, otherwise use a deterministic fallback.
- `nlp_dead_code(path)` — Detect top-level functions that are never referenced.
- `nlp_duplicates(path, min_lines)` — Detect repeated code blocks with a rolling hash window.
- `todo_stats(file)` — Show tier and category stats for a TODO file.
- `todo_verify(file)` — Verify which TODO tasks are still valid vs already fixed.
- `todo_fix_parallel(file, workers, dry_run, category)` — Auto-fix mechanical TODO tasks in parallel.
- `todo_list(file)` — Parse and display todo tasks from a file.
- `todo_run(file, tool, dry_run, limit)` — Execute todo tasks via Docker MCP.
- `todo_fix(file, tool, task_id, limit)` — Execute fix tasks (prefact-style) via Docker MCP.
- `todo_benchmark(limit, file, workers, compare)` — Benchmark TODO fix performance.
- `todo_hybrid(file, backend, tool, workers)` — Autofix: LLM-based code fixes (use --hybrid for mechanical + LLM).
- `todo_batch(file, backend, model, batch_size)` — BatchFix: grupowanie i optymalizacja podobnych zadań.
- `todo_verify_prefact(file, prune)` — Verify TODO.md against actual code using prefact.
- `fix_todos(todo_path, workers, dry_run, category)` — Convenience wrapper for parallel_fix.
- `classify_message(message)` — Classify a TODO message using pattern dispatch table.
- `classify_task(task)` — Classify a task-like object.
- `parse_todo(todo_path)` — Parse TODO.md → list of tasks, filtering worktree duplicates.
- `fix_file(file_path, tasks, dry_run)` — Fix all tasks in a single file using strategy dispatch.
- `parallel_fix(todo_path, workers, dry_run, category_filter)` — Fix all TODO tasks in parallel, one worker per file.
- `mark_tasks_completed(todo_path, completed_tasks)` — Mark completed tasks in TODO.md by changing - [ ] to - [x].
- `parallel_fix_and_update(todo_path, workers, dry_run, category_filter)` — Fix tasks and update TODO.md to mark completed tasks.
- `summarise_tasks(tasks)` — Summarise a list of tasks by category and tier.
- `load_todo_tasks(todo_path)` — Parse TODO tasks from a file.
- `filter_tasks(tasks)` — Filter tasks by tier and/or category.
- `partition_tasks(tasks)` — Partition tasks by tier.
- `repair_unused_import(path, name, line_idx)` — Remove unused import from file.
- `repair_return_type(path, suggested, line_idx)` — Add return type annotation to function.
- `repair_fstring(path, _unused, _unused2)` — Convert string concatenations to f-strings using flynt or simple rewrite.
- `repair_magic_number(path, number, line_idx, const_name)` — Replace magic number with named constant.
- `repair_module_block(path, _unused, _unused2)` — Add standard module execution block.
- `benchmark_sequential(tasks, dry_run)` — Run sequential benchmark.
- `benchmark_parallel(tasks, workers, dry_run)` — Run parallel benchmark.
- `benchmark_fix(todo_path, limit, workers, dry_run)` — Run benchmark on TODO tasks.
- `compare_modes(todo_path, limit, workers, dry_run)` — Compare parallel vs sequential execution.
- `verify_todos(todo_path, project_path)` — Pipeline: scan → parse → diff → result.
- `prune_outdated_tasks(todo_path, result)` — Remove outdated tasks from TODO.md.
- `verify_todos(todo_path)` — Quick verification function.
- `classify_prefact_line(line, task_id, base_dir)` — Convert one prefact-style TODO line into a MicroTask.
- `classify_todo_file(path)` — Parse a TODO file and return the MicroTask view.
- `group_tasks_by_file(tasks)` — Group micro tasks by file path.
- `get_logger()` — Get current logger instance.
- `start_session(backend, batch_size, parallel)` — Start new logging session.
- `end_session()` — End session and save log.
- `calc(x, y, op)` — —
- `process(items)` — —
- `load(path)` — —
- `divide(a, b)` — —
- `main()` — —
- `calculate_statistics(data)` — Calculate basic statistics for a dataset.
- `find_user(users, name)` — Find user by name.
- `process_file(filename)` — Process a file.
- `divide_numbers(a, b)` — Divide two numbers.
- `get_config(key)` — Get config value.
- `complex_function(data)` — A complex function with multiple issues.
- `bad_error_handling()` — Function with bad error handling.
- `check_ollama()` — Check if Ollama is running.
- `list_models()` — List available local models.
- `generate_code(prompt, model)` — Generate code using local Ollama model.
- `analyze_code(code, model)` — Analyze code using local Ollama model.
- `demo_code_generation()` — Demo: Generate a function using local LLM.
- `demo_code_analysis()` — Demo: Analyze code using local LLM.
- `demo_cost_comparison()` — Demo: Compare local vs cloud costs.
- `main()` — —
- `main()` — —
- `basic_github_actions_example()` — Generate basic GitHub Actions workflow.
- `gitlab_ci_example()` — Generate GitLab CI configuration.
- `quality_gates_example()` — Example of configuring quality gates.
- `dockerfile_example()` — Generate Dockerfile for algitex project.
- `precommit_hooks_example()` — Generate pre-commit configuration.
- `complete_ci_cd_setup()` — Example of complete CI/CD setup.
- `multi_platform_ci_example()` — Example of multi-platform CI/CD.
- `cleanup_ci_projects()` — Clean up all sample CI projects.
- `create_sample_project()` — Create sample project with code to refactor.
- `demo_refactoring()` — Demonstrate real refactoring workflow.
- `main()` — —
- `main()` — —
- `main()` — —
- `setup_sample_project(base_dir)` — Create a sample project structure for demonstration.
- `main()` — Demonstrate parallel refactoring of a real-world project.
- `demo_batch_dry_run()` — Demonstracja trybu dry-run.
- `demo_batch_execute()` — Demonstracja trybu execute.
- `demo_custom_batch_size()` — Demonstracja niestandardowego rozmiaru batch.
- `demo_comparison()` — Porównanie podejść.
- `main()` — —
- `main()` — —
- `load_workspace_config()` — Load the workspace configuration.
- `main()` — Demonstrate workspace coordination across multiple repositories.
- `main()` — Demonstrate parallel execution with region-based coordination.
- `create_sample_docker_project()` — Create sample project with Dockerfile.
- `run_docker_command(cmd, cwd)` — Run Docker command and return result.
- `demo_docker_operations()` — Demonstrate real Docker operations.
- `create_sample_code()` — Create sample Python code with issues to validate.
- `run_local_validation(code_dir)` — Run local validation tools if available.
- `demo_validation()` — Demonstrate real code validation.
- `demo_benchmark_quick()` — Demo: Quick benchmark (30 seconds).
- `demo_benchmark_cache()` — Demo: Cache performance testing.
- `demo_benchmark_tiers()` — Demo: Tier throughput comparison.
- `demo_benchmark_memory()` — Demo: Memory profiling for large files.
- `demo_benchmark_full()` — Demo: Full benchmark suite with export.
- `main()` — Run all benchmark demos.
- `main()` — —
- `complex_logic(n)` — —
- `load_env()` — Load .env file if present.
- `check_required_env()` — Check required environment variables.
- `show_workflow()` — Display the 7-step refactoring workflow.
- `demo_with_docker_tools()` — Demonstrate Docker tool usage if available.
- `show_cli_usage()` — Show CLI usage instructions.
- `unused_imports()` — —
- `magic_numbers()` — —
- `no_error_handling()` — —
- `main()` — —
- `bad_function_1(x, y)` — —
- `bad_function_2(data)` — —
- `bad_function_3(a, b, c, d)` — —
- `calculate(x, y, operation)` — —
- `process_items(data)` — —
- `load_file(path)` — —
- `divide_numbers(a, b)` — —
- `main()` — —
- `load_env()` — Load .env file if present.
- `roo_code_config()` — Settings for Roo Code (VS Code extension).
- `cline_config()` — Settings for Cline (VS Code extension).
- `continuedev_config()` — ~/.continue/config.json for Continue.dev.
- `aider_env()` — Environment variables for Aider.
- `cursor_config()` — Settings for Cursor / Windsurf.
- `claude_code_env()` — Environment variables for Claude Code.
- `main()` — —
- `main()` — —
- `demo_dashboard_live()` — Demo: Live dashboard with auto-refresh.
- `demo_dashboard_monitor()` — Demo: Monitor existing cache and metrics.
- `demo_dashboard_export()` — Demo: Export metrics to various formats.
- `demo_dashboard_with_todo()` — Demo: Dashboard integration with TODO commands.
- `main()` — Run all dashboard demos.
- `main()` — —
- `demo_classify_module()` — Demo: Using algitex.todo.classify directly.
- `demo_repair_module()` — Demo: Using algitex.todo.repair directly.
- `demo_verify_module()` — Demo: Using algitex.todo.verify directly.
- `demo_combined_workflow()` — Demo: Combining all three modules.
- `main()` — Run all module demos.
- `create_sample_project()` — Create sample project for GitHub workflow.
- `demo_github_workflow()` — Demonstrate GitHub workflow.
- `main()` — Main demo function.
- `basic_telemetry_example()` — Basic telemetry tracking example.
- `context_manager_example()` — Using telemetry as a context manager.
- `multi_model_comparison()` — Compare costs across different models.
- `budget_tracking_example()` — Track spending against a budget.
- `fetch_user_data(user_id, db_connection)` — Fetch user data from database.
- `calculate_discount(price, user_type)` — Calculate discounted price.
- `log_activity(user_id, action)` — Log user activity.
- `parse_config(config_string)` — Parse configuration from string.
- `authenticate_user(username, password)` — Authenticate user.
- `get_stored_password(username)` — Get stored password (mock).
- `process_large_file(filepath)` — Process large file.
- `generate_report(data, format)` — Generate report in various formats.
- `cleanup_old_files(directory, days)` — Clean up old files.
- `main()` — —
- `calculate(x, y, operation)` — —
- `process_items(data)` — —
- `load_file(path)` — —
- `divide_numbers(a, b)` — —
- `demo_microtask_classify()` — Demo: Microtask classification.
- `demo_microtask_plan()` — Demo: Microtask planning.
- `demo_microtask_run()` — Demo: Microtask execution.
- `demo_workflow()` — Demo: Complete microtask workflow.
- `main()` — Run all microtask demos.
- `main()` — —
- `calculate_price(qty, price, discount)` — Calculate final price.
- `process_users(users)` — Process user list.
- `format_message(name, value)` — Format message string.
- `load_data(filename)` — Load data from file.
- `divide(a, b)` — Divide two numbers.
- `complex_function(data, threshold, multiplier, offset)` — Process data with many parameters.
- `bad_error_handling()` — Example of bad error handling.
- `main()` — —
- `demo_dry_run(todo_file)` — Demo: Dry run to preview what would be fixed.
- `demo_verify_first(todo_file)` — Demo: Verify TODO tasks before fixing.
- `demo_benchmark(todo_file)` — Demo: Benchmark performance.
- `demo_mechanical_only(todo_file)` — Demo: Fix only mechanical issues (fastest).
- `demo_full_hybrid(todo_file, workers, rate_limit)` — Demo: Full hybrid with LLM backend.
- `demo_ollama_local(todo_file)` — Demo: 100% offline with Ollama.
- `main()` — Main entry point for Hybrid AutoFix example.
- `demo_tier_algorithm()` — Demo: Algorithm tier (deterministic fixes).
- `demo_tier_micro()` — Demo: Micro tier (small LLM fixes).
- `demo_tier_big()` — Demo: Big tier (large LLM fixes).
- `demo_all_tiers()` — Demo: Running all three tiers.
- `demo_dashboard_integration()` — Demo: Dashboard with 3-tier system.
- `main()` — Run all 3-tier demos.
- `main()` — Demonstrate MCP service orchestration.
- `main()` — —
- `demo_dict_dispatch()` — Demo: Dict dispatch pattern from classify.py
- `demo_strategy_pattern()` — Demo: Strategy pattern from repair.py
- `demo_pipeline_pattern()` — Demo: Pipeline pattern from verify.py
- `demo_orchestrator_pattern()` — Demo: Orchestrator pattern from fixer.py
- `main()` — Run all Sprint 3 pattern demos.
- `basic_feedback_example()` — Basic feedback controller example.
- `custom_policy_example()` — Example with custom feedback policy.
- `feedback_extraction_example()` — Example of extracting actionable feedback.
- `feedback_loop_simulation()` — Simulate complete feedback loop with mock execution.
- `escalation_scenarios()` — Different escalation scenarios.
- `cost_optimization_example()` — Example of optimizing costs with feedback policies.
- `create_sample_files()` — Create sample files for demonstration.
- `demo_file_operations()` — Demonstrate real filesystem operations.
- `abpr_pipeline(project_path)` — ABPR loop: Execute → Trace → Conflict → Rule → Validate → Repeat.
- `main()` — Demonstrate ABPR pipeline: Execute → Trace → Conflict → Rule → Validate → Repeat.
- `check_services()` — Check if all MCP services are running.
- `main()` — —
- `basic_context_example()` — Basic context building example.
- `context_optimization_example()` — Example of optimizing context for different use cases.
- `semantic_search_example()` — Example of semantic search for related code (placeholder).
- `prompt_engineering_example()` — Example of how context improves prompt engineering.
- `cleanup_example_projects()` — Clean up example projects.
- `main()` — —
- `calculate(x, y)` — Calculate sum.
- `calc(a, b, op)` — —
- `process_data(data)` — Process data with nested logic.
- `calculate(x, y, operation)` — —
- `hello()` — —
- `connect()` — —
- `retry()` — —
- `calculate()` — —
- `greet(name)` — —
- `format_price(amount, currency)` — —
- `build_path(base, filename)` — —
- `create_sample_workspace()` — Create a sample workspace configuration.
- `workspace_management_example()` — Example of workspace management operations.
- `cross_repo_analysis_example()` — Example of analyzing multiple repositories.
- `cross_repo_planning_example()` — Example of planning across repositories.
- `workspace_execution_example()` — Example of executing across the workspace.
- `advanced_workspace_features()` — Example of advanced workspace features.
- `cleanup_sample_workspace()` — Clean up the sample workspace.


## Project Structure

📄 `docker.aider-mcp.aider_mcp_server` (5 functions)
📄 `docker.code2llm.code2llm_mcp_server` (9 functions)
📄 `docker.code2llm.code2llm_server` (9 functions, 1 classes)
📄 `docker.planfile-mcp.planfile_mcp_server` (10 functions)
📄 `docker.proxym.proxym_mcp_server` (10 functions)
📄 `docker.proxym.proxym_server` (7 functions, 1 classes)
📄 `docker.vallm.vallm_mcp_server` (8 functions)
📄 `docker.vallm.vallm_server` (9 functions, 1 classes)
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
📄 `examples.09-workspace.main` (11 functions)
📄 `examples.09-workspace.run`
📄 `examples.10-cicd.main` (8 functions)
📄 `examples.10-cicd.run`
📄 `examples.11-aider-mcp.main` (2 functions)
📄 `examples.11-aider-mcp.run`
📄 `examples.11-aider-mcp.sample_project.calculator` (1 functions)
📄 `examples.12-filesystem-mcp.main` (2 functions)
📄 `examples.12-filesystem-mcp.run`
📄 `examples.12-filesystem-mcp.sample_files.src.main` (1 functions)
📄 `examples.13-vallm.main` (3 functions)
📄 `examples.13-vallm.run`
📄 `examples.13-vallm.sample_code.complex_module` (2 functions)
📄 `examples.14-docker-mcp.main` (3 functions)
📄 `examples.14-docker-mcp.run`
📄 `examples.14-docker-mcp.sample_docker_project.app` (1 functions, 1 classes)
📄 `examples.15-github-mcp.main` (2 functions)
📄 `examples.15-github-mcp.run`
📄 `examples.15-github-mcp.sample_github_project.main` (1 functions)
📄 `examples.17-docker-workflow.main` (5 functions)
📄 `examples.17-docker-workflow.run`
📄 `examples.18-ollama-local.buggy_code` (7 functions)
📄 `examples.18-ollama-local.main` (8 functions)
📄 `examples.18-ollama-local.run`
📄 `examples.19-local-mcp-tools.main` (2 functions)
📄 `examples.19-local-mcp-tools.run`
📄 `examples.20-self-hosted-pipeline.buggy_code` (12 functions, 1 classes)
📄 `examples.20-self-hosted-pipeline.main` (1 functions)
📄 `examples.20-self-hosted-pipeline.run`
📄 `examples.21-aider-cli-ollama.buggy_code` (10 functions, 1 classes)
📄 `examples.21-aider-cli-ollama.main` (1 functions)
📄 `examples.21-aider-cli-ollama.run`
📄 `examples.22-claude-code-ollama.buggy_code` (6 functions, 1 classes)
📄 `examples.22-claude-code-ollama.main` (1 functions)
📄 `examples.22-claude-code-ollama.run`
📄 `examples.23-continue-dev-ollama.buggy_code` (6 functions, 1 classes)
📄 `examples.23-continue-dev-ollama.main` (1 functions)
📄 `examples.23-continue-dev-ollama.run`
📄 `examples.24-ollama-batch.file1` (3 functions)
📄 `examples.24-ollama-batch.file2` (3 functions)
📄 `examples.24-ollama-batch.file3` (3 functions, 1 classes)
📄 `examples.24-ollama-batch.main` (1 functions)
📄 `examples.24-ollama-batch.run`
📄 `examples.25-local-model-comparison.main` (1 functions)
📄 `examples.25-local-model-comparison.run`
📄 `examples.26-litellm-proxy-ollama.buggy_code` (6 functions, 1 classes)
📄 `examples.26-litellm-proxy-ollama.main` (1 functions)
📄 `examples.26-litellm-proxy-ollama.run`
📄 `examples.27-unified-autofix.main` (1 functions)
📄 `examples.28-mcp-orchestration.main` (1 functions)
📄 `examples.28-mcp-orchestration.mcp_orchestrator` (1 functions)
📄 `examples.30-parallel-execution.main` (1 functions)
📄 `examples.30-parallel-execution.parallel_multi_tool` (1 functions)
📄 `examples.30-parallel-execution.parallel_real_world` (2 functions)
📄 `examples.30-parallel-execution.parallel_refactoring` (1 functions)
📄 `examples.31-abpr-workflow.abpr_pipeline` (1 functions)
📄 `examples.31-abpr-workflow.main` (1 functions)
📄 `examples.32-workspace-coordination.main` (9 functions)
📄 `examples.32-workspace-coordination.workspace_parallel` (1 functions)
📄 `examples.33-hybrid-autofix.main` (10 functions)
📄 `examples.34-batch-fix.main` (5 functions)
📄 `examples.34-batch-fix.sample_code.file1` (3 functions)
📄 `examples.34-batch-fix.sample_code.file2` (3 functions)
📄 `examples.34-batch-fix.sample_code.file3` (1 functions)
📄 `examples.35-sprint3-patterns.main` (5 functions)
📄 `examples.36-dashboard.main` (5 functions)
📄 `examples.37-benchmarks.main` (6 functions)
📄 `examples.38-new-modules.main` (5 functions)
📄 `examples.39-microtask-pipeline.main` (5 functions)
📄 `examples.40-three-tier-autofix.main` (6 functions)
📄 `project`
📄 `scripts.fix_readme` (1 functions)
📄 `scripts.generate_lib_docs` (7 functions)
📦 `src.algitex`
📦 `src.algitex.algo` (12 functions, 5 classes)
📄 `src.algitex.algo.loop`
📄 `src.algitex.benchmark` (17 functions, 6 classes)
📦 `src.algitex.cli` (2 functions)
📄 `src.algitex.cli.algo` (4 functions)
📄 `src.algitex.cli.benchmark` (5 functions)
📄 `src.algitex.cli.core` (11 functions)
📄 `src.algitex.cli.dashboard` (3 functions)
📄 `src.algitex.cli.docker` (5 functions)
📄 `src.algitex.cli.metrics` (4 functions)
📄 `src.algitex.cli.microtask` (10 functions)
📄 `src.algitex.cli.nlp` (8 functions)
📄 `src.algitex.cli.parallel` (6 functions)
📄 `src.algitex.cli.ticket` (3 functions)
📄 `src.algitex.cli.todo` (21 functions)
📄 `src.algitex.cli.workflow` (2 functions)
📄 `src.algitex.config` (7 functions, 4 classes)
📄 `src.algitex.dashboard` (24 functions, 4 classes)
📄 `src.algitex.metrics` (15 functions, 4 classes)
📦 `src.algitex.microtask` (2 functions, 3 classes)
📄 `src.algitex.microtask.classifier` (8 functions)
📄 `src.algitex.microtask.executor` (29 functions, 2 classes)
📄 `src.algitex.microtask.prompts` (6 functions, 2 classes)
📄 `src.algitex.microtask.slicer` (7 functions, 1 classes)
📦 `src.algitex.nlp` (19 functions, 5 classes)
📄 `src.algitex.prefact_integration` (18 functions, 3 classes)
📦 `src.algitex.project` (22 functions, 1 classes)
📄 `src.algitex.project.autofix` (5 functions, 1 classes)
📄 `src.algitex.project.batch` (3 functions, 1 classes)
📄 `src.algitex.project.benchmark` (4 functions, 1 classes)
📄 `src.algitex.project.config` (5 functions, 1 classes)
📄 `src.algitex.project.ide` (6 functions, 1 classes)
📄 `src.algitex.project.mcp` (8 functions, 1 classes)
📄 `src.algitex.project.ollama` (5 functions, 1 classes)
📄 `src.algitex.project.services` (4 functions, 1 classes)
📦 `src.algitex.propact` (18 functions, 3 classes)
📄 `src.algitex.propact.workflow`
📄 `src.algitex.shared_rules` (18 functions, 7 classes)
📦 `src.algitex.todo` (1 functions)
📄 `src.algitex.todo.audit` (13 functions, 3 classes)
📄 `src.algitex.todo.benchmark` (6 functions, 1 classes)
📄 `src.algitex.todo.classify` (3 functions, 1 classes)
📄 `src.algitex.todo.fixer` (16 functions, 2 classes)
📄 `src.algitex.todo.hybrid` (10 functions, 4 classes)
📄 `src.algitex.todo.micro` (19 functions, 5 classes)
📄 `src.algitex.todo.repair` (7 functions)
📄 `src.algitex.todo.tiering` (8 functions, 1 classes)
📄 `src.algitex.todo.verifier` (8 functions, 3 classes)
📄 `src.algitex.todo.verify` (7 functions, 2 classes)
📦 `src.algitex.tools` (4 functions, 1 classes)
📄 `src.algitex.tools.analysis` (8 functions, 3 classes)
📦 `src.algitex.tools.autofix` (14 functions, 1 classes)
📄 `src.algitex.tools.autofix.aider_backend` (11 functions, 1 classes)
📄 `src.algitex.tools.autofix.base` (2 functions, 3 classes)
📄 `src.algitex.tools.autofix.batch_backend` (16 functions, 2 classes)
📄 `src.algitex.tools.autofix.batch_logger` (17 functions, 3 classes)
📄 `src.algitex.tools.autofix.fallback_backend` (7 functions, 2 classes)
📄 `src.algitex.tools.autofix.ollama_backend` (7 functions, 1 classes)
📄 `src.algitex.tools.autofix.proxy_backend` (12 functions, 1 classes)
📄 `src.algitex.tools.batch` (20 functions, 4 classes)
📄 `src.algitex.tools.benchmark` (19 functions, 4 classes)
📄 `src.algitex.tools.cicd` (11 functions, 1 classes)
📄 `src.algitex.tools.config` (16 functions, 1 classes)
📄 `src.algitex.tools.context` (14 functions, 3 classes)
📄 `src.algitex.tools.docker` (20 functions, 3 classes)
📄 `src.algitex.tools.docker_transport` (17 functions, 1 classes)
📄 `src.algitex.tools.feedback` (12 functions, 4 classes)
📄 `src.algitex.tools.ide` (22 functions, 6 classes)
📄 `src.algitex.tools.logging` (11 functions, 1 classes)
📄 `src.algitex.tools.mcp` (18 functions, 2 classes)
📄 `src.algitex.tools.ollama` (16 functions, 4 classes)
📄 `src.algitex.tools.ollama_cache` (14 functions, 3 classes)
📦 `src.algitex.tools.parallel`
📄 `src.algitex.tools.parallel.executor` (11 functions, 1 classes)
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
📄 `src.algitex.tools.todo_runner` (12 functions, 2 classes)
📄 `src.algitex.tools.workspace` (20 functions, 2 classes)
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