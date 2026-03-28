#!/usr/bin/env python3
"""Example 17: Docker Workflow - Refactoring Pipeline Demo.

Demonstrates a complete refactoring cycle using Docker tools:
1. code2llm: Analyze code
2. planfile-mcp: Import analysis as tickets
3. aider-mcp: Fix high-complexity functions
4. vallm: Validate changes
5. playwright-mcp: Run tests
6. github-mcp: Create PR
7. planfile-mcp: Update ticket status
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
    github = os.getenv("GITHUB_PAT")
    gemini = os.getenv("GEMINI_API_KEY")
    
    if not github or not gemini:
        print("⚠️  Missing required environment variables!")
        print("  - GITHUB_PAT (for PR creation)")
        print("  - GEMINI_API_KEY (for aider-mcp)")
        print("Add them to .env file\n")
        return False
    return True


def show_workflow():
    """Display the 7-step refactoring workflow."""
    
    steps = [
        ("1", "Analyze the code", "code2llm", "Generate .toon diagnostics"),
        ("2", "Import analysis as tickets", "planfile-mcp", "Create tickets from analysis"),
        ("3", "Fix high-complexity function", "aider-mcp", "Refactor batch() CC=42→CC≤10"),
        ("4", "Validate changes", "vallm", "Run batch validation"),
        ("5", "Run tests", "playwright-mcp", "Navigate to test results"),
        ("6", "Create PR", "github-mcp", "Create pull request"),
        ("7", "Update ticket", "planfile-mcp", "Mark ticket as done"),
    ]
    
    print("\n=== Docker Workflow: Refactoring Pipeline ===\n")
    print("7-step automated refactoring cycle:\n")
    
    for num, title, tool, desc in steps:
        print(f"  {num}. {title}")
        print(f"      Tool: {tool}")
        print(f"      Description: {desc}")
        print()
    
    print("\n=== Refactoring Example ===\n")
    print("Target: batch() function in cli.py")
    print("  - Current CC: 42 (too complex)")
    print("  - Target CC: ≤10")
    print("  - Strategy: Split into _batch_collect_files, _batch_validate_file, _batch_report")
    print("  - API: Keep backward compatible")
    print("  - Add: Type hints")


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
        
        required = ["code2llm", "planfile-mcp", "aider-mcp", "vallm", 
                   "playwright-mcp", "github-mcp"]
        
        for tool in required:
            status = "✅" if tool in tools else "⚠️"
            print(f"  {status} {tool}")
            
    except ImportError as e:
        print(f"⚠️  Docker tools not available: {e}")


def show_cli_usage():
    """Show CLI usage instructions."""
    print("\n=== Running the Workflow ===\n")
    print("1. Save workflow to file (e.g., refactor-workflow.md)")
    print("2. Execute:")
    print("     algitex workflow run refactor-workflow.md")
    print("\n3. Multi-ticket pipeline:")
    print("     algitex workflow run multi-ticket-pipeline.md")


if __name__ == "__main__":
    load_env()
    
    if check_required_env():
        print("✅ Required environment variables set\n")
    else:
        print("⚠️  Running in demo mode\n")
    
    show_workflow()
    show_cli_usage()
    
    try:
        demo_with_docker_tools()
    except Exception as e:
        print(f"\n⚠️  Could not load Docker tools: {e}")
