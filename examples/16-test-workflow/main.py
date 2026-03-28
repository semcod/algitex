#!/usr/bin/env python3
"""Example 16: Comprehensive Test Workflow Demo.

Demonstrates full CI/CD pipeline with multiple Docker tools:
- code2llm: Project analysis
- planfile-mcp: Ticket management
- aider-mcp: Code refactoring
- vallm: Validation
- docker-mcp: Container operations
- github-mcp: PR creation
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


def check_required_env():
    """Check required environment variables."""
    required = ["GITHUB_PAT", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"]
    missing = [r for r in required if not os.getenv(r)]
    
    if missing:
        print(f"⚠️  Missing: {', '.join(missing)}")
        print("Add them to .env file\n")
        return False
    return True


def show_workflow():
    """Display the 14-step workflow."""
    
    steps = [
        ("1", "Initialize Project Analysis", "code2llm", "code2llm /project -f toon,evolution"),
        ("2", "Create Tickets from Analysis", "planfile-mcp", "planfile_create_tickets_bulk"),
        ("3", "Get High-Priority Tickets", "planfile-mcp", "planfile_list_tickets"),
        ("4", "Refactor High-Complexity Functions", "aider-mcp", "aider_ai_code"),
        ("5", "Validate Refactored Code", "vallm", "batch"),
        ("6", "Run Unit Tests", "docker-mcp", "docker_run_container (pytest)"),
        ("7", "Check Test Coverage", "vallm", "score"),
        ("8", "Generate Documentation", "aider-mcp", "aider_ai_code (docstrings)"),
        ("9", "Build Docker Image", "docker-mcp", "docker_build_image"),
        ("10", "Run Security Scan", "docker-mcp", "docker_run_container (trivy)"),
        ("11", "Push to Registry", "docker-mcp", "docker_push_image"),
        ("12", "Create Pull Request", "github-mcp", "create_pull_request"),
        ("13", "Update Ticket Status", "planfile-mcp", "planfile_update_ticket"),
        ("14", "Generate Report", "filesystem-mcp", "write_file (report.md)"),
    ]
    
    print("\n=== Comprehensive Test Workflow ===\n")
    print("14-step automated code quality improvement pipeline:\n")
    
    for num, title, tool, action in steps:
        print(f"  {num}. {title}")
        print(f"      Tool: {tool}")
        print(f"      Action: {action}")
        print()
    
    print("\n=== Expected Results ===\n")
    print("  - Cyclomatic Complexity: 42 → 8 (81% reduction)")
    print("  - Test Coverage: 78% → 95% (+22%)")
    print("  - Code Quality Score: 0.65 → 0.92 (+42%)")
    print("  - All tests passing")
    print("  - Security scan passed")
    print("  - Pull request created")


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
        
        required_tools = ["code2llm", "planfile-mcp", "aider-mcp", "vallm", 
                         "docker-mcp", "github-mcp", "filesystem-mcp"]
        
        for tool in required_tools:
            status = "✅" if tool in tools else "⚠️"
            print(f"  {status} {tool}")
            
    except ImportError as e:
        print(f"⚠️  Docker tools not available: {e}")


def show_cli_usage():
    """Show CLI usage instructions."""
    print("\n=== Running the Workflow ===\n")
    print("1. Save workflow to file (e.g., comprehensive-test.md)")
    print("2. Execute:")
    print("     algitex workflow run comprehensive-test.md")
    print("\n3. Monitor progress:")
    print("     algitex status")


if __name__ == "__main__":
    load_env()
    
    if check_required_env():
        print("✅ All required environment variables set\n")
    else:
        print("⚠️  Running in demo mode\n")
    
    show_workflow()
    show_cli_usage()
    
    try:
        demo_with_docker_tools()
    except Exception as e:
        print(f"\n⚠️  Could not load Docker tools: {e}")
