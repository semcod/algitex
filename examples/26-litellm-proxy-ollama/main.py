#!/usr/bin/env python3
"""Example 26: LiteLLM Proxy + Ollama - Simplified using algitex Project."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    print("=" * 60)
    print("Example 26: LiteLLM Proxy + Ollama")
    print("=" * 60)
    print()

    p = Project(".")

    # Check services
    print("Checking services...")
    p.print_service_status()

    # Generate TODO
    print("\nGenerating TODO.md...")
    result = p.generate_todo()
    print(f"✅ Created {result['filename']} with {result['count']} issues")

    print("\nNext steps:")
    print("  make proxy    # Start LiteLLM proxy")
    print("  p.fix_issues(backend='litellm-proxy')  # Fix via proxy")
    print("  algitex todo fix TODO.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
