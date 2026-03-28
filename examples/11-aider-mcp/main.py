from typing import Any

#!/usr/bin/env python3
"""Example 11: Aider MCP - Real Code Refactoring.

Creates sample code with issues and attempts to fix them using aider-mcp.
"""

import os
from pathlib import Path


def create_sample_project() -> Any:
    """Create sample project with code to refactor."""
    base_dir = Path(__file__).parent / "sample_project"
    base_dir.mkdir(exist_ok=True)
    
    # Create buggy code
    (base_dir / "calculator.py").write_text('''
def calc(a,b,op):
    if op=="+":
        return a+b
    elif op=="-":
        return a-b
    elif op=="*":
        return a*b
    elif op=="/":
        if b==0:
            return None
        return a/b
    else:
        return None
''')
    
    # Create TODO
    (base_dir / "TODO.md").write_text('''# TODO

- [ ] Add type hints to calculator.py
- [ ] Add docstrings
- [ ] Handle division by zero with exception
- [ ] Add input validation
''')
    
    return base_dir


def demo_refactoring() -> None:
    """Demonstrate real refactoring workflow."""
    print("=== Aider MCP - Real Refactoring Demo ===\n")
    
    # Create sample
    project_dir = create_sample_project()
    print(f"1. Created sample project: {project_dir}")
    
    # Show before
    calc_file = project_dir / "calculator.py"
    print(f"\n2. Original code ({calc_file}):")
    print("-" * 40)
    print(calc_file.read_text())
    print("-" * 40)
    
    # Show TODO
    todo_file = project_dir / "TODO.md"
    print(f"\n3. TODO list:")
    print(todo_file.read_text())
    
    # Check if can run real aider
    has_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    
    if has_api_key:
        print("\n4. Running aider-mcp to fix code...")
        print("   (Would call: algitex docker call aider-mcp ...)")
        # Here would be actual call
    else:
        print("\n4. ⚠️  No API keys - showing what would be done:")
        print("""
   Commands that would run:
   
   algitex docker spawn aider-mcp
   
   algitex docker call aider-mcp aider_ai_code -i '{
     "prompt": "Add type hints, docstrings, and proper error handling",
     "relative_editable_files": ["calculator.py"],
     "model": "gemini/gemini-2.5-pro"
   }'
   
   algitex docker teardown aider-mcp
   
   Expected changes:
   - Add type hints: def calc(a: float, b: float, op: str) -> float:
   - Add docstring explaining the function
   - Raise ValueError instead of returning None
   - Add input validation
        """)
    
    print(f"\n5. Files created:")
    print(f"   - {project_dir}/calculator.py (code to refactor)")
    print(f"   - {project_dir}/TODO.md (tasks)")
    print(f"\n   Project kept for manual experimentation.")
    print(f"   To clean up: rm -rf {project_dir}")


if __name__ == "__main__":
    demo_refactoring()
