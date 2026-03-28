"""Example: Parallel refactoring of independent hotspots.

algitex partitions tickets by AST regions, ensuring each agent
works on non-overlapping code. No merge conflicts.

Run:
    python examples/parallel_refactoring.py

What happens:
    1. Analyzes codebase → finds 4 hotspots
    2. Detects that PLF-001 and PLF-004 touch SAME FILE but DIFFERENT FUNCTIONS
    3. Groups them on same agent (sequential) while other agents run in parallel
    4. Merges all results — zero conflicts because regions don't overlap
"""
from pathlib import Path

from algitex import Project
from algitex.tools.parallel import ParallelExecutor, RegionExtractor, TaskPartitioner


def main():
    project_path = "./my-app"
    p = Project(project_path)

    # ─── Step 1: Analyze and create tickets ───────────────

    health = p.analyze()
    print(f"Project health: CC̄={health.cc}, criticals={health.criticals}")

    # Tickets from evolution.toon hotspots:
    tickets = [
        {
            "id": "PLF-001",
            "title": "Split Project.status (fan=18)",
            "priority": "high",
            "llm_hints": {
                "model_tier": "balanced",
                "files_to_modify": ["src/algitex/project/__init__.py"],
            },
            "description": (
                "Split Project.status() into _status_health(), _status_tickets(), "
                "_status_infra(), _status_algo(). Keep return dict structure."
            ),
        },
        {
            "id": "PLF-002",
            "title": "Split BatchProcessor.process (fan=17)",
            "priority": "high",
            "llm_hints": {
                "model_tier": "balanced",
                "files_to_modify": ["src/algitex/tools/batch.py"],
            },
            "description": "Split process() into _prepare(), _execute(), _collect().",
        },
        {
            "id": "PLF-003",
            "title": "Extract StdioTransport from call_stdio (fan=17)",
            "priority": "normal",
            "llm_hints": {
                "model_tier": "cheap",
                "files_to_modify": ["src/algitex/tools/docker_transport.py"],
            },
            "description": "Extract StdioTransport class with send/read/parse methods.",
        },
        {
            "id": "PLF-004",
            "title": "Lazy init Project.__init__ (fan=16)",
            "priority": "normal",
            "llm_hints": {
                "model_tier": "cheap",
                "files_to_modify": ["src/algitex/project/__init__.py"],
            },
            "description": (
                "Convert eager component init to lazy @property pattern. "
                "Keep public API unchanged."
            ),
        },
    ]

    # ─── Step 2: Partition by AST regions ─────────────────

    extractor = RegionExtractor(project_path)
    regions = extractor.extract_all()
    print(f"\nExtracted {len(regions)} AST regions from {len(set(r.file for r in regions))} files")

    partitioner = TaskPartitioner(regions)
    groups = partitioner.partition(tickets, max_agents=3)

    print("\n" + partitioner.explain_partition(tickets, groups))

    # Expected output:
    #
    # Agent 0:
    #   PLF-001: Split Project.status → src/algitex/project/__init__.py
    #   PLF-004: Lazy init Project.__init__ → src/algitex/project/__init__.py
    #     ↑ Same file, but different functions → grouped on same agent
    #
    # Agent 1:
    #   PLF-002: Split BatchProcessor.process → src/algitex/tools/batch.py
    #     ↑ Different file → separate agent, runs in parallel
    #
    # Agent 2:
    #   PLF-003: Extract StdioTransport → src/algitex/tools/docker_transport.py
    #     ↑ Different file → separate agent, runs in parallel

    # ─── Step 3: Execute in parallel ──────────────────────

    print("\nExecuting with 3 parallel agents...")
    executor = ParallelExecutor(project_path, max_agents=3)
    results = executor.execute(tickets, tool="aider-mcp")

    # ─── Step 4: Report ───────────────────────────────────

    print("\nResults:")
    for r in results:
        icon = "✓" if r.status == "clean" else "✗"
        tids = ", ".join(r.ticket_ids) if r.ticket_ids else "?"
        print(f"  {icon} Agent {r.agent_id}: {r.status} [{tids}]")
        if r.conflicts:
            for c in r.conflicts:
                print(f"    ⚠ Conflict: {c}")

    # ─── Step 5: Final validation ─────────────────────────

    post_health = p.analyze()
    print(f"\nAfter refactoring: CC̄={post_health.cc} (was {health.cc})")


if __name__ == "__main__":
    main()
