"""IDE integration helpers — support for various IDEs and editors.

Usage:
    from algitex.tools.ide import IDEHelper, ClaudeCodeHelper
    
    # Claude Code integration
    claude = ClaudeCodeHelper()
    claude.setup_environment()
    result = claude.fix_file("main.py", "Add type hints")
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class IDETool:
    """IDE tool configuration."""
    name: str
    command: str
    install_command: str
    env_vars: Dict[str, str] = None
    model_prefix: str = ""
    
    def __post_init__(self):
        if self.env_vars is None:
            self.env_vars = {}


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
            result = subprocess.run(
                ["which", tool.command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def setup_tool(self, tool_name: str) -> bool:
        """Setup environment for an IDE tool."""
        if tool_name not in self.tools:
            print(f"Unknown tool: {tool_name}")
            return False
        
        tool = self.tools[tool_name]
        
        # Check if tool is installed
        if not self.check_tool(tool_name):
            print(f"❌ {tool.name} not found")
            print(f"   Install: {tool.install_command}")
            return False
        
        # Set environment variables
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
                "env_vars": tool.env_vars
            }
        return status


class ClaudeCodeHelper(IDEHelper):
    """Helper for Claude Code (anthropic-curl) integration."""
    
    def __init__(self):
        super().__init__()
        self.tool_name = "claude-code"
    
    def setup_environment(self) -> Any:
        """Setup Claude Code environment for Ollama."""
        return self.setup_tool(self.tool_name)
    
    def fix_file(
        self,
        file_path: Union[str, Path],
        instruction: str,
        model: str = "qwen2.5-coder:7b",
        dry_run: bool = False
    ) -> bool:
        """Fix a file using Claude Code."""
        tool = self.tools[self.tool_name]
        model = tool.model_prefix + model
        
        cmd = [
            tool.command,
            "--model", model,
            "--message", instruction,
            "--file", str(file_path)
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        if dry_run:
            print("[DRY RUN] Would execute command")
            return True
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ File fixed successfully")
                return True
            else:
                print(f"❌ Failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Timeout (5 minutes)")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def chat(
        self,
        message: str,
        model: str = "qwen2.5-coder:7b",
        files: List[Union[str, Path]] = None
    ) -> Optional[str]:
        """Chat with Claude Code."""
        tool = self.tools[self.tool_name]
        model = tool.model_prefix + model
        
        cmd = [tool.command, "--model", model, "--message", message]
        
        if files:
            for file_path in files:
                cmd.extend(["--file", str(file_path)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"Error: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def batch_fix(
        self,
        issues: List[Dict[str, Any]],
        model: str = "qwen2.5-coder:7b",
        dry_run: bool = False
    ) -> Dict[str, bool]:
        """Fix multiple issues."""
        results = {}
        
        for i, issue in enumerate(issues, 1):
            file_path = issue.get("file")
            description = issue.get("description", "")
            
            if not file_path:
                continue
            
            print(f"[{i}/{len(issues)}] Fixing {file_path}")
            
            success = self.fix_file(
                file_path,
                description,
                model=model,
                dry_run=dry_run
            )
            
            results[file_path] = success
        
        return results


class AiderHelper(IDEHelper):
    """Helper for Aider integration."""
    
    def __init__(self):
        super().__init__()
        self.tool_name = "aider"
    
    def fix_file(
        self,
        file_path: Union[str, Path],
        instruction: str,
        model: str = "qwen2.5-coder:7b",
        dry_run: bool = False
    ) -> bool:
        """Fix a file using Aider."""
        tool = self.tools[self.tool_name]
        model = tool.model_prefix + model
        
        cmd = [
            tool.command,
            "--model", model,
            "--openai-api-key", "dummy",
            "--no-git",
            "--no-commit",
            "--yes",
            "--no-check-version",
            "--message", instruction,
            str(file_path)
        ]
        
        if dry_run:
            print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return True
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ File fixed successfully")
                return True
            else:
                print(f"❌ Failed: {result.stderr[:200]}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


class VSCodeHelper(IDEHelper):
    """Helper for VS Code integration."""
    
    def __init__(self):
        super().__init__()
        self.tool_name = "vscode"
    
    def open_file(self, file_path: Union[str, Path], line: Optional[int] = None) -> bool:
        """Open file in VS Code."""
        cmd = ["code", str(file_path)]
        
        if line:
            cmd.extend(["--goto", f"{file_path}:{line}"])
        
        try:
            subprocess.run(cmd, check=True)
            return True
        except:
            return False
    
    def install_extensions(self, extensions: List[str]) -> None:
        """Install VS Code extensions."""
        tool = self.tools[self.tool_name]
        
        for ext in extensions:
            print(f"Installing extension: {ext}")
            try:
                subprocess.run(
                    [tool.command, "--install-extension", ext],
                    check=True
                )
                print(f"✅ {ext}")
            except:
                print(f"❌ Failed to install {ext}")
    
    def recommended_extensions(self) -> List[str]:
        """Get recommended extensions for algitex workflow."""
        return [
            "ms-python.python",
            "ms-python.black-formatter",
            "ms-python.isort",
            "ms-python.flake8",
            "GitHub.copilot",
            "GitHub.copilot-chat",
            "ms-vscode.vscode-json",
            "redhat.vscode-yaml"
        ]


class EditorIntegration:
    """High-level editor integration manager."""
    
    def __init__(self):
        self.ide_helper = IDEHelper()
        self.claude = ClaudeCodeHelper()
        self.aider = AiderHelper()
        self.vscode = VSCodeHelper()
    
    def detect_editor(self) -> Optional[str]:
        """Detect which editor is available."""
        # Check environment variables
        if os.getenv("VSCODE_PID"):
            return "vscode"
        elif os.getenv("TMUX"):
            # Could be vim/nvim in tmux
            if self.ide_helper.check_tool("nvim"):
                return "nvim"
            elif self.ide_helper.check_tool("vim"):
                return "vim"
        
        # Check for running processes
        try:
            result = subprocess.run(
                ["ps", "-x"],
                capture_output=True,
                text=True
            )
            
            if "Cursor" in result.stdout:
                return "cursor"
            elif "Code" in result.stdout:
                return "vscode"
        except:
            pass
        
        return None
    
    def setup_best_integration(self) -> str:
        """Setup the best available integration."""
        # Priority: Claude Code > Aider > VS Code
        if self.claude.setup_environment():
            return "claude-code"
        elif self.aider.setup_tool("aider"):
            return "aider"
        elif self.vscode.check_tool("vscode"):
            self.vscode.setup_tool("vscode")
            return "vscode"
        else:
            return "none"
    
    def get_quick_fix_command(
        self,
        file_path: str,
        instruction: str,
        editor: Optional[str] = None
    ) -> Optional[str]:
        """Get a quick fix command for the editor."""
        editor = editor or self.detect_editor()
        
        if editor == "claude-code":
            tool = self.claude.tools["claude-code"]
            model = tool.model_prefix + "qwen2.5-coder:7b"
            return f"anthropic-curl --model {model} --message '{instruction}' --file {file_path}"
        
        elif editor == "aider":
            tool = self.aider.tools["aider"]
            model = tool.model_prefix + "qwen2.5-coder:7b"
            return f"aider --model {model} --message '{instruction}' --no-git --yes {file_path}"
        
        elif editor == "vscode":
            # For VS Code, we can only open the file
            return f"code {file_path}"
        
        return None
