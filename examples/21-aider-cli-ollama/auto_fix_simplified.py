#!/usr/bin/env python3
"""
Auto-fix script: Simplified version using algitex library.
Reads TODO.md and fixes code using available backends (Aider, Ollama, LiteLLM proxy).

Usage:
    prefact -a                    # Create TODO.md
    python auto_fix_simplified.py            # Fix all issues
    python auto_fix_simplified.py --limit 5  # Fix only first 5 issues
    python auto_fix_simplified.py --backend ollama  # Use specific backend
"""

import sys
import argparse
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    parser = argparse.ArgumentParser(
        description="Auto-fix code issues from TODO.md using algitex"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Limit number of issues to fix"
    )
    parser.add_argument(
        "--backend", "-b",
        type=str,
        default="auto",
        choices=["auto", "ollama", "aider", "litellm-proxy"],
        help="Backend to use for fixing"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without executing"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Fix issues only in this file"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Algitex Auto-Fix (Simplified)")
    print("=" * 70)
    print(f"Backend: {args.backend}")
    print()
    
    # Initialize project
    p = Project(".")
    
    # Set dry run mode
    if args.dry_run:
        p.autofix.dry_run = True
    
    # Check services
    print("Checking available backends...")
    backends = p.autofix.check_backends()
    for name, available in backends.items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {name}")
    
    # Check if TODO.md exists
    if not Path("TODO.md").exists():
        print("\n❌ TODO.md not found!")
        print("   Run: prefact -a")
        return 1
    
    # Fix issues
    print(f"\nFixing issues...")
    result = p.fix_issues(
        limit=args.limit,
        backend=args.backend,
        filter_file=args.file
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total issues: {result['total']}")
    print(f"✅ Fixed: {result['fixed']}")
    print(f"❌ Failed: {result['failed']}")
    
    if not args.dry_run and result['fixed'] > 0:
        print(f"\n📝 Review changes with: git diff")
        print(f"🚀 Commit with: git commit -m 'Fix {result['fixed']} issues via algitex'")
    
    return 0 if result['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
