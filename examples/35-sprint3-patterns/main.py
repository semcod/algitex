"""Example 35: Sprint 3 CC Reduction Patterns

Demonstrates the cyclomatic complexity reduction patterns introduced in Sprint 3:
- Dict dispatch pattern (classify.py)
- Strategy pattern (repair.py)
- Pipeline pattern (verify.py)

Run: python examples/35-sprint3-patterns/main.py
"""

from pathlib import Path


def demo_dict_dispatch():
    """Demo: Dict dispatch pattern from classify.py
    
    CC: 50 -> 4 (92% reduction)
    Pattern: Replace if/elif chains with dict lookup
    """
    print("\n=== Dict Dispatch Pattern (classify.py) ===")
    
    # Before: CC 50 - long if/elif chain
    def classify_message_before(message: str) -> str:
        lowered = message.lower()
        if "unused import" in lowered:
            return "unused_import"
        elif "return type" in lowered:
            return "return_type"
        elif "f-string" in lowered:
            return "fstring"
        # ... 20+ more elifs
        return "other"
    
    # After: CC 4 - dict dispatch
    from algitex.todo.classify import classify_message, KNOWN_MAGIC_CONSTANTS
    
    test_messages = [
        "Unused import: os",
        "Missing return type annotation",
        "Convert to f-string",
        "Magic number 42 should be named constant",
    ]
    
    print("\nClassifications:")
    for msg in test_messages:
        result = classify_message(msg)
        print(f"  '{msg[:40]}...' -> {result.category} (tier: {result.tier})")
    
    print(f"\nCC reduction: 50 -> 4 ({(1 - 4/50) * 100:.0f}%)")


def demo_strategy_pattern():
    """Demo: Strategy pattern from repair.py
    
    CC: 30 -> 6 (80% reduction)
    Pattern: Extract repair logic into separate functions
    """
    print("\n=== Strategy Pattern (repair.py) ===")
    
    from algitex.todo.repair import REPAIRERS
    
    print("\nAvailable repair strategies:")
    for category, repair_func in REPAIRERS.items():
        print(f"  • {category}: {repair_func.__name__}")
    
    print(f"\nTotal strategies: {len(REPAIRERS)}")
    print("CC reduction: 30 -> 6 (80%)")


def demo_pipeline_pattern():
    """Demo: Pipeline pattern from verify.py
    
    CC: 29 -> 5 (83% reduction)
    Pattern: Split verification into discrete steps
    """
    print("\n=== Pipeline Pattern (verify.py) ===")
    
    from algitex.todo.verify import VerifyResult, verify_todos
    
    print("\nVerification pipeline steps:")
    steps = [
        "1. _run_prefact_scan() - Scan code with prefact",
        "2. _parse_todo_file() - Parse TODO.md",
        "3. _diff_issues() - Compare found vs expected",
        "4. _validate_task_against_file() - Check each task",
        "5. _format_verify_report() - Generate report",
    ]
    for step in steps:
        print(f"  {step}")
    
    print("\nCC reduction: 29 -> 5 (83%)")


def demo_orchestrator_pattern():
    """Demo: Orchestrator pattern from fixer.py
    
    Lines: 724 -> ~450 (38% reduction)
    Pattern: Delegation to specialized modules
    """
    print("\n=== Orchestrator Pattern (fixer.py) ===")
    
    print("\nBefore: God module (724 lines)")
    print("  • Parsing logic")
    print("  • Classification logic (50 CC)")
    print("  • Repair logic (30 CC)")
    print("  • Reporting logic")
    
    print("\nAfter: Orchestrator only (~450 lines)")
    print("  • Imports from classify.py")
    print("  • Imports from repair.py")
    print("  • Delegates to specialized modules")
    print("  • Coordinates parallel execution")
    
    print("\nLine reduction: 724 -> ~450 (38%)")


def main():
    """Run all Sprint 3 pattern demos."""
    print("=" * 60)
    print("Sprint 3: CC Reduction Patterns Demo")
    print("=" * 60)
    
    demo_dict_dispatch()
    demo_strategy_pattern()
    demo_pipeline_pattern()
    demo_orchestrator_pattern()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("  • Dict dispatch: CC 50 -> 4 (92%)")
    print("  • Strategy: CC 30 -> 6 (80%)")
    print("  • Pipeline: CC 29 -> 5 (83%)")
    print("  • Orchestrator: 724L -> ~450L (38%)")
    print("=" * 60)


if __name__ == "__main__":
    main()
