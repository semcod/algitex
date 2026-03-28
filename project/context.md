# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/algitex
- **Primary Language**: python
- **Languages**: python: 118, shell: 26
- **Analysis Mode**: static
- **Total Functions**: 752
- **Total Classes**: 115
- **Modules**: 144
- **Entry Points**: 670

## Architecture by Module

### src.algitex.tools.ide
- **Functions**: 22
- **Classes**: 6
- **File**: `ide.py`

### src.algitex.tools.services
- **Functions**: 20
- **Classes**: 3
- **File**: `services.py`

### src.algitex.tools.batch
- **Functions**: 20
- **Classes**: 4
- **File**: `batch.py`

### src.algitex.tools.benchmark
- **Functions**: 19
- **Classes**: 4
- **File**: `benchmark.py`

### src.algitex.workflows
- **Functions**: 19
- **Classes**: 3
- **File**: `__init__.py`

### src.algitex.tools.mcp
- **Functions**: 18
- **Classes**: 2
- **File**: `mcp.py`

### src.algitex.tools.workspace
- **Functions**: 17
- **Classes**: 2
- **File**: `workspace.py`

### src.algitex.project
- **Functions**: 16
- **Classes**: 1
- **File**: `__init__.py`

### src.algitex.tools.ollama
- **Functions**: 16
- **Classes**: 4
- **File**: `ollama.py`

### src.algitex.tools.docker
- **Functions**: 15
- **Classes**: 3
- **File**: `docker.py`

### src.algitex.propact
- **Functions**: 15
- **Classes**: 3
- **File**: `__init__.py`

### src.algitex.tools.autofix
- **Functions**: 14
- **Classes**: 1
- **File**: `__init__.py`

### src.algitex.tools.docker_transport
- **Functions**: 14
- **Classes**: 1
- **File**: `docker_transport.py`

### src.algitex.tools.context
- **Functions**: 14
- **Classes**: 3
- **File**: `context.py`

### src.algitex.todo.fixer
- **Functions**: 14
- **Classes**: 2
- **File**: `fixer.py`

### src.algitex.tools.config
- **Functions**: 12
- **Classes**: 1
- **File**: `config.py`

### src.algitex.algo
- **Functions**: 12
- **Classes**: 5
- **File**: `__init__.py`

### src.algitex.tools.todo_executor
- **Functions**: 12
- **Classes**: 2
- **File**: `todo_executor.py`

### src.algitex.tools.feedback
- **Functions**: 12
- **Classes**: 4
- **File**: `feedback.py`

### src.algitex.tools.autofix.proxy_backend
- **Functions**: 12
- **Classes**: 1
- **File**: `proxy_backend.py`

## Key Entry Points

Main execution flows into the system:

### examples.32-workspace-coordination.main.main
> Demonstrate workspace coordination across multiple repositories.
- **Calls**: print, print, print, examples.32-workspace-coordination.main.load_workspace_config, print, print, print, print

### examples.31-abpr-workflow.main.main
> Demonstrate ABPR pipeline: Execute → Trace → Conflict → Rule → Validate → Repeat.
- **Calls**: print, print, print, print, print, print, str, Project

### examples.30-parallel-execution.main.main
> Demonstrate parallel execution with region-based coordination.
- **Calls**: print, print, print, str, Project, print, p.analyze, print

### examples.33-hybrid-autofix.main.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### examples.20-self-hosted-pipeline.main.main
> Main demo function.
- **Calls**: print, print, print, print, print, print, print, print

### examples.14-docker-mcp.main.demo_docker_operations
> Demonstrate real Docker operations.
- **Calls**: print, examples.14-docker-mcp.main.create_sample_docker_project, print, print, project_dir.iterdir, print, print, print

### examples.05-cost-tracking.main.main
- **Calls**: print, Tickets, print, print, print, sorted, print, Loop

### examples.18-ollama-local.main.main
- **Calls**: print, print, print, print, print, examples.18-ollama-local.main.list_models, examples.18-ollama-local.main.demo_code_generation, examples.18-ollama-local.main.demo_code_analysis

### examples.31-abpr-workflow.abpr_pipeline.abpr_pipeline
> ABPR loop: Execute → Trace → Conflict → Rule → Validate → Repeat.
- **Calls**: Project, Loop, print, loop.discover, print, p.analyze, print, print

### examples.13-vallm.main.demo_validation
> Demonstrate real code validation.
- **Calls**: print, examples.13-vallm.main.create_sample_code, print, print, print, print, print, print

