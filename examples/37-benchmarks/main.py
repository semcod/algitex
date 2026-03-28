"""Example 37: Performance Benchmarks

Demonstrates the benchmark framework for measuring cache, tiers, and memory.

Run: python examples/37-benchmarks/main.py
"""

import subprocess
import sys


def demo_benchmark_quick():
    """Demo: Quick benchmark (30 seconds)."""
    print("\n=== Quick Benchmark ===")
    print("\nCommand: algitex benchmark quick")
    print("\nFeatures:")
    print("  • 30-second performance test")
    print("  • Cache throughput")
    print("  • Tier comparison")
    print("  • Memory baseline")


def demo_benchmark_cache():
    """Demo: Cache performance testing."""
    print("\n=== Cache Benchmark ===")
    print("\nCommand: algitex benchmark cache --entries 100 --lookups 500")
    print("\nFeatures:")
    print("  • Hit rate measurement")
    print("  • Lookup latency")
    print("  • Deduplication ratio")
    print("  • Cache size growth")
    
    print("\nExample output:")
    print("  Entries:    100")
    print("  Lookups:    500")
    print("  Hit rate:   87.3%")
    print("  Avg latency: 2.1ms")


def demo_benchmark_tiers():
    """Demo: Tier throughput comparison."""
    print("\n=== Tier Benchmark ===")
    print("\nCommand: algitex benchmark tiers")
    print("\nCompares:")
    print("  • Algorithm tier (deterministic fixes)")
    print("  • Micro tier (small LLM calls)")
    print("  • Big tier (large LLM calls)")
    
    print("\nExample output:")
    print("  Algorithm: 45 tasks/sec (parallel)")
    print("  Micro:     3.2 tasks/sec (LLM-limited)")
    print("  Big:       0.8 tasks/sec (LLM-limited)")


def demo_benchmark_memory():
    """Demo: Memory profiling for large files."""
    print("\n=== Memory Benchmark ===")
    print("\nCommand: algitex benchmark memory --lines 1000")
    print("\nFeatures:")
    print("  • tracemalloc integration")
    print("  • Peak memory tracking")
    print("  • Per-function allocation")
    
    print("\nExample output:")
    print("  Lines processed: 1000")
    print("  Peak memory:     128.5 MB")
    print("  Current memory:  45.2 MB")


def demo_benchmark_full():
    """Demo: Full benchmark suite with export."""
    print("\n=== Full Benchmark Suite ===")
    print("\nCommand: algitex benchmark full --export results.json")
    print("\nIncludes:")
    print("  • Quick benchmark")
    print("  • Cache benchmark (100 entries, 500 lookups)")
    print("  • Tier benchmark")
    print("  • Memory benchmark (1000 lines)")
    print("  • JSON export for CI/CD")
    
    print("\nCI/CD integration:")
    print("  $ algitex benchmark full --export benchmark.json")
    print("  $ python -c \"import json; d=json.load(open('benchmark.json')); \"")
    print("      \"assert d['cache']['hit_rate'] > 80\"")


def main():
    """Run all benchmark demos."""
    print("=" * 60)
    print("Example 37: Performance Benchmarks")
    print("=" * 60)
    
    demo_benchmark_quick()
    demo_benchmark_cache()
    demo_benchmark_tiers()
    demo_benchmark_memory()
    demo_benchmark_full()
    
    print("\n" + "=" * 60)
    print("Quick Start:")
    print("  Quick test:  algitex benchmark quick")
    print("  Cache test:  algitex benchmark cache")
    print("  Full suite:  algitex benchmark full --export results.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
