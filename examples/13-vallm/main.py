#!/usr/bin/env python3
"""Example 13: Vallm - Real Code Validation.

Creates sample code with issues and demonstrates validation.
"""

,os
from pathlib import Path
import subprocess


def create_sample_code() -> Any:
    """Create sample Python code with issues to validate."""
    base_dir = Path(__file__).parent / "sample_code"
    base_dir.mkdir(exist_ok=True)
    
    # Create code with complexity issues
    (base_dir / "complex_module.py").write_text('''
def process_data(data):
    """Process data with nested logic."""
    result = []
    for item in data:
        if item:
            if isinstance(item, dict):
                if 'value' in item:
                    if item['value'] > 0:
                        for sub in item['items']:
                            if sub.valid:
                                result.append(sub.process())
    return result

def calculate(x, y, operation):
    if operation == "add":
        return x + y
    elif operation == "sub":
        return x - y
    elif operation == "mul":
        return x * y
    elif operation == "div":
        if y != 0:
            return x / y
        else:
            return None
    else:
        return None
''')
    
    # Create TODO
    (base_dir / "TODO.md").write_text('''# Validation TODO

- [ ] Run static analysis with ruff
- [ ] Check with mypy
- [ ] Calculate cyclomatic complexity
- [ ] Security scan with bandit
- [ ] Fix complexity issues
''')
    
    return base_dir


def run_local_validation(code_dir) -> Any:
    """Run local validation tools if available."""
    results = {}
    
    # Try ruff
    try:
        result = subprocess.run(
            ["ruff", "check", str(code_dir)],
            capture_output=True, text=True, timeout=10
        )
        results["ruff"] = {
            "returncode": result.returncode,
            "issues": len(result.stdout.splitlines()) if result.stdout else 0
        }
    except FileNotFoundError:
        results["ruff"] = "not installed"
    
    # Try mypy
    try:
        result = subprocess.run(
            ["mypy", str(code_dir)],
            capture_output=True, text=True, timeout=10
        )
        results["mypy"] = {
            "returncode": result.returncode,
            "issues": len(result.stdout.splitlines()) if result.stdout else 0
        }
    except FileNotFoundError:
        results["mypy"] = "not installed"
    
    return results


def demo_validation() -> None:
    """Demonstrate real code validation."""
    print("=== Vallm - Real Code Validation ===\n")
    
    # Create sample code
    code_dir = create_sample_code()
    print(f"1. Created sample code: {code_dir}")
    
    # Show the code
    code_file = code_dir / "complex_module.py"
    print(f"\n2. Code to validate ({code_file}):")
    print("-" * 40)
    print(code_file.read_text())
    print("-" * 40)
    
    # Show TODO
    todo_file = code_dir / "TODO.md"
    print(f"\n3. Validation TODO:")
    print(todo_file.read_text())
    
    # Run local validation
    print("\n4. Running local validation:")
    local_results = run_local_validation(code_dir)
    for tool, result in local_results.items():
        if result == "not installed":
            print(f"   {tool}: ⚠️  not installed")
        else:
            status = "✅" if result["returncode"] == 0 else "❌"
            print(f"   {tool}: {status} ({result['issues']} issues)")
    
    # Show what vallm would do
    print("\n5. Vallm validation to perform:")
    print(f"""
   Commands:
   
   # Static validation (ruff + mypy)
   algitex docker call vallm validate \\
     -i '{{"path": "{code_dir}", "files": ["complex_module.py"]}}'
   
   # Batch validation with scoring
   algitex docker call vallm batch \\
     -i '{{"path": "{code_dir}", "metrics": ["complexity", "security"]}}'
   
   # Quality score
   algitex docker call vallm score \\
     -i '{{"path": "{code_dir}", "threshold": 0.8}}'
        """)
    
    # Analysis of the code
    print("\n6. Manual analysis:")
    code = code_file.read_text()
    lines = code.splitlines()
    print(f"   - Total lines: {len(lines)}")
    print(f"   - Functions: {code.count('def ')}")
    
    # Count if/else (complexity indicator)
    complexity = code.count('if ') + code.count('elif ') + code.count('else:')
    print(f"   - Branch points: {complexity}")
    if complexity > 5:
        print(f"   ⚠️  High complexity detected (CC > 10 likely)")
    
    print(f"\n7. Files created:")
    print(f"   - {code_dir}/complex_module.py")
    print(f"   - {code_dir}/TODO.md")
    print(f"\n   Keep for manual validation.")
    print(f"   Clean up: rm -rf {code_dir}")


if __name__ == "__main__":
    demo_validation()
