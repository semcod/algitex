#!/usr/bin/env python3
"""Example 05: Cost Tracking & Budget.

Shows how devloop tracks LLM costs per-ticket
and how the algo loop reduces spending over time.

Run:
    python examples/05_cost_tracking.py
"""

from devloop import Project
from devloop.algo import Loop
from devloop.tools.tickets import Tickets


def main():
    print("=== Cost Tracking Demo ===\n")

    # 1. Create tickets with simulated cost metadata
    t = Tickets(".")
    tickets = [
        t.add("Fix auth module", priority="high", type="refactor",
              meta={"model": "claude-sonnet-4", "cost_usd": 0.045, "tier": "standard"}),
        t.add("Add unit tests", priority="normal", type="test",
              meta={"model": "claude-haiku-4.5", "cost_usd": 0.003, "tier": "cheap"}),
        t.add("Refactor god module cli.py", priority="critical", type="refactor",
              meta={"model": "claude-opus-4", "cost_usd": 0.182, "tier": "deep"}),
        t.add("Fix typo in README", priority="low", type="bug",
              meta={"model": "deepseek-v3", "cost_usd": 0.0004, "tier": "trivial"}),
        t.add("Design API schema", priority="high", type="feature",
              meta={"model": "gemini-2.5-flash", "cost_usd": 0.0, "tier": "free"}),
    ]

    # 2. Cost ledger per ticket
    print("Cost per ticket:")
    total = 0.0
    for ticket in tickets:
        cost = ticket.meta.get("cost_usd", 0)
        model = ticket.meta.get("model", "?")
        tier = ticket.meta.get("tier", "?")
        total += cost
        print(f"  {ticket.id} [{tier:>10}] ${cost:>7.4f}  {model:<25} {ticket.title}")

    print(f"\n  {'':>10} Total: ${total:.4f}")

    # 3. Cost by tier
    tier_costs = {}
    for ticket in tickets:
        tier = ticket.meta.get("tier", "unknown")
        tier_costs.setdefault(tier, 0.0)
        tier_costs[tier] += ticket.meta.get("cost_usd", 0)

    print("\nCost by tier:")
    for tier, cost in sorted(tier_costs.items(), key=lambda x: -x[1]):
        bar = "█" * max(1, int(cost / total * 40)) if total > 0 else ""
        print(f"  {tier:>10}: ${cost:.4f} {bar}")

    # 4. Algo loop savings simulation
    print("\n── Progressive Algorithmization Savings ──")
    loop = Loop(".")
    loop.discover()

    # Simulate: "Fix typo" pattern repeated 50 times over a month
    for _ in range(50):
        loop.add_trace(
            "Fix typo in this text: ...",
            "Here's the corrected text: ...",
            model="deepseek-v3",
            tier="trivial",
            cost_usd=0.0004,
        )

    # Simulate: "Format JSON" pattern repeated 30 times
    for _ in range(30):
        loop.add_trace(
            "Format this JSON",
            '{"formatted": true}',
            model="haiku",
            tier="cheap",
            cost_usd=0.002,
        )

    patterns = loop.extract(min_frequency=5)
    report = loop.report()

    print(f"  Traces collected: {report['total_requests']}")
    print(f"  Patterns found: {report['patterns_found']}")
    print(f"  Total LLM cost: ${report['total_cost_usd']:.2f}")

    # Calculate potential savings
    potential_savings = sum(p.frequency * p.avg_cost_usd for p in patterns)
    print(f"  Potential monthly savings: ${potential_savings:.2f}")
    print(f"  That's {potential_savings / max(report['total_cost_usd'], 0.01):.0%} "
          f"of current spend")

    print("\n✅ In production, devloop algo rules generates")
    print("   deterministic handlers for these patterns automatically.")


if __name__ == "__main__":
    main()
