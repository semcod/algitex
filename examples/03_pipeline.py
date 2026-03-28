#!/usr/bin/env python3
"""Example 03: Composable Pipeline.

Chain steps fluently: analyze → tickets → execute → validate → sync.
Each step is optional — skip what you don't need.

Run:
    python examples/03_pipeline.py
"""

from algitex import Pipeline


def main():
    print("=== Pipeline Demo ===\n")

    # Pattern A: Full pipeline
    print("[1] Full pipeline (dry run):")
    result = (
        Pipeline(".")
        .analyze(full=False)     # quick health check
        .create_tickets()        # auto-generate from analysis
        .report()
    )
    for step in result["steps"]:
        print(f"  ✓ {step}")

    # Pattern B: Analysis only
    print("\n[2] Analysis-only pipeline:")
    result = (
        Pipeline(".")
        .analyze()
        .report()
    )
    grade = result["results"].get("analysis", "N/A")
    if hasattr(grade, "split"):
        print(f"  Result: {grade[:100]}")

    # Pattern C: Custom ticket creation
    print("\n[3] Adding tickets from external source:")
    from algitex.tools.tickets import Tickets
    t = Tickets(".")
    t.add("Integrate with CI/CD", priority="normal", type="feature",
          source="human", tags=["ci", "devops"])
    t.add("Add rate limiting to proxy", priority="high", type="feature",
          source="human", tags=["proxy", "performance"])
    t.add("Fix flaky test in auth module", priority="critical", type="bug",
          source="human", tags=["test", "auth"])

    board = t.board()
    for col, tickets in board.items():
        if tickets:
            print(f"  {col.upper()}: {len(tickets)}")
            for ticket in tickets[:3]:
                print(f"    [{ticket.priority}] {ticket.id}: {ticket.title}")

    print("\n✅ Pipeline complete!")
    print("  Use algitex go for the full automated cycle.")


if __name__ == "__main__":
    main()
