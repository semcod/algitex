# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/algitex
- **Primary Language**: python
- **Languages**: python: 39, shell: 17
- **Analysis Mode**: static
- **Total Functions**: 302
- **Total Classes**: 45
- **Modules**: 56
- **Entry Points**: 287

## Architecture by Module

### src.algitex.cli
- **Functions**: 25
- **File**: `cli.py`

### src.algitex.tools.docker
- **Functions**: 23
- **Classes**: 3
- **File**: `docker.py`

### src.algitex.workflows
- **Functions**: 19
- **Classes**: 3
- **File**: `__init__.py`

### src.algitex.tools.workspace
- **Functions**: 17
- **Classes**: 2
- **File**: `workspace.py`

### src.algitex.tools.context
- **Functions**: 14
- **Classes**: 3
- **File**: `context.py`

### src.algitex.tools.todo_runner
- **Functions**: 13
- **Classes**: 2
- **File**: `todo_runner.py`

### src.algitex.project
- **Functions**: 12
- **Classes**: 1
- **File**: `project.py`

### src.algitex.algo
- **Functions**: 12
- **Classes**: 5
- **File**: `__init__.py`

### src.algitex.tools.todo_executor
- **Functions**: 12
- **Classes**: 2
- **File**: `todo_executor.py`

### src.algitex.propact
- **Functions**: 12
- **Classes**: 3
- **File**: `__init__.py`

### src.algitex.tools.feedback
- **Functions**: 12
- **Classes**: 4
- **File**: `feedback.py`

### src.algitex.tools.cicd
- **Functions**: 11
- **Classes**: 1
- **File**: `cicd.py`

### src.algitex.tools.tickets
- **Functions**: 11
- **Classes**: 2
- **File**: `tickets.py`

### src.algitex.tools.proxy
- **Functions**: 9
- **Classes**: 2
- **File**: `proxy.py`

### src.algitex.tools.telemetry
- **Functions**: 9
- **Classes**: 2
- **File**: `telemetry.py`

### src.algitex.tools.todo_parser
- **Functions**: 8
- **Classes**: 2
- **File**: `todo_parser.py`

### src.algitex.tools.analysis
- **Functions**: 8
- **Classes**: 3
- **File**: `analysis.py`

### examples.10-cicd.main
- **Functions**: 8
- **File**: `main.py`

### examples.04-ide-integration.main
- **Functions**: 8
- **File**: `main.py`

### src.algitex.config
- **Functions**: 7
- **Classes**: 4
- **File**: `config.py`

## Key Entry Points

Main execution flows into the system:

### examples.05-cost-tracking.main.main
- **Calls**: print, Tickets, print, print, print, sorted, print, Loop

### examples.09-workspace.main.advanced_workspace_features
> Example of advanced workspace features.
- **Calls**: print, examples.09-workspace.main.create_sample_workspace, Workspace, print, workspace.find_repos_by_tag, print, print, set

### examples.02-algo-loop.main.main
- **Calls**: print, Loop, print, loop.discover, loop.report, print, print, print

### examples.07-context.main.basic_context_example
> Basic context building example.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, None.write_text, None.write_text, None.write_text, None.write_text

### examples.06-telemetry.main.basic_telemetry_example
> Basic telemetry tracking example.
- **Calls**: print, Telemetry, print, tel.span, time.sleep, span1.finish, tel.span, time.sleep

### examples.10-cicd.main.complete_ci_cd_setup
> Example of complete CI/CD setup.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, CICDGenerator, generator.generate_all, print, print

### src.algitex.project.Project.status
> Full project status: health + tickets + budget + algo progress.
- **Calls**: self._tickets.board, Proxy, proxy.budget, proxy.health, proxy.close, src.algitex.tools.discover_tools, self.algo.report, sum

### examples.03-pipeline.main.main
- **Calls**: print, print, None.report, print, None.report, None.get, hasattr, print

### examples.04-ide-integration.main.main
- **Calls**: print, print, None.items, print, None.items, print, print, print

### examples.07-context.main.prompt_engineering_example
> Example of how context improves prompt engineering.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, None.write_text, None.write_text, ContextBuilder, builder.build

