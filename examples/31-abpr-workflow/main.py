"""Main demonstration of ABPR (Abduction-Based Procedural Refinement) workflow.

This script shows how algitex uses pipeline-first approach instead of prompt-first.
The LLM is just one step inside the pipeline, not the entire solution.
"""
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from algitex import Project, Loop


def main() -> None:
    """Demonstrate ABPR pipeline: Execute → Trace → Conflict → Rule → Validate → Repeat."""
    print("=" * 60)
    print("ABPR (Abduction-Based Procedural Refinement) Demo")
    print("=" * 60)
    print("\nPhilosophy: Pipeline-first, prompt-second")
    print("Instead of: 'fix this bug' → LLM global rewrite")
    print("We do: analyze → localize → generate rule → validate → repeat")
    
    project_path = str(Path(__file__).parent.parent.parent)
    p = Project(project_path)
    loop = Loop(project_path)
    
    # Stage 1: Execute — collect traces from LLM interactions
    print("\n" + "=" * 40)
    print("Stage 1: Execute — Discover patterns")
    print("=" * 40)
    print("Analyzing historical LLM interactions...")
    
    # Simulate pattern discovery
    patterns = [
        {"name": "validate_input", "frequency": 12, "type": "validation"},
        {"name": "handle_error", "frequency": 8, "type": "error_handling"},
        {"name": "log_access", "frequency": 15, "type": "logging"},
        {"name": "check_permissions", "frequency": 6, "type": "security"},
        {"name": "format_response", "frequency": 9, "type": "output"},
    ]
    
    print(f"Discovered {len(patterns)} recurring patterns:")
    for p in patterns:
        print(f"  - {p['name']}: {p['frequency']}x occurrences ({p['type']})")
    
    # Stage 2: Trace — structural analysis
    print("\n" + "=" * 40)
    print("Stage 2: Trace — Structural analysis")
    print("=" * 40)
    
    health = p.analyze()
    print(f"Codebase metrics:")
    print(f"  - CC̄: {health.cc_avg:.1f}")
    print(f"  - Critical issues: {health.criticals}")
    print(f"  - Total files: {health.files}")
    print(f"  - Lines of code: {health.lines}")
    
    # Stage 3: Conflict — pattern extraction
    print("\n" + "=" * 40)
    print("Stage 3: Conflict — Extract high-impact patterns")
    print("=" * 40)
    
    # Filter patterns by frequency threshold
    min_freq = 5
    high_impact_patterns = [p for p in patterns if p['frequency'] >= min_freq]
    
    print(f"Patterns with frequency ≥ {min_freq}:")
    for p in high_impact_patterns:
        confidence = min(95, 60 + p['frequency'] * 3)
        print(f"  - {p['name']}: {p['frequency']}x → confidence: {confidence}%")
    
    # Stage 4: Rule — generate deterministic rules
    print("\n" + "=" * 40)
    print("Stage 4: Rule — Generate deterministic rules")
    print("=" * 40)
    
    rules = []
    for p in high_impact_patterns:
        confidence = min(95, 60 + p['frequency'] * 3)
        if confidence >= 75:
            rules.append({
                "name": f"{p['name']}_rule",
                "pattern": p['name'],
                "confidence": confidence,
                "savings": p['frequency'] * 0.10  # $0.10 per LLM call saved
            })
            print(f"  ✓ Generated rule: {p['name']}_rule (confidence: {confidence}%)")
        else:
            print(f"  ✗ Pattern too variable: {p['name']} (confidence: {confidence}%)")
    
    # Stage 5: Validate — test rules on new cases
    print("\n" + "=" * 40)
    print("Stage 5: Validate — Test rule effectiveness")
    print("=" * 40)
    
    # Simulate validation
    test_cases = 20
    rule_coverage = len(rules) / len(high_impact_patterns) * 100
    passed_rules = sum(1 for r in rules if r['confidence'] >= 80)
    
    print(f"Validation results:")
    print(f"  - Test cases: {test_cases}")
    print(f"  - Rules generated: {len(rules)}")
    print(f"  - Rule coverage: {rule_coverage:.0f}%")
    print(f"  - Rules passing validation: {passed_rules}/{len(rules)}")
    
    # Stage 6: Repeat — iterate if needed
    print("\n" + "=" * 40)
    print("Stage 6: Repeat — Iterative refinement")
    print("=" * 40)
    
    iterations = 1
    if rule_coverage < 80:
        print("Rule coverage below 80%, triggering another iteration...")
        iterations += 1
        # In real implementation, would loop here
    else:
        print("✓ Sufficient rule coverage achieved")
    
    # Final report
    total_savings = sum(r['savings'] for r in rules)
    print("\n" + "=" * 60)
    print("ABPR Pipeline Report")
    print("=" * 60)
    print(f"Rules generated: {len(rules)}")
    print(f"Rule coverage: {rule_coverage:.0f}%")
    print(f"Cost savings: ${total_savings:.2f} per 100 requests")
    print(f"Iterations: {iterations}")
    print(f"Module stabilized: {'YES' if rule_coverage >= 80 else 'NO'}")
    
    print("\nBenefits of ABPR approach:")
    print("  • Deterministic rules for common cases")
    print("  • LLM reserved for edge cases")
    print("  • Progressive cost reduction")
    print("  • Consistent handling of patterns")
    print("  • Full audit trail of decisions")
    
    print("\n" + "=" * 60)
    print("To run a specific workflow:")
    print("  algitex workflow run examples/31-abpr-workflow/workflows/fix-auth.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
