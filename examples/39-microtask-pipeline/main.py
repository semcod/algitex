"""Example 39: Microtask Pipeline

Demonstrates the microtask classification, planning, and execution pipeline.

Run: python examples/39-microtask-pipeline/main.py
"""

from pathlib import Path


def demo_microtask_classify():
    """Demo: Microtask classification."""
    print("\n=== Microtask Classification ===")
    print("\nCommand: algitex microtask classify TODO.md")
    print("\nFeatures:")
    print("  • Task decomposition into atomic units")
    print("  • Context window estimation")
    print("  • Dependency analysis")
    
    print("\nExample classification:")
    print("  Task: 'Add type hints to functions'")
    print("  Decomposed into:")
    print("    1. Add hints to function 'process_data'")
    print("    2. Add hints to function 'validate_input'")
    print("    3. Add hints to function 'format_output'")


def demo_microtask_plan():
    """Demo: Microtask planning."""
    print("\n=== Microtask Planning ===")
    print("\nCommand: algitex microtask plan TODO.md")
    print("\nFeatures:")
    print("  • Batching strategy (by context window)")
    print("  • Execution order (dependencies)")
    print("  • Parallel group assignment")
    
    print("\nExample plan:")
    print("  Group 1 (parallel):")
    print("    • Fix imports in file_a.py")
    print("    • Fix imports in file_b.py")
    print("  Group 2 (sequential):")
    print("    • Add docstring to class A")
    print("    • Add docstring to class B (depends on A)")


def demo_microtask_run():
    """Demo: Microtask execution."""
    print("\n=== Microtask Execution ===")
    print("\nCommand: algitex microtask run TODO.md")
    print("\nThree-phase execution:")
    print("  Phase 1: Algorithmic fixes (parallel)")
    print("  Phase 2: Small LLM fixes (rate-limited)")
    print("  Phase 3: Big LLM fixes (batch processing)")
    
    print("\nOptions:")
    print("  --dry-run: Preview without changes")
    print("  --batch-size: Max files per batch (default: 5)")
    print("  --parallel: Parallel groups (default: 3)")


def demo_workflow():
    """Demo: Complete microtask workflow."""
    print("\n=== Complete Workflow ===")
    print("""
    # 1. Classify tasks
    $ algitex microtask classify TODO.md
    Analyzing 50 tasks...
    Created 120 microtasks (2.4x decomposition)
    
    # 2. Plan execution
    $ algitex microtask plan TODO.md --output plan.json
    Grouped into 8 parallel batches
    Estimated time: 12 minutes
    
    # 3. Execute
    $ algitex microtask run TODO.md --execute
    Phase 1: 45/45 algorithmic tasks ✓
    Phase 2: 60/75 small LLM tasks ✓ (15 failed)
    Phase 3: 15/15 big LLM tasks ✓
    """)


def main():
    """Run all microtask demos."""
    print("=" * 60)
    print("Example 39: Microtask Pipeline")
    print("=" * 60)
    
    demo_microtask_classify()
    demo_microtask_plan()
    demo_microtask_run()
    demo_workflow()
    
    print("\n" + "=" * 60)
    print("Quick Start:")
    print("  1. Classify: algitex microtask classify TODO.md")
    print("  2. Plan:     algitex microtask plan TODO.md")
    print("  3. Run:      algitex microtask run TODO.md --execute")
    print("=" * 60)


if __name__ == "__main__":
    main()
