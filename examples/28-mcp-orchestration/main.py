#!/usr/bin/env python3
"""Example 28: MCP Service Orchestration - Managing multiple MCP services."""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main() -> int:
    """Demonstrate MCP service orchestration."""
    print("=" * 60)
    print("Example 28: MCP Service Orchestration")
    print("=" * 60)
    print()
    
    # Initialize project
    p = Project(".")
    
    print("Available MCP services:")
    services = p.mcp.list_services()
    for service in services:
        info = p.mcp.get_service_info(service)
        print(f"  - {service}: {info['command']}")
    print()
    
    print("Commands:")
    print("  p.start_mcp_services()       # Start all services")
    print("  p.stop_mcp_services()        # Stop all services")
    print("  p.print_mcp_status()         # Check status")
    print("  p.restart_mcp_service('x')   # Restart service")
    print()
    print("Features:")
    print("  - Dependency-aware startup")
    print("  - Health checking")
    print("  - Graceful shutdown")
    print("  - Log collection")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
