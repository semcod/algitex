"""Docker subcommands for algitex CLI."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def docker_list() -> None:
    """List available Docker tools from docker-tools.yaml."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config

    mgr = DockerToolManager(Config.load())
    running = mgr.list_running()

    table = Table(title="Docker Tools")
    table.add_column("Status", style="bold")
    table.add_column("Tool", style="bold")
    table.add_column("Transport")
    table.add_column("Image")

    for name in mgr.list_tools():
        tool = mgr._tools[name]
        status = "\u25cf" if name in running else "\u25cb"
        table.add_row(status, name, tool.transport, tool.image)
    console.print(table)


def docker_spawn(tool_name: str = typer.Argument(...)) -> None:
    """Start a Docker tool container."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config

    mgr = DockerToolManager(Config.load())
    try:
        rt = mgr.spawn(tool_name)
        console.print(f"  \u25cf {tool_name} \u2192 {rt.container_id}")
        if rt.endpoint:
            console.print(f"  Endpoint: {rt.endpoint}")
    except Exception as e:
        console.print(f"\u274c Failed to spawn {tool_name}: {e}")


def docker_call(
    tool_name: str = typer.Argument(...),
    action: str = typer.Argument(...),
    input_json: Optional[str] = typer.Option(None, "--input", "-i", help="JSON input")
):
    """Call an MCP tool on a running Docker container."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config
    import json

    mgr = DockerToolManager(Config.load())
    args = json.loads(input_json) if input_json else {}

    try:
        result = mgr.call_tool(tool_name, action, args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"\u274c Failed to call {tool_name}.{action}: {e}")


def docker_teardown(tool_name: Optional[str] = typer.Argument(None)):
    """Stop Docker tool containers."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config

    mgr = DockerToolManager(Config.load())
    if tool_name:
        mgr.teardown(tool_name)
        console.print(f"  \u25cb {tool_name} stopped")
    else:
        mgr.teardown_all()
        console.print("  \u25cb All tools stopped")


def docker_caps(tool_name: str = typer.Argument(...)):
    """List MCP capabilities of a Docker tool."""
    from algitex.tools.docker import DockerToolManager
    from algitex.config import Config

    mgr = DockerToolManager(Config.load())

    if tool_name not in mgr.list_running():
        console.print(f"Spawning {tool_name} to check capabilities...")
        mgr.spawn(tool_name)

    for cap in mgr.get_capabilities(tool_name):
        console.print(f"  \u2192 {cap}")
