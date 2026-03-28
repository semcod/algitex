#!/usr/bin/env python3
"""
Example 20: Self-Hosted Pipeline - Full Local CI/CD

Demonstrates a complete local pipeline using algitex service management.
"""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex.tools.services import ServiceChecker
from algitex.tools.mcp import MCPOrchestrator


def main():
    """Main demo function."""
    print("=" * 60)
    print("Example 20: Self-Hosted Pipeline - Full Local CI/CD")
    print("=" * 60)
    print()
    print("This example demonstrates a complete local pipeline using:")
    print("  • algitex.tools.services  : Service health checking")
    print("  • algitex.tools.mcp       : MCP service orchestration")
    print()
    
    # Check services
    print("Checking services...")
    checker = ServiceChecker()
    services = {
        "code2llm-mcp": {"port": 8081},
        "vallm-mcp": {"port": 8080},
        "planfile-mcp": {"port": 8201},
    }
    statuses = checker.check_all(services)
    checker.print_status(statuses, show_details=True)
    
    # If services not running, offer to start them
    unhealthy = checker.get_unhealthy(statuses)
    if unhealthy:
        print("\n⚠️  Some services are not running!")
        print("   Start them with: python -c \"from algitex.tools.mcp import MCPOrchestrator; MCPOrchestrator().start_all()\"")
        return 1
    
    print("\n✅ All services ready!")
    
    # Show how to use MCP orchestrator
    print("\n" + "=" * 60)
    print("MCP Service Management")
    print("=" * 60)
    print()
    print("To manage MCP services programmatically:")
    print("```python")
    print("from algitex.tools.mcp import MCPOrchestrator")
    print()
    print("# Start all services")
    print("orchestrator = MCPOrchestrator()")
    print("orchestrator.start_all()")
    print("orchestrator.wait_for_ready()")
    print()
    print("# Check status")
    print("orchestrator.print_status()")
    print()
    print("# Stop all services")
    print("orchestrator.stop_all()")
    print("```")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run auto-fix workflow:")
    print("     python auto_fix_todos.py")
    print()
    print("  2. Use CLI with local model:")
    print("     export DEFAULT_MODEL=ollama/qwen2.5-coder:7b")
    print("     algitex analyze --model ollama/qwen2.5-coder:7b")
    print()
    print("  3. Manage services:")
    print("     python -c \"from algitex.tools.mcp import MCPOrchestrator; MCPOrchestrator().stop_all()\"")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
