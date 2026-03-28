"""Example 36: Live Dashboard Usage

Demonstrates real-time monitoring with the dashboard TUI.
Shows how to use dashboard in different modes.

Run: python examples/36-dashboard/main.py
"""

import subprocess
import sys


def demo_dashboard_live():
    """Demo: Live dashboard with auto-refresh."""
    print("\n=== Live Dashboard ===")
    print("\nCommand: algitex dashboard live")
    print("\nFeatures:")
    print("  • Real-time cache metrics (hits, misses, size)")
    print("  • Tier progress tracking (algorithm/micro/big)")
    print("  • Auto-refresh every 1 second")
    print("  • Keyboard interrupt (Ctrl+C) to exit")
    
    # Simulate running the command
    print("\n[Simulating: algitex dashboard live --duration 5]")
    print("  Cache: 156 hits, 23 misses, 89.2% hit rate")
    print("  Algorithm tier: 12/50 tasks complete")
    print("  Micro tier: idle")
    print("  Big tier: idle")


def demo_dashboard_monitor():
    """Demo: Monitor existing cache and metrics."""
    print("\n=== Monitor Mode ===")
    print("\nCommand: algitex dashboard monitor")
    print("\nFeatures:")
    print("  • View existing .algitex/cache stats")
    print("  • View .algitex/metrics.json")
    print("  • No execution, pure monitoring")
    
    print("\nExample:")
    print("  $ algitex dashboard monitor \\")
    print("      --cache .algitex/cache \\")
    print("      --metrics .algitex/metrics.json")


def demo_dashboard_export():
    """Demo: Export metrics to various formats."""
    print("\n=== Export Mode ===")
    print("\nCommands:")
    print("  JSON:       algitex dashboard export --format json")
    print("  Prometheus: algitex dashboard export --format prometheus")
    
    print("\nExample output (JSON):")
    print("""  {
    "timestamp": "2026-03-28T17:50:00",
    "cache": {
      "hits": 156,
      "misses": 23,
      "hit_rate": 89.2,
      "entries": 179,
      "size_bytes": 245760
    },
    "tiers": {
      "algorithm": {"total": 50, "current": 12},
      "micro": {"total": 0, "current": 0},
      "big": {"total": 0, "current": 0}
    }
  }""")


def demo_dashboard_with_todo():
    """Demo: Dashboard integration with TODO commands."""
    print("\n=== Dashboard + TODO Commands ===")
    
    examples = [
        ("3-tier fix", "algitex todo fix --all --dashboard"),
        ("Hybrid autofix", "algitex todo hybrid --execute --dashboard"),
        ("Batch operations", "algitex todo batch --execute --dashboard"),
    ]
    
    print("\nIntegration examples:")
    for name, cmd in examples:
        print(f"\n  {name}:")
        print(f"    $ {cmd}")
    
    print("\nDashboard shows:")
    print("  • Real-time progress for each tier")
    print("  • Cache hit/miss statistics")
    print("  • Current batch/file being processed")


def main():
    """Run all dashboard demos."""
    print("=" * 60)
    print("Example 36: Live Dashboard Usage")
    print("=" * 60)
    
    demo_dashboard_live()
    demo_dashboard_monitor()
    demo_dashboard_export()
    demo_dashboard_with_todo()
    
    print("\n" + "=" * 60)
    print("Quick Start:")
    print("  1. Start dashboard: algitex dashboard live")
    print("  2. Run with TODO:   algitex todo fix --all --dashboard")
    print("  3. Export metrics:  algitex dashboard export --format json")
    print("=" * 60)


if __name__ == "__main__":
    main()
