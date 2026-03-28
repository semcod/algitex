"""CLI — backward compatibility shim.

This module re-exports from the new cli package for backward compatibility.
New code should import directly from algitex.cli.
"""

# Re-export everything from the new package
from algitex.cli import (
    app,
    console,
    init, analyze, plan, go, status, tools, ask, sync,
    ticket_add, ticket_list, ticket_board,
    algo_discover, algo_extract, algo_rules, algo_report,
    workflow_run, workflow_validate,
    docker_list, docker_spawn, docker_call, docker_teardown, docker_caps,
    todo_list, todo_run, todo_fix, todo_verify, todo_fix_parallel, todo_benchmark, todo_hybrid,
)

if __name__ == "__main__":
    app()

__all__ = [
    "app", "console",
    "init", "analyze", "plan", "go", "status", "tools", "ask", "sync",
    "ticket_add", "ticket_list", "ticket_board",
    "algo_discover", "algo_extract", "algo_rules", "algo_report",
    "workflow_run", "workflow_validate",
    "docker_list", "docker_spawn", "docker_call", "docker_teardown", "docker_caps",
    "todo_list", "todo_run", "todo_fix", "todo_verify", "todo_fix_parallel", "todo_benchmark", "todo_hybrid",
]
