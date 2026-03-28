#!/usr/bin/env python3
"""
Auto-fix script using LiteLLM proxy + Ollama.
Reads TODO.md and fixes issues via LiteLLM API (OpenAI-compatible).
"""

import os
import sys
import re
import subprocess
import argparse
from typing import List, Dict, Any
import requests

# Configuration
TODO_FILE = "TODO.md"
PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")
PROXY_API_KEY = os.getenv("LITELLM_API_KEY", "dummy-key")
DEFAULT_MODEL = os.getenv("LITELLM_MODEL", "qwen-coder")


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
            if "## Current Issues" in line or "## 📋 Current Issues" in line:
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


def fix_with_llm(issue: Dict[str, Any], dry_run: bool = False) -> bool:
    """Fix a single issue using LiteLLM proxy API."""
    file_path = issue["file"]
    description = issue["description"]
    line_num = issue["line"]
    
    print(f"\n🔧 Fixing: {file_path}:{line_num}")
    print(f"   Issue: {description}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"   ⚠️  File not found: {file_path}")
        return False
    
    # Read file content
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
    except Exception as e:
        print(f"   ❌ Cannot read file: {e}")
        return False
    
    # Build prompt
    prompt = f"""You are a code reviewer. Fix this specific issue in the code.

File: {file_path}
Line: {line_num}
Issue: {description}

Current code:
```python
{file_content}
```

Provide ONLY the fixed code for this specific issue. Do not explain changes. Return the complete fixed file content."""
    
    if dry_run:
        print(f"   [DRY RUN] Would call {PROXY_URL}/v1/chat/completions")
        return True
    
    # Call LiteLLM proxy
    try:
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {PROXY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": "You are an expert Python code reviewer. Fix issues precisely."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            fixed_code = data["choices"][0]["message"]["content"]
            
            # Extract code from markdown if present
            code_match = re.search(r'```python\n(.*?)\n```', fixed_code, re.DOTALL)
            if code_match:
                fixed_code = code_match.group(1)
            
            # Write fixed code back
            with open(file_path, 'w') as f:
                f.write(fixed_code)
            
            print(f"   ✅ Fixed successfully")
            return True
        else:
            print(f"   ❌ API error: {response.status_code} - {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to proxy at {PROXY_URL}")
        print(f"   Start proxy with: litellm --config litellm_config.yaml --port 4000")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def mark_issue_done(issue: Dict[str, Any]) -> bool:
    """Mark an issue as done in TODO.md by changing - [ ] to - [x]."""
    try:
        with open(TODO_FILE, 'r') as f:
            content = f.read()
        
        # Find the line to update
        search_line = f"- [ ] {issue['full']}"
        replace_line = f"- [x] {issue['full']}"
        
        if search_line in content:
            content = content.replace(search_line, replace_line, 1)
            with open(TODO_FILE, 'w') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"   ⚠️  Could not update TODO.md: {e}")
        return False


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
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("LiteLLM Proxy + Ollama Auto-Fix")
    print("=" * 70)
    print(f"Proxy URL: {PROXY_URL}")
    print(f"Model: {args.model}")
    print()
    
    # Check prerequisites
    if not os.path.exists(TODO_FILE):
        print("❌ TODO.md not found!")
        print("   Run: prefact -a")
        return 1
    
    # Check if proxy is running
    try:
        r = requests.get(f"{PROXY_URL}/v1/models", timeout=2)
        if r.status_code != 200:
            print("❌ LiteLLM proxy not responding")
            print(f"   Start: litellm --config litellm_config.yaml --port 4000")
            return 1
        print("✅ LiteLLM proxy running")
    except:
        print("❌ LiteLLM proxy not running")
        print(f"   Start: litellm --config litellm_config.yaml --port 4000")
        return 1
    
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
        print(f"[{i}/{len(issues)}]", end=" ")
        
        if fix_with_llm(issue, dry_run=args.dry_run):
            fixed += 1
            # Mark as done in TODO.md
            if not args.dry_run:
                if mark_issue_done(issue):
                    print(f"   ✅ Marked as done in TODO.md")
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
        print(f"🚀 Commit with: git commit -m 'Fix {fixed} issues via LiteLLM + Ollama'")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