### src.algitex.cli.init
> Initialize algitex for a project.
- **Calls**: app.command, typer.Argument, None.resolve, project_path.mkdir, None.mkdir, Config.load, cfg.save, console.print

### examples.07-context.main.context_optimization_example
> Example of optimizing context for different use cases.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, None.write_text, None.write_text, None.write_text, None.write_text

### examples.08-feedback.main.basic_feedback_example
> Basic feedback controller example.
- **Calls**: print, FeedbackPolicy, print, print, print, print, print, FeedbackController

### examples.01-quickstart.main.main
- **Calls**: print, print, src.algitex.tools.discover_tools, tools.items, Project, print, p.analyze, print

### src.algitex.tools.feedback.FeedbackLoop.execute_with_feedback
> Execute a ticket with automatic retry/replan/escalate logic.
- **Calls**: self.controller.needs_approval, self.tickets.add, self._execute_single, self._validate_result, validation.get, self.controller.on_validation_failure, ticket.get, ticket.get

### src.algitex.cli.go
> Full pipeline: analyze → plan → execute → validate.
- **Calls**: app.command, typer.Option, typer.Option, console.print, Pipeline, console.print, console.print, pipeline.report

### src.algitex.cli.todo_run
> Execute todo tasks via Docker MCP.
- **Calls**: todo_app.command, typer.Argument, typer.Option, typer.Option, typer.Option, TodoRunner, runner.run_from_file, Table

### examples.08-feedback.main.cost_optimization_example
> Example of optimizing costs with feedback policies.
- **Calls**: print, print, print, print, print, print, print, print

### examples.09-workspace.main.workspace_management_example
> Example of workspace management operations.
- **Calls**: print, examples.09-workspace.main.create_sample_workspace, Workspace, print, workspace.status, print, print, print

### examples.09-workspace.main.cross_repo_planning_example
> Example of planning across repositories.
- **Calls**: print, examples.09-workspace.main.create_sample_workspace, Workspace, print, workspace.get_execution_plan, print, all_tickets.items, print

### examples.07-context.main.semantic_search_example
> Example of semantic search for related code (placeholder).
- **Calls**: print, Path, project_dir.mkdir, None.write_text, None.write_text, ContextBuilder, builder.build, print

### examples.08-feedback.main.feedback_loop_simulation
> Simulate complete feedback loop with mock execution.
- **Calls**: print, MockDockerManager, MockTickets, FeedbackController, FeedbackLoop, print, print, loop.execute_with_feedback

### src.algitex.cli.plan
> Generate sprint plan with auto-tickets.
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, console.print, console.print, console.print, console.status

### src.algitex.tools.docker.DockerToolManager._call_stdio
> Send JSON-RPC over stdin, read from stdout.
- **Calls**: json.dumps, rt.process.stdin.write, rt.process.stdin.flush, RuntimeError, time.time, None.join, rt.process.stdout.readline, response_lines.append

### src.algitex.tools.docker.DockerToolManager.get_capabilities
> List MCP tools available on a running container.
- **Calls**: self._running.get, json.dumps, rt.process.stdin.write, rt.process.stdin.flush, rt.process.stdout.readline, int, rt.process.stdout.readline, rt.process.stdout.read

### src.algitex.propact.Workflow.execute
> Execute all steps in the workflow.
- **Calls**: WorkflowResult, self.parse, str, len, time.time, result.steps.append, docker_mgr.teardown_all, result.steps.append

### examples.09-workspace.main.workspace_execution_example
> Example of executing across the workspace.
- **Calls**: print, examples.09-workspace.main.create_sample_workspace, Workspace, print, workspace.get_execution_plan, print, print, results.items

### src.algitex.cli.todo_list
> Parse and display todo tasks from a file.
- **Calls**: todo_app.command, typer.Argument, TodoParser, parser.parse, Table, table.add_column, table.add_column, table.add_column

### examples.10-cicd.main.basic_github_actions_example
> Generate basic GitHub Actions workflow.
- **Calls**: print, Path, project_dir.mkdir, None.write_text, CICDGenerator, generator.generate_github_actions, print, print

