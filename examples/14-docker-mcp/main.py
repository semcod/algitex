#!/usr/bin/env python3
"""Example 14: Docker MCP - Container Management Demo.

Demonstrates using docker-mcp through algitex's Docker tool orchestration
for managing Docker containers and images.
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


def demo_docker_operations():
    """Show example Docker operations."""
    
    examples = [
        {
            "title": "1. Listing All Containers",
            "action": "docker_list_containers",
            "input": {"all": True}
        },
        {
            "title": "2. Running a New Container",
            "action": "docker_run_container",
            "input": {
                "image": "nginx:latest",
                "name": "test-nginx",
                "ports": ["8080:80"],
                "detach": True
            }
        },
        {
            "title": "3. Building an Image",
            "action": "docker_build_image",
            "input": {
                "context_path": "/workspace",
                "dockerfile_path": "/workspace/Dockerfile",
                "tag": "my-app:latest",
                "build_args": ["VERSION=1.0.0"]
            }
        },
        {
            "title": "4. Stopping and Removing Containers",
            "action": "docker_stop_container",
            "input": {"container_id": "test-nginx", "remove": True}
        },
        {
            "title": "5. Inspecting Container Resources",
            "action": "docker_inspect",
            "input": {"target": "test-nginx", "type": "container"}
        },
        {
            "title": "6. Managing Container Networks",
            "action": "docker_create_network",
            "input": {
                "name": "algitex-network",
                "driver": "bridge",
                "subnet": "172.20.0.0/16"
            }
        },
        {
            "title": "7. Volume Management",
            "action": "docker_create_volume",
            "input": {
                "name": "algitex-data",
                "driver": "local",
                "labels": ["project=algitex"]
            }
        },
        {
            "title": "8. Container Logs",
            "action": "docker_logs",
            "input": {"container": "test-nginx", "follow": False, "tail": 100}
        }
    ]
    
    print("\n=== Docker MCP Container Management Examples ===\n")
    
    for ex in examples:
        print(f"\n{ex['title']}")
        print(f"   Action: {ex['action']}")
    
    print("\n\n=== CLI Usage Examples ===\n")
    print("Spawn docker-mcp:")
    print("  algitex docker spawn docker-mcp")
    print("\nList containers:")
    print('  algitex docker call docker-mcp docker_list_containers -i \'{"all": true}\'')
    print("\nRun container:")
    print('  algitex docker call docker-mcp docker_run_container -i \'{"image": "nginx:latest", "name": "test-nginx", "ports": ["8080:80"]}\'')
    print("\nTeardown:")
    print("  algitex docker teardown docker-mcp")


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
        
        if "docker-mcp" in tools:
            print("\n✅ docker-mcp is available!")
        else:
            print("\n⚠️  docker-mcp not found in docker-tools.yaml")
            
    except ImportError as e:
        print(f"⚠️  Docker tools not available: {e}")


if __name__ == "__main__":
    load_env()
    demo_docker_operations()
    
    try:
        demo_with_docker_tools()
    except Exception as e:
        print(f"\n⚠️  Could not load Docker tools: {e}")
