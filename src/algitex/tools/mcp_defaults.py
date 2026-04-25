"""Built-in default MCP service registrations."""

from __future__ import annotations

from typing import Dict

from algitex.tools.mcp_models import MCPService


def build_default_services() -> Dict[str, MCPService]:
    """Create the default MCP services registry."""
    services: Dict[str, MCPService] = {}

    services["aider"] = MCPService(
        name="aider",
        command=["python", "-m", "algitex.docker.aider_mcp_server"],
        port=8001,
        health_endpoint="http://localhost:8001/health",
        dependencies=[],
    )

    services["code2llm"] = MCPService(
        name="code2llm",
        command=["python", "-m", "algitex.docker.code2llm_mcp_server"],
        port=8002,
        health_endpoint="http://localhost:8002/health",
        dependencies=[],
    )

    services["filesystem"] = MCPService(
        name="filesystem",
        command=["npx", "@modelcontextprotocol/server-filesystem", "/tmp"],
        port=8003,
        dependencies=[],
    )

    services["github"] = MCPService(
        name="github",
        command=["npx", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
        port=8004,
        dependencies=[],
    )

    services["docker"] = MCPService(
        name="docker",
        command=["npx", "@modelcontextprotocol/server-docker"],
        port=8005,
        dependencies=[],
    )

    return services