### examples.07-context.main.basic_context_example
> Basic context building example.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, None.write_text, None.mkdir, None.write_text, None.write_text

### examples.02-algo-loop.main.main
- **Calls**: print, Loop, print, loop.discover, loop.report, print, print, print

### examples.27-unified-autofix.main.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, print, print, print

### examples.15-github-mcp.main.demo_github_workflow
> Demonstrate GitHub workflow.
- **Calls**: print, examples.15-github-mcp.main.create_sample_project, print, print, project_dir.iterdir, print, print, print

### examples.06-telemetry.main.basic_telemetry_example
> Basic telemetry tracking example.
- **Calls**: print, Telemetry, print, tel.span, time.sleep, span1.finish, tel.span, time.sleep

### examples.12-filesystem-mcp.main.demo_file_operations
> Demonstrate real filesystem operations.
- **Calls**: print, examples.12-filesystem-mcp.main.create_sample_files, print, print, files_dir.rglob, print, print, print

### src.algitex.cli.todo.todo_hybrid
> Autofix: LLM-based code fixes (use --hybrid for mechanical + LLM).
- **Calls**: typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### src.algitex.todo.hybrid.HybridAutofix.print_summary
> Print formatted summary of hybrid fix results.
- **Calls**: print, print, print, isinstance, print, print, print, print

### examples.10-cicd.main.complete_ci_cd_setup
> Example of complete CI/CD setup.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, CICDGenerator, generator.generate_all, print, print

### examples.19-local-mcp-tools.main.main
- **Calls**: print, print, print, print, print, print, print, print

### src.algitex.project.Project.generate_todo
> Generate TODO.md from analysis results.

Creates a TODO.md file with code issues found during analysis.
Uses the last analysis report if available, ot
- **Calls**: self.analyze, getattr, getattr, isinstance, open, f.write, f.write, f.write

### examples.30-parallel-execution.parallel_refactoring.main
- **Calls**: Project, p.analyze, print, RegionExtractor, extractor.extract_all, print, TaskPartitioner, partitioner.partition

### examples.03-pipeline.main.main
- **Calls**: print, print, None.report, print, None.report, None.get, hasattr, print

### examples.04-ide-integration.main.main
- **Calls**: print, print, None.items, print, None.items, print, print, print

### examples.07-context.main.prompt_engineering_example
> Example of how context improves prompt engineering.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, None.write_text, None.write_text, ContextBuilder, builder.build

### docker.vallm.vallm_server.VallmServer.create_fastapi_app
> Create FastAPI application.
- **Calls**: FastAPI, app.get, app.post, app.post, app.post, request.get, all, request.get

### examples.07-context.main.context_optimization_example
> Example of optimizing context for different use cases.
- **Calls**: print, Path, project_dir.mkdir, None.mkdir, None.write_text, None.write_text, None.mkdir, None.write_text

### examples.32-workspace-coordination.workspace_parallel.main
- **Calls**: Workspace, print, ws.analyze_all, print, print, sorted, print, ws.plan_all

### examples.08-feedback.main.feedback_loop_simulation
> Simulate complete feedback loop with mock execution.
- **Calls**: print, MockDockerManager, MockTickets, FeedbackController, FeedbackLoop, print, print, loop.execute_with_feedback

### examples.23-continue-dev-ollama.main.main
- **Calls**: print, print, print, print, Project, p.check_ollama, print, print

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [examples.32-workspace-coordination.main]
  └─> load_workspace_config
```

### Flow 2: demo_docker_operations
```
demo_docker_operations [examples.14-docker-mcp.main]
  └─> create_sample_docker_project
```

### Flow 3: abpr_pipeline
```
abpr_pipeline [examples.31-abpr-workflow.abpr_pipeline]
```

### Flow 4: demo_validation
```
demo_validation [examples.13-vallm.main]
  └─> create_sample_code
```

### Flow 5: basic_context_example
```
basic_context_example [examples.07-context.main]
```

### Flow 6: demo_github_workflow
```
demo_github_workflow [examples.15-github-mcp.main]
  └─> create_sample_project
```

### Flow 7: basic_telemetry_example
```
basic_telemetry_example [examples.06-telemetry.main]
```

### Flow 8: demo_file_operations
```
demo_file_operations [examples.12-filesystem-mcp.main]
  └─> create_sample_files
