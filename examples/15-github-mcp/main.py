from typing import Any

#!/usr/bin/env python3
"""Example 15: GitHub MCP - Real Repository Workflow.

Creates sample project and demonstrates GitHub workflow.
"""

import os
from pathlib import Path


def create_sample_project() -> Any:
    """Create sample project for GitHub workflow."""
    base_dir = Path(__file__).parent / "sample_github_project"
    base_dir.mkdir(exist_ok=True)
    
    # Create sample code
    (base_dir / "main.py").write_text('''#!/usr/bin/env python3
"""Sample application."""

def calculate(x, y):
    """Calculate sum."""
    return x + y

if __name__ == "__main__":
    print(calculate(1, 2))
''')
    
    # Create README
    (base_dir / "README.md").write_text('''# Sample Project

A sample project for GitHub MCP demonstration.

## Features
- Simple calculator
- Clean code

## TODO
- Add more operations
- Add tests
''')
    
    # Create TODO file
    (base_dir / "TODO.md").write_text('''# GitHub Workflow TODO

- [ ] Initialize git repository
- [ ] Create initial commit
- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Create issue for adding tests
- [ ] Create PR with improvements
''')
    
    # Create .gitignore
    (base_dir / ".gitignore").write_text('''__pycache__/
*.pyc
*.pyo
.env
.venv/
''')
    
    return base_dir


def demo_github_workflow() -> None:
    """Demonstrate GitHub workflow."""
    print("=== GitHub MCP - Real Repository Workflow ===\n")
    
    # Create sample project
    project_dir = create_sample_project()
    print(f"1. Created sample project: {project_dir}")
    
    # Show files
    print(f"\n2. Project files:")
    for f in project_dir.iterdir():
        print(f"   - {f.name}")
    
    # Show code
    main_file = project_dir / "main.py"
    print(f"\n3. Sample code ({main_file}):")
    print("-" * 40)
    print(main_file.read_text())
    print("-" * 40)
    
    # Show README
    readme = project_dir / "README.md"
    print(f"\n4. README:")
    print(readme.read_text())
    
    # Show TODO
    todo_file = project_dir / "TODO.md"
    print(f"\n5. TODO list:")
    print(todo_file.read_text())
    
    # Check GitHub token
    has_token = os.getenv("GITHUB_PAT")
    
    if has_token:
        print("\n6. ✅ GITHUB_PAT configured")
        print("   Can perform real GitHub operations")
    else:
        print("\n6. ⚠️  No GITHUB_PAT - showing workflow:")
        print("""
   Commands to run after 'git init' and 'git add .':
   
   algitex docker spawn github-mcp
   
   # Create issue
   algitex docker call github-mcp create_issue -i '{
     "owner": "myusername",
     "repo": "sample-project",
     "title": "Add unit tests",
     "body": "Need pytest tests for calculate function"
   }'
   
   # Create PR
   algitex docker call github-mcp create_pull_request -i '{
     "owner": "myusername",
     "repo": "sample-project",
     "title": "feat: Add subtract function",
     "head": "feature/subtract",
     "base": "main"
   }'
   
   algitex docker teardown github-mcp
        """)
    
    print(f"\n7. Files created:")
    print(f"   - {project_dir}/main.py")
    print(f"   - {project_dir}/README.md")
    print(f"   - {project_dir}/TODO.md")
    print(f"   - {project_dir}/.gitignore")
    print(f"\n   Project ready for GitHub workflow.")
    print(f"   Initialize with: cd {project_dir} && git init")
    print(f"   Clean up: rm -rf {project_dir}")


if __name__ == "__main__":
    demo_github_workflow()
