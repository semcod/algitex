#!/usr/bin/env python3
"""Example 21: Aider CLI + Ollama - Simplified using algitex library."""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    """Simplified version using algitex Project class."""
    print("=" * 60)
    print("Example 21: Aider CLI + Ollama (Simplified)")
    print("=" * 60)
    print()
    
    # Initialize project
    p = Project(".")
    
    # Check all services
    print("Checking services...")
    p.print_service_status(show_details=True)
    
    # Check Ollama specifically
    ollama_status = p.check_ollama()
    if not ollama_status["healthy"]:
        print("\n❌ Ollama is not running!")
        print("   Start it with: ollama serve")
        return 1
    
    # List TODO tasks
    tasks = p.list_todo_tasks()
    if not tasks:
        print("\nNo TODO tasks found. Run 'prefact -a' first.")
        return 0
    
    print(f"\nFound {len(tasks)} tasks to fix:")
    for task in tasks[:5]:
        print(f"  - {task['id']}: {task['description'][:50]}...")
    if len(tasks) > 5:
        print(f"  ... and {len(tasks) - 5} more")
    
    print("\nNext steps:")
    print("  1. prefact -a              # Create TODO.md")
    print("  2. python auto_fix.py      # Fix all issues")
    print("  3. python auto_fix.py -l 3 # Fix first 3 issues")
    print()
    print("Or run full demo:")
    print("  make run")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
