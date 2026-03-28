#!/usr/bin/env python3
"""Example 01: algitex in 60 seconds.

Shows the three main objects: Project, Loop, Workflow.
Works even without any tools installed — gracefully degrades.

Run:
    python examples/01_quickstart.py
"""

from algitex import Project
from algitex.tools import discover_tools


def main() -> None:
    print("=== algitex quickstart ===\n")

    # 1. Check what tools are available
    print("Installed tools:")
    tools = discover_tools()
    for name, status in tools.items():
        print(f"  {status}")

    # 2. Create a project
    p = Project(".")
    print(f"\nProject: {p.path}")

    # 3. Analyze (works offline — shows empty report if no tools)
    report = p.analyze(full=False)
    print(f"Health: Grade {report.grade}, CC̄={report.cc_avg:.1f}")
    print(f"Passed: {report.passed}")

    # 4. Plan — auto-create tickets from analysis
    plan = p.plan(sprints=1)
    print(f"\nPlan: {plan['tickets_created']} tickets created")

    # 5. Status — full dashboard
    status = p.status()
    print(f"\nTickets: {status['tickets']}")
    print(f"Algo stage: {status['algo']['stage']}")

    # 6. Add a ticket manually
    t = p.add_ticket("Learn algitex", priority="low", type="task")
    print(f"\nManual ticket: {t.id} — {t.title}")

    print("\n✅ Done! Next steps:")
    print("  algitex go                     # full pipeline")
    print("  algitex algo discover          # start collecting traces")
    print("  algitex ask 'What is CC̄?'      # quick LLM query")


if __name__ == "__main__":
    main()
