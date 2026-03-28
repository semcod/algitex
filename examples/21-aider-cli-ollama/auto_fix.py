#!/usr/bin/env python3
"""
Auto-fix script: Reads TODO.md created by prefact -a and fixes code using aider CLI with Ollama.

This demonstrates the complete workflow:
1. prefact -a → creates TODO.md with issues
2. This script → parses TODO.md and runs aider --model ollama/... for each issue
3. Aider with local LLM → fixes the code

Usage:
    prefact -a                    # Create TODO.md
    python auto_fix.py            # Fix all issues with aider + ollama
    python auto_fix.py --limit 5  # Fix only first 5 issues
"""

import os
import sys
import subprocess
import argparse
from typing import List, Dict, Any

TODO_FILE = "TODO.md"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ollama/qwen2.5-coder:7b")

def parse_todo_issues(limit: int = None) -> List[Dict[str, Any]]:
    """Parse TODO.md and extract issues from Current Issues section."""
    issues = []
    in_current_section = False
    
    if not os.path.exists(TODO_FILE):
        print(f"❌ {TODO_FILE} not found. Run 'prefact -a' first.")
        return issues
    
    with open(TODO_FILE) as f:
        for line in f:
            line = line.strip()
            
            # Start of Current Issues section
            if "## 📋 Current Issues" in line or "## Current Issues" in line:
                in_current_section = True
                continue
            
            # End of section (next ## header)
            if in_current_section and line.startswith("## "):
                break
            
            # Parse issue line: - [ ] file:line - description
            if in_current_section and line.startswith("- [ ]"):
                # Remove "- [ ] " prefix
                content = line[6:].strip()
                
                # Parse location and description
                if " - " in content:
                    parts = content.split(" - ", 1)
                    location = parts[0]
                    description = parts[1]
                    
                    # Parse file:line
                    if ":" in location:
                        file_path, line_num = location.rsplit(":", 1)
                        issues.append({
                            "file": file_path,
                            "line": int(line_num) if line_num.isdigit() else 0,
                            "description": description,
                            "full": content
                        })
    
    # Apply limit
    if limit and len(issues) > limit:
        issues = issues[:limit]
    
    return issues

def fix_with_aider(issue: Dict[str, Any], dry_run: bool = False) -> bool:
    """Fix a single issue using aider CLI with Ollama."""
    file_path = issue["file"]
    description = issue["description"]
    line_num = issue["line"]
    
    print(f"\n🔧 Fixing: {file_path}:{line_num}")
    print(f"   Issue: {description}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"   ⚠️  File not found: {file_path}")
        return False
    
    # Build aider prompt
    prompt = f"""Fix this issue in {file_path} at line {line_num}:
{description}

Make minimal changes to fix only this specific issue. Keep the code style consistent."""
    
    # Build aider command
    cmd = [
        "aider",
        "--model", OLLAMA_MODEL,
        "--no-git",
        "--yes",
        "--no-check-version",  # Skip version check
        "--message", prompt,
        file_path
    ]
    
    print(f"   Running: aider --model {OLLAMA_MODEL} ...")
    print(f"   (Note: Aider warnings about 'Unknown model' are expected with Ollama)")
    
    if dry_run:
        print(f"   [DRY RUN] Would execute: {' '.join(cmd)}")
        return True
    
    # Run aider
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Filter stderr to show only important errors, not model warnings
        stderr_lines = result.stderr.split('\n') if result.stderr else []
        important_errors = [
            line for line in stderr_lines
            if line.strip()
            and 'unknown context window' not in line.lower()
            and 'token costs' not in line.lower()
            and 'did you mean' not in line.lower()
            and 'missing.*environment variables' not in line.lower()
            and 'unable to verify' not in line.lower()
            and 'model warnings' not in line.lower()
        ]
        
        if result.returncode == 0:
            print(f"   ✅ Fixed successfully")
            if important_errors:
                print(f"   Notes: {'; '.join(important_errors[:2])}")
            return True
        else:
            error_msg = '; '.join(important_errors[:2]) if important_errors else "Aider failed"
            print(f"   ❌ {error_msg}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout (5min) - aider took too long")
        return False
    except FileNotFoundError:
        print(f"   ❌ 'aider' not found. Install with: pip install aider-chat")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Auto-fix code issues from TODO.md using aider + Ollama"
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
        default=OLLAMA_MODEL,
        help=f"Ollama model to use (default: {OLLAMA_MODEL})"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Aider + Ollama Auto-Fix")
    print("=" * 70)
    print(f"Model: {args.model}")
    print(f"TODO file: {TODO_FILE}")
    print()
    
    # Check prerequisites
    if not os.path.exists(TODO_FILE):
        print("❌ TODO.md not found!")
        print("   Run: prefact -a")
        return 1
    
    # Check if ollama is running
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code != 200:
            print("⚠️  Ollama not responding. Start it with: ollama serve")
    except:
        print("⚠️  Ollama not running. Start it with: ollama serve")
    
    # Parse issues
    print("📋 Parsing TODO.md...")
    issues = parse_todo_issues(limit=args.limit)
    
    if not issues:
        print("No issues found to fix.")
        return 0
    
    print(f"Found {len(issues)} issues to fix\n")
    
    # Fix issues
    fixed = 0
    failed = 0
    
    for i, issue in enumerate(issues, 1):
        print(f"[{i}/{len(issues)}] ", end="")
        
        if fix_with_aider(issue, dry_run=args.dry_run):
            fixed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total issues: {len(issues)}")
    print(f"✅ Fixed: {fixed}")
    print(f"❌ Failed: {failed}")
    
    if not args.dry_run and fixed > 0:
        print(f"\n📝 Review changes with: git diff")
        print(f"🚀 Commit with: git commit -m 'Fix {fixed} issues via aider + ollama'")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
