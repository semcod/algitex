# `tools.config`

Configuration management — generate and manage IDE/tool configurations.

Usage:
    from algitex.tools.config import ConfigManager
    
    # Generate Continue.dev config
    manager = ConfigManager()
    config = manager.generate_continue_config(models=["qwen3-coder:latest"])
    manager.install_config(config, "~/.continue/config.json")


## Classes

### `ConfigManager`

Manages configuration files for various IDEs and tools.

**Methods:**

#### `__init__`

```python
def __init__(self, backup: bool=True)
```

#### `install_config`

```python
def install_config(self, config: Dict[str, Any], config_path: Union[str, Path], format: str='json') -> bool
```

Install configuration to file.

#### `generate_continue_config`

```python
def generate_continue_config(self, models: Optional[List[str]]=None, api_base: str='http://localhost:11434', custom_commands: Optional[List[Dict[str, str]]]=None) -> Dict[str, Any]
```

Generate Continue.dev configuration for Ollama.

#### `install_continue_config`

```python
def install_continue_config(self, models: Optional[List[str]]=None, config_dir: Optional[str]=None) -> bool
```

Install Continue.dev configuration.

#### `generate_vscode_settings`

```python
def generate_vscode_settings(self, ollama_url: str='http://localhost:11434', model: str='qwen3-coder:latest') -> Dict[str, Any]
```

Generate VS Code settings for local LLM integration.

#### `install_vscode_settings`

```python
def install_vscode_settings(self, workspace_path: Union[str, Path]='.', settings: Optional[Dict[str, Any]]=None) -> bool
```

Install VS Code settings in workspace.

#### `generate_env_file`

```python
def generate_env_file(self, services: Dict[str, str], env_path: Union[str, Path]='.env') -> bool
```

Generate .env file for services.

#### `generate_docker_compose`

```python
def generate_docker_compose(self, services: Dict[str, Dict[str, Any]], output_path: Union[str, Path]='docker-compose.yml') -> bool
```

Generate docker-compose.yml for services.

#### `setup_project_configs`

```python
def setup_project_configs(self, project_path: Union[str, Path]='.', tools: List[str]=None) -> bool
```

Setup all configurations for a project.

#### `list_configs`

```python
def list_configs(self, config_dir: Union[str, Path]='~') -> Dict[str, List[str]]
```

List available configuration files.
