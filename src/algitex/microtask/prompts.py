"""Prompt templates for MicroTask execution."""

from __future__ import annotations

from collections.abc import Mapping

from algitex.microtask import MicroTask, TaskType


SYSTEM_PROMPTS: dict[int, str] = {
    0: "You are a precise Python refactoring assistant. Return only the minimal changed snippet.",
    1: "You are a careful Python refactoring assistant. Keep the rewrite local and small.",
    2: "You are a senior Python engineer. Preserve behavior and keep the change focused.",
    3: "You are a senior Python architect. Keep the whole module coherent and consistent.",
}

PROMPT_TEMPLATES: dict[TaskType, str] = {
    TaskType.UNKNOWN_MAGIC: "Return only a descriptive UPPER_SNAKE_CASE constant name for the number {number}.",
    TaskType.DOCSTRING_FIX: "Shorten the docstring to 1-2 lines while preserving the meaning.",
    TaskType.VARIABLE_RENAME: "Rename the unclear variable(s) to more descriptive names with the smallest safe edit.",
    TaskType.GUARD_CLAUSE: "Add one guard clause for the input validation path without refactoring unrelated code.",
    TaskType.TYPE_INFERENCE: "Add the smallest correct type annotations or return type hint possible.",
    TaskType.DICT_DISPATCH: "Convert the branching logic into a small dictionary dispatch if it simplifies the code.",
    TaskType.EXTRACT_METHOD: "Extract the repeated or complex block into a helper function or method.",
    TaskType.ERROR_HANDLING: "Improve exception handling with a minimal, local rewrite.",
    TaskType.SPLIT_FUNCTION: "Split the function into smaller helpers while keeping behavior identical.",
    TaskType.DEPENDENCY_CYCLE: "Break the dependency cycle with the smallest structural change.",
    TaskType.API_REDESIGN: "Propose a minimal API cleanup that keeps the existing behavior intact.",
    TaskType.FSTRING: "Rewrite string concatenation as an f-string or keep the change local.",
}


class _SafeDict(dict[str, str]):
    def __missing__(self, key: str) -> str:
        return ""


class PromptBuilder:
    """Build compact chat prompts for local LLMs."""

    def __init__(self, model_map: Mapping[int, str] | None = None) -> None:
        self.model_map = dict(
            model_map
            or {
                0: "none",
                1: "qwen3-coder:latest",
                2: "qwen2.5-coder:14b",
                3: "qwen2.5-coder:70b",
            }
        )

    def build(self, task: MicroTask, **extra: str) -> dict[str, object]:
        """Return Ollama-compatible chat payload for a task."""
        instruction = task.instruction or self._build_instruction(task, **extra)
        task.instruction = instruction

        system = SYSTEM_PROMPTS.get(task.tier, SYSTEM_PROMPTS[3])
        model = self._select_model(task)
        user = self._build_user_prompt(task, instruction)

        return {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": 0.0,
                "num_predict": task.type.max_output_tokens,
            },
        }

    def _select_model(self, task: MicroTask) -> str:
        """Choose a model for the task tier."""
        return self.model_map.get(task.tier, self.model_map[3])

    def _build_instruction(self, task: MicroTask, **extra: str) -> str:
        template = PROMPT_TEMPLATES.get(task.type)
        if not template:
            return "Return only the rewritten code snippet."

        values = _SafeDict(
            number=extra.get("number", ""),
            context=task.context,
            file=task.file,
            line=str(task.line_start),
            function_name=task.function_name,
            class_name=task.class_name,
            suggestion=task.suggested_fix,
        )
        return template.format_map(values)

    def _build_user_prompt(self, task: MicroTask, instruction: str) -> str:
        scope = task.function_name or task.class_name or "module"
        context = task.context.strip() or "[context unavailable]"
        suggested = task.suggested_fix.strip()
        lines = [
            f"Task ID: {task.id}",
            f"Task type: {task.type.value}",
            f"Tier: {task.tier} ({task.type.model_hint})",
            f"File: {task.file}",
            f"Target lines: {task.line_start}-{task.line_end}",
            f"Context lines: {task.context_start or task.line_start}-{task.context_end or task.line_end}",
            f"Scope: {scope}",
            f"Expected format: {task.expected_format}",
        ]
        if suggested:
            lines.append(f"Suggested fix: {suggested}")
        lines.extend(
            [
                "",
                "Context:",
                "```python",
                context,
                "```",
                "",
                "Instruction:",
                instruction,
                "",
                "Return only the requested code or identifier.",
            ]
        )
        return "\n".join(lines)


__all__ = ["PromptBuilder", "PROMPT_TEMPLATES", "SYSTEM_PROMPTS"]
