#!/usr/bin/env python3
"""Example 22: Claude Code + Ollama - Simplified using algitex library."""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    """Simplified version using algitex Project class."""
    print("=" * 60)
    print("Example 22: Claude Code + Ollama (Simplified)")
    print("=" * 60)
    print()
    
    # Initialize project
    p = Project(".")
    
    # Check services
    print("Checking services...")
    p.print_service_status()
    
    # Check Claude Code
    ide_status = p.get_ide_status()
    claude_available = ide_status.get("claude-code", {}).get("installed", False)
    
    if claude_available:
        print("✅ Claude Code (anthropic-curl) available")
    else:
        print("❌ Claude Code not found")
        print("   Install: pip install anthropic-curl")
    
    # Check Ollama
    ollama_status = p.check_ollama()
    if ollama_status["healthy"]:
        models = ollama_status["details"]["models"]
        print(f"✅ Ollama running with {len(models)} models")
    else:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
    
    print()
    print("Usage examples:")
    print("  p.fix_with_claude('file.py', 'Add type hints')")
    print("  p.setup_ide('claude-code')")
    print()
    print("Features:")
    print("  - Seamless Claude Code + Ollama integration")
    print("  - Environment auto-configuration")
    print("  - Batch processing from TODO.md")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
