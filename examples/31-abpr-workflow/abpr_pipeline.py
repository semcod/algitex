"""Example: ABPR-style pipeline (pipeline-first, prompt-second).

Instead of: "fix this bug" → LLM global rewrite
We do: analyze → localize → generate rule → validate → repeat

This is the core algitex philosophy: the user designs PIPELINES,
not prompts. LLM is just one step inside the pipeline.

Run:
    algitex workflow run examples/abpr_auth_fix.md --ticket SEC-2026-01
"""
from algitex import Project, Loop


def abpr_pipeline(project_path: str = "./my-app"):
    """ABPR loop: Execute → Trace → Conflict → Rule → Validate → Repeat."""

    p = Project(project_path)
    loop = Loop(project_path)

    # ─── Stage 1: Execute — collect traces ────────────────

    print("Stage 1: Discovering patterns from LLM interactions...")
    loop.discover()

    # ─── Stage 2: Build trace — structural analysis ───────

    print("Stage 2: Analyzing codebase structure...")
    health = p.analyze()
    print(f"  CC̄={health.cc_avg:.1f}, criticals={health.criticals}")

    # ─── Stage 3: Find conflict — pattern extraction ──────

    print("Stage 3: Extracting recurring patterns...")
    patterns = loop.extract(min_frequency=3)
    print(f"  Found {len(patterns)} patterns")
    for pat in patterns[:5]:
        print(f"    - {pat.name}: {pat.frequency}x occurrences")

    # ─── Stage 4: Apply rule — local fix, not rewrite ─────

    print("Stage 4: Generating deterministic rules...")
    total_rules = 0
    for pattern in patterns:
        rules = loop.generate_rules(pattern)
        total_rules += len(rules)
        for rule in rules:
            print(f"    Rule: {rule.name} (confidence: {rule.confidence:.0%})")

    # ─── Stage 5: Validate ────────────────────────────────

    print("Stage 5: Validating...")
    validation = p.execute(
        workflow="examples/abpr_auth_fix.md",
        ticket_ref="SEC-2026-01",
    )
    print(f"  Validation: {'PASSED' if validation.passed else 'FAILED'}")

    # ─── Stage 6: Repeat until stable ─────────────────────

    iteration = 0
    while not validation.passed and iteration < 5:
        iteration += 1
        print(f"\nIteration {iteration}: re-analyzing...")
        loop.discover()
        patterns = loop.extract()
        for pat in patterns:
            loop.generate_rules(pat)
        validation = p.execute(workflow="examples/abpr_auth_fix.md")
        print(f"  Validation: {'PASSED' if validation.passed else 'FAILED'}")

    # ─── Report ───────────────────────────────────────────

    report = loop.report()
    print(f"\n{'='*50}")
    print(f"Rules generated: {total_rules}")
    print(f"Rule coverage: {report.rule_coverage:.0%}")
    print(f"Cost savings: ${report.cost_saved:.2f}")
    print(f"Iterations: {iteration + 1}")
    print(f"Module stabilized: {'YES' if validation.passed else 'NO'}")


if __name__ == "__main__":
    abpr_pipeline()
