#!/usr/bin/env python3
"""
Auto-fix TODO issues workflow for Algitex
Uses local MCP tools to analyze, validate and fix code issues
"""

import os
import sys
import subprocess
import json
from typing import List, Dict, Any

# Configuration
CODE2LLM_URL = os.getenv("CODE2LLM_URL", "http://localhost:8081")
VALLM_URL = os.getenv("VALLM_URL", "http://localhost:8080")
PLANFILE_URL = os.getenv("PLANFILE_URL", "http://localhost:8201")
TODO_FILE = os.getenv("TODO_FILE", "../../TODO.md")

def get_last_todo_issues(count: int = 10) -> List[Dict[str, Any]]:
    """Parse TODO.md and get last N issues from Current Issues section."""
    issues = []
    in_current_section = False
    
    if not os.path.exists(TODO_FILE):
        print(f"❌ {TODO_FILE} not found")
        return issues
    
    with open(TODO_FILE) as f:
        for line in f:
            line = line.strip()
            if "## 📋 Current Issues" in line:
                in_current_section = True
                continue
            if in_current_section and line.startswith("## "):
                break
            if in_current_section and line.startswith("- [ ]"):
                # Parse: - [ ] file:line - description
                parts = line[6:].split(" - ", 1)  # Remove "- [ ] "
                if len(parts) == 2:
                    location = parts[0]
                    description = parts[1]
                    if ":" in location:
                        file_path, line_num = location.rsplit(":", 1)
                        issues.append({
                            "file": file_path,
                            "line": int(line_num) if line_num.isdigit() else 0,
                            "description": description,
                            "full": line
                        })
    
    # Return last N issues (most recently added)
    return issues[-count:] if len(issues) > count else issues


def analyze_file(file_path: str) -> Dict[str, Any]:
    """Analyze file using code2llm MCP."""
    try:
        import requests
        abs_path = os.path.abspath(file_path)
        response = requests.post(
            f"{CODE2LLM_URL}/analyze",
            json={"path": os.path.dirname(abs_path)},
            timeout=30
        )
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"⚠️  code2llm analysis failed: {e}")
        return {}


def validate_file(file_path: str) -> Dict[str, Any]:
    """Validate file using vallm MCP."""
    try:
        import requests
        abs_path = os.path.abspath(file_path)
        response = requests.post(
            f"{VALLM_URL}/validate",
            json={"path": os.path.dirname(abs_path)},
            timeout=30
        )
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"⚠️  vallm validation failed: {e}")
        return {}


def fix_unused_import(file_path: str, line_num: int, import_name: str) -> bool:
    """Fix unused import by removing it."""
    try:
        with open(file_path) as f:
            lines = f.readlines()
        
        # Find and remove the import line
        for i, line in enumerate(lines):
            if i + 1 == line_num and import_name in line and line.strip().startswith("import"):
                lines.pop(i)
                break
        
        with open(file_path, "w") as f:
            f.writelines(lines)
        
        print(f"✅ Removed unused import '{import_name}' from {file_path}:{line_num}")
        return True
    except Exception as e:
        print(f"❌ Failed to fix unused import: {e}")
        return False


def fix_f_string(file_path: str, line_num: int) -> bool:
    """Fix string concatenation to f-string."""
    try:
        with open(file_path) as f:
            lines = f.readlines()
        
        # Simple heuristic: replace " + " with f"..."
        line = lines[line_num - 1]
        # This is a simplified fix - real implementation would need AST parsing
        print(f"ℹ️  Manual review needed for f-string conversion at {file_path}:{line_num}")
        print(f"   Line: {line.strip()}")
        return False
    except Exception as e:
        print(f"❌ Failed to fix f-string: {e}")
        return False


def create_ticket_for_issue(issue: Dict[str, Any]) -> bool:
    """Create ticket in planfile-mcp for manual review."""
    try:
        import requests
        response = requests.post(
            f"{PLANFILE_URL}/tickets",
            json={
                "title": f"Fix: {issue['description'][:50]}",
                "description": f"File: {issue['file']}:{issue['line']}\nIssue: {issue['description']}\n\nFull: {issue['full']}",
                "priority": "normal",
                "tags": ["auto-fix", "todo"]
            },
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Created ticket for {issue['file']}:{issue['line']}")
            return True
    except Exception as e:
        print(f"⚠️  Failed to create ticket: {e}")
    return False


def main():
    """Main workflow."""
    print("=" * 60)
    print("Algitex Auto-Fix TODO Issues Workflow")
    print("=" * 60)
    
    # Get last 10 issues
    issues = get_last_todo_issues(10)
    print(f"\n📋 Found {len(issues)} issues to process\n")
    
    if not issues:
        print("No issues found. Exiting.")
        return
    
    fixed = 0
    tickets = 0
    failed = 0
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue['file']}:{issue['line']}")
        print(f"   {issue['description']}")
        
        file_path = os.path.join("../..", issue['file'])
        if not os.path.exists(file_path):
            print(f"   ⚠️  File not found: {file_path}")
            failed += 1
            continue
        
        # Analyze with code2llm
        analysis = analyze_file(file_path)
        if analysis:
            print(f"   📊 Complexity: {analysis.get('average_cc', 'N/A')}")
        
        # Validate with vallm
        validation = validate_file(file_path)
        if validation:
            print(f"   ✅ Validation: {validation.get('static_passed', False)}")
        
        # Auto-fix based on issue type
        desc = issue['description'].lower()
        success = False
        
        if 'unused import' in desc:
            import_name = issue['description'].split("'")[1] if "'" in issue['description'] else ""
            success = fix_unused_import(file_path, issue['line'], import_name)
        elif 'string concatenation' in desc:
            success = fix_f_string(file_path, issue['line'])
        else:
            # Create ticket for manual review
            success = create_ticket_for_issue(issue)
            if success:
                tickets += 1
        
        if success and 'unused import' in desc:
            fixed += 1
        elif not success and 'unused import' not in desc:
            # Already counted in tickets
            pass
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Fixed: {fixed}")
    print(f"🎫 Tickets created: {tickets}")
    print(f"❌ Failed: {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
