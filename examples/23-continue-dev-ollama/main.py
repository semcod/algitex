#!/usr/bin/env python3
"""Example 23: Continue.dev + Ollama - Simplified using algitex Project."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    print("=" * 60)
    print("Example 23: Continue.dev + Ollama")
    print("=" * 60)
    print()

    p = Project(".")

    # Check Ollama
    ollama_status = p.check_ollama()
    if not ollama_status["healthy"]:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1

    models = ollama_status["details"]["models"]
    print(f"✅ Ollama running with {len(models)} models")

    # Install Continue.dev config
    print("\nInstalling Continue.dev configuration...")
    if p.install_continue_config(models[:3]):
        print("✅ Configuration installed")
        print("   Config location: ~/.continue/config.json")
    else:
        print("❌ Failed to install configuration")

    # Generate TODO
    print("\nGenerating TODO.md...")
    result = p.generate_todo()
    print(f"✅ Created {result['filename']} with {result['count']} issues")

    print("\nNext steps:")
    print("  1. Open VS Code")
    print("  2. Install Continue.dev extension")
    print("  3. Press Ctrl+L to open Continue panel")
    print("  4. Select a model from the dropdown")

    return 0


if __name__ == "__main__":
    sys.exit(main())
