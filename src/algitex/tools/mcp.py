"""MCP (Model Context Protocol) service orchestration — manage multiple MCP services.

Usage:
    from algitex.tools.mcp import MCPOrchestrator

    # Start services
    orchestrator = MCPOrchestrator()
    orchestrator.start_all()
    orchestrator.wait_for_ready()
"""

from __future__ import annotations

import json
import signal
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from algitex.tools.mcp_defaults import build_default_services
from algitex.tools.mcp_lifecycle import MCPLifecycleManager
from algitex.tools.services import ServiceChecker, ServiceStatus


class MCPOrchestrator(MCPLifecycleManager):
    """Orchestrates multiple MCP services."""

    def __init__(self):
        super().__init__(build_default_services())
        self.service_checker = ServiceChecker()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def handler(signum, frame) -> None:
            self.stop_all()
            exit(0)

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def start_all(self, services: Optional[List[str]] = None) -> bool:
        """Start all or specified services."""
        if services is None:
            services = list(self.services.keys())

        success = True

        # Start services in dependency order
        started = set()
        attempts = 0
        max_attempts = len(services) * 2

        while len(started) < len(services) and attempts < max_attempts:
            attempts += 1

            for name in services:
                if name in started:
                    continue

                service = self.services[name]

                # Check if dependencies are ready
                deps_ready = all(
                    dep in started and self.services[dep].ready
                    for dep in service.dependencies
                )

                if deps_ready:
                    if self.start_service(name):
                        started.add(name)
                    else:
                        success = False

        return success

    def stop_all(self, timeout: int = 10) -> bool:
        """Stop all services."""
        print("Stopping all MCP services...")

        # Stop in reverse order
        success = True
        for name in reversed(list(self.services.keys())):
            if not self.stop_service(name, timeout):
                success = False

        return success

    def wait_for_ready(
        self, services: Optional[List[str]] = None, timeout: int = 60
    ) -> bool:
        """Wait for services to be ready."""
        if services is None:
            services = list(self.services.keys())

        print("Waiting for services to be ready...")

        start_time = time.time()
        ready_services = set()

        while len(ready_services) < len(services):
            if time.time() - start_time > timeout:
                print("❌ Timeout waiting for services")
                not_ready = set(services) - ready_services
                print(f"   Not ready: {', '.join(not_ready)}")
                return False

            for name in services:
                if name in ready_services:
                    continue

                service = self.services[name]

                # Check via health endpoint
                if service.health_endpoint:
                    status = self.service_checker.check_http_service(
                        name, service.health_endpoint
                    )
                    if status.healthy:
                        service.ready = True
                        ready_services.add(name)
                        print(f"✅ {name} ready")
                else:
                    # Check if process is running
                    if service.process and service.process.poll() is None:
                        service.ready = True
                        ready_services.add(name)
                        print(f"✅ {name} running")

            time.sleep(1)

        print("All services ready!")
        return True

    def check_health(self) -> Dict[str, ServiceStatus]:
        """Check health of all services."""
        statuses = {}

        for name, service in self.services.items():
            if service.health_endpoint:
                status = self.service_checker.check_http_service(
                    name, service.health_endpoint
                )
                statuses[name] = status
            else:
                # Simple process check
                if service.process and service.process.poll() is None:
                    statuses[name] = ServiceStatus(
                        name=name, healthy=True, details={"pid": service.process.pid}
                    )
                else:
                    statuses[name] = ServiceStatus(
                        name=name, healthy=False, error="Process not running"
                    )

        return statuses

    def get_logs(self, name: str, lines: int = 50) -> str:
        """Get logs from a service."""
        if name not in self.services:
            return f"Unknown service: {name}"

        service = self.services[name]

        if not service.process:
            return f"Service {name} is not running"

        # Note: This is a simplified approach
        # In practice, you'd want to capture logs properly
        stdout = service.process.stdout.read() if service.process.stdout else ""
        stderr = service.process.stderr.read() if service.process.stderr else ""

        output = []
        if stdout:
            output.append("STDOUT:")
            output.append(stdout)
        if stderr:
            output.append("STDERR:")
            output.append(stderr)

        return "\n".join(output)

    def list_services(self) -> List[str]:
        """List all registered services."""
        return list(self.services.keys())

    def get_service_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a service."""
        if name not in self.services:
            return None

        service = self.services[name]

        info = {
            "name": service.name,
            "command": service.command,
            "port": service.port,
            "dependencies": service.dependencies,
            "running": service.process is not None and service.process.poll() is None,
            "ready": service.ready,
        }

        if service.process:
            info["pid"] = service.process.pid

        return info

    def print_status(self) -> None:
        """Print status of all services."""
        print("\nMCP Services Status")
        print("=" * 60)

        for name in self.services:
            info = self.get_service_info(name)
            if not info:
                continue

            status = "🟢" if info["running"] else "🔴"
            ready = "✅" if info["ready"] else "❌"

            print(
                f"{status} {name:<15} PID: {info.get('pid', 'N/A'):<8} Ready: {ready}"
            )

            if info["dependencies"]:
                print(f"   Dependencies: {', '.join(info['dependencies'])}")

        print()

    def generate_mcp_config(
        self, output_path: Union[str, Path] = "mcp_config.json"
    ) -> bool:
        """Generate MCP client configuration."""
        config = {"mcpServers": {}}

        for name, service in self.services.items():
            if service.port:
                config["mcpServers"][name] = {
                    "command": "stdio",
                    "env": {"MCP_SERVER_PORT": str(service.port)},
                }
            else:
                config["mcpServers"][name] = {
                    "command": service.command[0],
                    "args": service.command[1:],
                    "env": service.env,
                }

        try:
            with open(output_path, "w") as f:
                json.dump(config, f, indent=2)
            print(f"Created: {output_path}")
            return True
        except Exception as e:
            print(f"Failed to write MCP config: {e}")
            return False