```

### Flow 9: todo_hybrid
```
todo_hybrid [src.algitex.cli.todo]
```

### Flow 10: print_summary
```
print_summary [src.algitex.todo.hybrid.HybridAutofix]
```

## Key Classes

### src.algitex.project.Project
> One project, all tools, zero boilerplate.
- **Methods**: 19
- **Key Methods**: src.algitex.project.Project.__init__, src.algitex.project.Project._analyzer, src.algitex.project.Project._tickets, src.algitex.project.Project._ollama_service, src.algitex.project.Project.analyze, src.algitex.project.Project.plan, src.algitex.project.Project.execute, src.algitex.project.Project.status, src.algitex.project.Project._status_health, src.algitex.project.Project._status_tickets
- **Inherits**: ServiceMixin, AutoFixMixin, OllamaMixin, BatchMixin, BenchmarkMixin, IDEMixin, ConfigMixin, MCPMixin

### src.algitex.tools.autofix.AutoFix
> Automated code fixing using various backends.
- **Methods**: 18
- **Key Methods**: src.algitex.tools.autofix.AutoFix.__init__, src.algitex.tools.autofix.AutoFix.ollama_service, src.algitex.tools.autofix.AutoFix.ollama_backend, src.algitex.tools.autofix.AutoFix.aider_backend, src.algitex.tools.autofix.AutoFix.proxy_backend, src.algitex.tools.autofix.AutoFix.check_backends, src.algitex.tools.autofix.AutoFix.choose_backend, src.algitex.tools.autofix.AutoFix._convert_task, src.algitex.tools.autofix.AutoFix.mark_task_done, src.algitex.tools.autofix.AutoFix.fix_with_ollama

### src.algitex.tools.mcp.MCPOrchestrator
> Orchestrates multiple MCP services.
- **Methods**: 17
- **Key Methods**: src.algitex.tools.mcp.MCPOrchestrator.__init__, src.algitex.tools.mcp.MCPOrchestrator._setup_signal_handlers, src.algitex.tools.mcp.MCPOrchestrator._register_default_services, src.algitex.tools.mcp.MCPOrchestrator.add_service, src.algitex.tools.mcp.MCPOrchestrator.add_custom_service, src.algitex.tools.mcp.MCPOrchestrator.start_service, src.algitex.tools.mcp.MCPOrchestrator.stop_service, src.algitex.tools.mcp.MCPOrchestrator.restart_service, src.algitex.tools.mcp.MCPOrchestrator.start_all, src.algitex.tools.mcp.MCPOrchestrator.stop_all

### src.algitex.tools.services.ServiceChecker
> Checker for various services used by algitex.
- **Methods**: 16
- **Key Methods**: src.algitex.tools.services.ServiceChecker.__init__, src.algitex.tools.services.ServiceChecker.check_http_service, src.algitex.tools.services.ServiceChecker.check_ollama, src.algitex.tools.services.ServiceChecker.check_litellm_proxy, src.algitex.tools.services.ServiceChecker.check_mcp_service, src.algitex.tools.services.ServiceChecker.check_command_exists, src.algitex.tools.services.ServiceChecker.check_file_exists, src.algitex.tools.services.ServiceChecker.check_all, src.algitex.tools.services.ServiceChecker._format_status_line, src.algitex.tools.services.ServiceChecker._print_status_details

### src.algitex.tools.docker.DockerToolManager
> Spawn Docker containers, connect via MCP/REST, call tools, teardown.
- **Methods**: 15
- **Key Methods**: src.algitex.tools.docker.DockerToolManager.__init__, src.algitex.tools.docker.DockerToolManager.__enter__, src.algitex.tools.docker.DockerToolManager.__exit__, src.algitex.tools.docker.DockerToolManager._load_tools, src.algitex.tools.docker.DockerToolManager._load_state, src.algitex.tools.docker.DockerToolManager._save_state, src.algitex.tools.docker.DockerToolManager.spawn, src.algitex.tools.docker.DockerToolManager._wait_healthy, src.algitex.tools.docker.DockerToolManager._get_http_client, src.algitex.tools.docker.DockerToolManager.call_tool

### src.algitex.tools.batch.BatchProcessor
> Generic batch processor with rate limiting and retries.
- **Methods**: 15
- **Key Methods**: src.algitex.tools.batch.BatchProcessor.__init__, src.algitex.tools.batch.BatchProcessor._rate_limit, src.algitex.tools.batch.BatchProcessor._process_item, src.algitex.tools.batch.BatchProcessor.process, src.algitex.tools.batch.BatchProcessor._prepare, src.algitex.tools.batch.BatchProcessor._execute, src.algitex.tools.batch.BatchProcessor._collect, src.algitex.tools.batch.BatchProcessor._setup_progress_bar, src.algitex.tools.batch.BatchProcessor._collect_results, src.algitex.tools.batch.BatchProcessor._get_start_time

### src.algitex.tools.workspace.Workspace
> Manage multiple repos as a single workspace.
- **Methods**: 14
- **Key Methods**: src.algitex.tools.workspace.Workspace.__init__, src.algitex.tools.workspace.Workspace._load_config, src.algitex.tools.workspace.Workspace._validate_dependencies, src.algitex.tools.workspace.Workspace._topo_sort, src.algitex.tools.workspace.Workspace.clone_all, src.algitex.tools.workspace.Workspace.pull_all, src.algitex.tools.workspace.Workspace.analyze_all, src.algitex.tools.workspace.Workspace.plan_all, src.algitex.tools.workspace.Workspace.execute_all, src.algitex.tools.workspace.Workspace.validate_all

### src.algitex.propact.Workflow
> Parse and execute Propact Markdown workflows.
- **Methods**: 14
- **Key Methods**: src.algitex.propact.Workflow.__init__, src.algitex.propact.Workflow.parse, src.algitex.propact.Workflow.validate, src.algitex.propact.Workflow._execute_step, src.algitex.propact.Workflow._update_result, src.algitex.propact.Workflow._handle_step_failure, src.algitex.propact.Workflow.execute, src.algitex.propact.Workflow.status, src.algitex.propact.Workflow._exec_shell, src.algitex.propact.Workflow._exec_rest

### src.algitex.tools.config.ConfigManager
> Manages configuration files for various IDEs and tools.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.config.ConfigManager.__init__, src.algitex.tools.config.ConfigManager._ensure_dir, src.algitex.tools.config.ConfigManager._backup_file, src.algitex.tools.config.ConfigManager.install_config, src.algitex.tools.config.ConfigManager.generate_continue_config, src.algitex.tools.config.ConfigManager.install_continue_config, src.algitex.tools.config.ConfigManager.generate_vscode_settings, src.algitex.tools.config.ConfigManager.install_vscode_settings, src.algitex.tools.config.ConfigManager.generate_env_file, src.algitex.tools.config.ConfigManager.generate_docker_compose

### src.algitex.tools.todo_executor.TodoExecutor
> Execute todo tasks using Docker MCP tools.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.todo_executor.TodoExecutor.__init__, src.algitex.tools.todo_executor.TodoExecutor.__enter__, src.algitex.tools.todo_executor.TodoExecutor.__exit__, src.algitex.tools.todo_executor.TodoExecutor.run, src.algitex.tools.todo_executor.TodoExecutor._execute_task, src.algitex.tools.todo_executor.TodoExecutor._parse_action, src.algitex.tools.todo_executor.TodoExecutor._parse_fix_action, src.algitex.tools.todo_executor.TodoExecutor._parse_create_action, src.algitex.tools.todo_executor.TodoExecutor._parse_delete_action, src.algitex.tools.todo_executor.TodoExecutor._parse_read_action

### src.algitex.tools.benchmark.ModelBenchmark
> Benchmark models on standardized tasks.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.benchmark.ModelBenchmark.__init__, src.algitex.tools.benchmark.ModelBenchmark._add_default_tasks, src.algitex.tools.benchmark.ModelBenchmark.add_task, src.algitex.tools.benchmark.ModelBenchmark.add_custom_task, src.algitex.tools.benchmark.ModelBenchmark.run_single_task, src.algitex.tools.benchmark.ModelBenchmark.compare_models, src.algitex.tools.benchmark.ModelBenchmark.print_results, src.algitex.tools.benchmark.ModelBenchmark._print_table, src.algitex.tools.benchmark.ModelBenchmark._print_summary, src.algitex.tools.benchmark.ModelBenchmark._print_detailed

### src.algitex.tools.autofix.proxy_backend.ProxyBackend
> Fix issues using LiteLLM proxy.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.autofix.proxy_backend.ProxyBackend.__init__, src.algitex.tools.autofix.proxy_backend.ProxyBackend.fix, src.algitex.tools.autofix.proxy_backend.ProxyBackend._validate, src.algitex.tools.autofix.proxy_backend.ProxyBackend._execute_fix, src.algitex.tools.autofix.proxy_backend.ProxyBackend._read_file, src.algitex.tools.autofix.proxy_backend.ProxyBackend._build_prompt, src.algitex.tools.autofix.proxy_backend.ProxyBackend._call_api, src.algitex.tools.autofix.proxy_backend.ProxyBackend._extract_code, src.algitex.tools.autofix.proxy_backend.ProxyBackend._write_file, src.algitex.tools.autofix.proxy_backend.ProxyBackend._success_result

### src.algitex.algo.Loop
> The progressive algorithmization engine.
- **Methods**: 11
- **Key Methods**: src.algitex.algo.Loop.__init__, src.algitex.algo.Loop.discover, src.algitex.algo.Loop.add_trace, src.algitex.algo.Loop.extract, src.algitex.algo.Loop.generate_rules, src.algitex.algo.Loop._llm_generate_rule, src.algitex.algo.Loop.route, src.algitex.algo.Loop.optimize, src.algitex.algo.Loop.report, src.algitex.algo.Loop._load

### src.algitex.tools.ollama.OllamaClient
> Client for interacting with Ollama API.
- **Methods**: 11
- **Key Methods**: src.algitex.tools.ollama.OllamaClient.__init__, src.algitex.tools.ollama.OllamaClient.health, src.algitex.tools.ollama.OllamaClient.list_models, src.algitex.tools.ollama.OllamaClient.pull_model, src.algitex.tools.ollama.OllamaClient.generate, src.algitex.tools.ollama.OllamaClient.chat, src.algitex.tools.ollama.OllamaClient.fix_code, src.algitex.tools.ollama.OllamaClient.analyze_code, src.algitex.tools.ollama.OllamaClient.close, src.algitex.tools.ollama.OllamaClient.__enter__

### src.algitex.tools.todo_local.LocalExecutor
> Execute simple code fixes locally without Docker.
- **Methods**: 11
- **Key Methods**: src.algitex.tools.todo_local.LocalExecutor.__init__, src.algitex.tools.todo_local.LocalExecutor.can_execute, src.algitex.tools.todo_local.LocalExecutor._determine_fix_and_apply, src.algitex.tools.todo_local.LocalExecutor.execute, src.algitex.tools.todo_local.LocalExecutor._fix_return_type, src.algitex.tools.todo_local.LocalExecutor._has_return_type, src.algitex.tools.todo_local.LocalExecutor._import_exists, src.algitex.tools.todo_local.LocalExecutor._fix_unused_import, src.algitex.tools.todo_local.LocalExecutor._fix_fstring, src.algitex.tools.todo_local.LocalExecutor._fix_standalone_main

### src.algitex.tools.autofix.aider_backend.AiderBackend
> Fix issues using Aider CLI.
- **Methods**: 11
- **Key Methods**: src.algitex.tools.autofix.aider_backend.AiderBackend.__init__, src.algitex.tools.autofix.aider_backend.AiderBackend.fix, src.algitex.tools.autofix.aider_backend.AiderBackend._validate_task, src.algitex.tools.autofix.aider_backend.AiderBackend._ensure_git_repo, src.algitex.tools.autofix.aider_backend.AiderBackend._build_command, src.algitex.tools.autofix.aider_backend.AiderBackend._build_prompt, src.algitex.tools.autofix.aider_backend.AiderBackend._execute_aider, src.algitex.tools.autofix.aider_backend.AiderBackend._process_result, src.algitex.tools.autofix.aider_backend.AiderBackend._dry_run_result, src.algitex.tools.autofix.aider_backend.AiderBackend._timeout_result

### src.algitex.tools.telemetry.Telemetry
> Track costs, tokens, time across an algitex pipeline run.
- **Methods**: 10
- **Key Methods**: src.algitex.tools.telemetry.Telemetry.__init__, src.algitex.tools.telemetry.Telemetry.span, src.algitex.tools.telemetry.Telemetry.total_cost, src.algitex.tools.telemetry.Telemetry.total_tokens, src.algitex.tools.telemetry.Telemetry.total_duration, src.algitex.tools.telemetry.Telemetry.error_count, src.algitex.tools.telemetry.Telemetry.summary, src.algitex.tools.telemetry.Telemetry.push_to_langfuse, src.algitex.tools.telemetry.Telemetry.save, src.algitex.tools.telemetry.Telemetry.report

### src.algitex.tools.tickets.Tickets
> Manage project tickets via planfile or local YAML.
- **Methods**: 10
- **Key Methods**: src.algitex.tools.tickets.Tickets.__init__, src.algitex.tools.tickets.Tickets.add, src.algitex.tools.tickets.Tickets.from_analysis, src.algitex.tools.tickets.Tickets.list, src.algitex.tools.tickets.Tickets.update, src.algitex.tools.tickets.Tickets.sync, src.algitex.tools.tickets.Tickets.board, src.algitex.tools.tickets.Tickets._load, src.algitex.tools.tickets.Tickets._save, src.algitex.tools.tickets.Tickets._planfile_add

### src.algitex.tools.todo_runner.TodoRunner
> Execute todo tasks using Docker MCP tools with local fallback.
- **Methods**: 10
- **Key Methods**: src.algitex.tools.todo_runner.TodoRunner.__init__, src.algitex.tools.todo_runner.TodoRunner.__enter__, src.algitex.tools.todo_runner.TodoRunner.__exit__, src.algitex.tools.todo_runner.TodoRunner.run_from_file, src.algitex.tools.todo_runner.TodoRunner.run, src.algitex.tools.todo_runner.TodoRunner._execute_local, src.algitex.tools.todo_runner.TodoRunner._execute_ollama, src.algitex.tools.todo_runner.TodoRunner._execute_task, src.algitex.tools.todo_runner.TodoRunner._format_output, src.algitex.tools.todo_runner.TodoRunner.get_summary

### src.algitex.tools.parallel.executor.ParallelExecutor
> Execute tickets in parallel using git worktrees + region locking.
- **Methods**: 10
- **Key Methods**: src.algitex.tools.parallel.executor.ParallelExecutor.__init__, src.algitex.tools.parallel.executor.ParallelExecutor.execute, src.algitex.tools.parallel.executor.ParallelExecutor._create_worktree, src.algitex.tools.parallel.executor.ParallelExecutor._run_agent, src.algitex.tools.parallel.executor.ParallelExecutor._merge_all, src.algitex.tools.parallel.executor.ParallelExecutor._detect_line_drift, src.algitex.tools.parallel.executor.ParallelExecutor._resolve_conflict, src.algitex.tools.parallel.executor.ParallelExecutor._changes_are_disjoint, src.algitex.tools.parallel.executor.ParallelExecutor._parse_diff_ranges, src.algitex.tools.parallel.executor.ParallelExecutor._cleanup_worktrees

## Data Transformation Functions

Key functions that process and transform data:

### docker.vallm.vallm_server.VallmServer._validate_static
> Static analysis with pylint, mypy, ruff.
- **Output to**: subprocess.run, subprocess.run, max, json.loads, errors.extend

### docker.vallm.vallm_server.VallmServer._validate_runtime
> Run tests with pytest.
- **Output to**: subprocess.run, result.stdout.split, line.split, str, int

### docker.vallm.vallm_server.VallmServer._validate_security
> Security scan with bandit.
- **Output to**: subprocess.run, max, len, logger.warning, json.loads

### src.algitex.tools.docker_transport.StdioTransport._serialize
> Serialize JSON-RPC request with MCP protocol headers.
- **Output to**: json.dumps, len

### src.algitex.tools.docker_transport.StdioTransport._parse
> Parse JSON response with error handling.
- **Output to**: json.loads, RuntimeError, str

### src.algitex.tools.todo_parser.TodoParser.parse
> Parse file and return list of pending tasks.
- **Output to**: self.file_path.read_text, tasks.extend, tasks.extend, tasks.extend, self.file_path.exists

### src.algitex.tools.todo_parser.TodoParser._parse_prefact
> Parse prefact-style: `file.py:10 - description`.
- **Output to**: set, self.PREFACT_PATTERN.finditer, match.group, int, None.strip

### src.algitex.tools.todo_parser.TodoParser._parse_github
> Parse GitHub-style checkboxes.
- **Output to**: set, self.GITHUB_PATTERN.finditer, None.lower, None.strip, seen.add

### src.algitex.tools.todo_parser.TodoParser._parse_generic
> Parse generic list items.
- **Output to**: set, self.GENERIC_PATTERN.finditer, match.group, None.strip, seen.add

### src.algitex.tools.workspace.Workspace._validate_dependencies
> Validate that all dependencies exist.
- **Output to**: set, self.repos.items, self.repos.keys, ValueError

### src.algitex.tools.workspace.Workspace.validate_all
> Run validation across all repositories.
- **Output to**: self._topo_sort, print, Pipeline, pipeline.validate, pipeline._results.get

### src.algitex.tools.context.ContextBuilder._format_ticket
> Format ticket information.
- **Output to**: ticket.get, ticket.get, ticket.get, ticket.get

### src.algitex.tools.services.ServiceChecker._format_status_line
> Format a single status line.

### src.algitex.tools.todo_executor.TodoExecutor._parse_action
> Parse task description to determine MCP action and arguments.
- **Output to**: task.description.lower, any, any, any, any

### src.algitex.tools.todo_executor.TodoExecutor._parse_fix_action
> Parse a fix/correction task.
- **Output to**: re.search, str, str, None.strip, match.group

### src.algitex.tools.todo_executor.TodoExecutor._parse_create_action
> Parse a create/add task.
- **Output to**: re.search, file_match.group, str

### src.algitex.tools.todo_executor.TodoExecutor._parse_delete_action
> Parse a remove/delete task.
- **Output to**: str, str

### src.algitex.tools.todo_executor.TodoExecutor._parse_read_action
> Parse a read/view task.
- **Output to**: str, str

### src.algitex.tools.logging.format_args
> Format arguments for display.
- **Output to**: kwargs.items, None.join, parts.append, parts.append, src.algitex.tools.logging.format_value

### src.algitex.tools.logging.format_value
> Format a value for display.
- **Output to**: repr, len

### src.algitex.tools.logging.format_result
> Format a result for display.
- **Output to**: repr, len

### src.algitex.tools.todo_runner.TodoRunner._format_output
> Extract meaningful output from MCP result.
- **Output to**: isinstance, isinstance, json.dumps, str, str

### src.algitex.tools.batch.BatchProcessor._process_item
> Process single item with retry logic.
- **Output to**: time.time, self._rate_limit, self.worker_func, BatchResult, BatchResult

### src.algitex.tools.batch.BatchProcessor.process
> Process items in parallel using 3-stage pipeline.
- **Output to**: self._prepare, self._execute, self._collect

### src.algitex.tools.batch.FileBatchProcessor.process_directory
> Process all files in directory.
- **Output to**: self.find_files, self.process

## Behavioral Patterns

### recursion_list
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: src.algitex.tools.tickets.Tickets.list

### recursion_complex_logic
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: examples.24-ollama-batch.file3.complex_logic

### state_machine_Proxy
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.proxy.Proxy.__init__, src.algitex.tools.proxy.Proxy.ask, src.algitex.tools.proxy.Proxy.budget, src.algitex.tools.proxy.Proxy.models, src.algitex.tools.proxy.Proxy.health

### state_machine_LoopState
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.algo.LoopState.deterministic_ratio, src.algitex.algo.LoopState.stage_name

### state_machine_OllamaClient
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.ollama.OllamaClient.__init__, src.algitex.tools.ollama.OllamaClient.health, src.algitex.tools.ollama.OllamaClient.list_models, src.algitex.tools.ollama.OllamaClient.pull_model, src.algitex.tools.ollama.OllamaClient.generate

### state_machine_DockerToolManager
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.docker.DockerToolManager.__init__, src.algitex.tools.docker.DockerToolManager.__enter__, src.algitex.tools.docker.DockerToolManager.__exit__, src.algitex.tools.docker.DockerToolManager._load_tools, src.algitex.tools.docker.DockerToolManager._load_state

### state_machine_TraceSpan
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.telemetry.TraceSpan.duration_s, src.algitex.tools.telemetry.TraceSpan.finish, src.algitex.tools.telemetry.TraceSpan.__enter__, src.algitex.tools.telemetry.TraceSpan.__exit__

### state_machine_ServiceChecker
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.services.ServiceChecker.__init__, src.algitex.tools.services.ServiceChecker.check_http_service, src.algitex.tools.services.ServiceChecker.check_ollama, src.algitex.tools.services.ServiceChecker.check_litellm_proxy, src.algitex.tools.services.ServiceChecker.check_mcp_service

### state_machine_TodoExecutor
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.todo_executor.TodoExecutor.__init__, src.algitex.tools.todo_executor.TodoExecutor.__enter__, src.algitex.tools.todo_executor.TodoExecutor.__exit__, src.algitex.tools.todo_executor.TodoExecutor.run, src.algitex.tools.todo_executor.TodoExecutor._execute_task

### state_machine_VerboseContext
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.logging.VerboseContext.__init__, src.algitex.tools.logging.VerboseContext.__enter__, src.algitex.tools.logging.VerboseContext.__exit__

### state_machine_TodoRunner
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.todo_runner.TodoRunner.__init__, src.algitex.tools.todo_runner.TodoRunner.__enter__, src.algitex.tools.todo_runner.TodoRunner.__exit__, src.algitex.tools.todo_runner.TodoRunner.run_from_file, src.algitex.tools.todo_runner.TodoRunner.run

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `examples.32-workspace-coordination.main.main` - 94 calls
- `examples.31-abpr-workflow.main.main` - 77 calls
- `examples.30-parallel-execution.main.main` - 55 calls
- `examples.33-hybrid-autofix.main.main` - 50 calls
- `examples.20-self-hosted-pipeline.main.main` - 49 calls
- `examples.14-docker-mcp.main.demo_docker_operations` - 40 calls
- `examples.05-cost-tracking.main.main` - 40 calls
- `examples.18-ollama-local.main.main` - 39 calls
- `examples.31-abpr-workflow.abpr_pipeline.abpr_pipeline` - 36 calls
- `examples.13-vallm.main.demo_validation` - 35 calls
- `examples.07-context.main.basic_context_example` - 34 calls
- `examples.02-algo-loop.main.main` - 33 calls
- `examples.27-unified-autofix.main.main` - 33 calls
- `examples.15-github-mcp.main.demo_github_workflow` - 30 calls
- `examples.06-telemetry.main.basic_telemetry_example` - 30 calls
- `examples.12-filesystem-mcp.main.demo_file_operations` - 30 calls
- `src.algitex.cli.todo.todo_hybrid` - 29 calls
- `src.algitex.todo.hybrid.HybridAutofix.print_summary` - 29 calls
- `examples.10-cicd.main.complete_ci_cd_setup` - 29 calls
- `examples.19-local-mcp-tools.main.main` - 28 calls
- `src.algitex.project.Project.generate_todo` - 27 calls
- `examples.30-parallel-execution.parallel_refactoring.main` - 27 calls
- `examples.03-pipeline.main.main` - 27 calls
- `examples.04-ide-integration.main.main` - 26 calls
- `examples.07-context.main.prompt_engineering_example` - 26 calls
- `docker.vallm.vallm_server.VallmServer.create_fastapi_app` - 25 calls
- `examples.07-context.main.context_optimization_example` - 25 calls
- `examples.32-workspace-coordination.workspace_parallel.main` - 24 calls
- `examples.08-feedback.main.feedback_loop_simulation` - 24 calls
- `examples.23-continue-dev-ollama.main.main` - 23 calls
- `examples.25-local-model-comparison.main.main` - 23 calls
- `src.algitex.tools.config.ConfigManager.list_configs` - 22 calls
- `src.algitex.tools.ollama.OllamaClient.chat` - 22 calls
- `src.algitex.cli.parallel.parallel` - 22 calls
- `src.algitex.cli.core.init` - 22 calls
- `examples.11-aider-mcp.main.demo_refactoring` - 22 calls
- `examples.21-aider-cli-ollama.main.main` - 22 calls
- `examples.28-mcp-orchestration.main.main` - 22 calls
- `examples.08-feedback.main.basic_feedback_example` - 22 calls
- `src.algitex.tools.feedback.FeedbackLoop.execute_with_feedback` - 21 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> print
    main --> load_workspace_confi
    main --> str
    main --> Project
    main --> ArgumentParser
    main --> add_argument
    demo_docker_operatio --> print
    demo_docker_operatio --> create_sample_docker
    demo_docker_operatio --> iterdir
    main --> Tickets
    abpr_pipeline --> Project
    abpr_pipeline --> Loop
    abpr_pipeline --> print
    abpr_pipeline --> discover
    demo_validation --> print
    demo_validation --> create_sample_code
    basic_context_exampl --> print
    basic_context_exampl --> Path
    basic_context_exampl --> mkdir
    basic_context_exampl --> write_text
    main --> Loop
    main --> discover
    main --> report
    main --> parse_args
    demo_github_workflow --> print
    demo_github_workflow --> create_sample_projec
    demo_github_workflow --> iterdir
    basic_telemetry_exam --> print
    basic_telemetry_exam --> Telemetry
    basic_telemetry_exam --> span
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.