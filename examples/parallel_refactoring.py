"""Example: Parallel refactoring of 4 independent hotspots.

algitex partitions tickets by AST regions, ensuring each agent
works on non-overlapping code. No merge conflicts.
"""
from algitex import Project
from algitex.tools.parallel import ParallelExecutor

def main():
    p = Project("./my-app")

    # 1. Analyze — generates tickets from hotspots
    p.analyze()
    tickets = p.tickets.from_analysis(p.analyze())

    # Example tickets (from evolution.toon):
    # PLF-001: Split Project.status (fan=18)     → project/__init__.py
    # PLF-002: Split BatchProcessor.process       → tools/batch.py
    # PLF-003: Extract StdioTransport             → tools/docker_transport.py
    # PLF-004: Lazy init Project.__init__          → project/__init__.py
    #
    # PLF-001 and PLF-004 touch the SAME FILE (project/__init__.py)
    # but DIFFERENT FUNCTIONS → algitex detects this and allows parallel!

    # 2. Parallel execute
    executor = ParallelExecutor("./my-app", max_agents=3)
    results = executor.execute(tickets, tool="aider-mcp")

    # Expected partition:
    # Agent 0: PLF-001 (Project.status)     — region project/__init__.py::status
    # Agent 0: PLF-004 (Project.__init__)   — region project/__init__.py::__init__
    #   ↑ Same file but disjoint regions → SAME agent (sequential within agent)
    # Agent 1: PLF-002 (BatchProcessor)     — region tools/batch.py::process
    # Agent 2: PLF-003 (StdioTransport)     — region tools/docker_transport.py::call_stdio
    #   ↑ Different files → PARALLEL agents (no conflict possible)

    # 3. Report
    for r in results:
        print(f"Agent {r.agent_id}: {r.status}")

    # 4. Final validation on merged result
    p.analyze()
    print(f"CC̄ after parallel refactoring: {p.status()['health']['cc_avg']}")


if __name__ == "__main__":
    main()
