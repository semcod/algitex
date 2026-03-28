# Comprehensive Docker Tools Test Workflow

This workflow demonstrates the full power of algitex's Docker tool orchestration by combining multiple tools in a real-world scenario: analyzing, refactoring, testing, and deploying code.

## Scenario: Automated Code Quality Improvement Pipeline

### Step 1: Initialize Project Analysis

```propact:docker
tool: code2llm
action: "code2llm /project -f toon,evolution"
```

### Step 2: Create Tickets from Analysis Results

```propact:docker
tool: planfile-mcp
action: planfile_create_tickets_bulk
input:
  source_tool: code2llm
  sprint: current
  auto_priority: true
```

### Step 3: Get High-Priority Tickets

```propact:docker
tool: planfile-mcp
action: planfile_list_tickets
input:
  status: "open"
  priority: "high"
  limit: 3
```

### Step 4: Refactor High-Complexity Functions

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Refactor the following high-complexity functions to reduce cyclomatic complexity:
    
    1. Split large functions into smaller, focused methods
    2. Extract common patterns into helper functions
    3. Use design patterns where appropriate
    4. Maintain backward compatibility
    5. Add comprehensive type hints
    
    Focus on functions with CC > 15 first.
  relative_editable_files:
    - "src/algitex/cli.py"
    - "src/algitex/workflows/__init__.py"
  relative_readonly_files:
    - "src/algitex/config.py"
    - "src/algitex/project.py"
  model: "anthropic/claude-3-5-sonnet"
```

### Step 5: Validate Refactored Code

```propact:docker
tool: vallm
action: batch
input:
  path: "/project/src"
  format: "json"
  errors_only: true
  threshold: 0.8
```

### Step 6: Run Unit Tests

```propact:docker
tool: docker-mcp
action: docker_run_container
input:
  image: "python:3.11"
  name: "test-runner"
  command: "cd /project && python -m pytest tests/ -v --cov=src"
  volumes:
    - "/project:/project"
  environment:
    - "PYTHONPATH=/project"
```

### Step 7: Check Test Coverage

```propact:docker
tool: vallm
action: score
input:
  path: "/project"
  metrics: ["test_coverage", "complexity"]
  threshold: 0.9
```

### Step 8: Generate Documentation

```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: |
    Generate comprehensive API documentation for the refactored modules:
    - Create docstrings for all public functions and classes
    - Generate usage examples
    - Document configuration options
    - Create a quick start guide
    
    Use Google-style docstrings and include type hints.
  relative_editable_files:
    - "src/algitex/tools/docker.py"
    - "src/algitex/propact/__init__.py"
  model: "gemini/gemini-2.5-pro"
```

### Step 9: Build Docker Image for Application

```propact:docker
tool: docker-mcp
action: docker_build_image
input:
  context_path: "/project"
  dockerfile_path: "/project/Dockerfile"
  tag: "algitex:test-${BUILD_NUMBER}"
  build_args:
    - "VERSION=0.2.0"
    - "BUILD_DATE=$(date +%Y-%m-%d)"
```

### Step 10: Run Security Scan

```propact:docker
tool: docker-mcp
action: docker_run_container
input:
  image: "aquasec/trivy:latest"
  name: "security-scan"
  command: "image algitex:test-${BUILD_NUMBER}"
  volumes:
    - "/var/run/docker.sock:/var/run/docker.sock"
```

### Step 11: Push to Registry (if tests pass)

```propact:docker
tool: docker-mcp
action: docker_push_image
input:
  image: "algitex:test-${BUILD_NUMBER}"
  registry: "docker.io/yourorg"
```

### Step 12: Create Pull Request

```propact:docker
tool: github-mcp
action: create_pull_request
input:
  owner: "yourorg"
  repo: "algitex"
  title: "refactor: Reduce complexity and improve code quality"
  body: |
    ## Summary
    Automated refactoring to reduce code complexity and improve maintainability.
    
    ## Changes
    - Reduced cyclomatic complexity from 42 to < 10 in critical functions
    - Added comprehensive type hints
    - Improved test coverage to 95%
    - Generated API documentation
    
    ## Validation
    - ✅ All tests passing
    - ✅ Code quality score: 0.92
    - ✅ Security scan passed
    - ✅ Documentation updated
    
    Closes #${ticket_ids}
  head: "refactor/complexity-reduction"
  base: "main"
  labels: ["refactoring", "automated", "quality-improvement"]
```

### Step 13: Update Ticket Status

```propact:docker
tool: planfile-mcp
action: planfile_update_ticket
input:
  ticket_id: "${ticket_id}"
  status: "done"
  resolution:
    tool: "aider-mcp"
    validation: "passed"
    pr_url: "${pr.url}"
    complexity_before: 42
    complexity_after: 8
```

### Step 14: Generate Report

```propact:docker
tool: filesystem-mcp
action: write_file
input:
  path: "/project/reports/refactoring-report-${BUILD_NUMBER}.md"
  content: |
    # Automated Refactoring Report
    
    ## Summary
    - Date: $(date +%Y-%m-%d)
    - Build: ${BUILD_NUMBER}
    - Tools used: code2llm, aider-mcp, vallm, docker-mcp, github-mcp
    
    ## Metrics
    | Metric | Before | After | Improvement |
    |--------|--------|-------|-------------|
    | Cyclomatic Complexity | 42 | 8 | 81% |
    | Test Coverage | 78% | 95% | 22% |
    | Code Quality Score | 0.65 | 0.92 | 42% |
    
    ## Actions Performed
    1. Analyzed code with code2llm
    2. Created 5 high-priority tickets
    3. Refactored 3 critical functions
    4. Validated with vallm
    5. Ran full test suite
    6. Generated documentation
    7. Built and scanned Docker image
    8. Created pull request
    
    ## Next Steps
    - Review and merge PR
    - Deploy to staging
    - Monitor performance
```

## Running the Workflow

1. Ensure all required environment variables are set:
   ```bash
   export GITHUB_PAT=your_github_token
   export GEMINI_API_KEY=your_gemini_key
   export ANTHROPIC_API_KEY=your_anthropic_key
   export BUILD_NUMBER=123
   ```

2. Save the workflow to a file (e.g., `comprehensive-test.md`)

3. Execute with:
   ```bash
   algitex workflow run comprehensive-test.md
   ```

4. Monitor progress:
   ```bash
   algitex status
   ```

## Expected Output

The workflow will:
1. Analyze the entire codebase
2. Identify high-complexity areas
3. Automatically refactor problematic code
4. Validate improvements
5. Run comprehensive tests
6. Generate documentation
7. Build and scan Docker images
8. Create a pull request with all changes
9. Generate a detailed report

## Troubleshooting

If any step fails:
1. Check tool logs with: `algitex docker caps <tool-name>`
2. Run individual steps manually using CLI commands
3. Check environment variables are properly set
4. Verify Docker is running and has sufficient permissions

## Customization

You can customize this workflow by:
- Changing the complexity threshold in Step 4
- Adding additional validation tools
- Modifying the build process in Step 9
- Adding deployment steps after PR creation
- Integrating with your CI/CD pipeline
