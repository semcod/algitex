"""Docker tool manager — spawn, connect, call, teardown."""

from __future__,annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing,Optional

import httpx
import yaml

from algitex.config import Config
from algitex.tools import docker_transport


# ─── Models ───────────────────────────────────────────────

@dataclass
class DockerTool:
    """Single Docker-based tool declaration from docker-tools.yaml."""
    name: str
    image: str
    transport: str  # "mcp-stdio" | "mcp-sse" | "rest" | "cli"
    port: Optional[int] = None
    env: dict = field(default_factory=dict)
    volumes: list = field(default_factory=list)
    capabilities: list = field(default_factory=list)
    health_check: Optional[str] = None
    auto_remove: bool = True

    @property
    def is_mcp(self) -> bool:
        return self.transport.startswith("mcp")

    @property
    def is_rest(self) -> bool:
        return self.transport == "rest"


@dataclass
class RunningTool:
    """A spawned Docker container with connection info."""
    tool: DockerTool
    container_id: str
    process: Optional[subprocess.Popen] = None  # for stdio
    endpoint: Optional[str] = None               # for SSE/REST
    pid: Optional[int] = None                    # for tracking


# ─── DockerToolManager ───────────────────────────────────

class DockerToolManager:
    """Spawn Docker containers, connect via MCP/REST, call tools, teardown."""

    def __init__(self, config: Config):
        self.config = config
        self._running: dict[str, RunningTool] = {}
        self._tools: dict[str, DockerTool] = {}
        self._http_client: Optional[httpx.Client] = None
        self._state_file = Path(config.project_path) / ".algitex" / "docker-state.json"
        self._load_tools()
        self._load_state()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown_all()
        if self._http_client:
            self._http_client.close()

    def _load_tools(self):
        """Load tool declarations from docker-tools.yaml."""
        path = Path(self.config.project_path) / "docker-tools.yaml"
        if not path.exists():
            return
        
        # Read and expand environment variables
        content = path.read_text()
        content = os.path.expandvars(content)
        
        data = yaml.safe_load(content)
        for name, spec in data.get("tools", {}).items():
            # Expand environment variables in tool configuration
            if "env" in spec:
                for k, v in spec["env"].items():
                    if isinstance(v, str):
                        spec["env"][k] = os.path.expandvars(v)
            
            # Expand environment variables in volumes
            if "volumes" in spec:
                expanded_volumes = []
                for v in spec["volumes"]:
                    # Set default PROJECT_DIR if not in environment
                    if "${PROJECT_DIR}" in v and "PROJECT_DIR" not in os.environ:
                        v = v.replace("${PROJECT_DIR}", os.getcwd())
                    expanded_volumes.append(os.path.expandvars(v))
                spec["volumes"] = expanded_volumes
            
            self._tools[name] = DockerTool(name=name, **spec)

    def _load_state(self):
        """Load running container state from file."""
        if not self._state_file.exists():
            return
        
        try:
            state = json.loads(self._state_file.read_text())
            for name, data in state.get("running", {}).items():
                # Check if container is still running
                result = subprocess.run(
                    ["docker", "inspect", "-f", "{{.State.Running}}", data["container_id"]],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and result.stdout.strip() == "true":
                    tool = self._tools.get(name)
                    if tool:
                        rt = RunningTool(
                            tool=tool,
                            container_id=data["container_id"],
                            endpoint=data.get("endpoint"),
                            pid=data.get("pid"),
                        )
                        self._running[name] = rt
        except Exception:
            pass  # Ignore state loading errors

    def _save_state(self):
        """Save running container state to file."""
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "running": {
                name: {
                    "container_id": rt.container_id,
                    "endpoint": rt.endpoint,
                    "pid": rt.pid,
                }
                for name, rt in self._running.items()
            }
        }
        self._state_file.write_text(json.dumps(state, indent=2))

    # ─── Lifecycle ────────────────────────────────────────

    def spawn(self, tool_name: str, **overrides) -> RunningTool:
        """Start a Docker container for the given tool."""
        if tool_name not in self._tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        if tool_name in self._running:
            return self._running[tool_name]

        tool = self._tools[tool_name]
        env = {**tool.env, **overrides.get("env", {})}

        if tool.transport == "mcp-stdio":
            return docker_transport.spawn_stdio(tool, env, self._running, self._save_state)
        elif tool.transport == "mcp-sse":
            return docker_transport.spawn_sse(tool, env, self._running, self._save_state, self._wait_healthy)
        elif tool.transport == "rest":
            return docker_transport.spawn_rest(tool, env, self._running, self._save_state)
        elif tool.transport == "cli":
            return docker_transport.spawn_cli(tool, env, self._running, self._save_state)
        else:
            raise ValueError(f"Unknown transport: {tool.transport}")

    def _wait_healthy(self, check: str, timeout: int = 30):
        """Poll health endpoint until ready."""
        deadline = time.time() + timeout
        client = self._get_http_client()
        while time.time() < deadline:
            try:
                r = client.get(check, timeout=2)
                if r.status_code < 500:
                    return
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError(f"Health check failed after {timeout}s")

    def _get_http_client(self) -> httpx.Client:
        """Get or create HTTP client for connection pooling."""
        if not self._http_client:
            self._http_client = httpx.Client(timeout=120)
        return self._http_client

    # ─── MCP Communication ────────────────────────────────

    def call_tool(self, tool_name: str, mcp_tool: str, arguments: dict) -> dict:
        """Call an MCP tool on a running container."""
        rt = self._running.get(tool_name)
        if not rt:
            rt = self.spawn(tool_name)

        if rt.tool.transport == "mcp-stdio":
            return docker_transport.call_stdio(rt, mcp_tool, arguments, self._get_http_client)
        elif rt.tool.transport == "mcp-sse":
            return docker_transport.call_sse(rt, mcp_tool, arguments, self._get_http_client)
        elif rt.tool.transport == "rest":
            return docker_transport.call_rest(rt, mcp_tool, arguments, self._get_http_client)
        elif rt.tool.transport == "cli":
            return docker_transport.call_cli(rt, mcp_tool, arguments, self._get_http_client)
        else:
            raise ValueError(f"Cannot call tool on transport: {rt.tool.transport}")

    # ─── Teardown ─────────────────────────────────────────

    def teardown(self, tool_name: str) -> None:
        """Stop and remove container."""
        rt = self._running.pop(tool_name, None)
        if not rt:
            return
        if rt.process:
            try:
                if rt.process.poll() is None:  # Still running
                    rt.process.terminate()
                    try:
                        rt.process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        rt.process.kill()
                        rt.process.wait()
                # Close pipes to avoid BrokenPipeError
                if rt.process.stdin:
                    try:
                        rt.process.stdin.close()
                    except (BrokenPipeError, OSError):
                        pass
            except (BrokenPipeError, OSError):
                pass  # Process already dead
        else:
            subprocess.run(
                ["docker", "rm", "-f", rt.container_id],
                capture_output=True,
            )
        self._save_state()

    def teardown_all(self) -> None:
        """Stop all running containers."""
        for name in list(self._running):
            self.teardown(name)

    # ─── Discovery ────────────────────────────────────────

    def list_tools(self) -> list[str]:
        """List declared tools from docker-tools.yaml."""
        return list(self._tools.keys())

    def list_running(self) -> list[str]:
        """List currently running tools."""
        return list(self._running.keys())

    def get_capabilities(self, tool_name: str) -> list[str]:
        """List MCP tools available on a running container."""
        rt = self._running.get(tool_name)
        if not rt or not rt.tool.is_mcp:
            return self._tools.get(tool_name, DockerTool("", "", "")).capabilities

        if rt.tool.transport == "mcp-stdio":
            if not rt.process or not rt.process.stdin:
                return []
            request = {
                "jsonrpc": "2.0", "id": 0,
                "method": "tools/list", "params": {},
            }
            content = json.dumps(request)
            message = f"Content-Length: {len(content)}\r\n\r\n{content}"
            rt.process.stdin.write(message)
            rt.process.stdin.flush()
            
            header_line = rt.process.stdout.readline()
            if not header_line.startswith("Content-Length:"):
                return []
            
            content_length = int(header_line.split(":")[1].strip())
            rt.process.stdout.readline()  # Empty line
            
            response = rt.process.stdout.read(content_length)
            data = json.loads(response)
            return [t["name"] for t in data.get("result", {}).get("tools", [])]
        return self._tools[tool_name].capabilities


# Backward compatibility exports
__all__ = ["DockerTool", "RunningTool", "DockerToolManager"]
