<!-- code2docs:start --># algitex

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-574-green)
> **574** functions | **68** classes | **110** files | CC̄ = 3.7

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
        ├── proxym_server        ├── vallm_mcp_server        ├── planfile_mcp_server        ├── code2llm_server        ├── aider_mcp_server        ├── code2llm_mcp_server        ├── vallm_server        ├── proxym_mcp_server    ├── algitex/            ├── loop        ├── cli        ├── config            ├── cicd            ├── proxy        ├── project        ├── algo/            ├── workspace            ├── todo_parser            ├── ollama        ├── tools/            ├── analysis            ├── docker            ├── telemetry            ├── autofix            ├── context            ├── tickets            ├── todo_executor            ├── services            ├── todo_local            ├── workflow            ├── todo_runner            ├── pipeline        ├── buggy_code        ├── propact/        ├── batch_fix        ├── buggy_code        ├── main        ├── main        ├── main        ├── workflows/            ├── feedback        ├── main        ├── main        ├── main        ├── main        ├── main        ├── file3        ├── main        ├── main        ├── file2        ├── main        ├── file1        ├── main        ├── main        ├── buggy_code        ├── main_simplified        ├── batch_analyze        ├── main        ├── buggy_code        ├── main        ├── main        ├── buggy_code        ├── auto_fix        ├── main        ├── buggy_code        ├── main        ├── main_simplified        ├── auto_fix_todos        ├── auto_fix_simplified        ├── main        ├── main        ├── main        ├── auto_fix        ├── main        ├── benchmark        ├── main                ├── main            ├── main        ├── buggy_code            ├── complex_module        ├── main├── project        ├── run        ├── run        ├── run        ├── run        ├── run            ├── calculator        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── run        ├── main            ├── app```

## API Overview

### Classes

- **`ProxymServer`** — LLM proxy with budget tracking.
- **`Code2LLMServer`** — Code analysis server for LLM context generation.
- **`VallmServer`** — Validation server with multiple validation levels.
- **`ProxyConfig`** — Proxym gateway settings.
- **`TicketConfig`** — Planfile ticket system settings.
- **`AnalysisConfig`** — Code analysis tool settings.
- **`Config`** — Unified config for the entire algitex stack.
- **`CICDGenerator`** — Generate CI/CD pipelines for algitex projects.
- **`LLMResponse`** — Simplified LLM response.
- **`Proxy`** — Simple wrapper around proxym gateway.
- **`Project`** — One project, all tools, zero boilerplate.
- **`TraceEntry`** — Single LLM interaction trace.
- **`Pattern`** — Extracted repeating pattern from traces.
- **`Rule`** — Deterministic replacement for an LLM pattern.
- **`LoopState`** — Current state of the progressive algorithmization loop.
- **`Loop`** — The progressive algorithmization engine.
- **`RepoConfig`** — Configuration for a single repository in the workspace.
- **`Workspace`** — Manage multiple repos as a single workspace.
- **`Task`** — Single todo task extracted from file.
- **`TodoParser`** — Parse todo lists from Markdown and text files.
- **`OllamaModel`** — Information about an Ollama model.
- **`OllamaResponse`** — Response from Ollama API.
- **`OllamaClient`** — Client for interacting with Ollama API.
- **`OllamaService`** — High-level service for Ollama operations.
- **`ToolStatus`** — —
- **`HealthReport`** — Combined analysis result from all tools.
- **`Analyzer`** — Unified interface for code analysis tools.
- **`CLIResult`** — —
- **`DockerTool`** — Single Docker-based tool declaration from docker-tools.yaml.
- **`RunningTool`** — A spawned Docker container with connection info.
- **`DockerToolManager`** — Spawn Docker containers, connect via MCP/REST, call tools, teardown.
- **`TraceSpan`** — Single operation span.
- **`Telemetry`** — Track costs, tokens, time across an algitex pipeline run.
- **`FixResult`** — Result of fixing an issue.
- **`AutoFix`** — Automated code fixing using various backends.
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
- **`Manager`** — —
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
- **`BadClass`** — —
- **`DataManager`** — —
- **`BatchProcessor`** — Batch processor for Ollama with rate limiting and retries.
- **`UserManager`** — Manages user operations.
- **`DataManager`** — —
- **`UserManager`** — Manage users.
- **`BadClass`** — Class with multiple issues.
- **`Handler`** — —

### Functions

- `validate_static(path)` — Run static analysis with ruff, mypy on the project.
- `validate_runtime(path)` — Run runtime tests with pytest.
- `validate_security(path)` — Run security scan with bandit.
- `validate_all(path)` — Run all validation levels: static, runtime, and security.
- `analyze_complexity(path)` — Analyze code complexity with radon.
- `calculate_quality_score(path)` — Calculate overall quality score combining validation and complexity.
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
- `aider_ai_code(prompt, relative_editable_files, model)` — Edit code using AI via Aider.
- `aider_list_models()` — List available AI models for Aider.
- `aider_chat(message, context)` — Chat with Aider AI about code.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `analyze_project(path)` — Analyze a Python project and return metrics.
- `generate_toon(path)` — Generate Toon notation report for a project.
- `generate_readme(path)` — Generate README.md content from code analysis.
- `evolution_export(path)` — Export evolution report with modules, dependencies, and hotspots.
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
- `count_tokens(text)` — Count tokens in text.
- `list_models()` — List available LLM models and their capabilities.
- `chat_completion(messages, model, temperature, max_tokens)` — Send chat completion request to LLM provider.
- `simple_prompt(prompt, model)` — Simple single-prompt completion.
- `get_budget_status()` — Get current budget/usage status (placeholder for budget tracking).
- `create_rest_api()` — Create FastAPI application for REST mode.
- `run_rest_server()` — Run as REST API server.
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
- `todo_fix(file, tool, task_id, limit)` — Execute fix tasks (prefact-style) via Docker MCP.
- `init_ci_cd(project_path, platform)` — Initialize CI/CD for a project.
- `create_quality_gate_config(max_cc, require_tests, security_scan)` — Create a quality gate configuration.
- `create_workspace_template(name, repos)` — Create a workspace configuration template.
- `init_workspace(name, config_path)` — Initialize a new workspace with template.
- `discover_tools()` — Check which tools are available.
- `require_tool(name)` — Raise helpful error if a tool is missing.
- `get_tool_module(name)` — Import and return a tool module, or None if unavailable.
- `calc(x, y, op)` — —
- `process(items)` — —
- `load(path)` — —
- `divide(a, b)` — —
- `parse_todo_issues(limit)` — Parse TODO.md and extract issues.
- `fix_with_claude_code(issue, model, dry_run)` — Fix a single issue using Claude Code (anthropic-curl).
- `main()` — —
- `calculate_statistics(data)` — Calculate basic statistics for a dataset.
- `find_user(users, name)` — Find user by name.
- `process_file(filename)` — Process a file.
- `divide_numbers(a, b)` — Divide two numbers.
- `get_config(key)` — Get config value.
- `complex_function(data)` — A complex function with multiple issues.
- `bad_error_handling()` — Function with bad error handling.
- `check_claude_code()` — Check if Claude Code (anthropic-curl) is installed.
- `check_ollama()` — Check if Ollama is running.
- `list_ollama_models()` — List available Ollama models.
- `demo_claude_code_fix(file_path, instruction, model)` — Demo: Fix file using Claude Code with Ollama.
- `demo_batch_fix(todo_file)` — Demo: Batch fix all issues from TODO.md.
- `main()` — —
- `main()` — —
- `check_ollama()` — Check if Ollama is running.
- `list_models()` — List available local models.
- `generate_code(prompt, model)` — Generate code using local Ollama model.
- `analyze_code(code, model)` — Analyze code using local Ollama model.
- `demo_code_generation()` — Demo: Generate a function using local LLM.
- `demo_code_analysis()` — Demo: Analyze code using local LLM.
- `demo_cost_comparison()` — Demo: Compare local vs cloud costs.
- `main()` — —
- `create_sample_project()` — Create sample project with code to refactor.
- `demo_refactoring()` — Demonstrate real refactoring workflow.
- `basic_github_actions_example()` — Generate basic GitHub Actions workflow.
- `gitlab_ci_example()` — Generate GitLab CI configuration.
- `quality_gates_example()` — Example of configuring quality gates.
- `dockerfile_example()` — Generate Dockerfile for algitex project.
- `precommit_hooks_example()` — Generate pre-commit configuration.
- `complete_ci_cd_setup()` — Example of complete CI/CD setup.
- `multi_platform_ci_example()` — Example of multi-platform CI/CD.
- `cleanup_ci_projects()` — Clean up all sample CI projects.
- `main()` — —
- `create_sample_docker_project()` — Create sample project with Dockerfile.
- `run_docker_command(cmd, cwd)` — Run Docker command and return result.
- `demo_docker_operations()` — Demonstrate real Docker operations.
- `main()` — —
- `complex_logic(n)` — —
- `create_sample_code()` — Create sample Python code with issues to validate.
- `run_local_validation(code_dir)` — Run local validation tools if available.
- `demo_validation()` — Demonstrate real code validation.
- `load_env()` — Load .env file if present.
- `check_required_env()` — Check required environment variables.
- `show_workflow()` — Display the 7-step refactoring workflow.
- `demo_with_docker_tools()` — Demonstrate Docker tool usage if available.
- `show_cli_usage()` — Show CLI usage instructions.
- `unused_imports()` — —
- `magic_numbers()` — —
- `no_error_handling()` — —
- `check_ollama()` — Check if Ollama is running.
- `main()` — —
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
- `calculate(x, y, operation)` — —
- `process_items(data)` — —
- `load_file(path)` — —
- `divide_numbers(a, b)` — —
- `main()` — Simplified version using algitex Project class.
- `find_files(directory, pattern)` — Find files matching pattern.
- `save_results(results, output_dir)` — Save results to JSON.
- `main()` — —
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
- `check_litellm()` — Check if litellm is installed.
- `check_ollama()` — Check if Ollama is running.
- `list_ollama_models()` — List available Ollama models.
- `test_proxy()` — Test if liteLLM proxy is running.
- `main()` — —
- `create_sample_project()` — Create sample project for GitHub workflow.
- `demo_github_workflow()` — Demonstrate GitHub workflow.
- `calculate(x, y, operation)` — —
- `process_items(data)` — —
- `load_file(path)` — —
- `divide_numbers(a, b)` — —
- `parse_todo_issues(limit)` — Parse TODO.md and extract issues from Current Issues section.
- `fix_with_llm(issue, dry_run)` — Fix a single issue using LiteLLM proxy API.
- `mark_issue_done(issue)` — Mark an issue as done in TODO.md by changing - [ ] to - [x].
- `main()` — —
- `check_services()` — Check if all MCP services are running.
- `demo_code_analysis()` — Demonstrate code analysis with code2llm.
- `demo_validation()` — Demonstrate validation with vallm.
- `demo_ticket_management()` — Demonstrate ticket management with planfile-mcp.
- `demo_sprint_status()` — Demonstrate sprint status.
- `main()` — Main demo function.
- `calculate_price(qty, price, discount)` — Calculate final price.
- `process_users(users)` — Process user list.
- `format_message(name, value)` — Format message string.
- `load_data(filename)` — Load data from file.
- `divide(a, b)` — Divide two numbers.
- `complex_function(data, threshold, multiplier, offset)` — Process data with many parameters.
- `bad_error_handling()` — Example of bad error handling.
- `generate_continue_config()` — Generate Continue.dev config for Ollama.
- `install_config()` — Install config to ~/.continue/config.json.
- `check_ollama()` — Check if Ollama is running.
- `list_models()` — List available Ollama models.
- `main()` — —
- `main()` — Simplified version using algitex Project class.
- `get_last_todo_issues(count)` — Parse TODO.md and get last N issues from Current Issues section.
- `analyze_file(file_path)` — Analyze file using code2llm MCP.
- `validate_file(file_path)` — Validate file using vallm MCP.
- `fix_unused_import(file_path, line_num, import_name)` — Fix unused import by removing it.
- `fix_f_string(file_path, line_num)` — Fix string concatenation to f-string.
- `create_ticket_for_issue(issue)` — Create ticket in planfile-mcp for manual review.
- `main()` — Main workflow.
- `analyze_buggy_code(file_path)` — Analyze buggy_code.py using code2llm MCP and report issues.
- `validate_buggy_code(file_path)` — Validate buggy_code.py using vallm MCP.
- `create_tickets_for_buggy_code(analysis, validation)` — Create tickets in planfile-mcp for issues found in buggy_code.py.
- `demo_buggy_code_workflow()` — Run full workflow on buggy_code.py: analyze → validate → create tickets.
- `main()` — —
- `check_prerequisites()` — Check if all required tools are installed.
- `main()` — —
- `basic_feedback_example()` — Basic feedback controller example.
- `custom_policy_example()` — Example with custom feedback policy.
- `feedback_extraction_example()` — Example of extracting actionable feedback.
- `feedback_loop_simulation()` — Simulate complete feedback loop with mock execution.
- `escalation_scenarios()` — Different escalation scenarios.
- `cost_optimization_example()` — Example of optimizing costs with feedback policies.
- `main()` — —
- `ensure_git_repo()` — Ensure we're in a git repo (aider requires it even with --no-git).
- `mark_issue_done(issue)` — Mark an issue as done in TODO.md by changing - [ ] to - [x].
- `parse_todo_issues(limit)` — Parse TODO.md and extract issues from Current Issues section.
- `fix_with_aider(issue, dry_run)` — Fix a single issue using aider CLI with Ollama.
- `main()` — —
- `create_sample_files()` — Create sample files for demonstration.
- `demo_file_operations()` — Demonstrate real filesystem operations.
- `check_ollama()` — Check if Ollama is running.
- `check_models_available(available_models)` — Check which models from DEFAULT_MODELS are available.
- `run_benchmark(model, task)` — Run single benchmark.
- `run_all_benchmarks(models)` — Run benchmarks for all models on all tasks.
- `print_results_table(results)` — Print results as table.
- `save_results(results)` — Save results to JSON.
- `main()` — —
- `basic_context_example()` — Basic context building example.
- `context_optimization_example()` — Example of optimizing context for different use cases.
- `semantic_search_example()` — Example of semantic search for related code (placeholder).
- `prompt_engineering_example()` — Example of how context improves prompt engineering.
- `cleanup_example_projects()` — Clean up example projects.
- `main()` — —
- `calculate(x, y)` — Calculate sum.
- `process_items(items)` — Process a list of items.
- `load_data(source)` — Load data from source.
- `cache_result(func)` — Decorator with issues.
- `parse_date(date_string)` — Parse date string.
- `recursive_function(n)` — Recursive function without proper termination.
- `process_data(data)` — Process data with nested logic.
- `calculate(x, y, operation)` — —
- `check_services()` — Check if all MCP services are running.
- `main()` — —
- `calc(a, b, op)` — —
- `create_sample_workspace()` — Create a sample workspace configuration.
- `workspace_management_example()` — Example of workspace management operations.
- `cross_repo_analysis_example()` — Example of analyzing multiple repositories.
- `cross_repo_planning_example()` — Example of planning across repositories.
- `workspace_execution_example()` — Example of executing across the workspace.
- `advanced_workspace_features()` — Example of advanced workspace features.
- `cleanup_sample_workspace()` — Clean up the sample workspace.


## Project Structure

📄 `docker.aider-mcp.aider_mcp_server` (5 functions)
📄 `docker.code2llm.code2llm_mcp_server` (6 functions)
📄 `docker.code2llm.code2llm_server` (6 functions, 1 classes)
📄 `docker.planfile-mcp.planfile_mcp_server` (10 functions)
📄 `docker.proxym.proxym_mcp_server` (10 functions)
📄 `docker.proxym.proxym_server` (7 functions, 1 classes)
📄 `docker.vallm.vallm_mcp_server` (8 functions)
📄 `docker.vallm.vallm_server` (7 functions, 1 classes)
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
📄 `examples.19-local-mcp-tools.buggy_code` (8 functions, 1 classes)
📄 `examples.19-local-mcp-tools.main` (2 functions)
📄 `examples.19-local-mcp-tools.run`
📄 `examples.20-self-hosted-pipeline.auto_fix_todos` (11 functions)
📄 `examples.20-self-hosted-pipeline.buggy_code` (12 functions, 1 classes)
📄 `examples.20-self-hosted-pipeline.main` (6 functions)
📄 `examples.20-self-hosted-pipeline.run`
📄 `examples.21-aider-cli-ollama.auto_fix` (5 functions)
📄 `examples.21-aider-cli-ollama.auto_fix_simplified` (1 functions)
📄 `examples.21-aider-cli-ollama.buggy_code` (10 functions, 1 classes)
📄 `examples.21-aider-cli-ollama.main` (2 functions)
📄 `examples.21-aider-cli-ollama.main_simplified` (1 functions)
📄 `examples.21-aider-cli-ollama.run`
📄 `examples.22-claude-code-ollama.batch_fix` (3 functions)
📄 `examples.22-claude-code-ollama.buggy_code` (6 functions, 1 classes)
📄 `examples.22-claude-code-ollama.main` (6 functions)
📄 `examples.22-claude-code-ollama.run`
📄 `examples.23-continue-dev-ollama.buggy_code` (6 functions, 1 classes)
📄 `examples.23-continue-dev-ollama.main` (5 functions)
📄 `examples.23-continue-dev-ollama.run`
📄 `examples.24-ollama-batch.batch_analyze` (7 functions, 1 classes)
📄 `examples.24-ollama-batch.file1` (3 functions)
📄 `examples.24-ollama-batch.file2` (3 functions)
📄 `examples.24-ollama-batch.file3` (3 functions, 1 classes)
📄 `examples.24-ollama-batch.main` (2 functions)
📄 `examples.24-ollama-batch.run`
📄 `examples.25-local-model-comparison.benchmark` (7 functions)
📄 `examples.25-local-model-comparison.main` (1 functions)
📄 `examples.25-local-model-comparison.run`
📄 `examples.26-litellm-proxy-ollama.auto_fix` (4 functions)
📄 `examples.26-litellm-proxy-ollama.buggy_code` (6 functions, 1 classes)
📄 `examples.26-litellm-proxy-ollama.main` (5 functions)
📄 `examples.26-litellm-proxy-ollama.main_simplified` (1 functions)
📄 `examples.26-litellm-proxy-ollama.run`
📄 `project`
📦 `src.algitex`
📦 `src.algitex.algo` (12 functions, 5 classes)
📄 `src.algitex.algo.loop`
📄 `src.algitex.cli` (25 functions)
📄 `src.algitex.config` (7 functions, 4 classes)
📄 `src.algitex.project` (22 functions, 1 classes)
📦 `src.algitex.propact` (12 functions, 3 classes)
📄 `src.algitex.propact.workflow`
📦 `src.algitex.tools` (4 functions, 1 classes)
📄 `src.algitex.tools.analysis` (8 functions, 3 classes)
📄 `src.algitex.tools.autofix` (14 functions, 2 classes)
📄 `src.algitex.tools.cicd` (11 functions, 1 classes)
📄 `src.algitex.tools.context` (14 functions, 3 classes)
📄 `src.algitex.tools.docker` (23 functions, 3 classes)
📄 `src.algitex.tools.feedback` (12 functions, 4 classes)
📄 `src.algitex.tools.ollama` (16 functions, 4 classes)
📄 `src.algitex.tools.proxy` (9 functions, 2 classes)
📄 `src.algitex.tools.services` (18 functions, 3 classes)
📄 `src.algitex.tools.telemetry` (9 functions, 2 classes)
📄 `src.algitex.tools.tickets` (11 functions, 2 classes)
📄 `src.algitex.tools.todo_executor` (12 functions, 2 classes)
📄 `src.algitex.tools.todo_local` (10 functions, 2 classes)
📄 `src.algitex.tools.todo_parser` (8 functions, 2 classes)
📄 `src.algitex.tools.todo_runner` (16 functions, 2 classes)
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