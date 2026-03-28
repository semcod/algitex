"""Example 38: Using New Sprint 3 Modules

Demonstrates how to use the new classify, repair, and verify modules directly.

Run: python examples/38-new-modules/main.py
"""

from pathlib import Path
import tempfile


def demo_classify_module():
    """Demo: Using algitex.todo.classify directly."""
    print("\n=== classify.py Module ===")
    
    from algitex.todo.classify import (
        KNOWN_MAGIC_CONSTANTS,
        TaskTriage,
        classify_message,
    )
    
    print("\n1. Classify a message:")
    msg = "Unused import: os module not used"
    result = classify_message(msg)
    print(f"   Message: '{msg}'")
    print(f"   Category: {result.category}")
    print(f"   Tier: {result.tier}")
    print(f"   Reason: {result.reason}")
    
    print("\n2. Known magic constants:")
    for num, name in list(KNOWN_MAGIC_CONSTANTS.items())[:5]:
        print(f"   {num} -> {name}")
    print(f"   ... ({len(KNOWN_MAGIC_CONSTANTS)} total)")


def demo_repair_module():
    """Demo: Using algitex.todo.repair directly."""
    print("\n=== repair.py Module ===")
    
    from algitex.todo.repair import (
        REPAIRERS,
        repair_fstring,
        repair_magic_number,
        repair_unused_import,
    )
    
    print("\n1. Available repairers:")
    for category, func in REPAIRERS.items():
        print(f"   {category}: {func.__name__}")
    
    print("\n2. Create a test file:")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import os\nimport sys\n\ndef hello():\n    print('Hello')\n")
        test_file = Path(f.name)
    
    print(f"   Created: {test_file}")
    print(f"   Content: {test_file.read_text()!r}")
    
    # Cleanup
    test_file.unlink()


def demo_verify_module():
    """Demo: Using algitex.todo.verify directly."""
    print("\n=== verify.py Module ===")
    
    from algitex.todo.verify import VerifyResult, verify_todos
    
    print("\n1. Verification pipeline:")
    steps = [
        "_run_prefact_scan()",
        "_parse_todo_file()",
        "_diff_issues()",
        "_validate_task_against_file()",
        "_format_verify_report()",
    ]
    for step in steps:
        print(f"   • {step}")
    
    print("\n2. VerifyResult dataclass:")
    print("   • valid_tasks: List of still-valid tasks")
    print("   • outdated_tasks: List of outdated tasks")
    print("   • new_issues: Issues found but not in TODO")
    print("   • report: Human-readable summary")


def demo_combined_workflow():
    """Demo: Combining all three modules."""
    print("\n=== Combined Workflow ===")
    
    print("\nExample: Auto-fix workflow")
    print("""
    from algitex.todo import classify_message, REPAIRERS
    from algitex.todo.verify import verify_todos
    
    # Step 1: Parse and classify
    tasks = parse_todo("TODO.md")
    for task in tasks:
        triage = classify_message(task.message)
        task.category = triage.category
        task.tier = triage.tier
    
    # Step 2: Group by tier
    algo_tasks = [t for t in tasks if t.tier == "algorithm"]
    micro_tasks = [t for t in tasks if t.tier == "micro"]
    big_tasks = [t for t in tasks if t.tier == "big"]
    
    # Step 3: Repair algorithmic tasks
    for task in algo_tasks:
        repairer = REPAIRERS.get(task.category)
        if repairer:
            repairer(Path(task.file), task.message, task.line)
    
    # Step 4: Verify results
    result = verify_todos("TODO.md")
    print(f"Valid: {len(result.valid_tasks)}, Outdated: {len(result.outdated_tasks)}")
    """)


def main():
    """Run all module demos."""
    print("=" * 60)
    print("Example 38: Using New Sprint 3 Modules")
    print("=" * 60)
    
    demo_classify_module()
    demo_repair_module()
    demo_verify_module()
    demo_combined_workflow()
    
    print("\n" + "=" * 60)
    print("Key Imports:")
    print("  from algitex.todo.classify import classify_message")
    print("  from algitex.todo.repair import REPAIRERS, repair_unused_import")
    print("  from algitex.todo.verify import verify_todos, VerifyResult")
    print("=" * 60)


if __name__ == "__main__":
    main()
