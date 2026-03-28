#!/usr/bin/env python3
"""
Claude Code + Ollama integration example.
Demonstrates using anthropic-curl with local Ollama backend.
"""

import os
import sys
import subprocess


def check_claude_code():
    """Check if Claude Code (anthropic-curl) is installed."""
    try:
        result = subprocess.run(
            ["which", "anthropic-curl"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except:
        return False


def list_ollama_models():
    """List available Ollama models."""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            models = r.json().get('models', [])
            return [m['name'] for m in models]
    except:
        pass
    return []


def demo_claude_code_fix(file_path: str, instruction: str, model: str = "ollama/qwen2.5-coder:7b"):
    """Demo: Fix file using Claude Code with Ollama."""
    print(f"\n🤖 Claude Code + Ollama Demo")
    print(f"   File: {file_path}")
    print(f"   Model: {model}")
    print(f"   Instruction: {instruction}")
    print()
    
    # Build command
    cmd = [
        "anthropic-curl",
        "--model", model,
        "--message", instruction,
        "--file", file_path
    ]
    
    print(f"   Command: {' '.join(cmd)}")
    print()
    
    # Check if we can run it
    if not check_claude_code():
        print("   ⚠️  anthropic-curl not installed")
        print("      Install: pip install anthropic-curl")
        return False
    
    if not check_ollama():
        print("   ⚠️  Ollama not running")
        print("      Start: ollama serve")
        return False
    
    print("   ✅ Ready to execute (dry-run mode)")
    return True


def demo_batch_fix(todo_file: str = "TODO.md"):
    """Demo: Batch fix all issues from TODO.md."""
    print(f"\n📋 Batch Processing Demo")
    print(f"   Reading issues from: {todo_file}")
    
    if not os.path.exists(todo_file):
        print(f"   ⚠️  {todo_file} not found")
        print("      Run: prefact -a")
        return False
    
    # Parse TODO.md (simplified)
    issues = []
    with open(todo_file) as f:
        for line in f:
            if line.strip().startswith("- [ ]"):
                issues.append(line.strip())
    
    print(f"   Found {len(issues)} issues")
    
    for i, issue in enumerate(issues[:3], 1):  # Show first 3
        print(f"   [{i}] {issue[:60]}...")
    
    print()
    print("   To fix all:")
    print("   python batch_fix.py")
    
    return True


def main():
    print("=" * 60)
    print("Example 22: Claude Code + Ollama")
    print("=" * 60)
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    
    claude_ok = check_claude_code()
    ollama_ok = check_ollama()
    
    if claude_ok:
        print("✅ anthropic-curl installed")
    else:
        print("❌ anthropic-curl not found")
        print("   Install: pip install anthropic-curl")
    
    if ollama_ok:
        models = list_ollama_models()
        print(f"✅ Ollama running ({len(models)} models)")
        
        # Check for qwen2.5-coder:7b
        target = "qwen2.5-coder:7b"
        if any(target in m for m in models):
            print(f"✅ Model {target} available")
        else:
            print(f"⚠️  Model {target} not found")
            print(f"   Pull: ollama pull {target}")
    else:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
    
    print()
    
    if not claude_ok or not ollama_ok:
        print("❌ Prerequisites not satisfied")
        return 1
    
    # Run demos
    print("Running demos...")
    print()
    
    # Demo 1: Simple fix
    demo_claude_code_fix(
        "buggy_code.py",
        "Add type hints and docstrings to all functions",
        "ollama/qwen2.5-coder:7b"
    )
    
    # Demo 2: Batch processing
    demo_batch_fix("TODO.md")
    
    print()
    print("=" * 60)
    print("Next steps:")
    print("  1. prefact -a                                    # Create TODO.md")
    print("  2. anthropic-curl --model ollama/qwen2.5-coder:7b # Interactive")
    print("  3. python batch_fix.py                           # Batch fix")
    print()
    print("Environment:")
    print("  export ANTHROPIC_BASE_URL=http://localhost:11434/v1")
    print("  export ANTHROPIC_API_KEY=ollama")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
