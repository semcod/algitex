# `tools.mcp`

MCP (Model Context Protocol) service orchestration — manage multiple MCP services.

Usage:
    from algitex.tools.mcp import MCPOrchestrator
    
    # Start services
    orchestrator = MCPOrchestrator()
    orchestrator.start_all()
    orchestrator.wait_for_ready()


## Classes

### `MCPService`

Definition of an MCP service.

### `MCPOrchestrator`

Orchestrates multiple MCP services.

**Methods:**

#### `__init__`

```python
def __init__(self)
```

#### `add_service`

```python
def add_service(self, service: MCPService) -> None
```

Add a custom service.

#### `add_custom_service`

```python
def add_custom_service(self, name: str, command: List[str], port: Optional[int]=None, **kwargs)
```

Add a custom service by parameters.

#### `start_service`

```python
def start_service(self, name: str) -> bool
```

Start a single service.

#### `stop_service`

```python
def stop_service(self, name: str, timeout: int=10) -> bool
```

Stop a single service.

#### `restart_service`

```python
def restart_service(self, name: str) -> bool
```

Restart a service.

#### `start_all`

```python
def start_all(self, services: Optional[List[str]]=None) -> bool
```

Start all or specified services.

#### `stop_all`

```python
def stop_all(self, timeout: int=10) -> bool
```

Stop all services.

#### `wait_for_ready`

```python
def wait_for_ready(self, services: Optional[List[str]]=None, timeout: int=60) -> bool
```

Wait for services to be ready.

#### `check_health`

```python
def check_health(self) -> Dict[str, ServiceStatus]
```

Check health of all services.

#### `get_logs`

```python
def get_logs(self, name: str, lines: int=50) -> str
```

Get logs from a service.

#### `list_services`

```python
def list_services(self) -> List[str]
```

List all registered services.

#### `get_service_info`

```python
def get_service_info(self, name: str) -> Optional[Dict[str, Any]]
```

Get information about a service.

#### `print_status`

```python
def print_status(self) -> None
```

Print status of all services.

#### `generate_mcp_config`

```python
def generate_mcp_config(self, output_path: Union[str, Path]='mcp_config.json') -> bool
```

Generate MCP client configuration.
