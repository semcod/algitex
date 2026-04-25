## Overview

- **Project**: /home/tom/github/semcod/algitex
- **Primary Language**: python
- **Languages**: python: 163, shell: 26
- **Analysis Mode**: static
- **Total Functions**: 1236
- **Total Classes**: 176
- **Modules**: 189
- **Entry Points**: 1011

### src.algitex.microtask.executor
- **Functions**: 29
- **Classes**: 2
- **File**: `executor.py`

### src.algitex.dashboard
- **Functions**: 24
- **Classes**: 4
- **File**: `dashboard.py`

### src.algitex.project
- **Functions**: 22
- **Classes**: 1
- **File**: `__init__.py`

### src.algitex.tools.ide
- **Functions**: 22
- **Classes**: 6
- **File**: `ide.py`

### src.algitex.cli.todo
- **Functions**: 21
- **File**: `todo.py`

### src.algitex.tools.docker
- **Functions**: 20
- **Classes**: 3
- **File**: `docker.py`

### src.algitex.tools.services
- **Functions**: 20
- **Classes**: 3
- **File**: `services.py`

### src.algitex.tools.batch
- **Functions**: 20
- **Classes**: 4
- **File**: `batch.py`

### src.algitex.tools.workspace
- **Functions**: 20
- **Classes**: 2
- **File**: `workspace.py`

### src.algitex.nlp
- **Functions**: 19
- **Classes**: 5
- **File**: `__init__.py`

### src.algitex.tools.benchmark
- **Functions**: 19
- **Classes**: 4
- **File**: `benchmark.py`

### src.algitex.workflows
- **Functions**: 19
- **Classes**: 3
- **File**: `__init__.py`

### src.algitex.todo.micro
- **Functions**: 19
- **Classes**: 5
- **File**: `micro.py`

### src.algitex.prefact_integration
- **Functions**: 18
- **Classes**: 3
- **File**: `prefact_integration.py`

### src.algitex.shared_rules
- **Functions**: 18
- **Classes**: 7
- **File**: `shared_rules.py`

### src.algitex.tools.mcp
- **Functions**: 18
- **Classes**: 2
- **File**: `mcp.py`

### src.algitex.propact
- **Functions**: 18
- **Classes**: 3
- **File**: `__init__.py`

### src.algitex.benchmark
- **Functions**: 17
- **Classes**: 6
- **File**: `benchmark.py`

### src.algitex.tools.docker_transport
- **Functions**: 17
- **Classes**: 1
- **File**: `docker_transport.py`

### src.algitex.todo.fixer
- **Functions**: 17
- **Classes**: 2
- **File**: `fixer.py`

## Key Entry Points

Main execution flows into the system:

### examples.31-abpr-workflow.main.main
> Demonstrate ABPR pipeline: Execute → Trace → Conflict → Rule → Validate → Repeat.
- **Calls**: print, print, print, print, print, print, str, Project

### examples.30-parallel-execution.main.main
> Demonstrate parallel execution with region-based coordination.
- **Calls**: print, print, print, str, Project, print, p.analyze, print

### src.algitex.cli.metrics.metrics_compare
> Compare tier performance (algorithm vs micro vs big LLM).
- **Calls**: command, option, MetricsCollector, collector.load, collector.get_tier_stats, collector.estimate_cost, Table, table.add_column

### examples.20-self-hosted-pipeline.main.main
> Main demo function.
- **Calls**: print, print, print, print, print, print, print, print

### src.algitex.cli.todo.todo_batch
> BatchFix: grupowanie i optymalizacja podobnych zadań.

