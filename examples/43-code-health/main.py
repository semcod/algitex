"""Example 43: Code Health Monitoring

Demonstrates continuous monitoring of code health metrics
using algitex analysis pipeline with historical tracking.

Run: python examples/43-code-health/main.py
"""

import json
from datetime import datetime
from pathlib import Path


def demo_health_metrics():
    """Show key code health metrics tracked by algitex."""
    print("\n=== Code Health Metrics ===")
    
    metrics = {
        "Cyclomatic Complexity (CC)": {
            "avg_cc": "Average across all functions (target: <1.8)",
            "max_cc": "Highest single function CC (target: <20)",
            "critical": "Functions with CC > 15 (target: 0)",
        },
        "Code Organization": {
            "god_modules": "Files >500L with >15 CC (target: 0)",
            "high_cc_funcs": "Functions with CC >= 15 (target: <4)",
            "duplicates": "Duplicate code clusters (target: 0)",
        },
        "Dependencies": {
            "cycles": "Circular import cycles (target: 0)",
            "hub_types": "Overly coupled types (target: 0)",
            "orphan_funcs": "Uncalled functions (target: identify)",
        },
        "Documentation": {
            "doc_coverage": "Functions with docstrings (target: >80%)",
            "type_coverage": "Functions with type hints (target: >90%)",
        }
    }
    
    for category, items in metrics.items():
        print(f"\n{category}:")
        for metric, description in items.items():
            print(f"  • {metric}: {description}")


def demo_analysis_pipeline():
    """Show the analysis pipeline that generates health reports."""
    print("\n=== Analysis Pipeline ===")
    
    pipeline = """
    1. code2llm: Static analysis
       - Parse all Python files
       - Calculate cyclomatic complexity
       - Build import graph
       - Identify declarations
       
    2. vallm: 4-tier validation
       - Syntax validation
       - Type checking (where possible)
       - Runtime validation (tests)
       - Security scanning
       
    3. redup: Duplication detection
       - Find duplicate code clusters
       - Calculate similarity scores
       - Suggest extraction candidates
       
    4. algitex: Integration
       - Aggregate all metrics
       - Generate health score
       - Create historical trends
       - Prioritize fixes
    """
    print(pipeline)


def demo_health_report():
    """Show example health report from analysis.toon.yaml."""
    print("\n=== Health Report Example ===")
    
    report = {
        "generated": "2026-04-25T12:44:46",
        "summary": {
            "total_files": 311,
            "total_lines": 91106,
            "total_functions": 1726,
            "avg_cc": 2.6,
            "critical_functions": 10,
            "duplicate_clusters": 3,
            "circular_cycles": 0,
        },
        "grades": {
            "complexity": "B+",
            "organization": "B",
            "duplication": "A-",
            "dependencies": "A",
            "documentation": "C+",
        },
        "alerts": [
            "🔴 _classify_message: CC=48 (limit: 15)",
            "🟡 todo_verify_prefact: CC=29 (limit: 15)",
            "🟡 fix_file: CC=25 (limit: 15)",
            "🟡 3 duplicate code clusters found",
        ]
    }
    
    print(f"\nGenerated: {report['generated']}")
    print(f"\nSummary:")
    for key, value in report['summary'].items():
        print(f"  {key}: {value}")
    
    print(f"\nGrades:")
    for metric, grade in report['grades'].items():
        print(f"  {metric}: {grade}")
    
    print(f"\nAlerts:")
    for alert in report['alerts']:
        print(f"  {alert}")


def demo_historical_tracking():
    """Show how health metrics evolve over time."""
    print("\n=== Historical Tracking ===")
    
    # Simulated historical data
    history = [
        ("2026-03-01", 2.9, 15, 7),
        ("2026-03-15", 2.8, 12, 6),
        ("2026-04-01", 2.7, 11, 5),
        ("2026-04-15", 2.6, 10, 4),
        ("2026-04-25", 2.5, 9, 3),
    ]
    
    print("\nCC and Critical Functions Over Time:")
    print(f"{'Date':<12} {'Avg CC':<8} {'Critical':<10} {'God Mods':<10}")
    print("-" * 45)
    for date, cc, crit, gods in history:
        print(f"{date:<12} {cc:<8} {crit:<10} {gods:<10}")
    
    print("\n\nTrends:")
    print("  ✓ Average CC: 2.9 → 2.5 (14% improvement)")
    print("  ✓ Critical functions: 15 → 9 (40% reduction)")
    print("  ✓ God modules: 7 → 3 (57% reduction)")
    
    print("\n\nHistorical tracking commands:")
    print("  # Store metrics after each analysis")
    print("  algitex analyze --store-metrics")
    print("  ")
    print("  # View trends over time")
    print("  algitex metrics history --chart")
    print("  ")
    print("  # Compare current to baseline")
    print("  algitex metrics compare --baseline 2026-03-01")


