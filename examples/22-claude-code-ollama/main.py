#!/usr/bin/env python3
"""Example 22: Claude Code + Ollama - Simplified using algitex Project."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main() -> int:
    print("=" * 60)
    print("Example 22: Claude Code + Ollama")
    print("=" * 60)
    print()

    p = Project(".")

    # Check services
    print("Checking services...")
    p.print_service_status()

    # Check Ollama specifically
    ollama_status = p.check_ollama()
    if ollama_status["healthy"]:
        models = ollama_status["details"]["models"]
        print(f"✅ Ollama running with {len(models)} models")
        target = "qwen3-coder:latest"
        if any(target in m for m in models):
            print(f"✅ Model {target} available")

    # Generate TODO
    print("\nGenerating TODO.md...")
    result = p.generate_todo()
    print(f"✅ Created {result['filename']} with {result['count']} issues")

    print("\nNext steps:")
    print("  p.fix_with_claude('buggy_code.py', 'Add type hints')")
    print("  p.fix_issues(backend='aider')")

    return 0


if __name__ == "__main__":
    sys.exit(main())
