"""Lifecycle operations for MCP services."""

from __future__ import annotations

import os
import subprocess
import time
from typing import Dict, List, Optional

from algitex.tools.mcp_models import MCPService


class MCPLifecycleManager:
    """Start/stop/restart operations for MCP services."""

    def __init__(self, services: Dict[str, MCPService]):
        self.services = services

    def add_service(self, service: MCPService) -> None:
        self.services[service.name] = service

    def add_custom_service(
        self,
        name: str,
        command: List[str],
        port: Optional[int] = None,
        **kwargs,
    ) -> MCPService:
        service = MCPService(name=name, command=command, port=port, **kwargs)
        self.add_service(service)
        return service

    def start_service(self, name: str) -> bool:
        if name not in self.services:
            print(f"Unknown service: {name}")
            return False

        service = self.services[name]

        if service.process and service.process.poll() is None:
            print(f"Service {name} is already running")
            return True

        for dep in service.dependencies:
            if dep not in self.services or not self.services[dep].ready:
                print(f"Dependency {dep} not ready for {name}")
                return False

        print(f"Starting {name}...")

        try:
            env = os.environ.copy()
            env.update(service.env)

            service.process = subprocess.Popen(
                service.command,
                env=env,
                cwd=service.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            time.sleep(1)

            if service.process.poll() is None:
                print(f"✅ {name} started (PID: {service.process.pid})")
                return True

            print(f"❌ {name} failed to start")
            stderr = service.process.stderr.read() if service.process.stderr else ""
            if stderr:
                print(f"   Error: {stderr[:200]}")
            return False
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False

    def stop_service(self, name: str, timeout: int = 10) -> bool:
        if name not in self.services:
            print(f"Unknown service: {name}")
            return False

        service = self.services[name]

        if not service.process or service.process.poll() is not None:
            print(f"Service {name} is not running")
            return True

        print(f"Stopping {name}...")

        try:
            service.process.terminate()
            try:
                service.process.wait(timeout=timeout)
                print(f"✅ {name} stopped")
                return True
            except subprocess.TimeoutExpired:
                service.process.kill()
                service.process.wait()
                print(f"✅ {name} killed")
                return True
        except Exception as e:
            print(f"❌ Failed to stop {name}: {e}")
            return False
        finally:
            service.process = None
            service.ready = False

    def restart_service(self, name: str) -> bool:
        print(f"Restarting {name}...")
        self.stop_service(name)
        time.sleep(1)
        return self.start_service(name)
