#!/usr/bin/env python3
"""Example 16: Test Workflow - Real Project Setup.

Creates sample project and demonstrates testing workflow.
"""

,os
from pathlib import Path
import subprocess


def create_sample_project() -> Any:
    """Create sample project with tests."""
    base_dir = Path(__file__).parent / "sample_test_project"
    base_dir.mkdir(exist_ok=True)
    
    # Create source code
    src_dir = base_dir / "src"
    src_dir.mkdir(exist_ok=True)
    (src_dir / "calculator.py").write_text('''
def add(x, y):
    """Add two numbers."""
    return x + y

def subtract(x, y):
    """Subtract y from x."""
    return x - y

def multiply(x, y):
    """Multiply two numbers."""
    return x * y

def divide(x, y):
    """Divide x by y."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y
''')
    
    # Create tests
    test_dir = base_dir / "tests"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "test_calculator.py").write_text('''
import sys
sys.path.insert(0, 'src')

from calculator import add, subtract, multiply, divide

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5

def test_divide_by_zero():
    try:
        divide(5, 0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

if __name__ == "__main__":
    test_add()
    test_subtract()
    test_multiply()
    test_divide()
    test_divide_by_zero()
    print("All tests passed!")
''')
    
    # Create requirements
    (base_dir / "requirements.txt").write_text('''pytest>=7.0.0
pytest-cov>=4.0.0
''')
    
    # Create TODO
    (base_dir / "TODO.md").write_text('''# Test Workflow TODO

- [ ] Install dependencies: pip install -r requirements.txt
- [ ] Run tests: pytest
- [ ] Check coverage: pytest --cov=src
- [ ] Run with coverage report: pytest --cov=src --cov-report=html
- [ ] Fix any failing tests
''')
    
    return base_dir


def run_tests(project_dir) -> Dict:
    """Try to run tests if pytest available."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-v"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "returncode": result.returncode
        }
    except FileNotFoundError:
        return {"success": False, "output": "pytest not found", "returncode": -1}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "timeout", "returncode": -1}


def demo_test_workflow() -> None:
    """Demonstrate test workflow."""
    print("=== Test Workflow - Real Project Setup ===\n")
    
    # Create sample project
    project_dir = create_sample_project()
    print(f"1. Created sample project: {project_dir}")
    
    # Show structure
    print(f"\n2. Project structure:")
    for f in project_dir.rglob("*"):
        rel = f.relative_to(project_dir)
        if f.is_file():
            print(f"   📄 {rel}")
    
    # Show source code
    src_file = project_dir / "src" / "calculator.py"
    print(f"\n3. Source code ({src_file}):")
    print("-" * 40)
    print(src_file.read_text())
    print("-" * 40)
    
    # Show tests
    test_file = project_dir / "tests" / "test_calculator.py"
    print(f"\n4. Test file ({test_file}):")
    print("-" * 40)
    print(test_file.read_text())
    print("-" * 40)
    
    # Show TODO
    todo_file = project_dir / "TODO.md"
    print(f"\n5. TODO list:")
    print(todo_file.read_text())
    
    # Try to run tests
    print("\n6. Running tests:")
    test_result = run_tests(project_dir)
    if test_result["success"]:
        print("   ✅ All tests passed!")
        print(test_result["output"][-500:] if len(test_result["output"]) > 500 else test_result["output"])
    else:
        print(f"   ⚠️  Tests not run: {test_result['output']}")
        print("   (Install pytest: pip install pytest)")
    
    # Show workflow steps
    print("\n7. Complete test workflow:")
    print(f"""
   Setup:
   cd {project_dir}
   pip install -r requirements.txt
   
   Run tests:
   pytest
   
   With coverage:
   pytest --cov=src --cov-report=term-missing
   
   Using Docker MCP tools:
   algitex docker call vallm validate -i '{{"path": "{project_dir}"}}'
        """)
    
    print(f"\n8. Files created:")
    print(f"   - {project_dir}/src/calculator.py")
    print(f"   - {project_dir}/tests/test_calculator.py")
    print(f"   - {project_dir}/requirements.txt")
    print(f"   - {project_dir}/TODO.md")
    print(f"\n   Project ready for testing.")
    print(f"   Clean up: rm -rf {project_dir}")


if __name__ == "__main__":
    demo_test_workflow()
