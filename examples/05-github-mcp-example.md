# Example: Using github-mcp for Repository Management

This example demonstrates how to use github-mcp through algitex's Docker tool orchestration for GitHub repository operations.

## Prerequisites
- Set GitHub Personal Access Token: `export GITHUB_PAT=your_token`
- Sufficient repository permissions

## Example 1: Creating an Issue

```propact:docker
tool: github-mcp
action: create_issue
input:
  owner: "myorg"
  repo: "myproject"
  title: "Refactor authentication module"
  body: |
    The current authentication module has high complexity and needs refactoring.
    
    **Tasks:**
    - [ ] Split authenticate() function into smaller methods
    - [ ] Add unit tests for edge cases
    - [ ] Update documentation
    
    **Acceptance Criteria:**
    - Cyclomatic complexity < 10
    - Test coverage > 90%
    - All existing functionality preserved
  labels: ["enhancement", "refactoring", "priority-high"]
```

## Example 2: Creating a Pull Request

```propact:docker
tool: github-mcp
action: create_pull_request
input:
  owner: "myorg"
  repo: "myproject"
  title: "feat: Add OAuth2 authentication support"
  body: |
    This PR adds OAuth2 authentication support to the application.
    
    ## Changes
    - Implemented OAuth2 flow with GitHub provider
    - Added refresh token support
    - Updated user model to store OAuth data
    - Added migration scripts
    
    ## Testing
    - Added comprehensive unit tests
    - Manual testing completed
    - CI/CD pipeline passing
    
    Closes #123
  head: "feature/oauth2-auth"
  base: "main"
  draft: false
```

## Example 3: Searching Code

```propact:docker
tool: github-mcp
action: search_code
input:
  query: "TODO: refactor"
  owner: "myorg"
  repo: "myproject"
  sort: "updated"
  order: "desc"
```

## Example 4: Listing Commits

```propact:docker
tool: github-mcp
action: list_commits
input:
  owner: "myorg"
  repo: "myproject"
  branch: "main"
  per_page: 20
```

## Example 5: Getting File Contents

```propact:docker
tool: github-mcp
action: get_file_contents
input:
  owner: "myorg"
  repo: "myproject"
  path: "README.md"
  ref: "main"
```

## Example 6: Creating or Updating a File

```propact:docker
tool: github-mcp
action: create_or_update_file
input:
  owner: "myorg"
  repo: "myproject"
  path: "docs/api/v2/changes.md"
  message: "docs: Add API v2 changelog"
  content: |
    # API v2 Changelog
    
    ## [2.0.0] - 2024-03-28
    
    ### Added
    - OAuth2 authentication endpoint
    - Refresh token support
    - Rate limiting headers
    
    ### Changed
    - Authentication header format
    - Response structure for user endpoints
    
    ### Deprecated
    - Basic authentication (will be removed in v3.0)
    
    ### Security
    - Added CSRF protection
    - Enhanced input validation
  branch: "main"
```

## Example 7: Creating Multiple Issues in Bulk

```propact:docker
tool: github-mcp
action: create_issue
input:
  owner: "myorg"
  repo: "myproject"
  title: "Add integration tests for payment module"
  body: |
    The payment module lacks integration tests.
    
    Required test scenarios:
    - Successful payment flow
    - Payment failure handling
    - Refund processing
    - Third-party API timeouts
  labels: ["testing", "payment", "priority-medium"]
```

## Running the Examples

To run these examples:

1. Save the workflow to a file (e.g., `github-operations.md`)
2. Execute with: `algitex workflow run github-operations.md`

## Using via CLI

```bash
# Spawn github-mcp
algitex docker spawn github-mcp

# Create an issue
algitex docker call github-mcp create_issue -i '{
  "owner": "myorg",
  "repo": "myproject",
  "title": "Bug: Fix authentication timeout",
  "body": "Users experiencing timeout after 30 seconds",
  "labels": ["bug", "authentication"]
}'

# Search code
algitex docker call github-mcp search_code -i '{
  "query": "class Authentication",
  "owner": "myorg",
  "repo": "myproject"
}'

# List commits
algitex docker call github-mcp list_commits -i '{
  "owner": "myorg",
  "repo": "myproject",
  "branch": "main",
  "per_page": 10
}'

# Teardown when done
algitex docker teardown github-mcp
```

## Integration Example: Automated Release Workflow

```markdown
# Automated Release Process

## 1. Get latest release notes
```propact:docker
tool: github-mcp
action: get_file_contents
input:
  owner: "myorg"
  repo: "myproject"
  path: "CHANGELOG.md"
  ref: "main"
```

## 2. Create release branch
```propact:docker
tool: github-mcp
action: create_pull_request
input:
  owner: "myorg"
  repo: "myproject"
  title: "release: Prepare v2.1.0"
  body: "Release preparation for v2.1.0"
  head: "release/v2.1.0"
  base: "main"
```

## 3. Update version files
```propact:docker
tool: github-mcp
action: create_or_update_file
input:
  owner: "myorg"
  repo: "myproject"
  path: "version.py"
  message: "bump: version to 2.1.0"
  content: "__version__ = '2.1.0'"
  branch: "release/v2.1.0"
```

## 4. Create release tag
```propact:docker
tool: github-mcp
action: create_release
input:
  owner: "myorg"
  repo: "myproject"
  tag_name: "v2.1.0"
  name: "Release v2.1.0"
  body: "## v2.1.0\n\n### Added\n- New feature X\n### Fixed\n- Bug Y\n"
  target_commitish: "release/v2.1.0"
```
