"""CLI — the algitex command.

Refactored: split into subcommand modules to reduce complexity.

Usage:
    algitex init ./my-app           # initialize
    algitex analyze                 # run all analysis
    algitex plan                    # generate sprint plan
    algitex go                      # full pipeline
    algitex status                  # dashboard

    algitex ask "question"          # quick LLM query
    algitex ticket add "title"      # add ticket
    algitex ticket list             # show tickets
    algitex sync                    # push to GitHub/Jira

    algitex algo discover           # start trace collection
    algitex algo extract            # find patterns
    algitex algo rules              # generate deterministic replacements
    algitex algo report             # show progress

    algitex workflow run f.md       # execute Propact workflow
    algitex workflow validate f.md  # check syntax
    algitex tools                   # show installed tools
"""

from __future__ import annotations

import typer
from rich.console import Console

from algitex.cli.core import init, analyze, plan, go, status, tools, ask, sync
from algitex.cli.ticket import ticket_add, ticket_list, ticket_board
from algitex.cli.algo import algo_discover, algo_extract, algo_rules, algo_report
from algitex.cli.workflow import workflow_run, workflow_validate
from algitex.cli.docker import docker_list, docker_spawn, docker_call, docker_teardown, docker_caps
from algitex.cli.todo import todo_list, todo_run, todo_fix, todo_verify, todo_fix_parallel, todo_benchmark, todo_hybrid
from algitex.cli.parallel import parallel

# Main app
app = typer.Typer(
    name="algitex",
    help="Progressive algorithmization toolchain — from LLM to deterministic, from proxy to tickets.",
    no_args_is_help=True,
)

# Subcommand groups
ticket_app = typer.Typer(help="Manage tickets.")
algo_app = typer.Typer(help="Progressive algorithmization.")
workflow_app = typer.Typer(help="Propact Markdown workflows.")
docker_app = typer.Typer(help="Manage Docker-based development tools.")
todo_app = typer.Typer(help="Execute todo lists via Docker MCP.")

app.add_typer(ticket_app, name="ticket")
app.add_typer(algo_app, name="algo")
app.add_typer(workflow_app, name="workflow")
app.add_typer(docker_app, name="docker")
app.add_typer(todo_app, name="todo")

console = Console()

# Register core commands
app.command()(init)
app.command()(analyze)
app.command()(plan)
app.command()(go)
app.command()(status)
app.command()(tools)
app.command()(ask)
app.command()(sync)
app.command()(parallel)

# Register ticket subcommands
ticket_app.command("add")(ticket_add)
ticket_app.command("list")(ticket_list)
ticket_app.command("board")(ticket_board)

# Register algo subcommands
algo_app.command("discover")(algo_discover)
algo_app.command("extract")(algo_extract)
algo_app.command("rules")(algo_rules)
algo_app.command("report")(algo_report)

# Register workflow subcommands
workflow_app.command("run")(workflow_run)
workflow_app.command("validate")(workflow_validate)

# Register docker subcommands
docker_app.command("list")(docker_list)
docker_app.command("spawn")(docker_spawn)
docker_app.command("call")(docker_call)
docker_app.command("teardown")(docker_teardown)
docker_app.command("caps")(docker_caps)

# Register todo subcommands
todo_app.command("list")(todo_list)
todo_app.command("run")(todo_run)
todo_app.command("fix")(todo_fix)
todo_app.command("verify")(todo_verify)
todo_app.command("fix-auto")(todo_fix_parallel)
todo_app.command("benchmark")(todo_benchmark)
todo_app.command("hybrid")(todo_hybrid)

# Top-level convenience command: algitex fix = algitex todo hybrid
app.command("fix", help="Quick hybrid autofix (alias for 'todo hybrid')")(todo_hybrid)

# Backward compatibility
__all__ = [
    "app", "console",
    "init", "analyze", "plan", "go", "status", "tools", "ask", "sync",
    "ticket_add", "ticket_list", "ticket_board",
    "algo_discover", "algo_extract", "algo_rules", "algo_report",
    "workflow_run", "workflow_validate",
    "docker_list", "docker_spawn", "docker_call", "docker_teardown", "docker_caps",
    "todo_list", "todo_run", "todo_fix", "todo_verify", "todo_fix_parallel", "todo_benchmark", "todo_hybrid",
]
