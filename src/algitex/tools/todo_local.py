"""Local todo executor - execute simple code fixes without Docker.

Handles common prefact-style fixes:
- Add return type annotations (-> None)
- Remove unused imports
- Convert string concatenation to f-strings
- Add module execution blocks
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from algitex.tools.todo_parser import Task


@dataclass
class LocalTaskResult:
    """Result of executing a single task locally."""
    task: Task
    success: bool
    action: str
    output: str = ""
    error: Optional[str] = None


class LocalExecutor:
    """Execute simple code fixes locally without Docker."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()

    def can_execute(self, task: Task) -> bool:
        """Check if task can be executed locally."""
        desc = task.description.lower()
        local_fixes = [
            "return type", "missing return", "-> none",
            "unused import", "unused import:",
 "f-string", "string concatenation",
 "standalone main function",
 "module execution block",
        ]
        return any(fix in desc for fix in local_fixes)

    def execute(self, task: Task) -> LocalTaskResult:
        """Execute a single task locally."""
        if not task.file_path:
            return LocalTaskResult(
                task=task,
                success=False,
                action="skip",
                error="No file path specified"
            )

        file_path = self.project_path / task.file_path
        if not file_path.exists():
            return LocalTaskResult(
                task=task,
                success=False,
                action="skip",
                error=f"File not found: {file_path}"
            )

        try:
            content = file_path.read_text()
            original_content = content

            # Determine fix type and apply
            desc = task.description.lower()

            if "return type" in desc or "-> none" in desc or "-> any" in desc:
                # Check if already has return type
                if self._has_return_type(content, task.line_number):
                    return LocalTaskResult(
                        task=task,
                        success=True,
                        action="already_fixed",
                        output=f"Return type already present in {task.file_path}:{task.line_number}"
                    )
                content = self._fix_return_type(content, task.line_number, desc)
                action = "fix_return_type"
            elif "unused import" in desc:
                # Check if import was already removed
                if not self._import_exists(content, task.line_number, desc):
                    return LocalTaskResult(
                        task=task,
                        success=True,
                        action="already_fixed",
                        output=f"Import already removed from {task.file_path}:{task.line_number}"
                    )
                content = self._fix_unused_import(content, task.line_number, desc)
                action = "fix_unused_import"
            elif "f-string" in desc or "string concatenation" in desc:
                content = self._fix_fstring(content, task.line_number)
                action = "fix_fstring"
            elif "standalone main function" in desc:
                content = self._fix_standalone_main(content)
                action = "fix_standalone_main"
            elif "module execution block" in desc:
                content = self._add_main_block(content)
                action = "add_main_block"
            else:
                return LocalTaskResult(
                    task=task,
                    success=False,
                    action="skip",
                    error="No local fix available for this task"
                )

            # Check if changes were made
            if content == original_content:
                return LocalTaskResult(
                    task=task,
                    success=False,
                    action=action,
                    error="No changes made (pattern not found)"
                )

            # Write changes
            file_path.write_text(content)

            return LocalTaskResult(
                task=task,
                success=True,
                action=action,
                output=f"Applied {action} to {task.file_path}"
            )

        except Exception as e:
            return LocalTaskResult(
                task=task,
                success=False,
                action="error",
                error=str(e)
            )

    def _fix_return_type(self, content: str, line_number: Optional[int], desc: str) -> str:
        """Add -> None return type to function."""
        lines = content.split('\n')
        if not line_number or line_number > len(lines):
            return content

        idx = line_number - 1
        line = lines[idx]

        # Check if function definition
        if not re.match(r'^(\s*)def\s+(\w+)\s*\(', line):
            return content

        # Check if already has return type
        if '->' in line:
            return content

        # Find the end of function definition (before colon)
        match = re.match(r'^(\s*def\s+\w+\s*\([^)]*\))', line)
        if match:
            func_def = match.group(1)
            rest = line[len(func_def):]
            # Add -> None before the colon
            if rest.startswith(':'):
                lines[idx] = func_def + ' -> None' + rest
            else:
                lines[idx] = func_def + ' -> None:' + rest[1:] if rest.startswith(':') else func_def + ' -> None:' + rest

        return '\n'.join(lines)

    def _has_return_type(self, content: str, line_number: Optional[int]) -> bool:
        """Check if function at line already has return type annotation."""
        lines = content.split('\n')
        if not line_number or line_number > len(lines):
            return False

        idx = line_number - 1
        line = lines[idx]

        # Check if function definition and has ->
        if not re.match(r'^(\s*)def\s+(\w+)\s*\(', line):
            return False

        return '->' in line

    def _import_exists(self, content: str, line_number: Optional[int], desc: str) -> bool:
        """Check if import still exists at the given line."""
        lines = content.split('\n')
        if not line_number or line_number > len(lines):
            return False

        idx = line_number - 1
        line = lines[idx]

        # Extract import name from description
        match = re.search(r"import['\"]?\s*(\w+)", desc)
        if match:
            import_name = match.group(1)
            # Check if this line contains the import
            return import_name in line and ('import' in line or 'from' in line)
        return False

    def _fix_unused_import(self, content: str, line_number: Optional[int], desc: str) -> str:
        """Remove unused import line."""
        lines = content.split('\n')
        if not line_number or line_number > len(lines):
            return content

        idx = line_number - 1

        # Extract import name from description
        match = re.search(r"import['\"]?\s*(\w+)", desc)
        if match:
            import_name = match.group(1)
            # Find and remove lines with this import
            new_lines = []
            for i, line in enumerate(lines):
                if i == idx or (import_name in line and ('import' in line or 'from' in line)):
                    # Check if it's the unused import
                    if import_name in line:
                        continue  # Skip this line
                new_lines.append(line)
            return '\n'.join(new_lines)

        return content

    def _fix_fstring(self, content: str, line_number: Optional[int]) -> str:
        """Convert simple string concatenation to f-string."""
        lines = content.split('\n')
        if not line_number or line_number > len(lines):
            return content

        idx = line_number - 1
        line = lines[idx]

        # Simple pattern: "text " + var + " text"
        # Convert to f"text {var} text"
        pattern = r'["\']([^"\']+)["\']\s*\+\s*(\w+)\s*\+\s*["\']([^"\']*)["\']'
        replacement = r'f"\1{\2}\3"'
        new_line = re.sub(pattern, replacement, line)

        lines[idx] = new_line
        return '\n'.join(lines)

    def _fix_standalone_main(self, content: str) -> str:
        """Add standalone check to main function - not applicable for local fix."""
        # This requires semantic understanding, skip
        return content

    def _add_main_block(self, content: str) -> str:
        """Add if __name__ == '__main__': block."""
        if 'if __name__' in content:
            return content

        lines = content.rstrip().split('\n')

        # Find if there's a main() call at the end
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                if re.match(r'^main\(\s*\)$', line):
                    # Replace with main block
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    lines[i] = ' ' * indent + "if __name__ == '__main__':"
                    lines.insert(i + 1, ' ' * (indent + 4) + 'main()')
                    return '\n'.join(lines) + '\n'

        # Just append main block at the end
        return content.rstrip() + "\n\nif __name__ == '__main__':\n    main()\n"
