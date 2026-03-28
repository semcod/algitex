# Example: Using aider-mcp for Code Refactoring

This example demonstrates how to use aider-mcp through algitex's Docker tool orchestration to perform code refactoring.

## Prerequisites
- Set up API keys: `export GEMINI_API_KEY=your_key` or `export ANTHROPIC_API_KEY=your_key`
- Ensure the project directory is mounted correctly

## Example 1: Simple Function Refactoring

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Refactor the following function to improve readability and reduce complexity:
    
    def process_data(items):
        results = []
        for item in items:
            if item is not None:
                if item.get('active', False):
                    if item.get('type') == 'A':
                        results.append(item['value'] * 2)
                    elif item.get('type') == 'B':
                        results.append(item['value'] + 10)
                    else:
                        results.append(item['value'])
        return results
    
    Split it into smaller, focused functions with clear names.
  relative_editable_files:
    - "src/example.py"
  model: "gemini/gemini-2.5-pro"
```

## Example 2: Adding Type Hints

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Add comprehensive type hints to all functions in the file.
    Use appropriate types from the typing module.
    Include return types for all functions.
  relative_editable_files:
    - "src/calculator.py"
  relative_readonly_files:
    - "src/models.py"
  model: "anthropic/claude-3-5-sonnet"
```

## Example 3: Documentation Generation

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Add comprehensive docstrings to all classes and methods following Google style.
    Include:
    - Description of what the function does
    - Args section with type and description
    - Returns section with type and description
    - Raises section for exceptions
  relative_editable_files:
    - "src/api/client.py"
  model: "gemini/gemini-2.5-pro"
```

## Example 4: Test Generation

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Generate comprehensive unit tests for the UserService class.
    Use pytest framework.
    Include tests for:
    - Normal operation cases
    - Edge cases
    - Error handling
    - Mock external dependencies
  relative_editable_files:
    - "tests/test_user_service.py"
  relative_readonly_files:
    - "src/services/user_service.py"
  model: "anthropic/claude-3-5-sonnet"
```

## Example 5: Performance Optimization

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Optimize the following database query function for better performance:
    
    def get_user_orders(user_id, date_from=None, date_to=None):
        query = "SELECT * FROM orders WHERE user_id = ?"
        params = [user_id]
        
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
            
        # Execute query and return results
        return db.execute(query, params).fetchall()
    
    Consider:
    - Using specific column selection instead of *
    - Adding database indexes
    - Using prepared statements
    - Pagination for large result sets
  relative_editable_files:
    - "src/database/orders.py"
  model: "gemini/gemini-2.5-pro"
```

## Running the Examples

To run these examples:

1. Save the workflow to a file (e.g., `aider-refactor.md`)
2. Execute with: `algitex workflow run aider-refactor.md`

You can also run individual steps using the CLI:

```bash
# Spawn aider-mcp
algitex docker spawn aider-mcp

# Call a specific action
algitex docker call aider-mcp aider_ai_code -i '{
  "prompt": "Add type hints to main.py",
  "relative_editable_files": ["main.py"],
  "model": "gemini/gemini-2.5-pro"
}'

# Teardown when done
algitex docker teardown aider-mcp
```
