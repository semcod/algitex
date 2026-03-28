#!/usr/bin/env python3
"""Example 24: Ollama Batch Processing - Simplified using algitex library."""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    """Simplified version using algitex Project class."""
    print("=" * 60)
    print("Example 24: Ollama Batch Processing (Simplified)")
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
    
    print(f"✅ Ollama running with {len(ollama_status['details']['models'])} models")
    print()
    
    # Show available commands
    print("Available commands:")
    print("  python batch_simplified.py --directory . --pattern '*.py'")
    print("  python batch_simplified.py --parallelism 8 --rate-limit 5")
    print()
    print("Features:")
    print("  - Parallel processing with configurable workers")
    print("  - Rate limiting to avoid overwhelming Ollama")
    print("  - Automatic retry with exponential backoff")
    print("  - Progress tracking and result saving")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