Zamiast wykonywać każde zadanie osobno, BatchFix grupuje podobne problemy
(np. "f-string", "mag
- **Calls**: command, option, option, option, option, option, option, option

### examples.30-parallel-execution.parallel_real_world.main
> Demonstrate parallel refactoring of a real-world project.
- **Calls**: tempfile.TemporaryDirectory, Path, print, examples.30-parallel-execution.parallel_real_world.setup_sample_project, Project, print, p.analyze, print

### src.algitex.tools.autofix.batch_backend.BatchFixBackend._parse_batch_response
> Parsuj odpowiedź batch i zastosuj fixy.
- **Calls**: print, print, re.findall, print, enumerate, sum, print, filepath.strip

### examples.14-docker-mcp.main.demo_docker_operations
> Demonstrate real Docker operations.
- **Calls**: print, examples.14-docker-mcp.main.create_sample_docker_project, print, print, project_dir.iterdir, print, print, print

### examples.05-cost-tracking.main.main
- **Calls**: print, Tickets, print, print, print, sorted, print, Loop

### examples.18-ollama-local.main.main
- **Calls**: print, print, print, print, print, examples.18-ollama-local.main.list_models, examples.18-ollama-local.main.demo_code_generation, examples.18-ollama-local.main.demo_code_analysis

### src.algitex.cli.todo.todo_hybrid
> Autofix: LLM-based code fixes (use --hybrid for mechanical + LLM).
- **Calls**: command, argument, option, option, option, option, option, option

### examples.31-abpr-workflow.abpr_pipeline.abpr_pipeline
> ABPR loop: Execute → Trace → Conflict → Rule → Validate → Repeat.
- **Calls**: Project, Loop, print, loop.discover, print, p.analyze, print, print

### src.algitex.tools.autofix.batch_backend.BatchFixBackend.fix_batch
> Wykonaj wszystkie zadania w batch z równoległym przetwarzaniem.

Args:
    tasks: Lista zadań do wykonania
    max_parallel: Liczba równoległych grup 
- **Calls**: time.time, self._group_tasks, len, print, print, print, self._verify_tasks_exist, print

### examples.13-vallm.main.demo_validation
> Demonstrate real code validation.
- **Calls**: print, examples.13-vallm.main.create_sample_code, print, print, print, print, print, print

### src.algitex.cli.dashboard.dashboard_monitor
> Monitor existing cache and metrics files.

Reads from existing cache/metrics and displays current state.
- **Calls**: command, option, option, LLMCache, cache_obj.stats, MetricsCollector, metrics_collector.load, metrics_collector.get_summary

### examples.07-context.main.basic_context_example
> Basic context building example.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, None.write_text, None.mkdir, None.write_text, None.write_text

### src.algitex.metrics.MetricsReporter.print_dashboard
> Print Rich dashboard to console.
- **Calls**: self.collector.get_summary, console.print, Table, table.add_column, table.add_column, table.add_column, table.add_column, table.add_column

### examples.02-algo-loop.main.main
- **Calls**: print, Loop, print, loop.discover, loop.report, print, print, print

### examples.27-unified-autofix.main.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, print, print, print

### src.algitex.cli.dashboard.dashboard_export
> Export dashboard data to file (JSON or Prometheus format).

Collects metrics for specified duration and exports to file.
- **Calls**: command, option, option, option, console.print, time.time, LLMCache, MetricsCollector

### src.algitex.todo.hybrid.HybridAutofix.fix_all
> Run both phases with full transparency and audit logging.

Returns:
    HybridResult with audit log path for rollback capability.
- **Calls**: self.audit.start_operation, print, print, print, print, print, print, print

### examples.06-telemetry.main.basic_telemetry_example
> Basic telemetry tracking example.
- **Calls**: print, Telemetry, print, tel.span, time.sleep, span1.finish, tel.span, time.sleep

### examples.15-github-mcp.main.demo_github_workflow
> Demonstrate GitHub workflow.
- **Calls**: print, examples.15-github-mcp.main.create_sample_project, print, print, project_dir.iterdir, print, print, print

### examples.12-filesystem-mcp.main.demo_file_operations
> Demonstrate real filesystem operations.
- **Calls**: print, examples.12-filesystem-mcp.main.create_sample_files, print, print, files_dir.rglob, print, print, print

### src.algitex.cli.todo.todo_fix
> Execute fix tasks (prefact-style) via Docker MCP.

5-step pipeline: parse → classify → execute → validate → report.
CC: 8 (5 functions + 3 branches)
W
- **Calls**: command, argument, option, option, option, option, option, option

### src.algitex.todo.hybrid.HybridAutofix.print_summary
> Print formatted summary of hybrid fix results.
- **Calls**: print, print, print, isinstance, print, print, print, print

### examples.10-cicd.main.complete_ci_cd_setup
> Example of complete CI/CD setup.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, CICDGenerator, generator.generate_all, print, print

### examples.19-local-mcp-tools.main.main
- **Calls**: print, print, print, print, print, print, print, print

### src.algitex.tools.autofix.batch_backend.BatchFixBackend._call_llm
> Wywołaj LLM z spinnerem i retry dla timeoutów.
- **Calls**: range, TimeoutError, threading.Thread, thread.start, time.time, sys.stdout.flush, thread.is_alive, thread.join

### examples.30-parallel-execution.parallel_refactoring.main
- **Calls**: Project, p.analyze, print, RegionExtractor, extractor.extract_all, print, TaskPartitioner, partitioner.partition

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [examples.31-abpr-workflow.main]
```

### Flow 2: metrics_compare
```
metrics_compare [src.algitex.cli.metrics]
```

### Flow 3: todo_batch
```
todo_batch [src.algitex.cli.todo]
```

### Flow 4: _parse_batch_response
```
_parse_batch_response [src.algitex.tools.autofix.batch_backend.BatchFixBackend]
```

### Flow 5: demo_docker_operations
```
demo_docker_operations [examples.14-docker-mcp.main]
  └─> create_sample_docker_project
```

### Flow 6: todo_hybrid
```
todo_hybrid [src.algitex.cli.todo]
```

### Flow 7: abpr_pipeline
```
abpr_pipeline [examples.31-abpr-workflow.abpr_pipeline]
```

### Flow 8: fix_batch
```
fix_batch [src.algitex.tools.autofix.batch_backend.BatchFixBackend]
```

### Flow 9: demo_validation
```
demo_validation [examples.13-vallm.main]
  └─> create_sample_code
```

### Flow 10: dashboard_monitor
```
dashboard_monitor [src.algitex.cli.dashboard]
```

### src.algitex.microtask.executor.MicroTaskExecutor
> Execute micro tasks in three tiers: algorithmic, small LLM, big LLM.
- **Methods**: 28
- **Key Methods**: src.algitex.microtask.executor.MicroTaskExecutor.__init__, src.algitex.microtask.executor.MicroTaskExecutor.execute, src.algitex.microtask.executor.MicroTaskExecutor.group_by_file, src.algitex.microtask.executor.MicroTaskExecutor._phase_algorithmic, src.algitex.microtask.executor.MicroTaskExecutor._process_algorithmic_batch, src.algitex.microtask.executor.MicroTaskExecutor._handle_unused_import, src.algitex.microtask.executor.MicroTaskExecutor._handle_return_type, src.algitex.microtask.executor.MicroTaskExecutor._handle_known_magic, src.algitex.microtask.executor.MicroTaskExecutor._handle_fstring, src.algitex.microtask.executor.MicroTaskExecutor._handle_sort_imports

### src.algitex.project.Project
> One project, all tools, zero boilerplate.
- **Methods**: 25
- **Key Methods**: src.algitex.project.Project.__init__, src.algitex.project.Project._analyzer, src.algitex.project.Project._tickets, src.algitex.project.Project._ollama_service, src.algitex.project.Project.analyze, src.algitex.project.Project.plan, src.algitex.project.Project.execute, src.algitex.project.Project.status, src.algitex.project.Project._status_health, src.algitex.project.Project._status_tickets
- **Inherits**: ServiceMixin, AutoFixMixin, OllamaMixin, BatchMixin, BenchmarkMixin, IDEMixin, ConfigMixin, MCPMixin

### src.algitex.tools.docker.DockerToolManager
> Spawn Docker containers, connect via MCP/REST, call tools, teardown.
- **Methods**: 20
- **Key Methods**: src.algitex.tools.docker.DockerToolManager.__init__, src.algitex.tools.docker.DockerToolManager.__enter__, src.algitex.tools.docker.DockerToolManager.__exit__, src.algitex.tools.docker.DockerToolManager._load_tools, src.algitex.tools.docker.DockerToolManager._read_yaml_with_expansion, src.algitex.tools.docker.DockerToolManager._expand_tool_spec, src.algitex.tools.docker.DockerToolManager._expand_env_vars, src.algitex.tools.docker.DockerToolManager._expand_volumes, src.algitex.tools.docker.DockerToolManager._load_state, src.algitex.tools.docker.DockerToolManager._save_state

### src.algitex.tools.autofix.AutoFix
> Automated code fixing using various backends.
- **Methods**: 18
- **Key Methods**: src.algitex.tools.autofix.AutoFix.__init__, src.algitex.tools.autofix.AutoFix.ollama_service, src.algitex.tools.autofix.AutoFix.ollama_backend, src.algitex.tools.autofix.AutoFix.aider_backend, src.algitex.tools.autofix.AutoFix.proxy_backend, src.algitex.tools.autofix.AutoFix.check_backends, src.algitex.tools.autofix.AutoFix.choose_backend, src.algitex.tools.autofix.AutoFix._convert_task, src.algitex.tools.autofix.AutoFix.mark_task_done, src.algitex.tools.autofix.AutoFix.fix_with_ollama

### src.algitex.tools.mcp.MCPOrchestrator
> Orchestrates multiple MCP services.
- **Methods**: 17
- **Key Methods**: src.algitex.tools.mcp.MCPOrchestrator.__init__, src.algitex.tools.mcp.MCPOrchestrator._setup_signal_handlers, src.algitex.tools.mcp.MCPOrchestrator._register_default_services, src.algitex.tools.mcp.MCPOrchestrator.add_service, src.algitex.tools.mcp.MCPOrchestrator.add_custom_service, src.algitex.tools.mcp.MCPOrchestrator.start_service, src.algitex.tools.mcp.MCPOrchestrator.stop_service, src.algitex.tools.mcp.MCPOrchestrator.restart_service, src.algitex.tools.mcp.MCPOrchestrator.start_all, src.algitex.tools.mcp.MCPOrchestrator.stop_all

### src.algitex.propact.Workflow
> Parse and execute Propact Markdown workflows.
- **Methods**: 17
- **Key Methods**: src.algitex.propact.Workflow.__init__, src.algitex.propact.Workflow.parse, src.algitex.propact.Workflow._extract_steps_from_content, src.algitex.propact.Workflow.validate, src.algitex.propact.Workflow._execute_step, src.algitex.propact.Workflow._update_result, src.algitex.propact.Workflow._handle_step_failure, src.algitex.propact.Workflow.execute, src.algitex.propact.Workflow.status, src.algitex.propact.Workflow._exec_shell

### src.algitex.tools.workspace.Workspace
> Manage multiple repos as a single workspace.
- **Methods**: 17
- **Key Methods**: src.algitex.tools.workspace.Workspace.__init__, src.algitex.tools.workspace.Workspace._load_config, src.algitex.tools.workspace.Workspace._validate_dependencies, src.algitex.tools.workspace.Workspace._topo_sort, src.algitex.tools.workspace.Workspace.clone_all, src.algitex.tools.workspace.Workspace.pull_all, src.algitex.tools.workspace.Workspace.analyze_all, src.algitex.tools.workspace.Workspace.plan_all, src.algitex.tools.workspace.Workspace.execute_all, src.algitex.tools.workspace.Workspace.validate_all

### src.algitex.dashboard.LiveDashboard
> Live Rich dashboard for monitoring algitex operations.
- **Methods**: 16
- **Key Methods**: src.algitex.dashboard.LiveDashboard.__init__, src.algitex.dashboard.LiveDashboard._create_layout, src.algitex.dashboard.LiveDashboard._render_header, src.algitex.dashboard.LiveDashboard._render_cache_panel, src.algitex.dashboard.LiveDashboard._render_tiers_panel, src.algitex.dashboard.LiveDashboard._render_footer, src.algitex.dashboard.LiveDashboard._render, src.algitex.dashboard.LiveDashboard._update_loop, src.algitex.dashboard.LiveDashboard.start, src.algitex.dashboard.LiveDashboard._run_live

### src.algitex.tools.config.ConfigManager
> Manages configuration files for various IDEs and tools.
- **Methods**: 16
- **Key Methods**: src.algitex.tools.config.ConfigManager.__init__, src.algitex.tools.config.ConfigManager._ensure_dir, src.algitex.tools.config.ConfigManager._backup_file, src.algitex.tools.config.ConfigManager.install_config, src.algitex.tools.config.ConfigManager.generate_continue_config, src.algitex.tools.config.ConfigManager.install_continue_config, src.algitex.tools.config.ConfigManager.generate_vscode_settings, src.algitex.tools.config.ConfigManager.install_vscode_settings, src.algitex.tools.config.ConfigManager.generate_env_file, src.algitex.tools.config.ConfigManager.generate_docker_compose

### src.algitex.tools.services.ServiceChecker
> Checker for various services used by algitex.
- **Methods**: 16
- **Key Methods**: src.algitex.tools.services.ServiceChecker.__init__, src.algitex.tools.services.ServiceChecker.check_http_service, src.algitex.tools.services.ServiceChecker.check_ollama, src.algitex.tools.services.ServiceChecker.check_litellm_proxy, src.algitex.tools.services.ServiceChecker.check_mcp_service, src.algitex.tools.services.ServiceChecker.check_command_exists, src.algitex.tools.services.ServiceChecker.check_file_exists, src.algitex.tools.services.ServiceChecker.check_all, src.algitex.tools.services.ServiceChecker._format_status_line, src.algitex.tools.services.ServiceChecker._print_status_details

### src.algitex.tools.autofix.batch_backend.BatchFixBackend
> Backend do optymalizacji fixów przez grupowanie.

Args:
    base_url: URL do Ollama (domyślnie local
- **Methods**: 16
- **Key Methods**: src.algitex.tools.autofix.batch_backend.BatchFixBackend.__init__, src.algitex.tools.autofix.batch_backend.BatchFixBackend.fix_batch, src.algitex.tools.autofix.batch_backend.BatchFixBackend._update_todo_mark_completed, src.algitex.tools.autofix.batch_backend.BatchFixBackend._create_backup, src.algitex.tools.autofix.batch_backend.BatchFixBackend._preflight_syntax_check, src.algitex.tools.autofix.batch_backend.BatchFixBackend._verify_tasks_exist, src.algitex.tools.autofix.batch_backend.BatchFixBackend._group_tasks, src.algitex.tools.autofix.batch_backend.BatchFixBackend._process_group, src.algitex.tools.autofix.batch_backend.BatchFixBackend._fix_batch_group, src.algitex.tools.autofix.batch_backend.BatchFixBackend._fix_individual

### src.algitex.tools.batch.BatchProcessor
> Generic batch processor with rate limiting and retries.
- **Methods**: 15
- **Key Methods**: src.algitex.tools.batch.BatchProcessor.__init__, src.algitex.tools.batch.BatchProcessor._rate_limit, src.algitex.tools.batch.BatchProcessor._process_item, src.algitex.tools.batch.BatchProcessor.process, src.algitex.tools.batch.BatchProcessor._prepare, src.algitex.tools.batch.BatchProcessor._execute, src.algitex.tools.batch.BatchProcessor._collect, src.algitex.tools.batch.BatchProcessor._setup_progress_bar, src.algitex.tools.batch.BatchProcessor._collect_results, src.algitex.tools.batch.BatchProcessor._get_start_time

### src.algitex.todo.audit.AuditLogger
> Comprehensive audit logging with rollback support.

Usage:
    audit = AuditLogger(".algitex/audit")
- **Methods**: 13
- **Key Methods**: src.algitex.todo.audit.AuditLogger.__init__, src.algitex.todo.audit.AuditLogger._get_user, src.algitex.todo.audit.AuditLogger._hash_content, src.algitex.todo.audit.AuditLogger._generate_op_id, src.algitex.todo.audit.AuditLogger.start_operation, src.algitex.todo.audit.AuditLogger.log_change, src.algitex.todo.audit.AuditLogger.complete_operation, src.algitex.todo.audit.AuditLogger._write_entry, src.algitex.todo.audit.AuditLogger.get_history, src.algitex.todo.audit.AuditLogger.get_last_operation

### src.algitex.tools.todo_executor.TodoExecutor
> Execute todo tasks using Docker MCP tools.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.todo_executor.TodoExecutor.__init__, src.algitex.tools.todo_executor.TodoExecutor.__enter__, src.algitex.tools.todo_executor.TodoExecutor.__exit__, src.algitex.tools.todo_executor.TodoExecutor.run, src.algitex.tools.todo_executor.TodoExecutor._execute_task, src.algitex.tools.todo_executor.TodoExecutor._parse_action, src.algitex.tools.todo_executor.TodoExecutor._parse_fix_action, src.algitex.tools.todo_executor.TodoExecutor._parse_create_action, src.algitex.tools.todo_executor.TodoExecutor._parse_delete_action, src.algitex.tools.todo_executor.TodoExecutor._parse_read_action

### src.algitex.tools.todo_runner.TodoRunner
> Execute todo tasks using Docker MCP tools with local fallback.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.todo_runner.TodoRunner.__init__, src.algitex.tools.todo_runner.TodoRunner.__enter__, src.algitex.tools.todo_runner.TodoRunner.__exit__, src.algitex.tools.todo_runner.TodoRunner.run_from_file, src.algitex.tools.todo_runner.TodoRunner.run, src.algitex.tools.todo_runner.TodoRunner._execute_local, src.algitex.tools.todo_runner.TodoRunner._execute_ollama, src.algitex.tools.todo_runner.TodoRunner._build_ollama_prompt, src.algitex.tools.todo_runner.TodoRunner._call_ollama_api, src.algitex.tools.todo_runner.TodoRunner._execute_task

### src.algitex.tools.benchmark.ModelBenchmark
> Benchmark models on standardized tasks.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.benchmark.ModelBenchmark.__init__, src.algitex.tools.benchmark.ModelBenchmark._add_default_tasks, src.algitex.tools.benchmark.ModelBenchmark.add_task, src.algitex.tools.benchmark.ModelBenchmark.add_custom_task, src.algitex.tools.benchmark.ModelBenchmark.run_single_task, src.algitex.tools.benchmark.ModelBenchmark.compare_models, src.algitex.tools.benchmark.ModelBenchmark.print_results, src.algitex.tools.benchmark.ModelBenchmark._print_table, src.algitex.tools.benchmark.ModelBenchmark._print_summary, src.algitex.tools.benchmark.ModelBenchmark._print_detailed

### src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend
> Fix issues using OpenRouter API directly.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend.__init__, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend.fix, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend._validate, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend._execute_fix, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend._read_file, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend._build_prompt, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend._call_api, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend._extract_code, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend._write_file, src.algitex.tools.autofix.openrouter_backend.OpenRouterBackend._success_result

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

## Data Transformation Functions

Key functions that process and transform data:

### docker.vallm.vallm_server.VallmServer._run_validate
> Core logic to run static, runtime, and security validations.
- **Output to**: all, self._validate_static, self._validate_runtime, self._validate_security, static_result.get

### docker.vallm.vallm_server.VallmServer._validate_static
> Static analysis with pylint, mypy, ruff.
- **Output to**: subprocess.run, subprocess.run, max, json.loads, errors.extend

### docker.vallm.vallm_server.VallmServer._validate_runtime
> Run tests with pytest.
- **Output to**: subprocess.run, result.stdout.split, line.split, str, int

### docker.vallm.vallm_server.VallmServer._validate_security
> Security scan with bandit.
- **Output to**: subprocess.run, max, len, logger.warning, json.loads

### docker.vallm.vallm_server.VallmServer._parse_radon_complexities
> Parse radon tool stdout and structure the complexity metric calculations.
- **Output to**: stdout.split, max, round, len, sum

### scripts.generate_lib_docs.parse_file
> Parse Python file and extract documentation.
- **Output to**: scripts.generate_lib_docs.extract_docstring, ast.iter_child_nodes, filepath.read_text, ast.parse, isinstance

### docker.vallm.vallm_mcp_server.validate_static
> Run static analysis with ruff, mypy on the project.

Args:
    path: Path to the project directory
 
- **Output to**: mcp.tool, subprocess.run, subprocess.run, max, None.isoformat

### docker.vallm.vallm_mcp_server.validate_runtime
> Run runtime tests with pytest.

Args:
    path: Path to the project directory
    
Returns:
    Dict
- **Output to**: mcp.tool, subprocess.run, result.stdout.split, None.isoformat, line.split

### docker.vallm.vallm_mcp_server.validate_security
> Run security scan with bandit.

Args:
    path: Path to the project directory
    
Returns:
    Dict
- **Output to**: mcp.tool, subprocess.run, max, len, None.isoformat

### docker.vallm.vallm_mcp_server.validate_all
> Run all validation levels: static, runtime, and security.

Args:
    path: Path to the project direc
- **Output to**: mcp.tool, docker.vallm.vallm_mcp_server.validate_static, docker.vallm.vallm_mcp_server.validate_runtime, docker.vallm.vallm_mcp_server.validate_security, all

### src.algitex.prefact_integration.PrefactRuleAdapter._parse_issues
> Parse prefact output into PrefactIssue objects.
- **Output to**: data.get, issues.append, PrefactIssue, issue_data.get, issue_data.get

### src.algitex.tools.todo_parser.TodoParser.parse
> Parse file and return list of pending tasks.
- **Output to**: self.file_path.read_text, src.algitex.tools.ollama_cache.LLMCache.set, self._parse_prefact, self._parse_github, self._parse_generic

### src.algitex.tools.todo_parser.TodoParser._parse_prefact
> Parse prefact-style: `file.py:10 - description`.
- **Output to**: src.algitex.tools.ollama_cache.LLMCache.set, self.PREFACT_PATTERN.finditer, match.group, int, None.strip

### src.algitex.tools.todo_parser.TodoParser._parse_github
> Parse GitHub-style checkboxes.
- **Output to**: src.algitex.tools.ollama_cache.LLMCache.set, self.GITHUB_PATTERN.finditer, None.lower, None.strip, seen.add

### src.algitex.tools.todo_parser.TodoParser._parse_generic
> Parse generic list items.
- **Output to**: src.algitex.tools.ollama_cache.LLMCache.set, self.GENERIC_PATTERN.finditer, match.group, None.strip, seen.add

### src.algitex.tools.docker_transport.StdioTransport._serialize
> Serialize JSON-RPC request with MCP protocol headers.
- **Output to**: json.dumps, len

### src.algitex.tools.docker_transport.StdioTransport._check_process_alive
> Raise RuntimeError if the process associated with stdout has exited.
- **Output to**: hasattr, RuntimeError, stdout._proc.poll, stdout._proc.poll

### src.algitex.tools.docker_transport.StdioTransport._parse
> Parse JSON response with error handling.
- **Output to**: json.loads, RuntimeError, str

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

### recursion_list
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: src.algitex.tools.tickets.Tickets.list

### recursion_complex_logic
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: examples.24-ollama-batch.file3.complex_logic

### recursion_recursive_function
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: examples.19-local-mcp-tools.buggy_code.recursive_function

### state_machine_VallmServer
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: docker.vallm.vallm_server.VallmServer.__init__, docker.vallm.vallm_server.VallmServer.create_fastapi_app, docker.vallm.vallm_server.VallmServer._run_validate, docker.vallm.vallm_server.VallmServer._validate_static, docker.vallm.vallm_server.VallmServer._validate_runtime

### state_machine_TierState
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.dashboard.TierState.percent, src.algitex.dashboard.TierState.eta_seconds

### state_machine_CacheState
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.dashboard.CacheState.hit_rate, src.algitex.dashboard.CacheState.size_mb

### state_machine_LiveDashboard
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.dashboard.LiveDashboard.__init__, src.algitex.dashboard.LiveDashboard._create_layout, src.algitex.dashboard.LiveDashboard._render_header, src.algitex.dashboard.LiveDashboard._render_cache_panel, src.algitex.dashboard.LiveDashboard._render_tiers_panel

### state_machine_SimpleProgressTracker
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.dashboard.SimpleProgressTracker.__init__, src.algitex.dashboard.SimpleProgressTracker.start, src.algitex.dashboard.SimpleProgressTracker.add_task, src.algitex.dashboard.SimpleProgressTracker.update, src.algitex.dashboard.SimpleProgressTracker.stop

### state_machine_LoopState
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.algo.LoopState.deterministic_ratio, src.algitex.algo.LoopState.stage_name

### state_machine_Proxy
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.proxy.Proxy.__init__, src.algitex.tools.proxy.Proxy.ask, src.algitex.tools.proxy.Proxy.budget, src.algitex.tools.proxy.Proxy.models, src.algitex.tools.proxy.Proxy.health

### state_machine_OllamaClient
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.ollama.OllamaClient.__init__, src.algitex.tools.ollama.OllamaClient.health, src.algitex.tools.ollama.OllamaClient.list_models, src.algitex.tools.ollama.OllamaClient.pull_model, src.algitex.tools.ollama.OllamaClient.generate

### state_machine_DockerToolManager
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.docker.DockerToolManager.__init__, src.algitex.tools.docker.DockerToolManager.__enter__, src.algitex.tools.docker.DockerToolManager.__exit__, src.algitex.tools.docker.DockerToolManager._load_tools, src.algitex.tools.docker.DockerToolManager._read_yaml_with_expansion

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

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `examples.31-abpr-workflow.main.main` - 77 calls
- `examples.30-parallel-execution.main.main` - 55 calls
- `src.algitex.cli.metrics.metrics_compare` - 54 calls
- `src.algitex.cli.todo.todo_verify_prefact` - 50 calls
- `examples.20-self-hosted-pipeline.main.main` - 49 calls
- `scripts.generate_lib_docs.generate_module_doc` - 48 calls
- `src.algitex.cli.todo.todo_batch` - 43 calls
- `examples.30-parallel-execution.parallel_real_world.main` - 43 calls
- `examples.14-docker-mcp.main.demo_docker_operations` - 40 calls
- `examples.05-cost-tracking.main.main` - 40 calls
- `examples.18-ollama-local.main.main` - 39 calls
- `src.algitex.cli.todo.todo_hybrid` - 38 calls
- `examples.31-abpr-workflow.abpr_pipeline.abpr_pipeline` - 36 calls
- `src.algitex.tools.autofix.batch_backend.BatchFixBackend.fix_batch` - 35 calls
- `examples.13-vallm.main.demo_validation` - 35 calls
- `src.algitex.cli.dashboard.dashboard_monitor` - 34 calls
- `examples.07-context.main.basic_context_example` - 34 calls
- `src.algitex.metrics.MetricsReporter.print_dashboard` - 33 calls
- `examples.02-algo-loop.main.main` - 33 calls
- `examples.27-unified-autofix.main.main` - 33 calls
- `scripts.generate_lib_docs.parse_file` - 32 calls
- `src.algitex.cli.dashboard.dashboard_export` - 31 calls
- `src.algitex.todo.hybrid.HybridAutofix.fix_all` - 31 calls
- `examples.06-telemetry.main.basic_telemetry_example` - 30 calls
- `examples.15-github-mcp.main.demo_github_workflow` - 30 calls
- `examples.12-filesystem-mcp.main.demo_file_operations` - 30 calls
- `src.algitex.cli.todo.todo_fix` - 29 calls
- `src.algitex.todo.hybrid.HybridAutofix.print_summary` - 29 calls
- `examples.10-cicd.main.complete_ci_cd_setup` - 29 calls
- `examples.19-local-mcp-tools.main.main` - 28 calls
- `examples.30-parallel-execution.parallel_refactoring.main` - 27 calls
- `examples.03-pipeline.main.main` - 27 calls
- `src.algitex.todo.fixer.fix_file` - 26 calls
- `examples.04-ide-integration.main.main` - 26 calls
- `examples.25-local-model-comparison.main.main` - 26 calls
- `examples.07-context.main.prompt_engineering_example` - 26 calls
- `src.algitex.tools.ollama.OllamaClient.chat` - 25 calls
- `src.algitex.cli.metrics.metrics_cache` - 25 calls
- `examples.07-context.main.context_optimization_example` - 25 calls
- `src.algitex.nlp.find_duplicate_blocks` - 24 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> print
    main --> str
    main --> Project
    metrics_compare --> command
    metrics_compare --> option
    metrics_compare --> MetricsCollector
    metrics_compare --> load
    metrics_compare --> get_tier_stats
    todo_batch --> command
    todo_batch --> option
    main --> TemporaryDirectory
    main --> Path
    main --> setup_sample_project
    _parse_batch_respons --> print
    _parse_batch_respons --> findall
    _parse_batch_respons --> enumerate
    demo_docker_operatio --> print
    demo_docker_operatio --> create_sample_docker
    demo_docker_operatio --> iterdir
    main --> Tickets
    todo_hybrid --> command
    todo_hybrid --> argument
    todo_hybrid --> option
    abpr_pipeline --> Project
    abpr_pipeline --> Loop
    abpr_pipeline --> print
    abpr_pipeline --> discover
    fix_batch --> time
    fix_batch --> _group_tasks
    fix_batch --> len
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.