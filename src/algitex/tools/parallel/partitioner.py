"""Task partitioning — partition tickets into non-conflicting groups."""
from typing import Dict, List, Set, Tuple

from algitex.tools.parallel.models import CodeRegion


class TaskPartitioner:
    """Partition tickets into non-conflicting groups for parallel execution."""

    def __init__(self, regions: List[CodeRegion]):
        self.regions = {r.key: r for r in regions}
        self._region_by_file = {}
        for r in regions:
            self._region_by_file.setdefault(r.file, []).append(r)

    def partition(self, tickets: List[Dict], max_agents: int = 4) -> Dict[int, List[str]]:
        """Assign tickets to agents ensuring no region overlap."""
        # Step 1: compute footprints
        footprints = self._compute_footprints(tickets)

        # Step 2: build conflict graph
        ticket_ids = [t["id"] for t in tickets]
        conflicts = self._build_conflict_graph(ticket_ids, footprints)

        # Step 3: greedy graph coloring with load balancing
        colors = self._greedy_coloring(ticket_ids, conflicts, footprints, max_agents)

        # Step 4: group by color
        return self._group_by_color(colors)

    def _compute_footprints(self, tickets: List[Dict]) -> Dict[str, Set[str]]:
        """Compute the set of code regions touched by each ticket."""
        footprints = {}
        for ticket in tickets:
            files = ticket.get("llm_hints", {}).get("files_to_modify", [])
            touched_regions = set()

            for f in files:
                for r in self._region_by_file.get(f, []):
                    touched_regions.add(r.key)
                    # Add dependencies
                    for dep in r.dependencies:
                        for r2 in self.regions.values():
                            if r2.name == dep or dep.endswith(f".{r2.name}"):
                                touched_regions.add(r2.key)
                    # Add shadow conflicts
                    for shadow in r.shadow_conflicts:
                        for r2 in self._regions_by_symbol(shadow, f):
                            touched_regions.add(r2.key)

            footprints[ticket["id"]] = touched_regions
        return footprints

    def _build_conflict_graph(
        self, ticket_ids: List[str], footprints: Dict[str, Set[str]]
    ) -> Dict[str, Set[str]]:
        """Build conflict graph where edges indicate overlapping footprints."""
        conflicts = {tid: set() for tid in ticket_ids}

        for i, t1 in enumerate(ticket_ids):
            for t2 in ticket_ids[i + 1 :]:
                if footprints[t1] & footprints[t2]:
                    conflicts[t1].add(t2)
                    conflicts[t2].add(t1)

        return conflicts

    def _greedy_coloring(
        self,
        ticket_ids: List[str],
        conflicts: Dict[str, Set[str]],
        footprints: Dict[str, Set[str]],
        max_agents: int,
    ) -> Dict[str, int]:
        """Assign tickets to agents using greedy graph coloring with load balancing."""
        colors = {}
        agent_loads = [0] * max_agents

        # Sort tickets by footprint size (largest first for better packing)
        sorted_tickets = sorted(
            ticket_ids, key=lambda tid: len(footprints[tid]), reverse=True
        )

        for tid in sorted_tickets:
            # Find least loaded agent with no conflicts
            available_agents = []
            used_colors = {colors[c] for c in conflicts[tid] if c in colors}

            for color in range(max_agents):
                if color not in used_colors:
                    available_agents.append((agent_loads[color], color))

            if available_agents:
                # Choose least loaded available agent
                _, color = min(available_agents)
            else:
                # All agents conflict, use least loaded
                color = min(range(max_agents), key=lambda i: agent_loads[i])

            colors[tid] = color
            agent_loads[color] += 1

        return colors

    def _group_by_color(self, colors: Dict[str, int]) -> Dict[int, List[str]]:
        """Group ticket IDs by their assigned color (agent)."""
        groups = {}
        for tid, color in colors.items():
            groups.setdefault(color, []).append(tid)
        return groups

    def _regions_by_symbol(self, symbol: str, file_path: str) -> List[str]:
        """Find all regions that reference a symbol."""
        matching = []
        for r in self._region_by_file.get(file_path, []):
            if symbol in r.dependencies or symbol in r.shadow_conflicts:
                matching.append(r.key)
        return matching
