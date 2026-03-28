#!/usr/bin/env python3
"""Example 21: Aider CLI + Ollama - Local Code Refactoring"""

import os
import sys
from typing import Any


def check_prerequisites() -> int:
    """Check if all required tools are installed."""
    print("=" * 60)
    print("Example 21: Aider CLI + Ollama")
    print("=" * 60)
    print()
    
    issues = []
    
    # Check algitex
    try:
        import algitex
        print("✅ algitex installed")
    except ImportError:
        print("❌ algitex not found")
        print("   Install: pip install -e ../../")
        issues.append("algitex")
    
    # Check aider
    import subprocess
    result = subprocess.run(["which", "aider"], capture_output=True)
    if result.returncode == 0:
        print("✅ aider installed")
    else:
        print("❌ aider not found")
        print("   Install: pip install aider-chat")
        issues.append("aider")
    
    # Check Ollama
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            print(f"✅ Ollama running ({len(models)} models)")
            
            # Check for qwen2.5-coder:7b
            target = "qwen2.5-coder:7b"
            if any(target in m for m in models):
                print(f"✅ Model {target} available")
            else:
                print(f"⚠️  Model {target} not found")
                print(f"   Pull: ollama pull {target}")
        else:
            print("❌ Ollama not responding")
            issues.append("ollama")
    except Exception as e:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        issues.append("ollama")
    
    # Check TODO.md
    if os.path.exists("TODO.md"):
        with open("TODO.md") as f:
            content = f.read()
            # Count issues
            current_issues = content.count("- [ ]")
            completed = content.count("- [x]")
            print(f"✅ TODO.md found ({current_issues} open, {completed} completed)")
    else:
        print("⚠️  TODO.md not found")
        print("   Create: python generate_todo.py")
    
    print()
    
    if issues:
        print("❌ Missing prerequisites:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        print("Run: make setup")
        return 1
    
    print("✅ All prerequisites satisfied!")
    print()
    print("Next steps:")
    print("  1. python generate_todo.py   # Create TODO.md")
    print("  2. python auto_fix.py        # Fix all issues")
    print("  3. python auto_fix.py -l 3   # Fix first 3 issues")
    print()
    print("Or run full demo:")
    print("  make run")
    
    return 0


def main() -> Any:
    return check_prerequisites()


if __name__ == "__main__":
    sys.exit(main())
