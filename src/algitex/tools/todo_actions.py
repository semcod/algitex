"""Todo action handlers — separate action logic from runner orchestration.

This module contains action handlers for different MCP tools, keeping the
TodoRunner class focused on orchestration rather than action details.
"""

from typing import Optional
from algitex.tools.todo_parser import Task


def nap_action(task: Task) -> tuple[str, dict]:
    """Generate nap action for automated code repair."""
    desc = task.description.lower()

    # Determine fix type based on description
    if any(kw in desc for kw in ["import", "unused import"]):
        return ("fix_imports", {
            "file_path": task.file_path,
            "line": task.line_number,
            "description": task.description,
        })

    if any(kw in desc for kw in ["return type", "missing return", "->"]):
        return ("fix_types", {
            "file_path": task.file_path,
            "line": task.line_number,
            "description": task.description,
        })

    if any(kw in desc for kw in ["style", "format", "whitespace", "f-string"]):
        return ("fix_style", {
            "file_path": task.file_path,
            "line": task.line_number,
            "description": task.description,
        })

    # Generic fix_issue for everything else
    return ("fix_issue", {
        "file_path": task.file_path,
        "line": task.line_number,
        "description": task.description,
        "issue_type": "auto",
    })


def aider_action(task: Task) -> tuple[str, dict]:
    """Generate aider-mcp action for code tasks."""
    desc = task.description

    # Extract file path and what needs to be done
    file_path = task.file_path
    line_hint = task.line_number

    # Build prompt for aider
    prompt = f"{desc}"
    if file_path:
        prompt = f"In {file_path}"
        if line_hint:
            prompt += f" at line {line_hint}"
        prompt += f": {desc}"

    return ("aider_ai_code", {
        "prompt": prompt,
        "file_path": file_path or ".",
    })


def ollama_action(task: Task) -> tuple[str, dict]:
    """Generate ollama-mcp action for code fixing with local LLM."""
    desc = task.description.lower()
    file_path = task.file_path
    line_hint = task.line_number

    # Determine fix type based on description
    if any(kw in desc for kw in ["import", "unused import"]):
        return ("remove_unused_imports", {
            "file_path": file_path,
            "line": line_hint,
            "description": task.description,
            "model": "codellama",
        })

    if any(kw in desc for kw in ["return type", "missing return", "->"]):
        return ("add_types", {
            "file_path": file_path,
            "line": line_hint,
            "description": task.description,
            "model": "codellama",
        })

    if any(kw in desc for kw in ["style", "format", "whitespace", "f-string"]):
        return ("refactor_code", {
            "file_path": file_path,
            "line": line_hint,
            "description": task.description,
            "refactor_type": "style_fix",
            "model": "codellama",
        })

    # Generic fix_code for everything else
    return ("fix_code", {
        "file_path": file_path,
        "line": line_hint,
        "description": task.description,
        "issue_type": "auto",
        "model": "codellama",
    })


def filesystem_action(task: Task) -> tuple[str, dict]:
    """Generate filesystem-mcp action."""
    desc = task.description.lower()

    # Determine operation type
    if any(kw in desc for kw in ["read", "show", "view", "get"]):
        return ("read_file", {
            "path": task.file_path or "."
        })
    elif any(kw in desc for kw in ["write", "create", "add", "save"]):
        return ("write_file", {
            "path": task.file_path or "output.txt",
            "content": ""
        })
    elif any(kw in desc for kw in ["list", "ls", "dir"]):
        return ("list_directory", {
            "path": task.file_path or "."
        })
    elif any(kw in desc for kw in ["search", "find", "grep"]):
        return ("search_files", {
            "path": ".",
            "pattern": task.description
        })
    else:
        # Default to read
        return ("read_file", {
            "path": task.file_path or "."
        })


def github_action(task: Task) -> tuple[str, dict]:
    """Generate github-mcp action."""
    desc = task.description.lower()

    if any(kw in desc for kw in ["issue", "bug", "ticket"]):
        return ("create_issue", {
            "title": task.description[:100],
            "body": task.description,
        })
    elif any(kw in desc for kw in ["pr", "pull request", "merge"]):
        return ("create_pull_request", {
            "title": task.description[:100],
            "body": task.description,
        })
    elif any(kw in desc for kw in ["commit", "push", "code"]):
        return ("search_code", {
            "query": task.description,
        })
    else:
        return ("get_file_contents", {
            "path": task.file_path or "README.md"
        })


def get_action_handler(tool: str) -> Optional[callable]:
    """Get the appropriate action handler for a tool.
    
    Args:
        tool: The tool name (e.g., 'nap', 'aider-mcp', 'ollama-mcp', etc.)
        
    Returns:
        The action handler function or None if not found.
    """
    handlers = {
        "nap": nap_action,
        "aider-mcp": aider_action,
        "ollama-mcp": ollama_action,
        "filesystem-mcp": filesystem_action,
        "github-mcp": github_action,
    }
    return handlers.get(tool)


def determine_action(task: Task, tool: str) -> tuple[str, dict]:
    """Determine MCP action and arguments for the task.
    
    This is the main entry point for action resolution.
    
    Args:
        task: The task to determine action for
        tool: The tool name to use
        
    Returns:
        Tuple of (action_name, arguments_dict)
    """
    handler = get_action_handler(tool)
    if handler:
        return handler(task)
    
    # Generic action for unknown tools
    return ("process", {"task": task.description})
