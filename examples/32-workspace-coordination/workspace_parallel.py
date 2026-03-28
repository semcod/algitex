"""Example: Multi-repo workspace with parallel execution.

The wronai ecosystem has 7+ repos. algitex workspace orchestrates
analysis and fixes across all of them — one agent per repo.
No file conflicts because each agent works in a separate repository.

Run:
    python examples/workspace_parallel.py

Requires workspace.yaml in current directory.
"""
from algitex.tools.workspace import Workspace


def main() -> None:
    ws = Workspace("./workspace.yaml")

    # ─── Step 1: Analyze all repos in parallel ────────────

    print("Analyzing all repositories...\n")
    all_health = ws.analyze_all()

    print(f"  {'Repo':<15} {'CC̄':>5} {'Crit':>5} {'LOC':>7} {'Files':>6}")
    print(f"  {'─'*15} {'─'*5} {'─'*5} {'─'*7} {'─'*6}")
    for name, health in sorted(all_health.items()):
        print(
            f"  {name:<15} {health['cc']:>5.1f} {health['criticals']:>5} "
            f"{health['loc']:>7} {health['files']:>6}"
        )

    # Expected output:
    #   Repo              CC̄  Crit     LOC  Files
    #   ─────────────── ───── ───── ─────── ──────
    #   algitex           3.3    22   12551     61
    #   code2llm          4.8    52   18340    102
    #   code2docs         4.4    10    3187     31
    #   llx               3.9    49   25632    120
    #   planfile          4.1    12    9626     49
    #   proxym            4.6   247   68692    259
    #   redup             3.8    15    8772     52
    #   vallm             3.5    12    8604     56

    # ─── Step 2: Plan across repos (dependency-aware) ─────

    print("\nPlanning cross-repo refactoring (2 sprints)...\n")
    plan = ws.plan_all(sprints=2)

    total = sum(len(tickets) for tickets in plan.values())
    print(f"  Total tickets: {total}")
    for repo, tickets in plan.items():
        print(f"  {repo}: {len(tickets)} tickets")

    # ─── Step 3: Execute — one agent per repo ─────────────

    print("\nExecuting (parallel — one agent per repo)...\n")
    results = ws.execute_all(tool="aider-mcp", max_tickets=5)

    # Each repo runs on its own agent with its own git worktree.
    # Zero conflict risk because agents never touch the same files.
    #
    # Dependency order is respected:
    #   Phase 1 (parallel): code2llm, vallm, redup (no deps)
    #   Phase 2 (parallel): planfile (deps: code2llm, vallm)
    #   Phase 3 (parallel): llx (deps: planfile)
    #   Phase 4 (parallel): proxym (deps: llx, planfile)
    #   Phase 5 (parallel): algitex (deps: all)

    print(f"  {'Repo':<15} {'Status':<12} {'Tickets':>8} {'Cost':>8}")
    print(f"  {'─'*15} {'─'*12} {'─'*8} {'─'*8}")
    for r in results:
        print(
            f"  {r['repo']:<15} {r['status']:<12} "
            f"{len(r['tickets']):>8} ${r.get('cost', 0):>7.2f}"
        )


if __name__ == "__main__":
    main()
