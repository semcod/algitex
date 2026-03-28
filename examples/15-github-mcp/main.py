#!/usr/bin/env python3
"""Example 15: GitHub MCP - Repository Management Demo.

Demonstrates using github-mcp through algitex's Docker tool orchestration
for GitHub repository operations.
"""

import os
from pathlib import Path


def load_env():
    """Load .env file if present."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = val


def check_github_token():
    """Check if GitHub PAT is set."""
    token = os.getenv("GITHUB_PAT")
    if not token:
        print("⚠️  GITHUB_PAT not found!")
        print("Set GITHUB_PAT in .env file")
        return False
    return True


def demo_github_operations():
    """Show example GitHub operations."""
    
    examples = [
        {
            "title": "1. Creating an Issue",
            "action": "create_issue",
            "description": "Create issue with tasks and acceptance criteria",
            "input": {
                "owner": "myorg",
                "repo": "myproject",
                "title": "Refactor authentication module",
                "labels": ["enhancement", "refactoring"]
            }
        },
        {
            "title": "2. Creating a Pull Request",
            "action": "create_pull_request",
            "description": "Create PR with detailed description",
            "input": {
                "owner": "myorg",
                "repo": "myproject",
                "title": "feat: Add OAuth2 authentication support",
                "head": "feature/oauth2-auth",
                "base": "main"
            }
        },
        {
            "title": "3. Searching Code",
            "action": "search_code",
            "description": "Search repository code",
            "input": {
                "query": "TODO: refactor",
                "owner": "myorg",
                "repo": "myproject"
            }
        },
        {
            "title": "4. Listing Commits",
            "action": "list_commits",
            "description": "Get recent commits",
            "input": {
                "owner": "myorg",
                "repo": "myproject",
                "branch": "main",
                "per_page": 20
            }
        },
        {
            "title": "5. Getting File Contents",
            "action": "get_file_contents",
            "description": "Fetch file from repository",
            "input": {
                "owner": "myorg",
                "repo": "myproject",
                "path": "README.md",
                "ref": "main"
            }
        },
        {
            "title": "6. Creating or Updating a File",
            "action": "create_or_update_file",
            "description": "Commit file changes",
            "input": {
                "owner": "myorg",
                "repo": "myproject",
                "path": "docs/changelog.md",
                "message": "docs: Add changelog"
            }
        }
    ]
    
    print("\n=== GitHub MCP Repository Management Examples ===\n")
    
    for ex in examples:
        print(f"\n{ex['title']}")
        print(f"   Description: {ex['description']}")
        print(f"   Action: {ex['action']}")
    
    print("\n\n=== CLI Usage Examples ===\n")
    print("Spawn github-mcp:")
    print("  algitex docker spawn github-mcp")
    print("\nCreate issue:")
    print('  algitex docker call github-mcp create_issue -i \'{"owner": "myorg", "repo": "myproject", "title": "Bug: Fix auth", "labels": ["bug"]}\'')
    print("\nSearch code:")
    print('  algitex docker call github-mcp search_code -i \'{"query": "class Auth", "owner": "myorg", "repo": "myproject"}\'')
    print("\nTeardown:")
    print("  algitex docker teardown github-mcp")


def demo_with_docker_tools():
    """Demonstrate Docker tool usage if available."""
    try:
        from algitex.tools.docker import DockerToolManager
        from algitex.config import Config
        
        config = Config.load()
        mgr = DockerToolManager(config)
        
        print("\n=== Docker Tools Status ===\n")
        
        tools = mgr.list_tools()
        print(f"Available: {len(tools)} tools")
        for tool in tools:
            print(f"  - {tool}")
        
        if "github-mcp" in tools:
            print("\n✅ github-mcp is available!")
        else:
            print("\n⚠️  github-mcp not found in docker-tools.yaml")
            
    except ImportError as e:
        print(f"⚠️  Docker tools not available: {e}")


if __name__ == "__main__":
    load_env()
    
    if check_github_token():
        print("✅ GITHUB_PAT configured\n")
    else:
        print("⚠️  Running in demo mode\n")
    
    demo_github_operations()
    
    try:
        demo_with_docker_tools()
    except Exception as e:
        print(f"\n⚠️  Could not load Docker tools: {e}")
