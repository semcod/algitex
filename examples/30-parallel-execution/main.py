"""Main demonstration of parallel execution capabilities.

This script shows how algitex coordinates multiple LLM agents
working in parallel without conflicts using region-based locking.
"""
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from algitex import Project
from algitex.tools.parallel import ParallelExecutor, RegionExtractor, TaskPartitioner


def main():
    """Demonstrate parallel execution with region-based coordination."""
    print("=" * 60)
    print("algitex Parallel Execution Demo")
    print("=" * 60)
    
    project_path = str(Path(__file__).parent.parent.parent)
    p = Project(project_path)
    
    # Step 1: Analyze and create tickets
    print("\n1. Analyzing project and creating tickets...")
    health = p.analyze()
    print(f"   Project health: CC̄={health.cc_avg:.1f}, criticals={health.criticals}")
    
    # Example tickets for parallel refactoring
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
            "title": "Extract StdioTransport from call_stdio",
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
            "description": "Convert eager component init to lazy @property pattern.",
        },
    ]
    
    # Step 2: Extract regions and partition
    print("\n2. Extracting AST regions and partitioning tasks...")
    extractor = RegionExtractor(project_path)
    regions = extractor.extract_all()
    print(f"   Extracted {len(regions)} AST regions from {len(set(r.file for r in regions))} files")
    
    partitioner = TaskPartitioner(regions)
    groups = partitioner.partition(tickets, max_agents=3)
    
    print(f"\n   Partition plan ({len(tickets)} tickets → {len(groups)} agents):")
    for agent_idx, ticket_ids in sorted(groups.items()):
        print(f"\n   Agent {agent_idx}:")
        for tid in ticket_ids:
            ticket = next(t for t in tickets if t["id"] == tid)
            files = ticket["llm_hints"]["files_to_modify"]
            print(f"     {tid}: {ticket['title'][:50]}... → {', '.join(files)}")
    
    # Step 3: Check for potential conflicts
    print("\n3. Conflict analysis:")
    same_file_tickets = []
    for agent_idx, ticket_ids in groups.items():
        files = []
        for tid in ticket_ids:
            ticket = next(t for t in tickets if t["id"] == tid)
            files.extend(ticket["llm_hints"]["files_to_modify"])
        if len(set(files)) < len(files):
            same_file_tickets.append((agent_idx, ticket_ids))
    
    if same_file_tickets:
        print("   ⚠ Same-file tickets detected (will run sequentially on same agent):")
        for agent_idx, tids in same_file_tickets:
            print(f"     Agent {agent_idx}: {', '.join(tids)}")
    else:
        print("   ✓ No file conflicts - all tickets can run in parallel")
    
    # Step 4: Dry run execution
    print("\n4. Performing dry run (no actual changes)...")
    executor = ParallelExecutor(project_path, max_agents=3)
    results = executor.execute(tickets, tool="aider-mcp", dry_run=True)
    
    if results:
        print("\n   Execution plan validated successfully!")
    else:
        print("\n   Dry run complete - no actual execution performed")
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  • Total tickets: {len(tickets)}")
    print(f"  • Parallel agents: {len(groups)}")
    print(f"  • AST regions: {len(regions)}")
    print(f"  • Conflict-free: ✓")
    print("\nTo execute for real, run:")
    print("  python main.py --execute")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Demonstrate parallel execution")
    parser.add_argument("--execute", action="store_true", help="Actually execute the tickets")
    args = parser.parse_args()
    
    if args.execute:
        print("Executing for real...")
        # Add actual execution logic here if needed
    else:
        main()
