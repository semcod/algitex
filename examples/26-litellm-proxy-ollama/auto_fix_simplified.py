#!/usr/bin/env python3
"""
Auto-fix script: Simplified version using algitex library.
Reads TODO.md and fixes code via LiteLLM proxy (OpenAI-compatible).

Usage:
    prefact -a                    # Create TODO.md
    python auto_fix_simplified.py            # Fix all issues
    python auto_fix_simplified.py --limit 5  # Fix only first 5 issues
"""

import sys
import argparse
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    parser = argparse.ArgumentParser(
        description="Auto-fix code issues from TODO.md using LiteLLM proxy + Ollama"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Limit number of issues to fix"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without executing"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="qwen-coder",
        help="Model to use via LiteLLM proxy"
    )
    parser.add_argument(
        "--proxy-url",
        type=str,
        default="http://localhost:4000",
        help="LiteLLM proxy URL"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("LiteLLM Proxy + Ollama Auto-Fix (Simplified)")
    print("=" * 70)
    print(f"Proxy URL: {args.proxy_url}")
    print(f"Model: {args.model}")
    print()
    
    # Initialize project
    p = Project(".")
    
    # Set proxy URL
    p.autofix.proxy_url = args.proxy_url
    
    # Set dry run mode
    if args.dry_run:
        p.autofix.dry_run = True
    
    # Check if TODO.md exists
    if not Path("TODO.md").exists():
        print("❌ TODO.md not found!")
        print("   Run: prefact -a")
        return 1
    
    # Check if proxy is running
    services = p.check_services()
    if not services.get("litellm-proxy", {}).get("healthy"):
        print("❌ LiteLLM proxy not running")
        print(f"   Start: litellm --config litellm_config.yaml --port 4000")
        return 1
    
    print("✅ LiteLLM proxy running")
    
    # Fix issues
    print(f"\nFixing issues...")
    result = p.fix_issues(
        limit=args.limit,
        backend="litellm-proxy"
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
        print(f"🚀 Commit with: git commit -m 'Fix {result['fixed']} issues via LiteLLM + Ollama'")
    
    return 0 if result['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
