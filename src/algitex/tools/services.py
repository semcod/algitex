"""Service health checker — unified monitoring for external services.

Usage:
    from algitex.tools.services import ServiceChecker
    
    checker = ServiceChecker()
    status = checker.check_all()
    checker.print_status(status)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from pathlib import Path

import httpx
import subprocess
import time


@dataclass
class ServiceStatus:
    """Status of a single service."""
    name: str
    healthy: bool
    url: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def status_icon(self) -> str:
        """Get status icon for display."""
        return "✅" if self.healthy else "❌"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "healthy": self.healthy,
            "url": self.url,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
            "details": self.details
        }


class ServiceChecker:
    """Checker for various services used by algitex."""
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
    
    def check_http_service(
        self,
        name: str,
        url: str,
        health_path: str = "/health",
        expected_status: int = 200
    ) -> ServiceStatus:
        """Check an HTTP service."""
        full_url = url.rstrip("/") + health_path
        
        start_time = time.time()
        try:
            response = self._client.get(full_url)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == expected_status:
                details = {}
                try:
                    if response.content:
                        details = response.json()
                except json.JSONDecodeError:
                    pass
                
                return ServiceStatus(
                    name=name,
                    healthy=True,
                    url=url,
                    response_time_ms=response_time,
                    details=details
                )
            else:
                return ServiceStatus(
                    name=name,
                    healthy=False,
                    url=url,
                    response_time_ms=response_time,
                    error=f"HTTP {response.status_code}"
                )
        except httpx.RequestError as e:
            return ServiceStatus(
                name=name,
                healthy=False,
                url=url,
                error=str(e)
            )
    
    def check_ollama(self, host: str = "http://localhost:11434") -> ServiceStatus:
        """Check Ollama service."""
        start_time = time.time()
        try:
            response = self._client.get(f"{host}/api/tags")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                
                return ServiceStatus(
                    name="ollama",
                    healthy=True,
                    url=host,
                    response_time_ms=response_time,
                    details={
                        "models_count": len(models),
                        "models": models[:10],  # Show first 10
                        "total_models": len(models)
                    }
                )
            else:
                return ServiceStatus(
                    name="ollama",
                    healthy=False,
                    url=host,
                    error=f"HTTP {response.status_code}"
                )
        except Exception as e:
            return ServiceStatus(
                name="ollama",
                healthy=False,
                url=host,
                error=str(e)
            )
    
    def check_litellm_proxy(self, url: str = "http://localhost:4000") -> ServiceStatus:
        """Check LiteLLM proxy."""
        start_time = time.time()
        try:
            response = self._client.get(f"{url}/v1/models")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                models = [m["id"] for m in data.get("data", [])]
                
                return ServiceStatus(
                    name="litellm-proxy",
                    healthy=True,
                    url=url,
                    response_time_ms=response_time,
                    details={
                        "models_count": len(models),
                        "models": models[:10],
                        "total_models": len(models)
                    }
                )
            else:
                return ServiceStatus(
                    name="litellm-proxy",
                    healthy=False,
                    url=url,
                    error=f"HTTP {response.status_code}"
                )
        except Exception as e:
            return ServiceStatus(
                name="litellm-proxy",
                healthy=False,
                url=url,
                error=str(e)
            )
    
    def check_mcp_service(self, name: str, port: int) -> ServiceStatus:
        """Check an MCP service by port."""
        url = f"http://localhost:{port}"
        return self.check_http_service(name, url, "/health")
    
    def check_command_exists(self, name: str, command: str) -> ServiceStatus:
        """Check if a command-line tool exists."""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                path = result.stdout.strip()
                return ServiceStatus(
                    name=name,
                    healthy=True,
                    url=path,
                    details={"path": path}
                )
            else:
                return ServiceStatus(
                    name=name,
                    healthy=False,
                    url="",
                    error="Command not found"
                )
        except subprocess.TimeoutExpired:
            return ServiceStatus(
                name=name,
                healthy=False,
                url="",
                error="Timeout checking command"
            )
        except Exception as e:
            return ServiceStatus(
                name=name,
                healthy=False,
                url="",
                error=str(e)
            )
    
    def check_file_exists(self, name: str, path: str) -> ServiceStatus:
        """Check if a file exists."""
        file_path = Path(path)
        
        if file_path.exists():
            details = {
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            }
            return ServiceStatus(
                name=name,
                healthy=True,
                url=str(file_path),
                details=details
            )
        else:
            return ServiceStatus(
                name=name,
                healthy=False,
                url=str(file_path),
                error="File not found"
            )
    
    def check_all(self, services: Optional[Dict[str, Any]] = None) -> List[ServiceStatus]:
        """Check all known services."""
        if services is None:
            services = {
                "ollama": {"host": "http://localhost:11434"},
                "litellm-proxy": {"url": "http://localhost:4000"},
                "code2llm-mcp": {"port": 8081},
                "vallm-mcp": {"port": 8080},
                "planfile-mcp": {"port": 8201},
                "aider": {"command": "aider"},
                "litellm": {"command": "litellm"},
                "prefact": {"command": "prefact"},
                "TODO.md": {"path": "TODO.md"},
            }
        
        statuses = []
        
        for service_name, config in services.items():
            if service_name == "ollama":
                statuses.append(self.check_ollama(config.get("host", "http://localhost:11434")))
            elif service_name == "litellm-proxy":
                statuses.append(self.check_litellm_proxy(config.get("url", "http://localhost:4000")))
            elif service_name.endswith("-mcp"):
                statuses.append(self.check_mcp_service(service_name, config["port"]))
            elif "command" in config:
                statuses.append(self.check_command_exists(service_name, config["command"]))
            elif "path" in config:
                statuses.append(self.check_file_exists(service_name, config["path"]))
            elif "url" in config:
                statuses.append(self.check_http_service(service_name, config["url"]))
        
        return statuses
    
    def _format_status_line(self, status: ServiceStatus) -> str:
        """Format a single status line."""
        line = f"{status.status_icon} {status.name:<20}"
        
        if status.response_time_ms:
            line += f" ({status.response_time_ms:.0f}ms)"
        
        if status.error:
            line += f" - {status.error}"
        
        return line

    def _print_status_details(self, status: ServiceStatus):
        """Print detailed information for a status."""
        if not status.details:
            return
            
        for key, value in status.details.items():
            if key == "models" and isinstance(value, list):
                print(f"    {key}: {', '.join(value[:5])}")
                if len(value) > 5:
                    print(f"    ... and {len(value) - 5} more")
            elif key == "models_count":
                print(f"    {key}: {value}")
            elif key == "path":
                print(f"    {key}: {value}")

    def print_status(self, statuses: List[ServiceStatus], show_details: bool = False):
        """Print service statuses in a formatted way."""
        print("\n" + "=" * 60)
        print("Service Status Check")
        print("=" * 60)
        
        healthy_count = sum(1 for s in statuses if s.healthy)
        total_count = len(statuses)
        
        for status in statuses:
            line = self._format_status_line(status)
            print(line)
            
            if show_details:
                self._print_status_details(status)
        
        print("-" * 60)
        print(f"Summary: {healthy_count}/{total_count} services healthy")
        
        if healthy_count == total_count:
            print("✅ All services ready!")
        else:
            print("⚠️  Some services need attention")
    
    def get_unhealthy(self, statuses: List[ServiceStatus]) -> List[ServiceStatus]:
        """Get list of unhealthy services."""
        return [s for s in statuses if not s.healthy]
    
    def wait_for_services(
        self,
        services: List[str],
        timeout_seconds: int = 60,
        check_interval: float = 2.0
    ) -> bool:
        """Wait for specific services to become healthy."""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            statuses = self.check_all()
            service_map = {s.name: s for s in statuses}
            
            all_healthy = all(service_map.get(s, ServiceStatus(s, False, "")).healthy for s in services)
            
            if all_healthy:
                return True
            
            time.sleep(check_interval)
        
        return False
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class ServiceDependency:
    """Manage service dependencies and startup order."""
    
    def __init__(self, checker: Optional[ServiceChecker] = None):
        self.checker = checker or ServiceChecker()
        self.dependencies = {
            "ollama": [],
            "litellm-proxy": ["ollama"],
            "code2llm-mcp": [],
            "vallm-mcp": [],
            "planfile-mcp": [],
        }
    
    def get_startup_order(self, services: List[str]) -> List[str]:
        """Get services in dependency order."""
        ordered = []
        visited = set()
        
        def visit(service: str):
            if service in visited or service not in services:
                return
            visited.add(service)
            
            for dep in self.dependencies.get(service, []):
                if dep in services:
                    visit(dep)
            
            ordered.append(service)
        
        for service in services:
            visit(service)
        
        return ordered
    
    def check_with_dependencies(self, services: List[str]) -> Dict[str, ServiceStatus]:
        """Check services with dependency awareness."""
        statuses = self.checker.check_all()
        status_map = {s.name: s for s in statuses}
        
        # Mark services as unhealthy if dependencies are not met
        for service in services:
            for dep in self.dependencies.get(service, []):
                if dep in status_map and not status_map[dep].healthy:
                    if service in status_map:
                        status_map[service].healthy = False
                        status_map[service].error = f"Dependency {dep} not healthy"
        
        return status_map
