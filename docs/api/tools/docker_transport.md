# `tools.docker_transport`

Docker transport implementations — spawn and communication for different transports.

This module contains transport-specific logic for Docker MCP tools:
- mcp-stdio: JSON-RPC over stdin/stdout
- mcp-sse: Server-Sent Events / HTTP MCP
- rest: REST/OpenAI-compatible endpoints
- cli: On-demand docker exec


## Functions

### `spawn_stdio`

```python
def spawn_stdio(tool: DockerTool, env: dict, running: dict, save_state: callable) -> 'RunningTool'
```

docker run -i → persistent subprocess with stdin/stdout MCP.

### `spawn_sse`

```python
def spawn_sse(tool: DockerTool, env: dict, running: dict, save_state: callable, wait_healthy: callable) -> 'RunningTool'
```

docker run -d -p PORT → SSE/HTTP MCP endpoint.

### `spawn_rest`

```python
def spawn_rest(tool: DockerTool, env: dict, running: dict, save_state: callable) -> 'RunningTool'
```

docker run -d -p PORT → REST/OpenAI-compatible endpoint.

### `spawn_cli`

```python
def spawn_cli(tool: DockerTool, env: dict, running: dict, save_state: callable) -> 'RunningTool'
```

CLI tool — run on demand via docker exec, no persistent container.

### `call_stdio`

```python
def call_stdio(rt: 'RunningTool', tool: str, args: dict, get_client: callable) -> dict
```

Send JSON-RPC over stdin, read from stdout with timeout.

### `call_sse`

```python
def call_sse(rt: 'RunningTool', tool: str, args: dict, get_client: callable) -> dict
```

POST to SSE/HTTP MCP endpoint.

### `call_rest`

```python
def call_rest(rt: 'RunningTool', tool: str, args: dict, get_client: callable) -> dict
```

Call REST endpoint using action name as path.

### `call_cli`

```python
def call_cli(rt: 'RunningTool', cmd: str, args: dict, get_client: callable) -> dict
```

docker exec on persistent container.

## Classes

### `StdioTransport`

Transport layer for JSON-RPC over stdin/stdout communication.

**Methods:**

#### `__init__`

```python
def __init__(self, timeout: int=30)
```

#### `send`

```python
def send(self, process: subprocess.Popen, request: dict) -> dict
```

Send JSON-RPC request and return parsed response.
