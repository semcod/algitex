"""Configuration management — generate and manage IDE/tool configurations.

Usage:
    from algitex.tools.config import ConfigManager
    
    # Generate Continue.dev config
    manager = ConfigManager()
    config = manager.generate_continue_config(models=["qwen2.5-coder:7b"])
    manager.install_config(config, "~/.continue/config.json")
"""

from __future__ import annotations

import json
,os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ConfigManager:
    """Manages configuration files for various IDEs and tools."""
    
    def __init__(self, backup: bool = True):
        self.backup = backup
    
    def _ensure_dir(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists."""
        path = Path(path).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def _backup_file(self, path: Union[str, Path]) -> Optional[Path]:
        """Backup existing file if it exists."""
        path = Path(path).expanduser()
        if path.exists():
            if self.backup:
                backup_path = path.with_suffix(path.suffix + ".backup")
                shutil.copy2(path, backup_path)
                return backup_path
        return None
    
    def install_config(
        self,
        config: Dict[str, Any],
        config_path: Union[str, Path],
        format: str = "json"
    ) -> bool:
        """Install configuration to file."""
        config_path = Path(config_path).expanduser()
        
        # Ensure directory exists
        self._ensure_dir(config_path.parent)
        
        # Backup existing config
        backup = self._backup_file(config_path)
        if backup:
            print(f"Backed up: {backup}")
        
        # Write new config
        try:
            with open(config_path, 'w') as f:
                if format == "json":
                    json.dump(config, f, indent=2)
                elif format == "yaml":
                    import yaml
                    yaml.dump(config, f, default_flow_style=False)
                else:
                    f.write(str(config))
            
            print(f"Created: {config_path}")
            return True
        except Exception as e:
            print(f"Failed to write config: {e}")
            return False
    
    def generate_continue_config(
        self,
        models: Optional[List[str]] = None,
        api_base: str = "http://localhost:11434",
        custom_commands: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate Continue.dev configuration for Ollama."""
        if models is None:
            models = ["qwen2.5-coder:7b", "llama3:8b", "codellama:7b"]
        
        # Model configurations
        config_models = []
        for model in models:
            title = model.replace(":", " ").title()
            config_models.append({
                "title": f"{title} (Local)",
                "provider": "ollama",
                "model": model,
                "apiBase": api_base
            })
        
        # Default custom commands
        if custom_commands is None:
            custom_commands = [
                {
                    "name": "refactor",
                    "prompt": "Refactor this code to be more readable, efficient, and maintainable. Add type hints, docstrings, and improve variable names.",
                    "description": "Refactor selected code"
                },
                {
                    "name": "fix",
                    "prompt": "Find and fix any bugs, issues, or code smells in this code. Explain what was wrong and how you fixed it.",
                    "description": "Fix code issues"
                },
                {
                    "name": "test",
                    "prompt": "Write comprehensive unit tests for this code using pytest. Include edge cases and error scenarios.",
                    "description": "Generate unit tests"
                },
                {
                    "name": "document",
                    "prompt": "Add comprehensive documentation to this code. Include docstrings, inline comments, and type hints.",
                    "description": "Add documentation"
                },
                {
                    "name": "optimize",
                    "prompt": "Optimize this code for better performance. Explain the optimizations made.",
                    "description": "Optimize performance"
                }
            ]
        
        config = {
            "models": config_models,
            "tabAutocompleteModel": {
                "title": f"{models[0].replace(':', ' ').title()} Autocomplete",
                "provider": "ollama",
                "model": models[0],
                "apiBase": api_base
            },
            "customCommands": custom_commands
        }
        
        return config
    
    def install_continue_config(
        self,
        models: Optional[List[str]] = None,
        config_dir: Optional[str] = None
    ) -> bool:
        """Install Continue.dev configuration."""
        if config_dir is None:
            config_dir = "~/.continue"
        
        config_path = Path(config_dir) / "config.json"
        config = self.generate_continue_config(models)
        
        return self.install_config(config, config_path)
    
    def generate_vscode_settings(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "qwen2.5-coder:7b"
    ) -> Dict[str, Any]:
        """Generate VS Code settings for local LLM integration."""
        settings = {
            "github.copilot.enable": {
                "*": False,
                "yaml": True,
                "plaintext": True
            },
            "github.copilot.editor.enableAutoCompletions": False,
            "continue.enable": True,
            "continue.model": model,
            "continue.apiBase": ollama_url,
            "python.defaultInterpreterPath": "./venv/bin/python",
            "python.formatting.provider": "black",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True,
            "python.linting.mypyEnabled": True,
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/.pytest_cache": True,
                "**/.mypy_cache": True,
                "**/.batch_results": True
            }
        }
        
        return settings
    
    def install_vscode_settings(
        self,
        workspace_path: Union[str, Path] = ".",
        settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Install VS Code settings in workspace."""
        workspace_path = Path(workspace_path).resolve()
        vscode_dir = workspace_path / ".vscode"
        
        # Generate settings if not provided
        if settings is None:
            settings = self.generate_vscode_settings()
        
        # Install settings.json
        settings_path = vscode_dir / "settings.json"
        success = self.install_config(settings, settings_path)
        
        # Create recommended extensions
        extensions = [
            "ms-python.python",
            "ms-python.black-formatter",
            "ms-python.isort",
            "ms-python.flake8",
            "ms-python.mypy-type-checker",
            "GitHub.copilot",
            "GitHub.copilot-chat",
            "Continue.continue",
            "ms-vscode.vscode-json",
            "redhat.vscode-yaml"
        ]
        
        extensions_config = {
            "recommendations": extensions
        }
        
        extensions_path = vscode_dir / "extensions.json"
        success_ext = self.install_config(extensions_config, extensions_path)
        
        return success and success_ext
    
    def generate_env_file(
        self,
        services: Dict[str, str],
        env_path: Union[str, Path] = ".env"
    ) -> bool:
        """Generate .env file for services."""
        env_lines = []
        
        for service, url in services.items():
            service = service.upper()
            if service == "OLLAMA":
                env_lines.append(f"OLLAMA_URL={url}")
            elif service == "LITELLM":
                env_lines.append(f"LITELLM_URL={url}")
                env_lines.append("LITELLM_API_KEY=dummy-key")
            elif service == "PROXYM":
                env_lines.append(f"PROXYM_URL={url}")
            elif service == "LLX":
                env_lines.append(f"LLX_URL={url}")
        
        env_content = "\n".join(env_lines) + "\n"
        
        try:
            with open(env_path, 'w') as f:
                f.write(env_content)
            print(f"Created: {env_path}")
            return True
        except Exception as e:
            print(f"Failed to write .env: {e}")
            return False
    
    def generate_docker_compose(
        self,
        services: Dict[str, Dict[str, Any]],
        output_path: Union[str, Path] = "docker-compose.yml"
    ) -> bool:
        """Generate docker-compose.yml for services."""
        compose = {
            "version": "3.8",
            "services": {}
        }
        
        # Add common services
        for name, config in services.items():
            if name == "ollama":
                compose["services"][name] = {
                    "image": "ollama/ollama",
                    "ports": ["11434:11434"],
                    "volumes": ["ollama:/root/.ollama"],
                    "environment": ["OLLAMA_HOST=0.0.0.0"]
                }
            elif name == "litellm":
                compose["services"][name] = {
                    "image": "ghcr.io/berriai/litellm:main",
                    "ports": ["4000:4000"],
                    "volumes": ["./litellm_config.yaml:/app/config.yaml"],
                    "environment": ["LITELLM_PORT=4000"]
                }
            elif name == "proxym":
                compose["services"][name] = {
                    "build": "./docker/proxym",
                    "ports": ["8000:8000"],
                    "environment": ["PROXYM_PORT=8000"]
                }
            else:
                # Custom service
                compose["services"][name] = config
        
        # Add volumes
        if "ollama" in services:
            compose["volumes"] = {"ollama": {}}
        
        try:
            with open(output_path, 'w') as f:
                import yaml
                yaml.dump(compose, f, default_flow_style=False)
            print(f"Created: {output_path}")
            return True
        except Exception as e:
            print(f"Failed to write docker-compose.yml: {e}")
            return False
    
    def setup_project_configs(
        self,
        project_path: Union[str, Path] = ".",
        tools: List[str] = None
    ) -> bool:
        """Setup all configurations for a project."""
        if tools is None:
            tools = ["vscode", "env", "docker"]
        
        project_path = Path(project_path).resolve()
        success = True
        
        print(f"Setting up configurations for {project_path}")
        print()
        
        if "vscode" in tools:
            print("Installing VS Code settings...")
            success &= self.install_vscode_settings(project_path)
        
        if "env" in tools:
            print("Generating .env file...")
            services = {
                "ollama": "http://localhost:11434",
                "litellm": "http://localhost:4000"
            }
            success &= self.generate_env_file(services, project_path / ".env")
        
        if "docker" in tools:
            print("Generating docker-compose.yml...")
            services = {
                "ollama": {},
                "litellm": {}
            }
            success &= self.generate_docker_compose(services, project_path / "docker-compose.yml")
        
        if "continue" in tools:
            print("Installing Continue.dev config...")
            success &= self.install_continue_config()
        
        return success
    
    def list_configs(self, config_dir: Union[str, Path] = "~") -> Dict[str, List[str]]:
        """List available configuration files."""
        config_dir = Path(config_dir).expanduser()
        configs = {
            "continue": [],
            "vscode": [],
            "env": [],
            "docker": []
        }
        
        # Continue.dev
        continue_config = config_dir / ".continue" / "config.json"
        if continue_config.exists():
            configs["continue"].append(str(continue_config))
        
        # VS Code (check workspace and global)
        vscode_workspace = Path.cwd() / ".vscode"
        if vscode_workspace.exists():
            configs["vscode"].extend([str(p) for p in vscode_workspace.glob("*.json")])
        
        vscode_global = config_dir / ".config" / "Code" / "User"
        if vscode_global.exists():
            configs["vscode"].extend([str(p) for p in vscode_global.glob("*.json")])
        
        # Environment files
        for env_file in Path.cwd().glob(".env*"):
            configs["env"].append(str(env_file))
        
        # Docker files
        for docker_file in Path.cwd().glob("docker-compose*.yml"):
            configs["docker"].append(str(docker_file))
        
        return configs
