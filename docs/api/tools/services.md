# `tools.services`

Service health checker — unified monitoring for external services.

Usage:
    from algitex.tools.services import ServiceChecker
    
    checker = ServiceChecker()
    status = checker.check_all()
    checker.print_status(status)


## Classes

### `ServiceStatus`

Status of a single service.

**Methods:**

#### `status_icon`

```python
def status_icon(self) -> str
```

Get status icon for display.

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary.

### `ServiceChecker`

Checker for various services used by algitex.

**Methods:**

#### `__init__`

```python
def __init__(self, timeout: float=5.0)
```

#### `check_http_service`

```python
def check_http_service(self, name: str, url: str, health_path: str='/health', expected_status: int=200) -> ServiceStatus
```

Check an HTTP service.

#### `check_ollama`

```python
def check_ollama(self, host: str='http://localhost:11434') -> ServiceStatus
```

Check Ollama service.

#### `check_litellm_proxy`

```python
def check_litellm_proxy(self, url: str='http://localhost:4000') -> ServiceStatus
```

Check LiteLLM proxy.

#### `check_mcp_service`

```python
def check_mcp_service(self, name: str, port: int) -> ServiceStatus
```

Check an MCP service by port.

#### `check_command_exists`

```python
def check_command_exists(self, name: str, command: str) -> ServiceStatus
```

Check if a command-line tool exists.

#### `check_file_exists`

```python
def check_file_exists(self, name: str, path: str) -> ServiceStatus
```

Check if a file exists.

#### `check_all`

```python
def check_all(self, services: Optional[Dict[str, Any]]=None) -> List[ServiceStatus]
```

Check all known services.

#### `print_status`

```python
def print_status(self, statuses: List[ServiceStatus], show_details: bool=False) -> None
```

Print service statuses in a formatted way.

#### `get_unhealthy`

```python
def get_unhealthy(self, statuses: List[ServiceStatus]) -> List[ServiceStatus]
```

Get list of unhealthy services.

#### `wait_for_services`

```python
def wait_for_services(self, services: List[str], timeout_seconds: int=60, check_interval: float=2.0) -> bool
```

Wait for specific services to become healthy.

#### `close`

```python
def close(self) -> None
```

Close the HTTP client.

### `ServiceDependency`

Manage service dependencies and startup order.

**Methods:**

#### `__init__`

```python
def __init__(self, checker: Optional[ServiceChecker]=None)
```

#### `get_startup_order`

```python
def get_startup_order(self, services: List[str]) -> List[str]
```

Get services in dependency order.

#### `check_with_dependencies`

```python
def check_with_dependencies(self, services: List[str]) -> Dict[str, ServiceStatus]
```

Check services with dependency awareness.
