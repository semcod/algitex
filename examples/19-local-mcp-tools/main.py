from typing import Any

#!/usr/bin/env python3
"""Example 19: Local MCP Tools - Self-hosted MCP services"""

import os
import sys
import requests

CODE2LLM_URL = os.getenv("CODE2LLM_URL", "http://localhost:8081")
VALLM_URL = os.getenv("VALLM_URL", "http://localhost:8080")
PLANFILE_URL = os.getenv("PLANFILE_URL", "http://localhost:8201")


def check_services() -> Any:
    """Check if all MCP services are running."""
    services = {}
    
    try:
        r = requests.get(f"{CODE2LLM_URL}/health", timeout=2)
        services["code2llm"] = r.status_code == 200
    except:
        services["code2llm"] = False
    
    try:
        r = requests.get(f"{VALLM_URL}/health", timeout=2)
        services["vallm"] = r.status_code == 200
    except:
        services["vallm"] = False
    
    try:
        r = requests.get(f"{PLANFILE_URL}/health", timeout=2)
        services["planfile"] = r.status_code == 200
    except:
        services["planfile"] = False
    
    return services


def main() -> Any:
    print("=" * 60)
    print("Example 19: Local MCP Tools")
    print("=" * 60)
    print()
    print("Self-hosted MCP tools running via Docker:")
    print("  • code2llm-mcp  :8081 - Code analysis")
    print("  • vallm-mcp     :8080 - Validation")
    print("  • planfile-mcp  :8201 - Ticket management")
    print()
    
    services = check_services()
    
    print("Service status:")
    for name, status in services.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    
    if all(services.values()):
        print("\n✅ All services ready!")
        print("\nNext steps:")
        print("  1. Analyze code:")
        print(f"     curl -X POST {CODE2LLM_URL}/analyze -d '{{\"path\": \"/workspace\"}}'")
        print("  2. Validate:")
        print(f"     curl -X POST {VALLM_URL}/validate -d '{{\"path\": \"/workspace\"}}'")
        print("  3. Create ticket:")
        print(f"     curl -X POST {PLANFILE_URL}/tickets -d '{{\"title\": \"Fix\"}}'")
    else:
        print("\n⚠️  Some services not running")
        print("   Start with: make up")
    
    print("=" * 60)
    return 0 if all(services.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
