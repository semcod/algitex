#!/usr/bin/env python3
"""Generate TODO.md from analysis of buggy_code.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex.tools.analysis import Analyzer
from algitex.tools.todo_local import TodoLocal


def main():
    """Generate TODO.md with issues from buggy_code.py analysis."""
    print("Generating TODO.md from analysis...")

    # Analyze the buggy code
    analyzer = Analyzer(".")
    report = analyzer.full()

    # Create TODO.md with common issues from the report
    todo = TodoLocal("TODO.md")

    # Add common code quality issues based on the analysis
    issues = []

    # Add issues based on complexity hotspots
    for hotspot in report.complexity_hotspots[:5]:
        issues.append({
            "description": f"Refactor high complexity function in {hotspot['file']}:{hotspot['function']} (CC={hotspot['complexity']})",
            "file": hotspot["file"],
            "line": hotspot.get("line", 1),
            "priority": "high" if hotspot["complexity"] > 10 else "normal"
        })

    # Add generic code quality issues
    generic_issues = [
        {"description": "Add type hints to all functions in buggy_code.py", "file": "buggy_code.py", "line": 1, "priority": "normal"},
        {"description": "Add docstrings to all public functions", "file": "buggy_code.py", "line": 1, "priority": "normal"},
        {"description": "Fix potential SQL injection in fetch_user_data", "file": "buggy_code.py", "line": 15, "priority": "high"},
        {"description": "Fix hardcoded credentials in authenticate_user", "file": "buggy_code.py", "line": 45, "priority": "critical"},
        {"description": "Fix path traversal vulnerability in cleanup_old_files", "file": "buggy_code.py", "line": 65, "priority": "high"},
    ]

    for issue in generic_issues:
        if not any(i["file"] == issue["file"] and i["line"] == issue["line"] for i in issues):
            issues.append(issue)

    # Save to TODO.md
    todo.save_tasks(issues)

    print(f"✅ Created TODO.md with {len(issues)} issues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
