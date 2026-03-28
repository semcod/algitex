from typing import Any

"""Main demonstration of workspace coordination across multiple repositories.

This script shows how algitex orchestrates analysis and fixes across
multiple repositories with dependency-aware scheduling.
"""
from pathlib import Path
import sys
import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))



def load_workspace_config() -> Any:
    """Load the workspace configuration."""
    config_path = Path(__file__).parent / "workspace.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def main() -> None:
    """Demonstrate workspace coordination across multiple repositories."""
    print("=" * 60)
    print("Workspace Coordination Demo")
    print("=" * 60)
    
    config = load_workspace_config()
    ws_name = config["workspace"]["name"]
    print(f"\nWorkspace: {ws_name}")
    print(f"Description: {config['workspace']['description']}")
    
    # Show repository overview
    print("\nRepository Overview:")
    print("-" * 40)
    repos = config["repos"]
    for repo in sorted(repos, key=lambda x: x.get("priority", 999)):
        deps = repo.get("depends_on", [])
        dep_str = f" (deps: {', '.join(deps)})" if deps else ""
        print(f"  {repo['name']:<15} P{repo.get('priority', 0)} {dep_str}")
        print(f"    {repo['role']}")
    
    # Simulate workspace analysis
    print("\n" + "=" * 40)
    print("Phase 1: Parallel Analysis")
    print("=" * 40)
    
    # Group by priority for parallel execution
    by_priority = {}
    for repo in repos:
        priority = repo.get("priority", 1)
        by_priority.setdefault(priority, []).append(repo)
    
    print("Execution phases (parallel within each phase):")
    for priority in sorted(by_priority):
        print(f"\nPhase {priority}:")
        for repo in by_priority[priority]:
            print(f"  - {repo['name']}")
    
    # Simulate analysis results
    print("\nSimulated analysis results:")
    print("-" * 40)
    
    mock_health = {
        "algitex": {"cc": 3.3, "criticals": 22, "loc": 12551, "files": 61},
        "code2llm": {"cc": 4.8, "criticals": 52, "loc": 18340, "files": 102},
        "vallm": {"cc": 3.5, "criticals": 12, "loc": 8604, "files": 56},
        "planfile": {"cc": 4.1, "criticals": 12, "loc": 9626, "files": 49},
        "llx": {"cc": 3.9, "criticals": 49, "loc": 25632, "files": 120},
        "proxym": {"cc": 4.6, "criticals": 247, "loc": 68692, "files": 259},
        "redup": {"cc": 3.8, "criticals": 15, "loc": 8772, "files": 52},
    }
    
    print(f"{'Repo':<15} {'CC̄':>5} {'Crit':>5} {'LOC':>7} {'Files':>6}")
    print(f"{'─'*15} {'─'*5} {'─'*5} {'─'*7} {'─'*6}")
    for name, health in sorted(mock_health.items()):
        print(
            f"{name:<15} {health['cc']:>5.1f} {health['criticals']:>5} "
            f"{health['loc']:>7} {health['files']:>6}"
        )
    
    # Calculate quality gates
    print("\n" + "=" * 40)
    print("Quality Gates")
    print("=" * 40)
    
    gates = config.get("gates", [])
    for gate in gates:
        metric = gate["metric"]
        operator = gate["operator"]
        threshold = gate["threshold"]
        
        print(f"\n{metric} {operator} {threshold}:")
        for name, health in mock_health.items():
            value = health.get(metric.replace("avg_", ""), 0)
            if metric == "avg_cc":
                value = health["cc"]
            
            # Simple evaluation
            passed = False
            if operator == "<=":
                passed = value <= threshold
            elif operator == ">=":
                passed = value >= threshold
            elif operator == "==":
                passed = value == threshold
            
            status = "✓" if passed else "✗"
            print(f"  {name:<15} {value:>7.1f} {status}")
    
    # Simulate planning
    print("\n" + "=" * 40)
    print("Phase 2: Cross-Repo Planning")
    print("=" * 40)
    
    # Generate mock tickets based on critical issues
    tickets = {}
    for name, health in mock_health.items():
        if health["criticals"] > 0:
            # Generate 1 ticket per 10 critical issues
            num_tickets = max(1, health["criticals"] // 10)
            tickets[name] = [f"{name.upper()}-PLF-{i:03d}" for i in range(1, num_tickets + 1)]
    
    total_tickets = sum(len(t) for t in tickets.values())
    print(f"Generated {total_tickets} tickets across {len(tickets)} repositories")
    
    for name, ticket_list in sorted(tickets.items()):
        print(f"  {name}: {len(ticket_list)} tickets")
    
    # Simulate execution
    print("\n" + "=" * 40)
    print("Phase 3: Parallel Execution")
    print("=" * 40)
    
    print("Execution with one agent per repository:")
    print("(Zero conflict risk - separate repositories)")
    
    results = []
    for priority in sorted(by_priority):
        print(f"\nPhase {priority} (parallel):")
        for repo in by_priority[priority]:
            # Simulate execution
            repo_tickets = tickets.get(repo["name"], [])
            cost = len(repo_tickets) * 0.25  # $0.25 per ticket
            status = "done" if repo["name"] != "proxym" else "partial"
            
            results.append({
                "repo": repo["name"],
                "status": status,
                "tickets": len(repo_tickets),
                "cost": cost
            })
            
            print(f"  ✓ {repo['name']}: {len(repo_tickets)} tickets, ${cost:.2f}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Execution Summary")
    print("=" * 60)
    
    total_cost = sum(r["cost"] for r in results)
    total_tickets_executed = sum(r["tickets"] for r in results)
    
    print(f"Total repositories: {len(repos)}")
    print(f"Total tickets executed: {total_tickets_executed}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Parallel phases: {len(by_priority)}")
    print(f"Conflicts: 0 (impossible with separate repos)")
    
    print("\nBenefits of workspace coordination:")
    print("  • Natural parallelism (one agent per repo)")
    print("  • Zero merge conflict risk")
    print("  • Dependency-aware scheduling")
    print("  • Unified planning across ecosystem")
    print("  • Consolidated reporting")
    
    print("\n" + "=" * 60)
    print("To run with actual workspace:")
    print("  algitex workspace analyze")
    print("  algitex workspace plan --sprints 2")
    print("  algitex workspace go --parallel")
    print("=" * 60)


if __name__ == "__main__":
    main()
