#!/usr/bin/env python3
"""Example 12: Filesystem MCP - File Operations Demo.

Demonstrates using filesystem-mcp through algitex's Docker tool orchestration
for file system operations.
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


def demo_filesystem_operations():
    """Show example filesystem operations."""
    
    examples = [
        {
            "title": "1. Reading File Contents",
            "action": "read_file",
            "input": {"path": "/workspace/README.md"}
        },
        {
            "title": "2. Listing Directory Contents",
            "action": "list_directory",
            "input": {"path": "/workspace/src", "recursive": False}
        },
        {
            "title": "3. Searching for Files",
            "action": "search_files",
            "input": {
                "pattern": "*.py",
                "path": "/workspace",
                "exclude_patterns": ["__pycache__", "*.pyc"]
            }
        },
        {
            "title": "4. Writing a New File",
            "action": "write_file",
            "input": {
                "path": "/workspace/docs/api_reference.md",
                "content": "# API Reference\n\n## Endpoints\n..."
            }
        },
        {
            "title": "5. Batch File Processing",
            "action": "search_files",
            "input": {"pattern": "*.md", "path": "/workspace/docs"}
        }
    ]
    
    print("\n=== Filesystem MCP Operations Examples ===\n")
    
    for ex in examples:
        print(f"\n{ex['title']}")
        print(f"   Action: {ex['action']}")
        print(f"   Input: {ex['input']}")
    
    print("\n\n=== CLI Usage Examples ===\n")
    print("Spawn filesystem-mcp:")
    print("  algitex docker spawn filesystem-mcp")
    print("\nList files:")
    print('  algitex docker call filesystem-mcp list_directory -i \'{"path": "/workspace"}\'')
    print("\nRead file:")
    print('  algitex docker call filesystem-mcp read_file -i \'{"path": "/workspace/README.md"}\'')
    print("\nTeardown:")
    print("  algitex docker teardown filesystem-mcp")


def demo_with_docker_tools():
    """Demonstrate Docker tool usage if available."""
    try:
        from algitex.tools.docker import DockerToolManager
        from algitex.config import Config
        
        config = Config.load()
        mgr = DockerToolManager(config)
        
        print("\n=== Docker Tools Status ===\n")
        
        tools = mgr.list_tools()
        print(f"Available Docker tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool}")
        
        if "filesystem-mcp" in tools:
            print("\n✅ filesystem-mcp is available!")
        else:
            print("\n⚠️  filesystem-mcp not found in docker-tools.yaml")
            
    except ImportError as e:
        print(f"⚠️  Docker tools not available: {e}")


if __name__ == "__main__":
    load_env()
    demo_filesystem_operations()
    
    try:
        demo_with_docker_tools()
    except Exception as e:
        print(f"\n⚠️  Could not load Docker tools: {e}")
