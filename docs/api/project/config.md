# `project.config`

Configuration management mixins for Project class.

## Classes

### `ConfigMixin`

Configuration management functionality for Project.

**Methods:**

#### `__init__`

```python
def __init__(self) -> None
```

#### `setup_configs`

```python
def setup_configs(self, tools: Optional[List[str]]=None) -> bool
```

Setup project configurations.

#### `install_continue_config`

```python
def install_continue_config(self, models: Optional[List[str]]=None) -> bool
```

Install Continue.dev configuration.

#### `install_vscode_settings`

```python
def install_vscode_settings(self) -> bool
```

Install VS Code settings.

#### `generate_env_file`

```python
def generate_env_file(self, services: Optional[dict]=None) -> bool
```

Generate .env file.
