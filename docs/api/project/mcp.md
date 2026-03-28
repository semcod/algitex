# `project.mcp`

MCP service orchestration mixins for Project class.

## Classes

### `MCPMixin`

MCP service orchestration functionality for Project.

**Methods:**

#### `__init__`

```python
def __init__(self) -> None
```

#### `start_mcp_services`

```python
def start_mcp_services(self, services: Optional[list]=None) -> bool
```

Start MCP services.

#### `stop_mcp_services`

```python
def stop_mcp_services(self) -> bool
```

Stop all MCP services.

#### `restart_mcp_service`

```python
def restart_mcp_service(self, service: str) -> bool
```

Restart a specific MCP service.

#### `wait_for_mcp_ready`

```python
def wait_for_mcp_ready(self, timeout: int=60) -> bool
```

Wait for MCP services to be ready.

#### `get_mcp_status`

```python
def get_mcp_status(self) -> dict
```

Get MCP services status.

#### `print_mcp_status`

```python
def print_mcp_status(self) -> None
```

Print MCP services status.

#### `generate_mcp_config`

```python
def generate_mcp_config(self) -> bool
```

Generate MCP client configuration.
