# Example: Using vallm for Code Validation

This example demonstrates how to use vallm through algitex's Docker tool orchestration for code validation and quality assessment.

## Prerequisites
- Ensure the project directory is properly mounted
- Have Python files to validate

## Example 1: Basic Code Validation

```propact:docker
tool: vallm
action: validate
input:
  path: "/project/src"
  recursive: true
  format: "json"
```

## Example 2: Batch Validation with Error Reporting

```propact:docker
tool: vallm
action: batch
input:
  path: "/project"
  format: "json"
  errors_only: true
  output_file: "/project/validation_report.json"
```

## Example 3: Scoring Code Quality

```propact:docker
tool: vallm
action: score
input:
  path: "/project/src/algitex"
  threshold: 0.8
  metrics: ["complexity", "maintainability", "readability"]
```

## Example 4: Comprehensive Analysis

```propact:docker
tool: vallm
action: analyze
input:
  path: "/project"
  output_format: "toon"
  include_metrics:
    - cyclomatic_complexity
    - lines_of_code
    - test_coverage
    - duplication
  exclude_patterns:
    - "__pycache__"
    - "*.pyc"
    - ".git"
```

## Example 5: Evolution Export for Tracking Changes

```propact:docker
tool: vallm
action: evolution-export
input:
  path: "/project"
  baseline_file: "/project/baseline.json"
  output_file: "/project/evolution_report.json"
  compare_with: "last_commit"
```

## Example 6: Custom Validation Rules

```propact:docker
tool: vallm
action: validate
input:
  path: "/project/src"
  rules:
    - name: "max_complexity"
      threshold: 10
      message: "Function complexity exceeds threshold"
    - name: "min_test_coverage"
      threshold: 80
      message: "Test coverage below 80%"
    - name: "no_print_statements"
      enabled: true
      message: "Remove print statements from production code"
```

## Running the Examples

To run these examples:

1. Save the workflow to a file (e.g., `vallm-validation.md`)
2. Execute with: `algitex workflow run vallm-validation.md`

## Using via CLI

```bash
# Spawn vallm
algitex docker spawn vallm

# Run basic validation
algitex docker call vallm validate -i '{
  "path": "/project/src",
  "recursive": true,
  "format": "json"
}'

# Run batch analysis
algitex docker call vallm batch -i '{
  "path": "/project",
  "format": "json",
  "errors_only": true
}'

# Get code scores
algitex docker call vallm score -i '{
  "path": "/project/src",
  "threshold": 0.8
}'

# Teardown when done
algitex docker teardown vallm
```

## Integration with Other Tools

Vallm can be combined with other tools in a workflow:

```markdown
# Complete Validation Pipeline

## Step 1: Analyze with code2llm
```propact:docker
tool: code2llm
action: "code2llm /project -f toon"
```

## Step 2: Validate with vallm
```propact:docker
tool: vallm
action: batch
input:
  path: "/project"
  format: "json"
  errors_only: true
```

## Step 3: Create tickets for issues found
```propact:docker
tool: planfile-mcp
action: planfile_create_tickets_bulk
input:
  source_tool: vallm
  priority: "high"
```