### examples.08-feedback.main.escalation_scenarios
> Different escalation scenarios.
- **Calls**: print, print, print, print, FeedbackController, controller.needs_approval, range, FeedbackPolicy

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [examples.05-cost-tracking.main]
```

### Flow 2: advanced_workspace_features
```
advanced_workspace_features [examples.09-workspace.main]
  └─> create_sample_workspace
      └─ →> init_workspace
          └─> create_workspace_template
```

### Flow 3: basic_context_example
```
basic_context_example [examples.07-context.main]
```

### Flow 4: basic_telemetry_example
```
basic_telemetry_example [examples.06-telemetry.main]
```

### Flow 5: complete_ci_cd_setup
```
complete_ci_cd_setup [examples.10-cicd.main]
```

### Flow 6: status
```
status [src.algitex.project.Project]
```

### Flow 7: prompt_engineering_example
```
prompt_engineering_example [examples.07-context.main]
```

### Flow 8: init
```
init [src.algitex.cli]
```

### Flow 9: context_optimization_example
```
context_optimization_example [examples.07-context.main]
```

### Flow 10: basic_feedback_example
```
basic_feedback_example [examples.08-feedback.main]
```

## Key Classes

### src.algitex.tools.docker.DockerToolManager
> Spawn Docker containers, connect via MCP/REST, call tools, teardown.
- **Methods**: 23
- **Key Methods**: src.algitex.tools.docker.DockerToolManager.__init__, src.algitex.tools.docker.DockerToolManager.__enter__, src.algitex.tools.docker.DockerToolManager.__exit__, src.algitex.tools.docker.DockerToolManager._load_tools, src.algitex.tools.docker.DockerToolManager._load_state, src.algitex.tools.docker.DockerToolManager._save_state, src.algitex.tools.docker.DockerToolManager.spawn, src.algitex.tools.docker.DockerToolManager._spawn_stdio, src.algitex.tools.docker.DockerToolManager._spawn_sse, src.algitex.tools.docker.DockerToolManager._spawn_rest

### src.algitex.tools.workspace.Workspace
> Manage multiple repos as a single workspace.
- **Methods**: 14
- **Key Methods**: src.algitex.tools.workspace.Workspace.__init__, src.algitex.tools.workspace.Workspace._load_config, src.algitex.tools.workspace.Workspace._validate_dependencies, src.algitex.tools.workspace.Workspace._topo_sort, src.algitex.tools.workspace.Workspace.clone_all, src.algitex.tools.workspace.Workspace.pull_all, src.algitex.tools.workspace.Workspace.analyze_all, src.algitex.tools.workspace.Workspace.plan_all, src.algitex.tools.workspace.Workspace.execute_all, src.algitex.tools.workspace.Workspace.validate_all

### src.algitex.tools.todo_runner.TodoRunner
> Execute todo tasks using Docker MCP tools.
- **Methods**: 13
- **Key Methods**: src.algitex.tools.todo_runner.TodoRunner.__init__, src.algitex.tools.todo_runner.TodoRunner.__enter__, src.algitex.tools.todo_runner.TodoRunner.__exit__, src.algitex.tools.todo_runner.TodoRunner.run_from_file, src.algitex.tools.todo_runner.TodoRunner.run, src.algitex.tools.todo_runner.TodoRunner._execute_task, src.algitex.tools.todo_runner.TodoRunner._determine_action, src.algitex.tools.todo_runner.TodoRunner._nap_action, src.algitex.tools.todo_runner.TodoRunner._aider_action, src.algitex.tools.todo_runner.TodoRunner._filesystem_action

### src.algitex.project.Project
> One project, all tools, zero boilerplate.
- **Methods**: 12
- **Key Methods**: src.algitex.project.Project.__init__, src.algitex.project.Project.analyze, src.algitex.project.Project.plan, src.algitex.project.Project.execute, src.algitex.project.Project.status, src.algitex.project.Project.run_workflow, src.algitex.project.Project.ask, src.algitex.project.Project.add_ticket, src.algitex.project.Project.sync, src.algitex.project.Project._build_prompt

### src.algitex.tools.todo_executor.TodoExecutor
> Execute todo tasks using Docker MCP tools.
- **Methods**: 12
- **Key Methods**: src.algitex.tools.todo_executor.TodoExecutor.__init__, src.algitex.tools.todo_executor.TodoExecutor.__enter__, src.algitex.tools.todo_executor.TodoExecutor.__exit__, src.algitex.tools.todo_executor.TodoExecutor.run, src.algitex.tools.todo_executor.TodoExecutor._execute_task, src.algitex.tools.todo_executor.TodoExecutor._parse_action, src.algitex.tools.todo_executor.TodoExecutor._parse_fix_action, src.algitex.tools.todo_executor.TodoExecutor._parse_create_action, src.algitex.tools.todo_executor.TodoExecutor._parse_delete_action, src.algitex.tools.todo_executor.TodoExecutor._parse_read_action

### src.algitex.algo.Loop
> The progressive algorithmization engine.
- **Methods**: 11
- **Key Methods**: src.algitex.algo.Loop.__init__, src.algitex.algo.Loop.discover, src.algitex.algo.Loop.add_trace, src.algitex.algo.Loop.extract, src.algitex.algo.Loop.generate_rules, src.algitex.algo.Loop._llm_generate_rule, src.algitex.algo.Loop.route, src.algitex.algo.Loop.optimize, src.algitex.algo.Loop.report, src.algitex.algo.Loop._load

### src.algitex.propact.Workflow
> Parse and execute Propact Markdown workflows.
- **Methods**: 11
- **Key Methods**: src.algitex.propact.Workflow.__init__, src.algitex.propact.Workflow.parse, src.algitex.propact.Workflow.validate, src.algitex.propact.Workflow.execute, src.algitex.propact.Workflow.status, src.algitex.propact.Workflow._exec_shell, src.algitex.propact.Workflow._exec_rest, src.algitex.propact.Workflow._exec_mcp, src.algitex.propact.Workflow._exec_docker, src.algitex.propact.Workflow._execute_with_manager

### src.algitex.tools.telemetry.Telemetry
> Track costs, tokens, time across an algitex pipeline run.
- **Methods**: 10
- **Key Methods**: src.algitex.tools.telemetry.Telemetry.__init__, src.algitex.tools.telemetry.Telemetry.span, src.algitex.tools.telemetry.Telemetry.total_cost, src.algitex.tools.telemetry.Telemetry.total_tokens, src.algitex.tools.telemetry.Telemetry.total_duration, src.algitex.tools.telemetry.Telemetry.error_count, src.algitex.tools.telemetry.Telemetry.summary, src.algitex.tools.telemetry.Telemetry.push_to_langfuse, src.algitex.tools.telemetry.Telemetry.save, src.algitex.tools.telemetry.Telemetry.report

### src.algitex.tools.tickets.Tickets
> Manage project tickets via planfile or local YAML.
- **Methods**: 10
- **Key Methods**: src.algitex.tools.tickets.Tickets.__init__, src.algitex.tools.tickets.Tickets.add, src.algitex.tools.tickets.Tickets.from_analysis, src.algitex.tools.tickets.Tickets.list, src.algitex.tools.tickets.Tickets.update, src.algitex.tools.tickets.Tickets.sync, src.algitex.tools.tickets.Tickets.board, src.algitex.tools.tickets.Tickets._load, src.algitex.tools.tickets.Tickets._save, src.algitex.tools.tickets.Tickets._planfile_add

### src.algitex.tools.cicd.CICDGenerator
> Generate CI/CD pipelines for algitex projects.
- **Methods**: 9
- **Key Methods**: src.algitex.tools.cicd.CICDGenerator.__init__, src.algitex.tools.cicd.CICDGenerator._load_config, src.algitex.tools.cicd.CICDGenerator.generate_github_actions, src.algitex.tools.cicd.CICDGenerator.generate_gitlab_ci, src.algitex.tools.cicd.CICDGenerator._get_complexity_check, src.algitex.tools.cicd.CICDGenerator.generate_dockerfile, src.algitex.tools.cicd.CICDGenerator.generate_precommit_config, src.algitex.tools.cicd.CICDGenerator.generate_all, src.algitex.tools.cicd.CICDGenerator.update_config

### src.algitex.tools.context.ContextBuilder
> Build rich context for LLM coding tasks from .toon files + git + planfile.
- **Methods**: 9
- **Key Methods**: src.algitex.tools.context.ContextBuilder.__init__, src.algitex.tools.context.ContextBuilder.build, src.algitex.tools.context.ContextBuilder._load_toon_summary, src.algitex.tools.context.ContextBuilder._load_architecture, src.algitex.tools.context.ContextBuilder._resolve_targets, src.algitex.tools.context.ContextBuilder._find_related, src.algitex.tools.context.ContextBuilder._load_conventions, src.algitex.tools.context.ContextBuilder._git_recent, src.algitex.tools.context.ContextBuilder._format_ticket

### src.algitex.tools.proxy.Proxy
> Simple wrapper around proxym gateway.
- **Methods**: 8
- **Key Methods**: src.algitex.tools.proxy.Proxy.__init__, src.algitex.tools.proxy.Proxy.ask, src.algitex.tools.proxy.Proxy.budget, src.algitex.tools.proxy.Proxy.models, src.algitex.tools.proxy.Proxy.health, src.algitex.tools.proxy.Proxy.close, src.algitex.tools.proxy.Proxy.__enter__, src.algitex.tools.proxy.Proxy.__exit__

### src.algitex.workflows.Pipeline
> Composable workflow: chain steps fluently.
- **Methods**: 8
- **Key Methods**: src.algitex.workflows.Pipeline.__init__, src.algitex.workflows.Pipeline.analyze, src.algitex.workflows.Pipeline.create_tickets, src.algitex.workflows.Pipeline.execute, src.algitex.workflows.Pipeline.validate, src.algitex.workflows.Pipeline.sync, src.algitex.workflows.Pipeline.report, src.algitex.workflows.Pipeline.finish

### src.algitex.workflows.TicketExecutor
> Handles ticket execution with Docker tools, telemetry, context, and feedback.
- **Methods**: 8
- **Key Methods**: src.algitex.workflows.TicketExecutor.__init__, src.algitex.workflows.TicketExecutor.execute_tickets, src.algitex.workflows.TicketExecutor._get_open_tickets, src.algitex.workflows.TicketExecutor._execute_single_ticket, src.algitex.workflows.TicketExecutor._call_tool_with_context, src.algitex.workflows.TicketExecutor._validate_with_vallm, src.algitex.workflows.TicketExecutor._mark_ticket_done, src.algitex.workflows.TicketExecutor._build_fix_prompt

### src.algitex.tools.todo_parser.TodoParser
> Parse todo lists from Markdown and text files.
- **Methods**: 7
- **Key Methods**: src.algitex.tools.todo_parser.TodoParser.__init__, src.algitex.tools.todo_parser.TodoParser.parse, src.algitex.tools.todo_parser.TodoParser._parse_prefact, src.algitex.tools.todo_parser.TodoParser._parse_github, src.algitex.tools.todo_parser.TodoParser._parse_generic, src.algitex.tools.todo_parser.TodoParser._extract_location, src.algitex.tools.todo_parser.TodoParser.get_stats

### src.algitex.tools.analysis.Analyzer
> Unified interface for code analysis tools.
- **Methods**: 6
- **Key Methods**: src.algitex.tools.analysis.Analyzer.__init__, src.algitex.tools.analysis.Analyzer.health, src.algitex.tools.analysis.Analyzer.full, src.algitex.tools.analysis.Analyzer._run_code2llm, src.algitex.tools.analysis.Analyzer._run_vallm, src.algitex.tools.analysis.Analyzer._run_redup

### src.algitex.tools.feedback.FeedbackLoop
> Integrates feedback controller into the pipeline execution.
- **Methods**: 6
- **Key Methods**: src.algitex.tools.feedback.FeedbackLoop.__init__, src.algitex.tools.feedback.FeedbackLoop.execute_with_feedback, src.algitex.tools.feedback.FeedbackLoop._execute_single, src.algitex.tools.feedback.FeedbackLoop._validate_result, src.algitex.tools.feedback.FeedbackLoop._mark_ticket_done, src.algitex.tools.feedback.FeedbackLoop._mark_ticket_skipped

### src.algitex.tools.feedback.FeedbackController
> Orchestrate retry/replan/escalate decisions.
- **Methods**: 5
- **Key Methods**: src.algitex.tools.feedback.FeedbackController.__init__, src.algitex.tools.feedback.FeedbackController.on_validation_failure, src.algitex.tools.feedback.FeedbackController.on_success, src.algitex.tools.feedback.FeedbackController.needs_approval, src.algitex.tools.feedback.FeedbackController._extract_feedback

### src.algitex.tools.telemetry.TraceSpan
> Single operation span.
- **Methods**: 4
- **Key Methods**: src.algitex.tools.telemetry.TraceSpan.duration_s, src.algitex.tools.telemetry.TraceSpan.finish, src.algitex.tools.telemetry.TraceSpan.__enter__, src.algitex.tools.telemetry.TraceSpan.__exit__

### src.algitex.tools.context.SemanticCache
> Optional semantic caching using Qdrant for context retrieval.
- **Methods**: 4
- **Key Methods**: src.algitex.tools.context.SemanticCache.__init__, src.algitex.tools.context.SemanticCache._get_client, src.algitex.tools.context.SemanticCache.search_similar_context, src.algitex.tools.context.SemanticCache.store_context

## Data Transformation Functions

Key functions that process and transform data:

### src.algitex.cli.workflow_validate
> Check a Propact workflow for errors.
- **Output to**: workflow_app.command, typer.Argument, Workflow, wf.validate, console.print

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

### src.algitex.tools.todo_runner.TodoRunner._format_output
> Extract meaningful output from MCP result.
- **Output to**: isinstance, isinstance, json.dumps, str, str

### src.algitex.propact.Workflow.parse
> Parse Markdown into executable steps.
- **Output to**: self.path.read_text, HEADING_PATTERN.search, enumerate, self.path.exists, FileNotFoundError

### src.algitex.propact.Workflow.validate
> Check workflow for errors without executing.
- **Output to**: self.parse, None.split, errors.append, step.content.strip, None.strip

### src.algitex.tools.feedback.FeedbackLoop._validate_result
> Validate the execution result.
- **Output to**: self.docker_mgr.list_tools, self.docker_mgr.call_tool

### src.algitex.workflows.Pipeline.validate
> Step: multi-level validation (static + runtime + security).
- **Output to**: TicketValidator, validator.validate_all, self._steps.append, DockerToolManager, validation_results.get

### src.algitex.workflows.TicketExecutor._validate_with_vallm
> Validate ticket execution with vallm.
- **Output to**: self.docker_mgr.call_tool, validation.get, self._mark_ticket_done

### src.algitex.workflows.TicketValidator.validate_all
> Run all validation levels.
- **Output to**: all, self.docker_mgr.list_tools, self.docker_mgr.call_tool, static.get, self.docker_mgr.list_tools

## Behavioral Patterns

### recursion_list
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: src.algitex.tools.tickets.Tickets.list

### state_machine_Proxy
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.proxy.Proxy.__init__, src.algitex.tools.proxy.Proxy.ask, src.algitex.tools.proxy.Proxy.budget, src.algitex.tools.proxy.Proxy.models, src.algitex.tools.proxy.Proxy.health

### state_machine_LoopState
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.algo.LoopState.deterministic_ratio, src.algitex.algo.LoopState.stage_name

### state_machine_TraceSpan
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.telemetry.TraceSpan.duration_s, src.algitex.tools.telemetry.TraceSpan.finish, src.algitex.tools.telemetry.TraceSpan.__enter__, src.algitex.tools.telemetry.TraceSpan.__exit__

### state_machine_TodoExecutor
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.todo_executor.TodoExecutor.__init__, src.algitex.tools.todo_executor.TodoExecutor.__enter__, src.algitex.tools.todo_executor.TodoExecutor.__exit__, src.algitex.tools.todo_executor.TodoExecutor.run, src.algitex.tools.todo_executor.TodoExecutor._execute_task

### state_machine_TodoRunner
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.todo_runner.TodoRunner.__init__, src.algitex.tools.todo_runner.TodoRunner.__enter__, src.algitex.tools.todo_runner.TodoRunner.__exit__, src.algitex.tools.todo_runner.TodoRunner.run_from_file, src.algitex.tools.todo_runner.TodoRunner.run

### state_machine_DockerToolManager
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.algitex.tools.docker.DockerToolManager.__init__, src.algitex.tools.docker.DockerToolManager.__enter__, src.algitex.tools.docker.DockerToolManager.__exit__, src.algitex.tools.docker.DockerToolManager._load_tools, src.algitex.tools.docker.DockerToolManager._load_state

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `examples.05-cost-tracking.main.main` - 40 calls
- `examples.09-workspace.main.advanced_workspace_features` - 37 calls
- `examples.02-algo-loop.main.main` - 33 calls
- `examples.07-context.main.basic_context_example` - 33 calls
- `examples.06-telemetry.main.basic_telemetry_example` - 30 calls
- `examples.10-cicd.main.complete_ci_cd_setup` - 29 calls
- `src.algitex.project.Project.status` - 27 calls
- `examples.03-pipeline.main.main` - 27 calls
- `examples.04-ide-integration.main.main` - 26 calls
- `examples.07-context.main.prompt_engineering_example` - 26 calls
- `src.algitex.cli.init` - 23 calls
- `examples.07-context.main.context_optimization_example` - 22 calls
- `examples.08-feedback.main.basic_feedback_example` - 22 calls
- `examples.01-quickstart.main.main` - 21 calls
- `src.algitex.tools.feedback.FeedbackLoop.execute_with_feedback` - 21 calls
- `src.algitex.cli.go` - 19 calls
- `src.algitex.cli.todo_run` - 19 calls
- `examples.08-feedback.main.cost_optimization_example` - 19 calls
- `examples.09-workspace.main.workspace_management_example` - 19 calls
- `examples.09-workspace.main.cross_repo_planning_example` - 19 calls
- `examples.07-context.main.semantic_search_example` - 18 calls
- `examples.08-feedback.main.feedback_loop_simulation` - 18 calls
- `src.algitex.cli.plan` - 17 calls
- `src.algitex.tools.docker.DockerToolManager.get_capabilities` - 17 calls
- `src.algitex.propact.Workflow.execute` - 17 calls
- `examples.09-workspace.main.create_sample_workspace` - 17 calls
- `examples.09-workspace.main.workspace_execution_example` - 17 calls
- `src.algitex.cli.todo_list` - 16 calls
- `examples.10-cicd.main.basic_github_actions_example` - 16 calls
- `examples.08-feedback.main.escalation_scenarios` - 16 calls
- `examples.09-workspace.main.cross_repo_analysis_example` - 16 calls
- `src.algitex.cli.todo_fix` - 15 calls
- `src.algitex.tools.proxy.Proxy.ask` - 15 calls
- `examples.10-cicd.main.quality_gates_example` - 15 calls
- `examples.10-cicd.main.precommit_hooks_example` - 15 calls
- `examples.10-cicd.main.multi_platform_ci_example` - 15 calls
- `src.algitex.cli.algo_extract` - 14 calls
- `src.algitex.project.Project.execute` - 14 calls
- `src.algitex.algo.Loop.extract` - 14 calls
- `src.algitex.propact.Workflow.parse` - 14 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> print
    main --> Tickets
    advanced_workspace_f --> print
    advanced_workspace_f --> create_sample_worksp
    advanced_workspace_f --> Workspace
    advanced_workspace_f --> find_repos_by_tag
    main --> Loop
    main --> discover
    main --> report
    basic_context_exampl --> print
    basic_context_exampl --> Path
    basic_context_exampl --> mkdir
    basic_context_exampl --> write_text
    basic_telemetry_exam --> print
    basic_telemetry_exam --> Telemetry
    basic_telemetry_exam --> span
    basic_telemetry_exam --> sleep
    complete_ci_cd_setup --> print
    complete_ci_cd_setup --> Path
    complete_ci_cd_setup --> mkdir
    complete_ci_cd_setup --> write_text
    complete_ci_cd_setup --> CICDGenerator
    status --> board
    status --> Proxy
    status --> budget
    status --> health
    status --> close
    main --> items
    prompt_engineering_e --> print
    prompt_engineering_e --> Path
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.