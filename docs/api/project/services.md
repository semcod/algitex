# `project.services`

Service management mixins for Project class.

## Classes

### `ServiceMixin`

Service management functionality for Project.

**Methods:**

#### `__init__`

```python
def __init__(self) -> None
```

#### `check_services`

```python
def check_services(self, services: Optional[dict]=None) -> dict
```

Check status of all services.

#### `print_service_status`

```python
def print_service_status(self, show_details: bool=False) -> None
```

Print service status in a formatted way.

#### `ensure_service`

```python
def ensure_service(self, service: str, timeout_seconds: int=60) -> bool
```

Wait for a service to become healthy.
