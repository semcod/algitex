"""Docker tool manager — spawn, connect, call, teardown."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import httpx
import yaml

from algitex.config import Config


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


# ─── DockerToolManager ───────────────────────────────────

class DockerToolManager:
    """Spawn Docker containers, connect via MCP/REST, call tools, teardown."""

    def __init__(self, config: Config):
        self.config = config
        self._running: dict[str, RunningTool] = {}
        self._tools: dict[str, DockerTool] = {}
        self._http_client: Optional[httpx.Client] = None
        self._load_tools()

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
        data = yaml.safe_load(path.read_text())
        for name, spec in data.get("tools", {}).items():
            self._tools[name] = DockerTool(name=name, **spec)

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
            return self._spawn_stdio(tool, env)
        elif tool.transport == "mcp-sse":
            return self._spawn_sse(tool, env)
        elif tool.transport == "rest":
            return self._spawn_rest(tool, env)
        elif tool.transport == "cli":
            return self._spawn_cli(tool, env)
        else:
            raise ValueError(f"Unknown transport: {tool.transport}")

    def _spawn_stdio(self, tool: DockerTool, env: dict) -> RunningTool:
        """docker run -i --rm → subprocess with stdin/stdout MCP."""
        cmd = ["docker", "run", "-i"]
        if tool.auto_remove:
            cmd.append("--rm")
        for k, v in env.items():
            cmd.extend(["-e", f"{k}={v}"])
        for vol in tool.volumes:
            cmd.extend(["-v", vol])
        cmd.append(tool.image)

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        rt = RunningTool(
            tool=tool,
            container_id=f"stdio-{tool.name}-{proc.pid}",
            process=proc,
        )
        self._running[tool.name] = rt
        return rt

    def _spawn_sse(self, tool: DockerTool, env: dict) -> RunningTool:
        """docker run -d -p PORT → SSE/HTTP MCP endpoint."""
        port = tool.port or 8080
        cmd = ["docker", "run", "-d", "-p", f"{port}:{port}"]
        for k, v in env.items():
            cmd.extend(["-e", f"{k}={v}"])
        for vol in tool.volumes:
            cmd.extend(["-v", vol])
        cmd.append(tool.image)

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()[:12]

        rt = RunningTool(
            tool=tool,
            container_id=container_id,
            endpoint=f"http://localhost:{port}/mcp",
        )
        self._running[tool.name] = rt

        # Wait for health
        if tool.health_check:
            self._wait_healthy(tool.health_check)

        return rt

    def _spawn_rest(self, tool: DockerTool, env: dict) -> RunningTool:
        """docker run -d -p PORT → REST/OpenAI-compatible endpoint."""
        port = tool.port or 4000
        cmd = ["docker", "run", "-d", "-p", f"{port}:{port}"]
        for k, v in env.items():
            cmd.extend(["-e", f"{k}={v}"])
        for vol in tool.volumes:
            cmd.extend(["-v", vol])
        cmd.append(tool.image)

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()[:12]

        rt = RunningTool(
            tool=tool,
            container_id=container_id,
            endpoint=f"http://localhost:{port}",
        )
        self._running[tool.name] = rt
        return rt

    def _spawn_cli(self, tool: DockerTool, env: dict) -> RunningTool:
        """CLI tool — run on demand via docker exec, no persistent container."""
        cmd = ["docker", "run", "-d"]
        for k, v in env.items():
            cmd.extend(["-e", f"{k}={v}"])
        for vol in tool.volumes:
            cmd.extend(["-v", vol])
        cmd.extend([tool.image, "sleep", "infinity"])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()[:12]

        rt = RunningTool(tool=tool, container_id=container_id)
        self._running[tool.name] = rt
        return rt

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
            return self._call_stdio(rt, mcp_tool, arguments)
        elif rt.tool.transport == "mcp-sse":
            return self._call_sse(rt, mcp_tool, arguments)
        elif rt.tool.transport == "rest":
            return self._call_rest(rt, mcp_tool, arguments)
        elif rt.tool.transport == "cli":
            return self._call_cli(rt, mcp_tool, arguments)
        else:
            raise ValueError(f"Cannot call tool on transport: {rt.tool.transport}")

    def _call_stdio(self, rt: RunningTool, tool: str, args: dict) -> dict:
        """Send JSON-RPC over stdin, read from stdout."""
        if not rt.process or not rt.process.stdin:
            raise RuntimeError("stdio process not available")

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        }
        
        # MCP stdio uses Content-Length headers (like LSP protocol)
        content = json.dumps(request)
        message = f"Content-Length: {len(content)}\r\n\r\n{content}"
        
        rt.process.stdin.write(message)
        rt.process.stdin.flush()
        
        # Read response with Content-Length header
        header_data = b""
        while b"\r\n\r\n" not in header_data:
            chunk = rt.process.stdout.read(1)
            if not chunk:
                raise RuntimeError("Unexpected EOF while reading MCP headers")
            header_data += chunk
        
        headers = header_data.decode().split("\r\n")
        content_length = None
        for header in headers:
            if header.startswith("Content-Length:"):
                content_length = int(header.split(":")[1].strip())
                break
        
        if content_length is None:
            raise RuntimeError("Missing Content-Length header in MCP response")
        
        response = rt.process.stdout.read(content_length)
        return json.loads(response)

    def _call_sse(self, rt: RunningTool, tool: str, args: dict) -> dict:
        """POST to SSE/HTTP MCP endpoint."""
        client = self._get_http_client()
        response = client.post(
            rt.endpoint,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool, "arguments": args},
            },
        )
        response.raise_for_status()
        return response.json()

    def _call_rest(self, rt: RunningTool, tool: str, args: dict) -> dict:
        """Call REST endpoint (OpenAI-compatible or custom)."""
        client = self._get_http_client()
        response = client.post(
            f"{rt.endpoint}/v1/chat/completions",
            json=args,
        )
        response.raise_for_status()
        return response.json()

    def _call_cli(self, rt: RunningTool, cmd: str, args: dict) -> dict:
        """docker exec on persistent container."""
        # For CLI tools, cmd is the actual command to run
        full_cmd = ["docker", "exec", rt.container_id] + cmd.split()
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr, "rc": result.returncode}

    # ─── Teardown ─────────────────────────────────────────

    def teardown(self, tool_name: str):
        """Stop and remove container."""
        rt = self._running.pop(tool_name, None)
        if not rt:
            return
        if rt.process:
            rt.process.terminate()
            try:
                rt.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                rt.process.kill()
                rt.process.wait()
        else:
            subprocess.run(
                ["docker", "rm", "-f", rt.container_id],
                capture_output=True,
            )

    def teardown_all(self):
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
