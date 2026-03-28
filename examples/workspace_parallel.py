"""Example: Multi-repo workspace with parallel execution across repos.

The wronai ecosystem has 7 repos. algitex workspace analyzes all of them,
creates cross-repo tickets, and executes fixes in parallel — one agent per repo.
"""
from algitex.tools.workspace import Workspace

def main():
    ws = Workspace("./workspace.yaml")

    # 1. Analyze all repos (parallel — no conflicts, different repos)
    all_health = ws.analyze_all()
    for name, health in all_health.items():
        print(f"  {name}: CC̄={health['cc_avg']}, criticals={health['criticals']}")

    # 2. Plan — cross-repo dependency-aware
    plan = ws.plan_all(sprints=2)
    print(f"\n  {len(plan)} tickets across {len(all_health)} repos")

    # 3. Execute — one agent per repo (inherently parallel, no file conflicts)
    results = ws.go_all(tool="aider-mcp", parallel=True)

    # Output:
    # Agent 0 → code2llm repo: PLF-050, PLF-051 (parser refactoring)
    # Agent 1 → vallm repo: PLF-060 (import fix)
    # Agent 2 → planfile repo: PLF-070, PLF-071 (model merge)
    # Agent 3 → llx repo: PLF-080..PLF-085 (import fix + strategy merge)
    # Agent 4 → proxym repo: PLF-090 (llx bridge)
    # → All run simultaneously, zero conflict risk

    for r in results:
        print(f"  {r['repo']}: {r['status']} ({len(r['tickets'])} tickets)")


if __name__ == "__main__":
    main()
