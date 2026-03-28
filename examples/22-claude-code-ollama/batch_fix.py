#!/usr/bin/env python3
"""
Batch fix script for Claude Code + Ollama.
Reads TODO.md and fixes issues using anthropic-curl.
"""

import os
import sys
import subprocess
import argparse
from typing import List, Dict, Any

TODO_FILE = "TODO.md"
DEFAULT_MODEL = "ollama/qwen2.5-coder:7b"


def parse_todo_issues(limit: int = None) -> List[Dict[str, Any]]:
    """Parse TODO.md and extract issues."""
    issues = []
    in_current_section = False
    
    if not os.path.exists(TODO_FILE):
        print(f"❌ {TODO_FILE} not found. Run 'prefact -a' first.")
        return issues
    
    with open(TODO_FILE) as f:
        for line in f:
            line = line.strip()
            
            if "## Current Issues" in line or "## 📋 Current Issues" in line:
                in_current_section = True
                continue
            
            if in_current_section and line.startswith("## "):
                break
            
            if in_current_section and line.startswith("- [ ]"):
                content = line[6:].strip()
                
                if " - " in content:
                    parts = content.split(" - ", 1)
                    location = parts[0]
                    description = parts[1]
                    
                    if ":" in location:
                        file_path, line_num = location.rsplit(":", 1)
                        issues.append({
                            "file": file_path,
                            "line": int(line_num) if line_num.isdigit() else 0,
                            "description": description,
                            "full": content
                        })
    
    if limit and len(issues) > limit:
        issues = issues[:limit]
    
    return issues


def fix_with_claude_code(issue: Dict[str, Any], model: str, dry_run: bool = False) -> bool:
    """Fix a single issue using Claude Code (anthropic-curl)."""
    file_path = issue["file"]
    description = issue["description"]
    
    print(f"\n🔧 Fixing: {file_path}")
    print(f"   Issue: {description}")
    
    if not os.path.exists(file_path):
        print(f"   ⚠️  File not found")
        return False
    
    # Build prompt
    prompt = f"""Fix this issue: {description}

File: {file_path}
Make minimal, focused changes."""
    
    # Build anthropic-curl command
    cmd = [
        "anthropic-curl",
        "--model", model,
        "--message", prompt,
        "--file", file_path
    ]
    
    print(f"   Running: anthropic-curl --model {model} ...")
    
    if dry_run:
        print(f"   [DRY RUN] Would execute")
        return True
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"   ✅ Fixed")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Batch fix with Claude Code + Ollama")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of issues")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Dry run")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="Model")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Claude Code + Ollama Batch Fix")
    print("=" * 60)
    
    issues = parse_todo_issues(limit=args.limit)
    
    if not issues:
        print("No issues found.")
        return 0
    
    print(f"Found {len(issues)} issues\n")
    
    fixed = 0
    failed = 0
    
    for i, issue in enumerate(issues, 1):
        print(f"[{i}/{len(issues)}]", end=" ")
        if fix_with_claude_code(issue, args.model, args.dry_run):
            fixed += 1
        else:
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"✅ Fixed: {fixed}")
    print(f"❌ Failed: {failed}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
