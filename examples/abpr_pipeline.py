"""Example: ABPR-style pipeline (Abduction-Based Procedural Refinement).

Instead of: "fix this bug" (prompt-first)
We do: analyze → localize → generate rule → validate → repeat (pipeline-first)

This is the core algitex philosophy: pipeline-first, prompt-second.
"""
from algitex import Project, Loop
from algitex.workflows import Workflow

def main():
    p = Project("./my-app")
    loop = Loop("./my-app")

    # Stage 1: Execute — collect traces from LLM interactions
    loop.discover()

    # Stage 2: Build trace — structural analysis (not imagined state)
    health = p.analyze()
    print(f"CC̄={health.cc_avg}, criticals={health.criticals}")

    # Stage 3: Find conflict — pattern extraction
    patterns = loop.extract(min_frequency=3)
    print(f"Found {len(patterns)} recurring patterns")

    # Stage 4: Apply rule — local fix, not global rewrite
    for pattern in patterns:
        rules = loop.generate_rules(pattern)
        for rule in rules:
            print(f"  Generated rule: {rule.name} (confidence: {rule.confidence})")

    # Stage 5: Route — deterministic if possible, LLM if not
    for request in get_incoming_requests():
        result = loop.route(request)
        if result.used_rule:
            print(f"  Handled by rule: {result.rule_name} (no LLM cost)")
        else:
            print(f"  Handled by LLM: {result.model} (${result.cost})")

    # Stage 6: Optimize — report savings
    report = loop.report()
    print(f"Rules cover {report.rule_coverage}% of requests")
    print(f"Cost savings: ${report.cost_saved}")


def get_incoming_requests():
    """Mock incoming requests for demonstration."""
    return [
        {"type": "refactor", "target": "Project.status"},
        {"type": "optimize", "target": "BatchProcessor.process"},
        {"type": "extract", "target": "call_stdio"},
    ]


if __name__ == "__main__":
    main()
