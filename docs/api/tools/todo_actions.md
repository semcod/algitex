# `tools.todo_actions`

Todo action handlers — separate action logic from runner orchestration.

This module contains action handlers for different MCP tools, keeping the
TodoRunner class focused on orchestration rather than action details.


## Functions

### `nap_action`

```python
def nap_action(task: Task) -> tuple[str, dict]
```

Generate nap action for automated code repair.

### `aider_action`

```python
def aider_action(task: Task) -> tuple[str, dict]
```

Generate aider-mcp action for code tasks.

### `ollama_action`

```python
def ollama_action(task: Task) -> tuple[str, dict]
```

Generate ollama-mcp action for code fixing with local LLM.

### `filesystem_action`

```python
def filesystem_action(task: Task) -> tuple[str, dict]
```

Generate filesystem-mcp action.

### `github_action`

```python
def github_action(task: Task) -> tuple[str, dict]
```

Generate github-mcp action.

### `get_action_handler`

```python
def get_action_handler(tool: str) -> Optional[callable]
```

Get the appropriate action handler for a tool.
    
    Args:
        tool: The tool name (e.g., 'nap', 'aider-mcp', 'ollama-mcp', etc.)
        
    Returns:
        The action handler function or None if not found.
    

### `determine_action`

```python
def determine_action(task: Task, tool: str) -> tuple[str, dict]
```

Determine MCP action and arguments for the task.
    
    This is the main entry point for action resolution.
    
    Args:
        task: The task to determine action for
        tool: The tool name to use
        
    Returns:
        Tuple of (action_name, arguments_dict)
    
