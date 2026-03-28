"""Docker transport implementations — spawn and communication for different transports.

This module contains transport-specific logic for Docker MCP tools:
- mcp-stdio: JSON-RPC over stdin/stdout
- mcp-sse: Server-Sent Events / HTTP MCP
- rest: REST/OpenAI-compatible endpoints
- cli: On-demand docker exec
"""

from __future__ import annotations

import json
import subprocess
import time
from typing import TYPE_CHECKING

,httpx

if TYPE_CHECKING:
    from algitex.tools.docker import DockerTool, RunningTool


def spawn_stdio(tool: DockerTool, env: dict, running: dict, save_state: callable) -> "RunningTool":
    """docker run -i → persistent subprocess with stdin/stdout MCP."""
    from algitex.tools.docker import RunningTool
    
    cmd = ["docker", "run", "-i"]
    if tool.auto_remove:
        cmd.append("--rm")
    for k, v in env.items():
        cmd.extend(["-e", f"{k}={v}"])
    for vol in tool.volumes:
        cmd.extend(["-v", vol])
    
    # Special handling for filesystem-mcp which needs directory argument
    if tool.name == "filesystem-mcp":
        cmd.extend([tool.image, "/workspace"])
    else:
        cmd.append(tool.image)

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    # Give the server a moment to start up
    time.sleep(1.0)
    
    # Check if process crashed immediately
    if proc.poll() is not None:
        stderr_output = proc.stderr.read() if proc.stderr else ""
        stdout_output = proc.stdout.read() if proc.stdout else ""
        raise RuntimeError(
            f"MCP container '{tool.name}' exited immediately with code {proc.poll()}. "
            f"Image: {tool.image}. "
            f"Stderr: {stderr_output[:1000]}. "
            f"Stdout: {stdout_output[:500]}"
        )
    
    rt = RunningTool(
        tool=tool,
        container_id=f"stdio-{tool.name}-{proc.pid}",
        process=proc,
        pid=proc.pid,
    )
    running[tool.name] = rt
    save_state()
    return rt


def spawn_sse(tool: DockerTool, env: dict, running: dict, save_state: callable, 
              wait_healthy: callable) -> "RunningTool":
    """docker run -d -p PORT → SSE/HTTP MCP endpoint."""
    from algitex.tools.docker import RunningTool
    
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
    running[tool.name] = rt
    save_state()

    # Wait for health
    if tool.health_check:
        wait_healthy(tool.health_check)

    return rt


def spawn_rest(tool: DockerTool, env: dict, running: dict, save_state: callable) -> "RunningTool":
    """docker run -d -p PORT → REST/OpenAI-compatible endpoint."""
    from algitex.tools.docker import RunningTool
    
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
    running[tool.name] = rt
    save_state()
    return rt


def spawn_cli(tool: DockerTool, env: dict, running: dict, save_state: callable) -> "RunningTool":
    """CLI tool — run on demand via docker exec, no persistent container."""
    from algitex.tools.docker import RunningTool
    
    cmd = ["docker", "run", "-d"]
    for k, v in env.items():
        cmd.extend(["-e", f"{k}={v}"])
    for vol in tool.volumes:
        cmd.extend(["-v", vol])
    cmd.extend([tool.image, "sleep", "infinity"])

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    container_id = result.stdout.strip()[:12]

    rt = RunningTool(tool=tool, container_id=container_id)
    running[tool.name] = rt
    save_state()
    return rt


class StdioTransport:
    """Transport layer for JSON-RPC over stdin/stdout communication."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def send(self, process: subprocess.Popen, request: dict) -> dict:
        """Send JSON-RPC request and return parsed response."""
        # Serialize request
        message = self._serialize(request)
        
        # Send to process
        self._write(process.stdin, message)
        
        # Read response
        response_data = self._read_with_timeout(process.stdout)
        
        # Parse and return
        return self._parse(response_data)
    
    def _serialize(self, request: dict) -> str:
        """Serialize JSON-RPC request with MCP protocol headers."""
        content = json.dumps(request)
        return f"Content-Length: {len(content)}\r\n\r\n{content}"
    
    def _write(self, stdin, message: str):
        """Write message to stdin with error handling."""
        try:
            stdin.write(message)
            stdin.flush()
        except BrokenPipeError:
            raise RuntimeError("MCP server process crashed or closed connection")
    
    def _read_with_timeout(self, stdout) -> str:
        """Read response from stdout with timeout using select."""
        import select
        
        start_time = time.time()
        response_lines = []
        
        while time.time() - start_time < self.timeout:
            # Check if stdout has data
            ready, _, _ = select.select([stdout], [], [], 1.0)
            if not ready:
                # Check if process died
                if hasattr(stdout, '_proc') and stdout._proc.poll() is not None:
                    raise RuntimeError(f"MCP server exited with code {stdout._proc.poll()}")
                continue
            
            line = stdout.readline()
            if not line:
                if hasattr(stdout, '_proc') and stdout._proc.poll() is not None:
                    raise RuntimeError(f"MCP server exited with code {stdout._proc.poll()}")
                break
            
            response_lines.append(line)
            
            # Parse Content-Length header
            if line.startswith("Content-Length:"):
                content_length = int(line.split(":")[1].strip())
                # Read empty line
                stdout.readline()
                # Read the JSON response
                response_data = stdout.read(content_length)
                return response_data
        
        raise RuntimeError(f"MCP server timeout after {self.timeout}s")
    
    def _parse(self, raw_response: str) -> dict:
        """Parse JSON response with error handling."""
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {str(e)}")


def call_stdio(rt: "RunningTool", tool: str, args: dict, get_client: callable) -> dict:
    """Send JSON-RPC over stdin, read from stdout with timeout."""
    if not rt.process or not rt.process.stdin:
        return {"error": "stdio process not available"}
    
    # Create transport
    transport = StdioTransport(timeout=30)
    
    # Attach process reference for timeout handling
    rt.process.stdout._proc = rt.process
    
    # Build request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    }
    
    # Send and receive
    try:
        response = transport.send(rt.process, request)
        return response
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Communication error: {str(e)}"}


def call_sse(rt: "RunningTool", tool: str, args: dict, get_client: callable) -> dict:
    """POST to SSE/HTTP MCP endpoint."""
    client = get_client()
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


def call_rest(rt: "RunningTool", tool: str, args: dict, get_client: callable) -> dict:
    """Call REST endpoint using action name as path."""
    client = get_client()
    # Use the action name as the endpoint path
    endpoint = f"{rt.endpoint}/{tool}"
    # Use GET for endpoints without arguments, POST otherwise
    if args:
        response = client.post(endpoint, json=args)
    else:
        response = client.get(endpoint)
    response.raise_for_status()
    return response.json()


def call_cli(rt: "RunningTool", cmd: str, args: dict, get_client: callable) -> dict:
    """docker exec on persistent container."""
    # For CLI tools, cmd is the actual command to run
    full_cmd = ["docker", "exec", rt.container_id] + cmd.split()
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return {"stdout": result.stdout, "stderr": result.stderr, "rc": result.returncode}
