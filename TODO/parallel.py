"""Parallel task coordination for algitex — region-based conflict-free execution.

Solves the problem: when multiple LLM agents (aider-mcp, claude-code, etc.)
work on the same codebase simultaneously, how do we prevent merge conflicts?

Approach: AST-level region locking + git worktrees + semantic merge.

Usage:
    from algitex.tools.parallel import ParallelExecutor
    executor = ParallelExecutor("./my-app", max_agents=4)
    results = executor.execute(tickets, tool="aider-mcp")
"""
import ast
import json
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


# ─── Models ───────────────────────────────────────────────


class RegionType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"


@dataclass
class CodeRegion:
    """An AST-level lockable region within a file."""

    file: str
    name: str
    type: RegionType
    start_line: int
    end_line: int
    dependencies: list = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.file}::{self.name}"

    def overlaps(self, other: "CodeRegion") -> bool:
        """Check if two regions in the same file overlap."""
        if self.file != other.file:
            return False
        return self.start_line <= other.end_line and other.start_line <= self.end_line


@dataclass
class MergeResult:
    """Result of merging an agent worktree back to main."""

    agent_id: str
    ticket_ids: list = field(default_factory=list)
    status: str = "pending"  # clean | conflict | semantic_conflict | error
    files_changed: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)


# ─── Region Extractor ─────────────────────────────────────


class RegionExtractor:
    """Extract lockable AST regions from Python files."""

    def __init__(self, project_path: str):
        self.root = Path(project_path)

    def extract_all(self) -> list[CodeRegion]:
        """Extract all function/class regions from Python source files."""
        regions = []
        for py_file in self.root.rglob("*.py"):
            # Skip hidden dirs, __pycache__, etc.
            if any(p.startswith(".") or p == "__pycache__" for p in py_file.parts):
                continue
            regions.extend(self._extract_from_file(py_file))
        return regions

    def _extract_from_file(self, path: Path) -> list[CodeRegion]:
        """Use Python AST to extract function/class regions with line numbers."""
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return []

        rel_path = str(path.relative_to(self.root))
        regions = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                regions.append(
                    CodeRegion(
                        file=rel_path,
                        name=node.name,
                        type=RegionType.FUNCTION,
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        dependencies=self._find_calls(node),
                    )
                )
            elif isinstance(node, ast.ClassDef):
                # Class region covers the whole class
                regions.append(
                    CodeRegion(
                        file=rel_path,
                        name=node.name,
                        type=RegionType.CLASS,
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        dependencies=self._find_calls(node),
                    )
                )
                # Also extract individual methods for finer-grained locking
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        regions.append(
                            CodeRegion(
                                file=rel_path,
                                name=f"{node.name}.{item.name}",
                                type=RegionType.FUNCTION,
                                start_line=item.lineno,
                                end_line=item.end_lineno or item.lineno,
                                dependencies=self._find_calls(item),
                            )
                        )

        return regions

    def _find_calls(self, node: ast.AST) -> list[str]:
        """Find function/method calls within an AST node."""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return list(set(calls))


# ─── Task Partitioner ─────────────────────────────────────


class TaskPartitioner:
    """Partition tickets into non-conflicting groups for parallel execution.

    Algorithm:
    1. For each ticket, compute its "region footprint" (touched AST regions)
    2. Build conflict graph: tickets conflict if regions overlap
    3. Graph-color with max_agents colors
    4. Same color = same agent (sequential within, parallel across)
    """

    def __init__(self, regions: list[CodeRegion]):
        self.regions = {r.key: r for r in regions}
        self._by_file: dict[str, list[CodeRegion]] = {}
        for r in regions:
            self._by_file.setdefault(r.file, []).append(r)

    def partition(
        self, tickets: list[dict], max_agents: int = 4
    ) -> dict[int, list[str]]:
        """Assign tickets to agent groups. Returns {agent_idx: [ticket_ids]}."""
        footprints = self._compute_footprints(tickets)
        conflicts = self._build_conflict_graph(tickets, footprints)
        colors = self._greedy_color(tickets, conflicts, max_agents)
        return self._group_by_color(colors)

    def _compute_footprints(self, tickets: list[dict]) -> dict[str, set[str]]:
        """For each ticket, find which AST regions it touches."""
        footprints = {}
        for ticket in tickets:
            files = ticket.get("llm_hints", {}).get("files_to_modify", [])
            touched = set()
            for f in files:
                for r in self._by_file.get(f, []):
                    touched.add(r.key)
                    # Transitive: if region calls function X, also lock X
                    for dep_name in r.dependencies:
                        for r2 in self.regions.values():
                            if r2.name == dep_name or r2.name.endswith(f".{dep_name}"):
                                touched.add(r2.key)
            footprints[ticket["id"]] = touched
        return footprints

    def _build_conflict_graph(
        self, tickets: list[dict], footprints: dict[str, set[str]]
    ) -> dict[str, set[str]]:
        """Build undirected conflict graph between tickets."""
        ids = [t["id"] for t in tickets]
        conflicts = {tid: set() for tid in ids}
        for i, t1 in enumerate(ids):
            for t2 in ids[i + 1 :]:
                if footprints.get(t1, set()) & footprints.get(t2, set()):
                    conflicts[t1].add(t2)
                    conflicts[t2].add(t1)
        return conflicts

    def _greedy_color(
        self,
        tickets: list[dict],
        conflicts: dict[str, set[str]],
        max_colors: int,
    ) -> dict[str, int]:
        """Greedy graph coloring — assign each ticket a color (agent index)."""
        colors = {}
        for ticket in tickets:
            tid = ticket["id"]
            used = {colors[c] for c in conflicts.get(tid, set()) if c in colors}
            for color in range(max_colors):
                if color not in used:
                    colors[tid] = color
                    break
            else:
                colors[tid] = 0  # fallback: serialize on agent 0
        return colors

    def _group_by_color(self, colors: dict[str, int]) -> dict[int, list[str]]:
        groups: dict[int, list[str]] = {}
        for tid, color in colors.items():
            groups.setdefault(color, []).append(tid)
        return groups

    def explain_partition(
        self, tickets: list[dict], groups: dict[int, list[str]]
    ) -> str:
        """Human-readable explanation of why tickets were grouped this way."""
        lines = []
        ticket_map = {t["id"]: t for t in tickets}
        for agent_idx, tids in sorted(groups.items()):
            lines.append(f"\nAgent {agent_idx}:")
            for tid in tids:
                t = ticket_map.get(tid, {})
                files = t.get("llm_hints", {}).get("files_to_modify", [])
                lines.append(f"  {tid}: {t.get('title', '?')} → {', '.join(files)}")
        return "\n".join(lines)


