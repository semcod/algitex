#!/usr/bin/env python3
"""Example 26: LiteLLM Proxy + Ollama - Simplified using algitex library."""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    """Simplified version using algitex Project class."""
    print("=" * 60)
    print("Example 26: LiteLLM Proxy + Ollama (Simplified)")
    print("=" * 60)
    print()
    
    # Initialize project
    p = Project(".")
    
    # Check all services
    print("Checking services...")
    p.print_service_status(show_details=True)
    
    # Check Ollama specifically
    ollama_status = p.check_ollama()
    if ollama_status["healthy"]:
        models = ollama_status["details"]["models"]
        print(f"\n✅ Ollama running with {len(models)} models")
        
        # Check for recommended models
        recommended = ["qwen2.5-coder:7b", "qwen2.5-coder:3b", "llama3:8b"]
        found = [m for m in models if any(r in m for r in recommended)]
        if found:
            print(f"   Recommended: {', '.join(found[:3])}")
    else:
        print("\n❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    print()
    print("=" * 60)
    print("Next steps:")
    print("=" * 60)
    print()
    print("1. Start proxy:")
    print("   make proxy")
    print()
    print("2. In another terminal, analyze code:")
    print("   prefact -a")
    print()
    print("3. Fix issues:")
    print("   python auto_fix_simplified.py --limit 5")
    print()
    print("Or run full demo:")
    print("   make run")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
