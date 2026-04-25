"""Example 41: God Module Splitting

Demonstrates how to split large "god modules" into focused submodules
while preserving backward compatibility through re-exports.

This mirrors the real-world refactoring of algitex's own modules:
- src/algitex/cli/todo.py (1159L -> split into classify, repair, verify)
- src/algitex/todo/fixer.py (724L -> orchestrator only)

Run: python examples/41-god-module-splitting/main.py
"""

from pathlib import Path
import tempfile


def demo_god_module_problem():
    """Show what a god module looks like and why it's problematic."""
    print("\n=== The God Module Problem ===")
    
    # Simulated god module: everything in one file
    god_module = """
    # old_todo.py - 1159 lines, CC=29
    
    def parse_todo_file(path):
        # 80 lines of parsing logic
        pass
    
    def classify_message(msg):
        # 120 lines of classification (CC=50)
        pass
    
    def apply_fix(task):
        # 200 lines of repair logic (CC=30)
        pass
    
    def verify_results():
        # 150 lines of verification (CC=29)
        pass
    
    def run_batch():
        # 300 lines of orchestration
        pass
    
    def export_report():
        # 80 lines of reporting
        pass
    
    # ... 229 more lines
    """
    
    print(f"God module size: ~1159 lines")
    print(f"Max cyclomatic complexity: CC=50 (classify_message)")
    print(f"Total functions doing different things: 21")
    print(f"\nProblems:")
    print(f"  - Hard to test (tight coupling)")
    print(f"  - Hard to navigate (mixed concerns)")
    print(f"  - Merge conflicts (everyone touches one file)")
    print(f"  - Can't reuse parts independently")


def demo_split_strategy():
    """Show the splitting strategy used in algitex."""
    print("\n=== Splitting Strategy ===")
    
    strategy = """
    Step 1: Identify cohesive groups
      - Parsing -> todo_parser.py
      - Classification -> classify.py
      - Repair -> repair.py
      - Verification -> verify.py
      - Orchestration -> fixer.py (thin)
    
    Step 2: Extract each group to its own module
      - Move code verbatim first
      - Fix imports afterward
    
    Step 3: Create thin orchestrator
      - fixer.py imports from submodules
      - Delegates to specialists
      - Only coordinates, doesn't implement
    
    Step 4: Preserve backward compatibility
      - __init__.py re-exports everything
      - Old imports still work
    """
    
    print(strategy)


def demo_before_and_after():
    """Compare module structure before and after split."""
    print("\n=== Before vs After ===")
    
    print("\nBEFORE (god module):")
    before = {
        "todo.py": {"lines": 1159, "cc_max": 50, "concerns": 6},
    }
    for name, stats in before.items():
        print(f"  {name}: {stats['lines']}L, CC={stats['cc_max']}, {stats['concerns']} concerns")
    
    print("\nAFTER (focused modules):")
    after = {
        "__init__.py": {"lines": 40, "cc_max": 2, "concerns": "re-exports"},
        "fixer.py": {"lines": 450, "cc_max": 12, "concerns": "orchestration"},
        "classify.py": {"lines": 120, "cc_max": 4, "concerns": "classification"},
        "repair.py": {"lines": 260, "cc_max": 6, "concerns": "repair strategies"},
        "verify.py": {"lines": 150, "cc_max": 5, "concerns": "verification pipeline"},
        "hybrid.py": {"lines": 240, "cc_max": 10, "concerns": "hybrid routing"},
    }
    for name, stats in after.items():
        print(f"  {name}: {stats['lines']}L, CC={stats['cc_max']}, {stats['concerns']}")
    
    total_before = sum(s["lines"] for s in before.values())
    total_after = sum(s["lines"] for s in after.values() if isinstance(s["lines"], int))
    
    print(f"\nTotal lines: {total_before} -> {total_after} (+{total_after-total_before} for __init__)")
    print(f"Max CC: 50 -> 12 (76% reduction)")
    print(f"Average CC: ~29 -> ~6.5")


def demo_import_compatibility():
    """Show how backward compatibility is maintained."""
    print("\n=== Backward Compatibility ===")
    
    print("\nUser code still works (no changes needed):")
    print("  from algitex.todo import classify_message")
    print("  from algitex.todo import REPAIRERS")
    print("  from algitex.todo import verify_todos")
    
    print("\nInternal __init__.py does re-exports:")
    init_code = '''
    # src/algitex/todo/__init__.py
    from .classify import classify_message, KNOWN_MAGIC_CONSTANTS
    from .repair import REPAIRERS, apply_repair
    from .verify import verify_todos, VerifyResult
    from .fixer import fix_todos, benchmark_fix
    # ... all old exports preserved
    '''
    print(init_code)
    
    print("Benefits:")
    print("  - Users don't need to update imports")
    print("  - Gradual migration possible")
    print("  - Tests continue to pass")


def demo_real_metrics():
    """Show actual metrics from algitex refactoring."""
    print("\n=== Real Refactoring Metrics ===")
    
    modules = [
        ("todo/classify.py", "CC 50 -> 4", "Dict dispatch pattern", "92%"),
        ("todo/repair.py", "CC 30 -> 6", "Strategy pattern", "80%"),
        ("todo/verify.py", "CC 29 -> 5", "Pipeline pattern", "83%"),
        ("todo/fixer.py", "724L -> 450L", "Orchestrator only", "38%"),
        ("microtask/executor.py", "CC 27 -> 5", "Dispatch table", "81%"),
        ("tools/batch_logger.py", "CC 22 -> 2", "Split to_markdown", "91%"),
    ]
    
    print("\n{:<25} {:<15} {:<20} {:<10}".format(
        "Module", "CC Change", "Pattern", "Reduction"
    ))
    print("-" * 75)
    for module, cc, pattern, reduction in modules:
        print(f"{module:<25} {cc:<15} {pattern:<20} {reduction:<10}")
    
    print("\nOverall project impact:")
    print("  - Average CC: 2.9 -> 2.5 (14% improvement)")
    print("  - God modules: 3 -> 0")
    print("  - High-CC functions (>=15): 9 -> 4")
    print("  - Test suite: 317 tests passing")


def demo_how_to_split_your_module():
    """Provide practical steps for splitting any god module."""
    print("\n=== How To Split Your God Module ===")
    
    steps = [
        ("1. Analyze", "Run code2llm or similar to find high-CC functions"),
        ("2. Group", "Cluster functions by concern (parsing, logic, IO)"),
        ("3. Extract", "Move each group to a new file (copy-paste first)"),
        ("4. Fix imports", "Update internal imports between new modules"),
        ("5. Re-export", "Add imports to __init__.py for compatibility"),
        ("6. Test", "Run existing tests - they should pass unchanged"),
        ("7. Refine", "Clean up cross-module coupling"),
    ]
    
    for step, desc in steps:
        print(f"\n  {step}: {desc}")
    
    print("\n\nAnti-patterns to avoid:")
    print("  - Circular imports between new modules")
    print("  - Splitting too granularly (nano-modules)")
    print("  - Breaking public API without deprecation")


def main():
    """Run all god module splitting demos."""
    print("=" * 70)
    print("Example 41: God Module Splitting")
    print("=" * 70)
    
    demo_god_module_problem()
    demo_split_strategy()
    demo_before_and_after()
    demo_import_compatibility()
    demo_real_metrics()
    demo_how_to_split_your_module()
    
    print("\n" + "=" * 70)
    print("Key Takeaway:")
    print("  Split by concern, preserve imports, measure CC before/after.")
    print("  A 1159-line god module becomes 6 focused files under 450L each.")
    print("=" * 70)


if __name__ == "__main__":
    main()