def demo_ci_integration():
    """Show CI/CD integration for health gates."""
    print("\n=== CI/CD Health Gates ===")
    
    print("\nGitHub Actions workflow:")
    workflow = """
    name: Code Health Check
    on: [pull_request]
    
    jobs:
      health:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          
          - name: Setup algitex
            run: pip install algitex
          
          - name: Analyze code health
            run: |
              algitex analyze --format json --output health.json
              
          - name: Check health thresholds
            run: |
              # Fail if CC increased
              algitex metrics check-thresholds \
                --max-cc 15 \
                --max-avg-cc 2.5 \
                --max-critical 10
          
          - name: Comment PR
            uses: actions/github-script@v6
            with:
              script: |
                const health = require('./health.json');
                github.rest.issues.createComment({
                  issue_number: context.issue.number,
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  body: `Code Health: ${health.grade}\nAvg CC: ${health.avg_cc}`
                });
    """
    print(workflow)
    
    print("\n\nThreshold configuration (pyproject.toml):")
    config = """
    [tool.algitex.health]
    max_avg_cc = 2.5
    max_function_cc = 15
    max_critical_functions = 10
    max_duplicate_clusters = 3
    min_doc_coverage = 0.8
    min_type_coverage = 0.9
    """
    print(config)


def demo_regression_prevention():
    """Show how to prevent health regressions."""
    print("\n=== Regression Prevention ===")
    
    print("\nStrategies:")
    
    strategies = [
        ("Pre-commit hooks", "Block commits that increase CC"),
        ("PR checks", "Fail build if new critical functions added"),
        ("Sprint goals", "Reduce X critical functions per sprint"),
        ("Refactoring Fridays", "Dedicated time for health improvements"),
        ("Health dashboards", "Visible metrics for the team"),
    ]
    
    for strategy, description in strategies:
        print(f"  • {strategy}: {description}")
    
    print("\n\nPre-commit hook configuration:")
    hook = """
    # .pre-commit-config.yaml
    - repo: local
      hooks:
        - id: code-health
          name: Check code health
          entry: algitex analyze --check-thresholds
          language: system
          pass_filenames: false
          always_run: true
    """
    print(hook)


def demo_health_improvement_workflow():
    """Show complete workflow for improving code health."""
    print("\n=== Health Improvement Workflow ===")
    
    workflow = """
    Step 1: Analyze current state
      $ algitex analyze
      → View project/analysis.toon.yaml
      
    Step 2: Identify priorities
      $ algitex plan --focus complexity
      → Creates tickets for high-CC functions
      
    Step 3: Fix systematically
      # Week 1: Address god modules
      $ algitex todo run --category god-module --limit 3
      
      # Week 2: Reduce high-CC functions
      $ algitex todo fix-auto --category high-cc
      
      # Week 3: Remove duplicates
      $ algitex todo fix-auto --category duplicate
      
    Step 4: Measure improvement
      $ algitex analyze --compare-to 2026-03-01
      → Shows CC reduction, line changes
      
    Step 5: Update baseline
      $ algitex metrics set-baseline
      → New threshold for future PRs
    """
    print(workflow)


def main():
    """Run all code health monitoring demos."""
    print("=" * 70)
    print("Example 43: Code Health Monitoring")
    print("=" * 70)
    
    demo_health_metrics()
    demo_analysis_pipeline()
    demo_health_report()
    demo_historical_tracking()
    demo_ci_integration()
    demo_regression_prevention()
    demo_health_improvement_workflow()
    
    print("\n" + "=" * 70)
    print("Key Takeaway:")
    print("  Monitor CC, duplication, and dependencies continuously.")
    print("  Set thresholds in CI, track trends, fix systematically.")
    print("=" * 70)


if __name__ == "__main__":
    main()
