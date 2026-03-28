#!/usr/bin/env python3
"""Example 11: Aider MCP - Code Refactoring Demo.

Demonstrates using aider-mcp through algitex's Docker tool orchestration
to perform code refactoring operations.
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


def check_api_keys():
    """Check if required API keys are set."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not gemini_key and not anthropic_key:
        print("⚠️  No API keys found!")
        print("Set GEMINI_API_KEY or ANTHROPIC_API_KEY in .env file")
        print("Demo mode: showing example workflow only")
        return False
    return True


def demo_refactoring_examples():
    """Show example refactoring operations that aider-mcp can perform."""
    
    examples = [
        {
            "title": "1. Simple Function Refactoring",
            "description": "Split complex nested functions into smaller focused functions",
            "files": ["src/example.py"],
            "model": "gemini/gemini-2.5-pro"
        },
        {
            "title": "2. Adding Type Hints",
            "description": "Add comprehensive type hints to all functions",
            "files": ["src/calculator.py"],
            "model": "anthropic/claude-3-5-sonnet"
        },
        {
            "title": "3. Documentation Generation",
            "description": "Add Google-style docstrings to classes and methods",
            "files": ["src/api/client.py"],
            "model": "gemini/gemini-2.5-pro"
        },
        {
            "title": "4. Test Generation",
            "description": "Generate comprehensive unit tests with pytest",
            "files": ["tests/test_user_service.py"],
            "model": "anthropic/claude-3-5-sonnet"
        },
        {
            "title": "5. Performance Optimization",
            "description": "Optimize database queries and add pagination",
            "files": ["src/database/orders.py"],
            "model": "gemini/gemini-2.5-pro"
        }
    ]
    
    print("\n=== Aider MCP Code Refactoring Examples ===\n")
    
    for ex in examples:
        print(f"\n{ex['title']}")
        print(f"   Description: {ex['description']}")
        print(f"   Files: {', '.join(ex['files'])}")
        print(f"   Model: {ex['model']}")
    
    print("\n\n=== CLI Usage Examples ===\n")
    print("Spawn aider-mcp:")
    print("  algitex docker spawn aider-mcp")
    print("\nCall refactoring action:")
    print('  algitex docker call aider-mcp aider_ai_code -i \'{"prompt": "Add type hints", "relative_editable_files": ["main.py"], "model": "gemini/gemini-2.5-pro"}\'')
    print("\nTeardown when done:")
    print("  algitex docker teardown aider-mcp")


def demo_with_docker_tools():
    """Demonstrate actual Docker tool usage if available."""
    try:
        from algitex.tools.docker import DockerToolManager
        from algitex.config import Config
        
        config = Config.load()
        mgr = DockerToolManager(config)
        
        print("\n=== Docker Tools Status ===\n")
        
        # List available tools
        tools = mgr.list_tools()
        print(f"Available Docker tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool}")
        
        # Check if aider-mcp is available
        if "aider-mcp" in tools:
            print("\n✅ aider-mcp is available!")
            print("Run with: algitex docker spawn aider-mcp")
        else:
            print("\n⚠️  aider-mcp not found in docker-tools.yaml")
            
    except ImportError as e:
        print(f"⚠️  Docker tools not available: {e}")


if __name__ == "__main__":
    load_env()
    
    if check_api_keys():
        print("✅ API keys configured")
    else:
        print("⚠️  Running in demo mode\n")
    
    demo_refactoring_examples()
    
    # Try to show Docker tools status
    try:
        demo_with_docker_tools()
    except Exception as e:
        print(f"\n⚠️  Could not load Docker tools: {e}")
        print("Ensure algitex is installed: pip install -e .")
