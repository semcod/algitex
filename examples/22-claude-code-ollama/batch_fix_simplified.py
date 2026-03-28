#!/usr/bin/env python3
"""
Batch fix script: Simplified version using algitex library.
Reads TODO.md and fixes issues using Claude Code + Ollama.

Usage:
    python batch_fix_simplified.py
    python batch_fix_simplified.py --limit 5 --dry-run
"""

import sys
import argparse
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    parser = argparse.ArgumentParser(
        description="Batch fix with Claude Code + Ollama using algitex"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        help="Limit number of issues to fix"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without executing"
    )
    parser.add_argument(
        "--model", "-m",
        default="qwen2.5-coder:7b",
        help="Ollama model to use"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Claude Code + Ollama Batch Fix (Simplified)")
    print("=" * 60)
    print(f"Model: {args.model}")
    if args.dry_run:
        print("Mode: DRY RUN")
    print()
    
    # Initialize project
    p = Project(".")
    
    # Setup Claude Code
    if not p.setup_ide("claude-code"):
        print("❌ Failed to setup Claude Code")
        return 1
    
    # Get TODO tasks
    tasks = p.list_todo_tasks()
    if not tasks:
        print("No TODO tasks found. Run 'prefact -a' first.")
        return 0
    
    # Apply limit
    if args.limit:
        tasks = tasks[:args.limit]
    
    print(f"Found {len(tasks)} tasks to fix")
    print()
    
    # Fix tasks
    fixed = 0
    failed = 0
    
    for i, task in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] {task['id']}: {task['description'][:50]}...")
        
        if task.get("file_path"):
            success = p.fix_with_claude(
                task["file_path"],
                task["description"],
                model=args.model
            )
            
            if success:
                fixed += 1
                print("   ✅ Fixed")
            else:
                failed += 1
                print("   ❌ Failed")
        else:
            print("   ⚠️  No file path")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Fixed: {fixed}")
    print(f"❌ Failed: {failed}")
    
    if not args.dry_run and fixed > 0:
        print(f"\n📝 Review changes with: git diff")
        print(f"🚀 Commit with: git commit -m 'Fix {fixed} issues via Claude Code'")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
