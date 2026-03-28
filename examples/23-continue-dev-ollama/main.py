#!/usr/bin/env python3
"""Example 23: Continue.dev + Ollama - Simplified using algitex library."""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    """Simplified version using algitex Project class."""
    print("=" * 60)
    print("Example 23: Continue.dev + Ollama (Simplified)")
    print("=" * 60)
    print()

    # Initialize project
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
    if p.install_continue_config(models[:3]):  # Use first 3 models
        print("✅ Configuration installed")
    else:
        print("❌ Failed to install configuration")
        return 1

    print("\nNext steps:")
    print("1. Open VS Code")
    print("2. Install Continue.dev extension")
    print("3. Press Ctrl+L to open Continue panel")
    print("4. Select a model from the dropdown")
    print()
    print("Config location: ~/.continue/config.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