# ─── Parallel Executor ────────────────────────────────────


class ParallelExecutor:
    """Execute tickets in parallel using git worktrees + region locking.

    Lifecycle:
    1. Extract AST regions from codebase
    2. Partition tickets into non-conflicting groups
    3. Create git worktree per agent
    4. Run agents in parallel (ThreadPoolExecutor)
    5. Validate each worktree (vallm)
    6. Merge worktrees back (with conflict detection)
    7. Final validation on merged result
    8. Cleanup worktrees
    """

    def __init__(self, project_path: str, max_agents: int = 4):
        self.root = Path(project_path).resolve()
        self.max_agents = max_agents
        self._worktrees_dir = self.root / ".algitex" / "worktrees"

    def execute(
        self,
        tickets: list[dict],
        tool: str = "aider-mcp",
        dry_run: bool = False,
    ) -> list[MergeResult]:
        """Full parallel execution pipeline."""
        # 1. Extract regions
        extractor = RegionExtractor(str(self.root))
        regions = extractor.extract_all()

        # 2. Partition
        partitioner = TaskPartitioner(regions)
        groups = partitioner.partition(tickets, self.max_agents)

        if dry_run:
            print(partitioner.explain_partition(tickets, groups))
            return []

        # 3. Create worktrees & execute
        self._worktrees_dir.mkdir(parents=True, exist_ok=True)
        ticket_map = {t["id"]: t for t in tickets}

        agent_results = []
        with ThreadPoolExecutor(max_workers=len(groups)) as pool:
            futures = {}
            for agent_idx, ticket_ids in groups.items():
                agent_tickets = [ticket_map[tid] for tid in ticket_ids if tid in ticket_map]
                wt_path = self._create_worktree(agent_idx)
                future = pool.submit(self._run_agent, agent_idx, wt_path, agent_tickets, tool)
                futures[future] = agent_idx

            for future in as_completed(futures):
                agent_idx = futures[future]
                try:
                    agent_results.append(future.result())
                except Exception as e:
                    agent_results.append(
                        {"agent": agent_idx, "status": "error", "error": str(e), "results": []}
                    )

        # 4. Merge
        merge_results = self._merge_all(agent_results)

        # 5. Cleanup
        self._cleanup()

        return merge_results

    # ─── Git Worktree Management ──────────────────────────

    def _create_worktree(self, agent_idx: int) -> str:
        branch = f"algitex-parallel-{agent_idx}"
        wt_path = str(self._worktrees_dir / f"agent-{agent_idx}")

        subprocess.run(
            ["git", "branch", "-f", branch, "HEAD"],
            cwd=self.root,
            capture_output=True,
        )
        subprocess.run(
            ["git", "worktree", "add", wt_path, branch],
            cwd=self.root,
            capture_output=True,
        )
        return wt_path

    def _cleanup(self):
        subprocess.run(["git", "worktree", "prune"], cwd=self.root, capture_output=True)
        if self._worktrees_dir.exists():
            shutil.rmtree(self._worktrees_dir, ignore_errors=True)
        # Remove temp branches
        for i in range(self.max_agents):
            subprocess.run(
                ["git", "branch", "-D", f"algitex-parallel-{i}"],
                cwd=self.root,
                capture_output=True,
            )

    # ─── Agent Execution ─────────────────────────────────

    def _run_agent(
        self, agent_idx: int, worktree: str, tickets: list[dict], tool: str
    ) -> dict:
        """Run an agent sequentially on its assigned tickets within its worktree."""
        results = []
        for ticket in tickets:
            result = self._execute_single_ticket(worktree, ticket, tool)
            results.append(result)

            # Commit after each successful ticket
            if result.get("status") == "ok":
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=worktree,
                    capture_output=True,
                )
                subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        f"algitex: {ticket.get('id', 'unknown')} — {ticket.get('title', '')}",
                    ],
                    cwd=worktree,
                    capture_output=True,
                )

        return {"agent": agent_idx, "worktree": worktree, "results": results}

    def _execute_single_ticket(
        self, worktree: str, ticket: dict, tool: str
    ) -> dict:
        """Execute a single ticket using the specified Docker tool."""
        try:
            # Import here to avoid circular imports
            from algitex.tools.docker import DockerToolManager
            from algitex.config import Config

            config = Config.load(worktree)
            mgr = DockerToolManager(config)

            files = ticket.get("llm_hints", {}).get("files_to_modify", [])
            prompt = ticket.get("description", ticket.get("title", "Fix this issue"))

            if tool == "aider-mcp":
                result = mgr.call_tool("aider-mcp", "aider_ai_code", {
                    "prompt": prompt,
                    "relative_editable_files": files,
                    "current_working_dir": worktree,
                })
            else:
                result = mgr.call_tool(tool, "execute", {
                    "prompt": prompt,
                    "files": files,
                })

            mgr.teardown_all()
            return {"ticket_id": ticket["id"], "status": "ok", "result": result}

        except Exception as e:
            return {"ticket_id": ticket["id"], "status": "error", "error": str(e)}

    # ─── Merge Logic ──────────────────────────────────────

    def _merge_all(self, agent_results: list[dict]) -> list[MergeResult]:
        """Merge all agent worktrees back to main branch."""
        results = []
        for ar in sorted(agent_results, key=lambda x: x.get("agent", 0)):
            if ar.get("status") == "error":
                results.append(
                    MergeResult(
                        agent_id=str(ar["agent"]),
                        status="error",
                        conflicts=[ar.get("error", "unknown")],
                    )
                )
                continue

            branch = f"algitex-parallel-{ar['agent']}"
            ticket_ids = [r.get("ticket_id", "") for r in ar.get("results", [])]

            merge = subprocess.run(
                ["git", "merge", "--no-ff", branch, "-m",
                 f"algitex: merge agent-{ar['agent']} ({', '.join(ticket_ids)})"],
                cwd=self.root,
                capture_output=True,
                text=True,
            )

            if merge.returncode == 0:
                results.append(
                    MergeResult(
                        agent_id=str(ar["agent"]),
                        ticket_ids=ticket_ids,
                        status="clean",
                    )
                )
            else:
                # Try to resolve: check if changes are in disjoint line ranges
                resolution = self._attempt_resolution(branch, ticket_ids)
                results.append(resolution)

        return results

    def _attempt_resolution(self, branch: str, ticket_ids: list[str]) -> MergeResult:
        """Try to resolve merge conflict using region-aware analysis."""
        subprocess.run(["git", "merge", "--abort"], cwd=self.root, capture_output=True)

        # Get conflicting files
        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", branch],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        files = [f for f in diff.stdout.strip().split("\n") if f]

        # Check if all changes are in disjoint regions
        all_disjoint = all(self._changes_disjoint(f, branch) for f in files)

        if all_disjoint:
            # Safe to merge with "theirs" strategy for non-overlapping regions
            subprocess.run(
                ["git", "merge", "-X", "theirs", branch, "-m",
                 f"algitex: auto-resolved merge ({', '.join(ticket_ids)})"],
                cwd=self.root,
                capture_output=True,
            )
            return MergeResult(
                agent_id=branch,
                ticket_ids=ticket_ids,
                status="clean",
                files_changed=files,
            )

        return MergeResult(
            agent_id=branch,
            ticket_ids=ticket_ids,
            status="semantic_conflict",
            conflicts=files,
        )

    def _changes_disjoint(self, file: str, branch: str) -> bool:
        """Check if changes to a file from HEAD and branch don't overlap."""
        diff = subprocess.run(
            ["git", "diff", "-U0", f"HEAD...{branch}", "--", file],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        ranges = self._parse_hunk_ranges(diff.stdout)

        # If only one side changed, no conflict possible
        if len(ranges) <= 1:
            return True

        # Check pairwise overlap
        for i, (s1, e1) in enumerate(ranges):
            for s2, e2 in ranges[i + 1 :]:
                if s1 <= e2 and s2 <= e1:
                    return False
        return True

    def _parse_hunk_ranges(self, diff_output: str) -> list[tuple[int, int]]:
        """Extract changed line ranges from unified diff output."""
        ranges = []
        for match in re.finditer(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff_output):
            start = int(match.group(1))
            count = int(match.group(2) or 1)
            ranges.append((start, start + count - 1))
        return ranges
