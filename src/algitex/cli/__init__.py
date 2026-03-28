"""CLI — the algitex command.

Refactored: split into subcommand modules to reduce complexity.
Uses clickmd for markdown-enhanced CLI output.
"""

from __future__ import annotations

import clickmd
from clickmd import (
    blockquote, render_md as markdown, group, command, option, argument,
    Path, Choice, INT, BOOL
)
from clickmd.help import success, warning, error, info, echo_md
from rich.console import Console

from algitex.cli.core import init, analyze, plan, go, status, tools, ask, sync
from algitex.cli.ticket import ticket_add, ticket_list, ticket_board
from algitex.cli.algo import algo_discover, algo_extract, algo_rules, algo_report
from algitex.cli.workflow import workflow_run, workflow_validate
from algitex.cli.docker import docker_list, docker_spawn, docker_call, docker_teardown, docker_caps
from algitex.cli.todo import todo_list, todo_run, todo_stats, todo_fix, todo_verify, todo_fix_parallel, todo_benchmark, todo_hybrid, todo_batch, todo_verify_prefact
from algitex.cli.microtask import microtask_classify, microtask_plan, microtask_run
from algitex.cli.nlp import nlp_dead_code, nlp_docstrings, nlp_duplicates, nlp_imports
from algitex.cli.parallel import parallel
from algitex.cli.metrics import metrics_show, metrics_clear, metrics_cache, metrics_compare
from algitex.cli.benchmark import benchmark_cache, benchmark_tiers, benchmark_memory, benchmark_full, benchmark_quick
from algitex.cli.dashboard import dashboard_live, dashboard_monitor, dashboard_export

console = Console()

# Main app group
main_help = """# Algitex CLI

Progressive algorithmization toolchain — from LLM to deterministic, from proxy to tickets.

## Commands

- **init** — Initialize algitex project
- **analyze** — Analyze codebase
- **plan** — Create execution plan
- **go** — Execute plan
- **status** — Show project status
- **tools** — List available tools
- **ask** — Ask questions about code
- **sync** — Sync project state
- **ticket** — Manage tickets
- **algo** — Progressive algorithmization
- **workflow** — Markdown workflows
- **docker** — Docker-based tools
- **todo** — Execute todo lists
- **microtask** — MicroTask pipeline
- **nlp** — NLP refactor helpers
- **metrics** — Metrics and observability
- **benchmark** — Performance benchmarks
- **dashboard** — Real-time monitoring

Use `algitex <command> --help` for more info.
"""


@group(invoke_without_command=True, no_args_is_help=True, help=markdown(main_help))
@clickmd.pass_context
def app(ctx):
    """Algitex CLI main group."""
    if ctx.invoked_subcommand is None:
        clickmd.echo(markdown(main_help))


# Subcommand groups
@group(help="Manage tickets.")
def ticket():
    """Ticket management commands."""
    pass


@group(help="Progressive algorithmization.")
def algo():
    """Algorithmization commands."""
    pass


@group(help="Propact Markdown workflows.")
def workflow():
    """Workflow commands."""
    pass


@group(help="Manage Docker-based development tools.")
def docker():
    """Docker management commands."""
    pass


@group(help="Execute todo lists via Docker MCP.")
def todo():
    """Todo execution commands."""
    pass


@group(help="Atomic MicroTask pipeline for small LLMs.")
def microtask():
    """Microtask pipeline commands."""
    pass


@group(help="Deterministic NLP refactor helpers.")
def nlp():
    """NLP helper commands."""
    pass


@group(help="Metrics and observability.")
def metrics():
    """Metrics commands."""
    pass


@group(help="Performance benchmarks.")
def benchmark():
    """Benchmark commands."""
    pass


@group(help="Real-time monitoring dashboard.")
def dashboard():
    """Dashboard commands."""
    pass


# Register subcommand groups
app.add_command(ticket, name="ticket")
app.add_command(algo, name="algo")
app.add_command(workflow, name="workflow")
app.add_command(docker, name="docker")
app.add_command(todo, name="todo")
app.add_command(microtask, name="microtask")
app.add_command(nlp, name="nlp")
app.add_command(metrics, name="metrics")
app.add_command(benchmark, name="benchmark")
app.add_command(dashboard, name="dashboard")

