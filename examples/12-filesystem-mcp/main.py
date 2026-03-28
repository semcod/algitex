#!/usr/bin/env python3
"""Example 12: Filesystem MCP - Real File Operations.

Creates sample files and demonstrates real filesystem operations.
"""

import os
from pathlib import Path


def create_sample_files():
    """Create sample files for demonstration."""
    base_dir = Path(__file__).parent / "sample_files"
    base_dir.mkdir(exist_ok=True)
    
    # Create sample code file
    (base_dir / "README.md").write_text("""# Sample Project

This is a sample project for filesystem-mcp demo.

## Structure
- src/: source code
- docs/: documentation
- tests/: test files
""")
    
    src_dir = base_dir / "src"
    src_dir.mkdir(exist_ok=True)
    (src_dir / "main.py").write_text("""#!/usr/bin/env python3
def main():
    print("Hello from sample project!")

if __name__ == "__main__":
    main()
""")
    
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "guide.md").write_text("""# User Guide

This is the user guide.
""")
    
    return base_dir


def demo_file_operations():
    """Demonstrate real filesystem operations."""
    print("=== Filesystem MCP - Real File Operations ===\n")
    
    # Create sample files
    files_dir = create_sample_files()
    print(f"1. Created sample files in: {files_dir}")
    
    # Show directory structure
    print(f"\n2. Directory structure:")
    for f in files_dir.rglob("*"):
        rel = f.relative_to(files_dir)
        indent = "  " * len(rel.parts)
        if f.is_dir():
            print(f"{indent}📁 {rel}/")
        else:
            print(f"{indent}📄 {rel} ({f.stat().st_size} bytes)")
    
    # Read and display file
    readme = files_dir / "README.md"
    print(f"\n3. Content of {readme}:")
    print("-" * 40)
    print(readme.read_text())
    print("-" * 40)
    
    # Create TODO
    todo_file = files_dir / "TODO.md"
    todo_file.write_text("""# Filesystem Operations TODO

- [ ] List all Python files
- [ ] Read main.py content
- [ ] Search for markdown files
- [ ] Create summary report
""")
    print(f"\n4. Created TODO.md:")
    print(todo_file.read_text())
    
    # Show what filesystem-mcp would do
    print("\n5. Filesystem operations to perform:")
    print(f"""
   Commands:
   
   # List files
   algitex docker call filesystem-mcp list_directory \\
     -i '{{"path": "{files_dir}"}}'
   
   # Read file
   algitex docker call filesystem-mcp read_file \\
     -i '{{"path": "{files_dir}/README.md"}}'
   
   # Search for .py files
   algitex docker call filesystem-mcp search_files \\
     -i '{{"pattern": "*.py", "path": "{files_dir}"}}'
        """)
    
    print(f"\n6. Files created:")
    print(f"   - {files_dir}/")
    print(f"   - {files_dir}/README.md")
    print(f"   - {files_dir}/src/main.py")
    print(f"   - {files_dir}/docs/guide.md")
    print(f"   - {files_dir}/TODO.md")
    print(f"\n   Keep for manual experimentation.")
    print(f"   Clean up: rm -rf {files_dir}")


if __name__ == "__main__":
    demo_file_operations()
