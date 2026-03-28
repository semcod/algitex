#!/usr/bin/env python3
"""Example 27: Unified AutoFix - Complete demonstration of algitex features.

This example shows how to use algitex's integrated features:
- Service health checking
- Ollama integration
- AutoFix with multiple backends
- TODO management
"""

import sys
import argparse
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def check_and_setup(project: Project, args) -> bool:
    """Check services and setup if needed."""
    print("\n" + "=" * 60)
    print("1. Service Health Check")
    print("=" * 60)
    
    # Print service status
    project.print_service_status(show_details=True)
    
    # Check Ollama models
    ollama_status = project.check_ollama()
    if ollama_status["healthy"]:
        models = ollama_status["details"]["models"]
        print(f"\n✅ Ollama has {len(models)} models")
        
        # Check if we have a coding model
        coding_models = [m for m in models if "coder" in m or "code" in m]
        if not coding_models and args.auto_pull:
            print("No coding models found. Pulling qwen2.5-coder:7b...")
            if project.pull_ollama_model("qwen2.5-coder:7b"):
                print("✅ Model pulled successfully")
            else:
                print("❌ Failed to pull model")
                return False
    else:
        print("\n⚠️  Ollama not running. Some features may not work.")
    
    return True


def analyze_and_plan(project: Project, args):
    """Analyze project and create plan."""
    print("\n" + "=" * 60)
    print("2. Project Analysis")
    print("=" * 60)
    
    # Analyze project
    report = project.analyze(full=False)
    print(f"Project grade: {report.grade}")
    print(f"Files: {report.files}, Lines: {report.lines}")
    
    # Check TODO tasks
    tasks = project.list_todo_tasks()
    if tasks:
        print(f"\nFound {len(tasks)} TODO tasks:")
        for task in tasks[:5]:
            print(f"  - {task['id']}: {task['description'][:50]}...")
        if len(tasks) > 5:
            print(f"  ... and {len(tasks) - 5} more")
    else:
        print("\nNo TODO tasks found. Run 'prefact -a' to create them.")
    
    return tasks


def execute_fixes(project: Project, tasks, args):
    """Execute fixes using chosen backend."""
    if not tasks:
        print("\nNo tasks to fix.")
        return
    
    print("\n" + "=" * 60)
    print("3. AutoFix Execution")
    print("=" * 60)
    
    # Choose backend
    backend = args.backend
    if backend == "auto":
        backends = project.autofix.check_backends()
        if backends.get("ollama"):
            backend = "ollama"
        elif backends.get("litellm-proxy"):
            backend = "litellm-proxy"
        elif backends.get("aider"):
            backend = "aider"
        else:
            print("❌ No fixing backends available!")
            return
    
    print(f"Using backend: {backend}")
    
    # Execute fixes
    result = project.fix_issues(
        limit=args.limit,
        backend=backend,
        filter_file=args.file
    )
    
    # Show results
    print("\n" + "=" * 60)
    print("4. Results Summary")
    print("=" * 60)
    print(f"Total issues: {result['total']}")
    print(f"✅ Fixed: {result['fixed']}")
    print(f"❌ Failed: {result['failed']}")
    
    if result['fixed'] > 0:
        print(f"\nFixed issues:")
        for r in result['results']:
            if r['success']:
                print(f"  ✅ {r['task_id']}: {r['task_description'][:50]}...")
    
    if result['failed'] > 0:
        print(f"\nFailed issues:")
        for r in result['results']:
            if not r['success']:
                print(f"  ❌ {r['task_id']}: {r['error']}")


def demo_features(project: Project):
    """Demonstrate additional features."""
    print("\n" + "=" * 60)
    print("5. Additional Features Demo")
    print("=" * 60)
    
    # Generate code with Ollama
    ollama_status = project.check_ollama()
    if ollama_status["healthy"]:
        print("\n📝 Generating code with Ollama...")
        prompt = "Write a Python function to validate email addresses"
        code = project.generate_with_ollama(
            prompt,
            system="You are a Python expert. Write clean, well-documented code."
        )
        print("Generated code:")
        print("```python")
        print(code[:300] + "..." if len(code) > 300 else code)
        print("```")
    
    # Show project status
    print("\n📊 Project Status:")
    status = project.status()
    print(f"  Health grade: {status['health']['grade']}")
    print(f"  Open tickets: {status['tickets']['open']}")
    print(f"  Total cost: ${status['cost_ledger']['total_spent_usd']:.4f}")


def main():
    parser = argparse.ArgumentParser(
        description="Unified AutoFix - Complete algitex demonstration"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Limit number of issues to fix"
    )
    parser.add_argument(
        "--backend", "-b",
        type=str,
        default="auto",
        choices=["auto", "ollama", "aider", "litellm-proxy"],
        help="Backend to use for fixing"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Fix issues only in this file"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without executing"
    )
    parser.add_argument(
        "--auto-pull",
        action="store_true",
        help="Automatically pull missing models"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run additional feature demos"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Example 27: Unified AutoFix")
    print("=" * 60)
    print("Complete demonstration of algitex features")
    print()
    
    # Initialize project
    project = Project(".")
    
    # Set dry run mode
    if args.dry_run:
        project.autofix.dry_run = True
        print("🔍 DRY RUN MODE - No changes will be made")
    
    # Step 1: Check services
    if not check_and_setup(project, args):
        return 1
    
    # Step 2: Analyze and plan
    tasks = analyze_and_plan(project, args)
    
    # Step 3: Execute fixes
    if not args.dry_run or tasks:
        execute_fixes(project, tasks, args)
    
    # Step 4: Demo features
    if args.demo:
        demo_features(project)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
