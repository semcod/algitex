"""Configuration management mixins for Project class."""

from __future__ import annotations

from typing import List, Optional

from algitex.tools.config import ConfigManager


class ConfigMixin:
    """Configuration management functionality for Project."""

    def __init__(self) -> None:
        self.config_manager = ConfigManager()

    def setup_configs(self, tools: Optional[List[str]] = None) -> bool:
        """Setup project configurations."""
        return self.config_manager.setup_project_configs(".", tools)

    def install_continue_config(self, models: Optional[List[str]] = None) -> bool:
        """Install Continue.dev configuration."""
        return self.config_manager.install_continue_config(models)

    def install_vscode_settings(self) -> bool:
        """Install VS Code settings."""
        return self.config_manager.install_vscode_settings(".")

    def generate_env_file(self, services: Optional[dict] = None) -> bool:
        """Generate .env file."""
        from pathlib import Path
        if services is None:
            services = {
                "ollama": "http://localhost:11434",
                "litellm": "http://localhost:4000"
            }
        return self.config_manager.generate_env_file(services, Path(".") / ".env")
