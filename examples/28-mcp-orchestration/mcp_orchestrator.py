#!/usr/bin/env python3
"""MCP Service Orchestrator - Standalone script for managing MCP services.

This is an alternative to using the algitex Project class directly.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex.tools.mcp import MCPOrchestrator


def main():
    parser = argparse.ArgumentParser(description="MCP Service Orchestrator")
    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "restart", "list"],
        help="Command to execute"
    )
    parser.add_argument(
        "--service", "-s",
        help="Specific service name (for restart)"
    )
    
    args = parser.parse_args()
    
    orchestrator = MCPOrchestrator()
    
    if args.command == "list":
        print("Available MCP services:")
        for name in orchestrator.list_services():
            info = orchestrator.get_service_info(name)
            status = "🟢" if info["running"] else "🔴"
            print(f"  {status} {name:<15} (port: {info.get('port', 'N/A')})")
    
    elif args.command == "start":
        print("Starting all MCP services...")
        orchestrator.start_all()
        orchestrator.wait_for_ready()
        print("\n✅ All services started")
    
    elif args.command == "stop":
        print("Stopping all MCP services...")
        orchestrator.stop_all()
        print("\n✅ All services stopped")
    
    elif args.command == "status":
        orchestrator.print_status()
    
    elif args.command == "restart":
        if not args.service:
            print("❌ Please specify --service for restart")
            sys.exit(1)
        orchestrator.restart_service(args.service)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
