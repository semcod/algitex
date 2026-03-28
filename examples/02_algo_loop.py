#!/usr/bin/env python3
"""Example 02: Progressive Algorithmization Loop.

Demonstrates the 5-stage journey from "LLM handles everything"
to "most traffic runs deterministically."

This example simulates trace collection and pattern extraction
without needing a live proxym instance.

Run:
    python examples/02_algo_loop.py
"""

import time
from devloop.algo import Loop


def main():
    print("=== Progressive Algorithmization Demo ===\n")

    loop = Loop(".")

    # ── Stage 1: Discovery ────────────────────────────
    print("[Stage 1] Discovery — collecting traces...")
    loop.discover()

    # Simulate 20 LLM interactions with repeating patterns
    patterns_data = [
        # Pattern A: same question asked 8 times ($0.02 each)
        ("What is a for loop in Python?", "A for loop iterates...", 0.02),
        # Pattern B: formatting request 6 times ($0.01 each)
        ("Format this JSON: {}", "Here's the formatted...", 0.01),
        # Pattern C: unique questions (no pattern)
        ("Explain quantum computing", "Quantum computing uses...", 0.05),
        ("Design a microservice architecture", "Consider using...", 0.08),
        ("Debug this race condition", "The issue is...", 0.12),
    ]

    for prompt, response, cost in patterns_data:
        repeat = 8 if "for loop" in prompt else (6 if "Format" in prompt else 1)
        for _ in range(repeat):
            loop.add_trace(
                prompt=prompt,
                response=response,
                model="haiku" if cost < 0.03 else "sonnet",
                tier="cheap" if cost < 0.03 else "standard",
                cost_usd=cost,
                elapsed_ms=150 + cost * 5000,
            )

    report = loop.report()
    print(f"  Traces collected: {report['total_requests']}")
    print(f"  Total cost: ${report['total_cost_usd']:.2f}")

    # ── Stage 2: Pattern Extraction ───────────────────
    print("\n[Stage 2] Extraction — finding patterns...")
    patterns = loop.extract(min_frequency=3)
    print(f"  Patterns found: {len(patterns)}")
    for p in patterns:
        savings = p.frequency * p.avg_cost_usd
        print(f"  {p.id}: '{p.description[:40]}...' "
              f"(freq={p.frequency}, potential savings=${savings:.2f})")

    # ── Stage 3: Rule Generation ──────────────────────
    print("\n[Stage 3] Rule Generation — creating deterministic handlers...")
    # Without proxym, generate stub rules
    rules = loop.generate_rules(use_llm=False)
    print(f"  Rules generated: {len(rules)}")
    for r in rules:
        print(f"  {r.pattern_id}: {r.name} ({r.type})")

    # ── Stage 4: Hybrid Routing ───────────────────────
    print("\n[Stage 4] Hybrid Routing — route by confidence...")
    test_prompts = [
        "What is a for loop in Python?",    # known pattern → rule
        "Explain quantum entanglement",      # unknown → LLM
        "Format this JSON: {}",              # known pattern → rule
    ]
    for prompt in test_prompts:
        decision = loop.route(prompt)
        handler = decision["handler"]
        icon = "⚡" if handler == "rule" else "🤖"
        print(f"  {icon} '{prompt[:40]}...' → {handler}")

    # ── Stage 5: Optimization Report ──────────────────
    print("\n[Stage 5] Optimization — final report:")
    final = loop.report()
    print(f"  Stage: {final['stage']}")
    print(f"  Total requests: {final['total_requests']}")
    print(f"  Deterministic: {final['deterministic_ratio']}")
    print(f"  Rules active: {final['rules_active']}")
    print(f"  Money saved: ${final['saved_cost_usd']:.2f}")
    print(f"  Money spent: ${final['total_cost_usd']:.2f}")

    print("\n✅ Loop complete!")
    print("  In production, traces arrive automatically from proxym.")
    print("  Run: devloop algo report")


if __name__ == "__main__":
    main()
