"""MCP (Model Context Protocol) service orchestration — manage multiple MCP services.

Usage:
    from algitex.tools.mcp import MCPOrchestrator
    
    # Start services
    orchestrator = MCPOrchestrator()
    orchestrator.start_all()
    orchestrator.wait_for_ready()
"""

from __future__,annotations

import json
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from algitex.tools.services import ServiceChecker, ServiceStatus


@dataclass
class MCPService:
    """Definition of an MCP service."""
    name: str
    command: List[str]
    port: Optional[int] = None
    health_endpoint: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    process: Optional[subprocess.Popen] = field(default=None, init=False)
    ready: bool = field(default=False, init=False)
    
    def __post_init__(self):
        if self.port and not self.health_endpoint:
            self.health_endpoint = f"http://localhost:{self.port}/health"


class MCPOrchestrator:
    """Orchestrates multiple MCP services."""
    
    def __init__(self):
        self.services: Dict[str, MCPService] = {}
        self.service_checker = ServiceChecker()
        self._register_default_services()
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def handler(signum, frame):
            self.stop_all()
            exit(0)
        
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
    
    def _register_default_services(self):
        """Register default MCP services."""
        # Aider MCP
        self.services["aider"] = MCPService(
            name="aider",
            command=["python", "-m", "algitex.docker.aider_mcp_server"],
            port=8001,
            health_endpoint="http://localhost:8001/health",
            dependencies=[]
        )
        
        # Code2LLM MCP
        self.services["code2llm"] = MCPService(
            name="code2llm",
            command=["python", "-m", "algitex.docker.code2llm_mcp_server"],
            port=8002,
            health_endpoint="http://localhost:8002/health",
            dependencies=[]
        )
        
        # Filesystem MCP
        self.services["filesystem"] = MCPService(
            name="filesystem",
            command=["npx", "@modelcontextprotocol/server-filesystem", "/tmp"],
            port=8003,
            dependencies=[]
        )
        
        # GitHub MCP
        self.services["github"] = MCPService(
            name="github",
            command=["npx", "@modelcontextprotocol/server-github"],
            env={"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
            port=8004,
            dependencies=[]
        )
        
        # Docker MCP
        self.services["docker"] = MCPService(
            name="docker",
            command=["npx", "@modelcontextprotocol/server-docker"],
            port=8005,
            dependencies=[]
        )
    
    def add_service(self, service: MCPService) -> None:
        """Add a custom service."""
        self.services[service.name] = service
    
    def add_custom_service(
        self,
        name: str,
        command: List[str],
        port: Optional[int] = None,
        **kwargs
    ):
        """Add a custom service by parameters."""
        service = MCPService(
            name=name,
            command=command,
            port=port,
            **kwargs
        )
        self.add_service(service)
    
    def start_service(self, name: str) -> bool:
        """Start a single service."""
        if name not in self.services:
            print(f"Unknown service: {name}")
            return False
        
        service = self.services[name]
        
        if service.process and service.process.poll() is None:
            print(f"Service {name} is already running")
            return True
        
        # Check dependencies
        for dep in service.dependencies:
            if dep not in self.services or not self.services[dep].ready:
                print(f"Dependency {dep} not ready for {name}")
                return False
        
        print(f"Starting {name}...")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(service.env)
            
            # Start process
            service.process = subprocess.Popen(
                service.command,
                env=env,
                cwd=service.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(1)
            
            if service.process.poll() is None:
                print(f"✅ {name} started (PID: {service.process.pid})")
                return True
            else:
                print(f"❌ {name} failed to start")
                stderr = service.process.stderr.read() if service.process.stderr else ""
                if stderr:
                    print(f"   Error: {stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False
    
    def stop_service(self, name: str, timeout: int = 10) -> bool:
        """Stop a single service."""
        if name not in self.services:
            print(f"Unknown service: {name}")
            return False
        
        service = self.services[name]
        
        if not service.process or service.process.poll() is not None:
            print(f"Service {name} is not running")
            return True
        
        print(f"Stopping {name}...")
        
        try:
            # Try graceful shutdown
            service.process.terminate()
            
            # Wait for graceful shutdown
            try:
                service.process.wait(timeout=timeout)
                print(f"✅ {name} stopped")
                return True
            except subprocess.TimeoutExpired:
                # Force kill
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
        """Restart a service."""
        print(f"Restarting {name}...")
        self.stop_service(name)
        time.sleep(1)
        return self.start_service(name)
    
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
        self,
        services: Optional[List[str]] = None,
        timeout: int = 60
    ) -> bool:
        """Wait for services to be ready."""
        if services is None:
            services = list(self.services.keys())
        
        print(f"Waiting for services to be ready...")
        
        start_time = time.time()
        ready_services = set()
        
        while len(ready_services) < len(services):
            if time.time() - start_time > timeout:
                print(f"❌ Timeout waiting for services")
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
                        name,
                        service.health_endpoint
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
        
        print(f"All services ready!")
        return True
    
    def check_health(self) -> Dict[str, ServiceStatus]:
        """Check health of all services."""
        statuses = {}
        
        for name, service in self.services.items():
            if service.health_endpoint:
                status = self.service_checker.check_http_service(
                    name,
                    service.health_endpoint
                )
                statuses[name] = status
            else:
                # Simple process check
                if service.process and service.process.poll() is None:
                    statuses[name] = ServiceStatus(
                        name=name,
                        healthy=True,
                        details={"pid": service.process.pid}
                    )
                else:
                    statuses[name] = ServiceStatus(
                        name=name,
                        healthy=False,
                        error="Process not running"
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
            "ready": service.ready
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
            
            print(f"{status} {name:<15} PID: {info.get('pid', 'N/A'):<8} Ready: {ready}")
            
            if info["dependencies"]:
                print(f"   Dependencies: {', '.join(info['dependencies'])}")
        
        print()
    
    def generate_mcp_config(
        self,
        output_path: Union[str, Path] = "mcp_config.json"
    ) -> bool:
        """Generate MCP client configuration."""
        config = {
            "mcpServers": {}
        }
        
        for name, service in self.services.items():
            if service.port:
                config["mcpServers"][name] = {
                    "command": "stdio",
                    "env": {
                        "MCP_SERVER_PORT": str(service.port)
                    }
                }
            else:
                config["mcpServers"][name] = {
                    "command": service.command[0],
                    "args": service.command[1:],
                    "env": service.env
                }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Created: {output_path}")
            return True
        except Exception as e:
            print(f"Failed to write MCP config: {e}")
            return False