# Register main commands
app.add_command(init, name="init")
app.add_command(analyze, name="analyze")
app.add_command(plan, name="plan")
app.add_command(go, name="go")
app.add_command(status, name="status")
app.add_command(tools, name="tools")
app.add_command(ask, name="ask")
app.add_command(sync, name="sync")
app.add_command(parallel, name="parallel")

# Register ticket subcommands
ticket.add_command(ticket_add, name="add")
ticket.add_command(ticket_list, name="list")
ticket.add_command(ticket_board, name="board")

# Register algo subcommands
algo.add_command(algo_discover, name="discover")
algo.add_command(algo_extract, name="extract")
algo.add_command(algo_rules, name="rules")
algo.add_command(algo_report, name="report")

# Register workflow subcommands
workflow.add_command(workflow_run, name="run")
workflow.add_command(workflow_validate, name="validate")

# Register docker subcommands
docker.add_command(docker_list, name="list")
docker.add_command(docker_spawn, name="spawn")
docker.add_command(docker_call, name="call")
docker.add_command(docker_teardown, name="teardown")
docker.add_command(docker_caps, name="caps")

# Register todo subcommands
todo.add_command(todo_list, name="list")
todo.add_command(todo_run, name="run")
todo.add_command(todo_stats, name="stats")
todo.add_command(todo_fix, name="fix")
todo.add_command(todo_verify, name="verify")
todo.add_command(todo_fix_parallel, name="fix-auto")
todo.add_command(todo_benchmark, name="benchmark")
todo.add_command(todo_hybrid, name="hybrid")
todo.add_command(todo_batch, name="batch")
todo.add_command(todo_verify_prefact, name="verify-prefact")

# Register microtask subcommands
microtask.add_command(microtask_classify, name="classify")
microtask.add_command(microtask_plan, name="plan")
microtask.add_command(microtask_run, name="run")

# Register nlp subcommands
nlp.add_command(nlp_docstrings, name="docstrings")
nlp.add_command(nlp_imports, name="imports")
nlp.add_command(nlp_dead_code, name="dead-code")
nlp.add_command(nlp_duplicates, name="duplicates")

# Register metrics subcommands
metrics.add_command(metrics_show, name="show")
metrics.add_command(metrics_clear, name="clear")
metrics.add_command(metrics_cache, name="cache")
metrics.add_command(metrics_compare, name="compare")

# Register benchmark subcommands
benchmark.add_command(benchmark_cache, name="cache")
benchmark.add_command(benchmark_tiers, name="tiers")
benchmark.add_command(benchmark_memory, name="memory")
benchmark.add_command(benchmark_full, name="full")
benchmark.add_command(benchmark_quick, name="quick")

# Register dashboard subcommands
dashboard.add_command(dashboard_live, name="live")
dashboard.add_command(dashboard_monitor, name="monitor")
dashboard.add_command(dashboard_export, name="export")

# Backward compatibility
__all__ = [
    "app", "console",
    "ticket", "algo", "workflow", "docker", "todo", "microtask", "nlp", "metrics", "benchmark", "dashboard",
    "init", "analyze", "plan", "go", "status", "tools", "ask", "sync",
    "ticket_add", "ticket_list", "ticket_board",
    "algo_discover", "algo_extract", "algo_rules", "algo_report",
    "workflow_run", "workflow_validate",
    "docker_list", "docker_spawn", "docker_call", "docker_teardown", "docker_caps",
    "todo_list", "todo_run", "todo_stats", "todo_fix", "todo_verify", "todo_fix_parallel", "todo_benchmark", "todo_hybrid",
    "microtask_classify", "microtask_plan", "microtask_run",
    "nlp_docstrings", "nlp_imports", "nlp_dead_code", "nlp_duplicates",
    "metrics_show", "metrics_clear", "metrics_cache", "metrics_compare",
    "benchmark_cache", "benchmark_tiers", "benchmark_memory", "benchmark_full", "benchmark_quick",
    "dashboard_live", "dashboard_monitor", "dashboard_export",
]
