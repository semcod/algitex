"""Core IDE helper logic and shared utilities."""

from __future__ import annotations

import os
import subprocess
from typing import Any, Dict, List

from .ide_models import IDETool


class IDEHelper:
    """Base class for IDE integrations."""

    def __init__(self):
        self.tools: Dict[str, IDETool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default IDE tools."""
        self.tools["claude-code"] = IDETool(
            name="Claude Code",
            command="anthropic-curl",
            install_command="pip install anthropic-curl",
            env_vars={
                "ANTHROPIC_API_KEY": "ollama",
                "ANTHROPIC_BASE_URL": "http://localhost:11434/v1"
            },
            model_prefix="ollama/"
        )

        self.tools["aider"] = IDETool(
            name="Aider",
            command="aider",
            install_command="pip install aider-chat",
            model_prefix="ollama/"
        )

        self.tools["cursor"] = IDETool(
            name="Cursor",
            command="cursor",
            install_command="# Download from cursor.sh",
            env_vars={
                "CURSOR_API_BASE": "http://localhost:11434/v1"
            }
        )

        self.tools["vscode"] = IDETool(
            name="VS Code",
            command="code",
            install_command="# Download from code.visualstudio.com"
        )

    def check_tool(self, tool_name: str) -> bool:
        """Check if an IDE tool is available."""
        if tool_name not in self.tools:
            return False

        tool = self.tools[tool_name]
        try:
            result = subprocess.run(["which", tool.command], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def setup_tool(self, tool_name: str) -> bool:
        """Setup environment for an IDE tool."""
        if tool_name not in self.tools:
            print(f"Unknown tool: {tool_name}")
            return False

        tool = self.tools[tool_name]

        if not self.check_tool(tool_name):
            print(f"❌ {tool.name} not found")
            print(f"   Install: {tool.install_command}")
            return False

        for key, value in tool.env_vars.items():
            if not os.getenv(key):
                os.environ[key] = value
                print(f"   Set {key}={value}")

        print(f"✅ {tool.name} ready")
        return True

    def list_tools(self) -> List[str]:
        """List all supported IDE tools."""
        return list(self.tools.keys())

    def get_tool_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all IDE tools."""
        status = {}
        for name, tool in self.tools.items():
            installed = self.check_tool(name)
            status[name] = {
                "name": tool.name,
                "installed": installed,
                "command": tool.command,
                "model_prefix": tool.model_prefix,
                "env_vars": tool.env_vars,
            }
        return status
