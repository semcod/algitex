"""Build prompts for micro-LLM fixes."""

from __future__ import annotations

from algitex.todo.micro_models import FunctionSnippet
from algitex.todo.micro_utils import extract_first_int
from algitex.todo.tiering import TaskTriage
from algitex.tools.todo_parser import Task


class MicroPromptBuilder:
    """Build narrow prompts for micro-LLM fixes."""

    SYSTEM_PROMPT = (
        "You are a precise Python refactoring assistant. "
        "Make the smallest possible change. Return ONLY the requested content."
    )

    def build(self, triage: TaskTriage, snippet: FunctionSnippet, task: Task) -> list[dict[str, str]]:
        """Build Ollama chat messages for the given task."""
        prompt = self._build_user_prompt(triage, snippet, task)
        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

    def _build_user_prompt(self, triage: TaskTriage, snippet: FunctionSnippet, task: Task) -> str:
        """Create the user-facing prompt text."""
        header = [
            f"Task category: {triage.category}",
            f"File: {task.file_path or snippet.file_path}",
            f"Line: {task.line_number or snippet.start_line}",
            f"Target: {snippet.kind} `{snippet.name}`",
            "",
        ]

        if triage.category == "docstring":
            instruction = (
                "Rewrite the function docstring to be concise (1-2 lines max). "
                "Preserve behavior and public API. Return ONLY the updated function source."
            )
        elif triage.category == "rename":
            instruction = (
                "Rename the unclear variable(s) to more descriptive names within this function. "
                "Make the smallest safe edit and return ONLY the updated function source."
            )
        elif triage.category == "guard_clause":
            instruction = (
                "Add one guard clause for the indicated parameter or input validation path. "
                "Do not refactor unrelated code. Return ONLY the updated function source."
            )
        elif triage.category == "dispatch":
            instruction = (
                "If appropriate, convert the branching logic to a small dictionary dispatch or lookup table. "
                "Keep the behavior identical. Return ONLY the updated function source."
            )
        elif triage.category == "magic":
            number = triage.number if triage.number is not None else extract_first_int(task.description)
            instruction = (
                f"Suggest a descriptive UPPER_SNAKE_CASE constant name for the magic number {number}. "
                "Return ONLY the name, nothing else."
            )
        else:
            instruction = (
                "Improve this function with a minimal local edit that matches the task. "
                "Return ONLY the updated function source."
            )

        return "\n".join(header + [instruction, "", "```python", snippet.source, "```"])
