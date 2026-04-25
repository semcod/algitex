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
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .ide_base import IDEHelper
from .ide_claude import ClaudeCodeHelper
from .ide_models import IDETool


class AiderHelper(IDEHelper):
    """Helper for Aider integration."""
    
    def __init__(self):
        super().__init__()
        self.tool_name = "aider"
    
    def fix_file(
        self,
        file_path: Union[str, Path],
        instruction: str,
        model: str = "qwen3-coder:latest",
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
            model = tool.model_prefix + "qwen3-coder:latest"
            return f"anthropic-curl --model {model} --message '{instruction}' --file {file_path}"
        
        elif editor == "aider":
            tool = self.aider.tools["aider"]
            model = tool.model_prefix + "qwen3-coder:latest"
            return f"aider --model {model} --message '{instruction}' --no-git --yes {file_path}"
        
        elif editor == "vscode":
            # For VS Code, we can only open the file
            return f"code {file_path}"
        
        return None
