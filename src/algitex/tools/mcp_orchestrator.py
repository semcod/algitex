"""MCP service orchestration."""

from __future__ import annotations

import signal
from typing import Dict, List, Optional

from algitex.tools.mcp_defaults import build_default_services
from algitex.tools.mcp_lifecycle import MCPLifecycleManager
from algitex.tools.mcp_models import MCPService
from algitex.tools.services import ServiceChecker


class MCPOrchestrator:
    """Orchestrates multiple MCP services."""

    def __init__(self):
        self.services: Dict[str, MCPService] = {}
        self.service_checker = ServiceChecker()
        self.lifecycle = MCPLifecycleManager(self.services)
        self._register_default_services()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def handler(signum, frame) -> None:
            self.stop_all()
            exit(0)

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def _register_default_services(self):
        """Register default MCP services."""
        self.services.update(build_default_services())

    def add_service(self, service: MCPService) -> None:
        self.lifecycle.add_service(service)

    def add_custom_service(
        self,
        name: str,
        command: List[str],
        port: Optional[int] = None,
        **kwargs,
    ):
        return self.lifecycle.add_custom_service(name, command, port, **kwargs)

    def start_service(self, name: str) -> bool:
        return self.lifecycle.start_service(name)

    def stop_service(self, name: str, timeout: int = 10) -> bool:
        return self.lifecycle.stop_service(name, timeout)

    def restart_service(self, name: str) -> bool:
        return self.lifecycle.restart_service(name)

    def start_all(self, services: Optional[List[str]] = None) -> bool:
        if services is None:
            services = list(self.services.keys())

        success = True
        started = set()
        attempts = 0
        max_attempts = len(services) * 2

        while len(started) < len(services) and attempts < max_attempts:
            attempts += 1

            for name in services:
                if name in started:
                    continue

                service = self.services[name]
                deps_ready = all(
                    dep in started and self.services[dep].ready
                    for dep in service.dependencies
                )

                if deps_ready:
                    if self.start_service(name):
                        started.add(name)
                    else:
                        success = False

        return success and len(started) == len(services)

    def stop_all(self, services: Optional[List[str]] = None) -> bool:
        if services is None:
            services = list(self.services.keys())

        success = True
        for name in reversed(services):
            if not self.stop_service(name):
                success = False
        return success

    def wait_for_ready(self, timeout: int = 60) -> bool:
        return True
