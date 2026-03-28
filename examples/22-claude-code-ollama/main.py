#!/usr/bin/env python3
"""
Example 22: Claude Code + Ollama integration.
Demonstrates using algitex's ClaudeCodeHelper with local Ollama backend.
"""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex.tools.claude import ClaudeCodeHelper


def main():
    print("=" * 60)
    print("Example 22: Claude Code + Ollama")
    print("=" * 60)
    print()
    
    # Initialize helper
    helper = ClaudeCodeHelper()
    
    # Check prerequisites
    print("Checking prerequisites...")
    
    if not helper.is_available():
        print("❌ claude CLI not found")
        print("   Install: npm install -g @anthropic-ai/claude-code")
        return 1
    
    print(f"✅ Claude Code CLI available (version: {helper.get_version()})")
    
    # Check Ollama
    if not helper.check_ollama():
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    models = helper.list_ollama_models()
    print(f"✅ Ollama running ({len(models)} models)")
    
    # Check for coding model
    target = "qwen2.5-coder:7b"
    if any(target in m for m in models):
        print(f"✅ Model {target} available")
    else:
        print(f"⚠️  Model {target} not found")
        print(f"   Pull: ollama pull {target}")
    
    print()
    
    # Demo 1: Fix a file
    print("Demo 1: Fix file using Claude Code + Ollama")
    print("-" * 50)
    
    result = helper.fix_with_ollama(
        "buggy_code.py",
        "Add type hints and docstrings to all functions",
        model=target
    )
    
    if result.success:
        print(f"✅ Fixed successfully")
        print(f"   Output: {result.output[:200]}...")
    else:
        print(f"❌ Failed: {result.error}")
    
    # Demo 2: Show batch processing
    print("\nDemo 2: Batch Processing")
    print("-" * 50)
    
    print("To fix multiple issues from TODO.md:")
    print("```python")
    print("# Parse issues and fix them")
    print("issues = helper.parse_todo_issues()")
    print("results = helper.batch_fix(issues, model=target)")
    print("```")
    
    # Demo 3: Configuration
    print("\nDemo 3: Configuration")
    print("-" * 50)
    
    print("To install Claude Code config for Ollama models:")
    print("```python")
    print("helper.install_config(models[:3])")
    print("```")
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("  1. python -c \"from algitex import Project; p = Project('.'); p.plan()\"")
    print("  2. Use algitex Project class:")
    print("     from algitex import Project")
    print("     p = Project('.')")
    print(f"     p.fix_with_claude('buggy_code.py', 'Fix type hints', '{target}')")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
