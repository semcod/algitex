"""Example 40: Three-Tier Autofix System

Demonstrates the complete 3-tier autofix workflow with all phases.

Run: python examples/40-three-tier-autofix/main.py
"""


def demo_tier_algorithm():
    """Demo: Algorithm tier (deterministic fixes)."""
    print("\n=== Tier 1: Algorithm (Deterministic) ===")
    print("\nCommand: algitex todo fix --algo")
    
    print("\nCategories:")
    categories = [
        ("unused_import", "Remove unused imports"),
        ("return_type", "Add return type annotations"),
        ("fstring", "Convert to f-strings"),
        ("magic_known", "Replace known magic numbers"),
        ("sort_imports", "Sort import statements"),
        ("trailing_whitespace", "Remove trailing whitespace"),
    ]
    for cat, desc in categories:
        print(f"  • {cat}: {desc}")
    
    print("\nCharacteristics:")
    print("  • No LLM calls (100% deterministic)")
    print("  • Fast execution (parallel processing)")
    print("  • High success rate (>95%)")
    print("  • Workers: 8 (configurable)")


def demo_tier_micro():
    """Demo: Micro tier (small LLM fixes)."""
    print("\n=== Tier 2: Micro (Small LLM) ===")
    print("\nCommand: algitex todo fix --micro")
    
    print("\nCategories:")
    categories = [
        ("docstring", "Add missing docstrings"),
        ("rename", "Improve variable names"),
        ("guard_clause", "Add input validation"),
        ("dispatch", "Replace if/elif with dict"),
    ]
    for cat, desc in categories:
        print(f"  • {cat}: {desc}")
    
    print("\nCharacteristics:")
    print("  • Small LLM calls (qwen3-coder:latest)")
    print("  • Rate limited (10 calls/sec)")
    print("  • Medium success rate (~80%)")
    print("  • Workers: 4 (configurable)")


def demo_tier_big():
    """Demo: Big tier (large LLM fixes)."""
    print("\n=== Tier 3: Big (Large LLM) ===")
    print("\nCommand: algitex todo fix --all (includes big)")
    
    print("\nCategories:")
    categories = [
        ("split_function", "Split large functions"),
        ("dependency_cycle", "Fix circular dependencies"),
        ("architecture", "API redesign"),
        ("refactor", "Major refactoring"),
    ]
    for cat, desc in categories:
        print(f"  • {cat}: {desc}")
    
    print("\nCharacteristics:")
    print("  • Large LLM calls (context-aware)")
    print("  • Rate limited (customizable)")
    print("  • Lower success rate (~60%)")
    print("  • Manual review recommended")


def demo_all_tiers():
    """Demo: Running all three tiers."""
    print("\n=== All Three Tiers ===")
    print("\nCommand: algitex todo fix --all")
    
    print("\nExecution order:")
    print("  Phase 1: Algorithm (parallel, fast)")
    print("          ↓")
    print("  Phase 2: Micro (rate-limited)")
    print("          ↓")
    print("  Phase 3: Big (sequential, careful)")
    
    print("\nExample output:")
    print("  Tiered Summary")
    print("    • Algorithm: fixed=45, skipped=3, errors=0")
    print("    • Small LLM: fixed=38, skipped=7, errors=2")
    print("    • Big LLM: fixed=12, skipped=8, errors=0")


def demo_dashboard_integration():
    """Demo: Dashboard with 3-tier system."""
    print("\n=== Dashboard Integration ===")
    print("\nCommand: algitex todo fix --all --dashboard")
    
    print("\nDashboard shows:")
    print("  ┌─────────────────────────────────────────┐")
    print("  │ Algorithm:  [████████░░░░░░░░░░] 45/50  │")
    print("  │ Micro:      [░░░░░░░░░░░░░░░░░░] 0/75   │")
    print("  │ Big:       [░░░░░░░░░░░░░░░░░░] 0/20   │")
    print("  ├─────────────────────────────────────────┤")
    print("  │ Cache: 156 hits, 23 misses (89.2%)   │")
    print("  └─────────────────────────────────────────┘")


def main():
    """Run all 3-tier demos."""
    print("=" * 60)
    print("Example 40: Three-Tier Autofix System")
    print("=" * 60)
    
    demo_tier_algorithm()
    demo_tier_micro()
    demo_tier_big()
    demo_all_tiers()
    demo_dashboard_integration()
    
    print("\n" + "=" * 60)
    print("Quick Start:")
    print("  Algorithm only:  algitex todo fix --algo")
    print("  Micro only:       algitex todo fix --micro")
    print("  All tiers:        algitex todo fix --all")
    print("  With dashboard:   algitex todo fix --all --dashboard")
    print("=" * 60)


if __name__ == "__main__":
    main()
