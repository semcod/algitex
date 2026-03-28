#!/usr/bin/env python3
"""Example 24: Ollama Batch Processing - Simplified using algitex Project."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main() -> int:
    print("=" * 60)
    print("Example 24: Ollama Batch Processing")
    print("=" * 60)
    print()

    p = Project(".")

    # Check services
    print("Checking services...")
    p.print_service_status()

    # Check Ollama
    ollama_status = p.check_ollama()
    if not ollama_status["healthy"]:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1

    models = ollama_status["details"]["models"]
    print(f"✅ Ollama running with {len(models)} models")

    print("\nNext steps:")
    print("  p.batch_analyze()                      # Batch analyze all files")
    print("  p.batch_analyze(directory='./src')     # Analyze specific directory")
    print("  p.batch_analyze(pattern='*.py')        # Analyze Python files only")

    return 0


if __name__ == "__main__":
    sys.exit(main())
