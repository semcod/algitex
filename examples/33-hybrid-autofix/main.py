#!/usr/bin/env python3
"""Example 33: Hybrid AutoFix - Fast Parallel + LLM with Rate Limiting.

This example demonstrates the HybridAutofix class that combines:
- Phase 1: Fast parallel mechanical fixes (no LLM, ~1500 tps)
- Phase 2: Rate-limited parallel LLM fixes (~10-50 tps with rate limiting)

Usage:
    cd examples/33-hybrid-autofix
    python main.py --dry-run                    # Preview changes
    python main.py --execute --workers 4        # Execute with 4 workers
    python main.py --backend ollama --rate 5    # Use Ollama with 5 req/sec
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex.todo import HybridAutofix, verify_todos, benchmark_fix

# Default TODO.md path (relative to script location - works with symlink)
DEFAULT_TODO = Path(__file__).parent / "TODO.md"


def demo_dry_run(todo_file=DEFAULT_TODO):
    """Demo: Dry run to preview what would be fixed."""
    print("\n" + "=" * 70)
    print("DEMO 1: Dry Run (Preview)")
    print("=" * 70)

    fixer = HybridAutofix(
        backend="litellm-proxy",
        proxy_url="http://localhost:4000",
        workers=4,
        rate_limit=10,
        dry_run=True  # <-- Preview mode
    )

    result = fixer.fix_all(todo_file)
    fixer.print_summary(result)

    print("\n✅ This was a dry run. No actual changes made.")
    print("   Use --execute to apply fixes.")


def demo_verify_first(todo_file=DEFAULT_TODO):
    """Demo: Verify TODO tasks before fixing."""
    print("\n" + "=" * 70)
    print("DEMO 2: Verify TODO Tasks First")
    print("=" * 70)

    result = verify_todos(todo_file)
    print(f"\nStill open: {result.still_open}")
    print(f"Already fixed: {result.already_fixed}")
    print(f"Invalid (duplicates): {result.invalid}")


def demo_benchmark(todo_file=DEFAULT_TODO):
    """Demo: Benchmark performance."""
    print("\n" + "=" * 70)
    print("DEMO 3: Benchmark Performance")
    print("=" * 70)

    # Benchmark mechanical fixes
    result = benchmark_fix(todo_file, limit=100, workers=8, mode="parallel")
    result.print_report(detailed=True)


def demo_mechanical_only(todo_file=DEFAULT_TODO):
    """Demo: Fix only mechanical issues (fastest)."""
    print("\n" + "=" * 70)
    print("DEMO 4: Mechanical Fixes Only (Fast)")
    print("=" * 70)

    fixer = HybridAutofix(workers=8, dry_run=False)

    # Only Phase 1 - no LLM calls
    result = fixer.fix_mechanical(todo_file)
    print(f"\nFixed: {result['fixed']}, Skipped: {result['skipped']}, Errors: {result['errors']}")


def demo_full_hybrid(todo_file=DEFAULT_TODO, workers=4, rate_limit=10):
    """Demo: Full hybrid with LLM backend."""
    print("\n" + "=" * 70)
    print("DEMO 5: Full Hybrid (Mechanical + LLM)")
    print("=" * 70)

    fixer = HybridAutofix(
        backend="litellm-proxy",
        proxy_url="http://localhost:4000",
        workers=workers,
        rate_limit=rate_limit,          # LLM calls per second
        retry_attempts=3,
        dry_run=False           # <-- Actually execute
    )

    print("\n🔧 Phase 1: Parallel mechanical fixes (8 workers)")
    print("🤖 Phase 2: Rate-limited LLM fixes (10 req/sec)")
    print()

    result = fixer.fix_all(todo_file)
    fixer.print_summary(result)


def demo_ollama_local(todo_file=DEFAULT_TODO):
    """Demo: 100% offline with Ollama."""
    print("\n" + "=" * 70)
    print("DEMO 6: Ollama Local (100% Offline)")
    print("=" * 70)

    fixer = HybridAutofix(
        backend="ollama",
        workers=2,              # Fewer workers for local LLM
        rate_limit=5,           # 5 req/sec (Ollama is slower)
        retry_attempts=2,
        dry_run=False
    )

    result = fixer.fix_all(todo_file)
    fixer.print_summary(result)


def main():
    parser = argparse.ArgumentParser(
        description="Hybrid AutoFix - Parallel + LLM with Rate Limiting"
    )
    parser.add_argument(
        "--demo",
        choices=["dry-run", "verify", "benchmark", "mechanical", "hybrid", "ollama", "all"],
        default="all",
        help="Which demo to run"
    )
    parser.add_argument("--execute", action="store_true", help="Actually apply fixes")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--rate-limit", "-r", type=int, default=10, help="LLM calls per second")
    parser.add_argument("--backend", "-b", default="litellm-proxy",
                        choices=["litellm-proxy", "ollama", "aider"],
                        help="LLM backend")
    parser.add_argument("--proxy-url", default="http://localhost:4000",
                        help="LiteLLM proxy URL")
    parser.add_argument("--todo-file", "-f", type=Path, default=Path(__file__).parent / "TODO.md",
                        help="Path to TODO.md file (default: ./TODO.md)")

    args = parser.parse_args()

    print("=" * 70)
    print("Example 33: Hybrid AutoFix")
    print("Fast Parallel Mechanical + Rate-Limited LLM")
    print("=" * 70)

    if args.demo == "dry-run" or args.demo == "all":
        demo_dry_run(args.todo_file)

    if args.demo == "verify" or args.demo == "all":
        demo_verify_first(args.todo_file)

    if args.demo == "benchmark" or args.demo == "all":
        demo_benchmark(args.todo_file)

    if args.demo == "mechanical":
        demo_mechanical_only(args.todo_file)

    if args.demo == "hybrid":
        demo_full_hybrid(args.todo_file, args.workers, args.rate_limit)

    if args.demo == "ollama":
        demo_ollama_local(args.todo_file)

    print("\n" + "=" * 70)
    print("Done! Check the TODO.md for remaining tasks.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
