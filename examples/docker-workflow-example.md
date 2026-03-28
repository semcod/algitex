# Example: Refactor with Docker Tools

This workflow demonstrates how to use algitex's Docker tool orchestration to perform a complete refactoring cycle.

## Step 1: Analyze the code with code2llm

```propact:docker
tool: code2llm
action: "code2llm /project -f toon,evolution"
```

## Step 2: Import analysis results as tickets

```propact:docker
tool: planfile-mcp
action: planfile_create_tickets_bulk
input:
  source_tool: code2llm
  sprint: current
  auto_priority: true
```

## Step 3: Fix the highest complexity function with aider-mcp

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Refactor the `batch` function in cli.py (currently CC=42) to reduce complexity:
    - Split into smaller functions: _batch_collect_files, _batch_validate_file, _batch_report
    - Keep the public API unchanged
    - Add proper type hints
    - Preserve all existing functionality
  relative_editable_files:
    - "src/algitex/cli.py"
  relative_readonly_files:
    - "src/algitex/config.py"
  model: "gemini/gemini-2.5-pro"
```

## Step 4: Validate the refactoring with vallm

```propact:docker
tool: vallm
action: "batch"
input:
  path: "/project"
  format: "json"
  errors_only: true
```

## Step 5: Run the test suite

```propact:docker
tool: playwright-mcp
action: navigate
input:
  url: "http://localhost:8080/tests"
  wait_for: "#test-results"
```

## Step 6: Create a pull request if validation passes

```propact:docker
tool: github-mcp
action: create_pull_request
input:
  title: "refactor: split batch() CC=42 → CC≤10"
  body: |
    Automated refactoring via algitex Pipeline + aider-mcp
    
    - Split high-complexity batch function into smaller, focused functions
    - Maintained backward compatibility
    - Added comprehensive type hints
    - All tests passing
  head: "refactor/batch-split"
  base: "main"
  draft: false
```

## Step 7: Update ticket status

```propact:docker
tool: planfile-mcp
action: planfile_update_ticket
input:
  ticket_id: "${ticket.id}"
  status: "done"
  resolution:
    tool: "aider-mcp"
    validation: "passed"
    pr_url: "${pr.url}"
```

---

# Full Pipeline Example

For a complete pipeline that processes multiple tickets:

```markdown
# Multi-ticket Processing Pipeline

## Initialize
```propact:shell
echo "Starting multi-ticket processing pipeline"
```

## Process each high-priority ticket
```propact:docker
tool: planfile-mcp
action: planfile_list_tickets
input:
  status: "open"
  priority: "high"
  limit: 5
```

## For each ticket: analyze → fix → validate → PR
```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: "Fix the issue described in ticket ${ticket.title}: ${ticket.description}"
  relative_editable_files: "${ticket.files_to_modify}"
  model: "claude-3-5-sonnet"
```

## Batch validation
```propact:docker
tool: vallm
action: "score"
input:
  path: "/project"
  threshold: 0.9
```

## Cleanup
```propact:shell
echo "Pipeline complete. Cleaning up..."
```
