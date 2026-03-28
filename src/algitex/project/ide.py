"""IDE integration mixins for Project class."""

from __future__ import annotations

from typing import Optional

from algitex.tools.ide import IDEHelper, ClaudeCodeHelper, AiderHelper, EditorIntegration


class IDEMixin:
    """IDE integration functionality for Project."""

    def __init__(self) -> None:
        self.ide = IDEHelper()
        self.claude = ClaudeCodeHelper()
        self.aider = AiderHelper()
        self.editor = EditorIntegration()

    def setup_ide(self, tool_name: str) -> bool:
        """Setup IDE tool."""
        return self.ide.setup_tool(tool_name)

    def fix_with_claude(
        self,
        file_path: str,
        instruction: str,
        model: str = "qwen2.5-coder:7b"
    ) -> bool:
        """Fix file using Claude Code."""
        return self.claude.fix_file(file_path, instruction, model)

    def fix_with_aider(
        self,
        file_path: str,
        instruction: str,
        model: str = "qwen2.5-coder:7b"
    ) -> bool:
        """Fix file using Aider."""
        return self.aider.fix_file(file_path, instruction, model)

    def detect_editor(self) -> Optional[str]:
        """Detect which editor is available."""
        return self.editor.detect_editor()

    def get_ide_status(self) -> dict:
        """Get status of all IDE tools."""
        return self.ide.get_tool_status()
