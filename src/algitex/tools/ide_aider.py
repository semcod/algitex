"""Aider integration helper."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Union

from .ide_base import IDEHelper


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
        dry_run: bool = False,
    ) -> bool:
        """Fix a file using Aider."""
        tool = self.tools[self.tool_name]
        model = tool.model_prefix + model

        cmd = [
            tool.command,
            "--model",
            model,
            "--openai-api-key",
            "dummy",
            "--no-git",
            "--no-commit",
            "--yes",
            "--no-check-version",
            "--message",
            instruction,
            str(file_path),
        ]

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
