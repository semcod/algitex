# Example: Using filesystem-mcp for File Operations

This example demonstrates how to use filesystem-mcp through algitex's Docker tool orchestration for file system operations.

## Prerequisites
- Ensure the project directory is properly mounted in the container

## Example 1: Reading File Contents

```propact:docker
tool: filesystem-mcp
action: read_file
input:
  path: "/workspace/README.md"
```

## Example 2: Listing Directory Contents

```propact:docker
tool: filesystem-mcp
action: list_directory
input:
  path: "/workspace/src"
  recursive: false
```

## Example 3: Searching for Files

```propact:docker
tool: filesystem-mcp
action: search_files
input:
  pattern: "*.py"
  path: "/workspace"
  exclude_patterns: ["__pycache__", "*.pyc"]
```

## Example 4: Writing a New File

```propact:docker
tool: filesystem-mcp
action: write_file
input:
  path: "/workspace/docs/api_reference.md"
  content: |
    # API Reference
    
    ## Authentication
    All API endpoints require authentication using Bearer tokens.
    
    ## Endpoints
    
    ### GET /api/users
    Retrieve a list of all users.
    
    ### POST /api/users
    Create a new user.
    
    ### GET /api/users/{id}
    Retrieve a specific user by ID.
```

## Example 5: Batch File Processing

```propact:docker
tool: filesystem-mcp
action: search_files
input:
  pattern: "*.md"
  path: "/workspace/docs"
```

## Example 6: Creating Directory Structure

```propact:docker
tool: filesystem-mcp
action: write_file
input:
  path: "/workspace/tests/fixtures/test_data.json"
  content: |
    {
      "users": [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
      ],
      "posts": [
        {"id": 1, "user_id": 1, "title": "First Post", "content": "Hello World!"},
        {"id": 2, "user_id": 2, "title": "Second Post", "content": "Another Post"}
      ]
    }
```

## Running the Examples

To run these examples:

1. Save the workflow to a file (e.g., `filesystem-operations.md`)
2. Execute with: `algitex workflow run filesystem-operations.md`

## Using via CLI

```bash
# Spawn filesystem-mcp
algitex docker spawn filesystem-mcp

# List files
algitex docker call filesystem-mcp list_directory -i '{
  "path": "/workspace"
}'

# Read a file
algitex docker call filesystem-mcp read_file -i '{
  "path": "/workspace/README.md"
}'

# Teardown when done
algitex docker teardown filesystem-mcp
```
