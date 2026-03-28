#!/usr/bin/env python3
"""Example 21: Aider CLI + Ollama - Simplified using algitex library."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    print("=" * 60)
    print("Example 21: Aider CLI + Ollama (Simplified)")
    print("=" * 60)
    print()

    # Initialize project
    p = Project(".")

    # Check services
    print("Checking services...")
    p.print_service_status()

    # Analyze and generate TODO
    print("\nAnalyzing code and generating TODO.md...")
    result = p.generate_todo()
    print(f"✅ Created {result['filename']} with {result['count']} issues")
    print(f"   Project grade: {result['grade']}")

    # Show available backends
    print("\nAvailable fix backends:")
    backends = p.autofix.check_backends()
    for name, available in backends.items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {name}")

    print("\nNext steps:")
    print("  p.fix_issues()                    # Fix all issues")
    print("  p.fix_issues(limit=3)             # Fix first 3 issues")
    print("  p.fix_issues(backend='ollama')    # Use specific backend")
    print()
    print("Or use CLI:")
    print("  algitex todo fix TODO.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
