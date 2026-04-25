"""Claude Code integration helper."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .ide_base import IDEHelper


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
        model: str = "qwen3-coder:latest",
        dry_run: bool = False,
    ) -> bool:
        """Fix a file using Claude Code."""
        tool = self.tools[self.tool_name]
        model = tool.model_prefix + model

        cmd = [tool.command, "--model", model, "--message", instruction, "--file", str(file_path)]

        print(f"Running: {' '.join(cmd)}")

        if dry_run:
            print("[DRY RUN] Would execute command")
            return True

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ File fixed successfully")
                return True
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
        model: str = "qwen3-coder:latest",
        files: List[Union[str, Path]] = None,
    ) -> Optional[str]:
        """Chat with Claude Code."""
        tool = self.tools[self.tool_name]
        model = tool.model_prefix + model

        cmd = [tool.command, "--model", model, "--message", message]

        if files:
            for file_path in files:
                cmd.extend(["--file", str(file_path)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return result.stdout
            print(f"Error: {result.stderr}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def batch_fix(
        self,
        issues: List[Dict[str, Any]],
        model: str = "qwen3-coder:latest",
        dry_run: bool = False,
    ) -> Dict[str, bool]:
        """Fix multiple issues."""
        results = {}

        for i, issue in enumerate(issues, 1):
            file_path = issue.get("file")
            description = issue.get("description", "")

            if not file_path:
                continue

            print(f"[{i}/{len(issues)}] Fixing {file_path}")
            success = self.fix_file(file_path, description, model=model, dry_run=dry_run)
            results[file_path] = success

        return results
