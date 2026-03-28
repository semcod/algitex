"""MCP service orchestration mixins for Project class."""

from __future__ import annotations

from typing import Optional

from algitex.tools.mcp import MCPOrchestrator


class MCPMixin:
    """MCP service orchestration functionality for Project."""

    def __init__(self) -> None:
        self.mcp = MCPOrchestrator()

    def start_mcp_services(self, services: Optional[list] = None) -> bool:
        """Start MCP services."""
        return self.mcp.start_all(services)

    def stop_mcp_services(self) -> bool:
        """Stop all MCP services."""
        return self.mcp.stop_all()

    def restart_mcp_service(self, service: str) -> bool:
        """Restart a specific MCP service."""
        return self.mcp.restart_service(service)

    def wait_for_mcp_ready(self, timeout: int = 60) -> bool:
        """Wait for MCP services to be ready."""
        return self.mcp.wait_for_ready(timeout=timeout)

    def get_mcp_status(self) -> dict:
        """Get MCP services status."""
        return {
            name: status.to_dict()
            for name, status in self.mcp.check_health().items()
        }

    def print_mcp_status(self):
        """Print MCP services status."""
        self.mcp.print_status()

    def generate_mcp_config(self) -> bool:
        """Generate MCP client configuration."""
        from pathlib import Path
        return self.mcp.generate_mcp_config(Path(".") / "mcp_config.json")
