"""Parallel execution — execute tickets using git worktrees with region locking."""
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple

from algitex.tools.parallel.extractor import RegionExtractor
from algitex.tools.parallel.models import MergeResult
from algitex.tools.parallel.partitioner import TaskPartitioner


class ParallelExecutor:
    """Execute tickets in parallel using git worktrees + region locking."""

    def __init__(self, project_path: str, max_agents: int = 4):
        self.root = Path(project_path)
        self.max_agents = max_agents
        self.worktrees_dir = self.root / ".algitex" / "worktrees"
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, tickets: List[Dict], tool: str = "aider-mcp") -> List[MergeResult]:
        """Full parallel execution pipeline."""
        # 1. Extract regions
        extractor = RegionExtractor(str(self.root))
        regions = extractor.extract_all()

        # 2. Partition
        partitioner = TaskPartitioner(regions)
        groups = partitioner.partition(tickets, self.max_agents)

        # 3. Create worktrees + execute in parallel
        results = []
        with ThreadPoolExecutor(max_workers=len(groups)) as pool:
            futures = {}
            for agent_idx, ticket_ids in groups.items():
                agent_tickets = [t for t in tickets if t["id"] in ticket_ids]
                wt = self._create_worktree(agent_idx)
                future = pool.submit(
                    self._run_agent, agent_idx, wt, agent_tickets, tool
                )
                futures[future] = agent_idx

            for future in as_completed(futures):
                agent_idx = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "agent": agent_idx,
                        "status": "error",
                        "error": str(e),
                    })

        # 4. Merge all worktrees back
        merge_results = self._merge_all(results)

        # 5. Cleanup worktrees
        self._cleanup_worktrees()

        return merge_results

    def _create_worktree(self, agent_idx: int) -> str:
        """Create a git worktree for an agent."""
        branch = f"algitex-agent-{agent_idx}"
        wt_path = str(self.worktrees_dir / f"agent-{agent_idx}")

        # Create branch from current HEAD
        subprocess.run(
            ["git", "branch", "-f", branch, "HEAD"],
            cwd=self.root, capture_output=True, check=True
        )

        # Create worktree
        subprocess.run(
            ["git", "worktree", "add", wt_path, branch],
            cwd=self.root, capture_output=True, check=True
        )

        return wt_path

    def _run_agent(self, agent_idx: int, worktree: str, tickets: List[Dict], tool: str) -> Dict:
        """Run an agent sequentially on its assigned tickets."""
        from algitex.workflows import Pipeline

        results = []
        for ticket in tickets:
            try:
                pipeline = Pipeline(worktree, config=None)
                result = pipeline.execute(ticket=ticket, tool=tool)
                results.append({
                    "ticket_id": ticket["id"],
                    "status": result.get("status", "unknown"),
                })
            except Exception as e:
                results.append({
                    "ticket_id": ticket["id"],
                    "status": "error",
                    "error": str(e),
                })

        return {
            "agent": agent_idx,
            "worktree": worktree,
            "results": results,
        }

    def _merge_all(self, agent_results: List[Dict]) -> List[MergeResult]:
        """Merge all agent worktrees back to main branch."""
        merge_results = []

        for result in agent_results:
            if result.get("status") == "error":
                merge_results.append(MergeResult(
                    agent_id=str(result["agent"]),
                    ticket_id="",
                    status="error",
                    conflicts=[result.get("error", "")],
                ))
                continue

            worktree = result["worktree"]
            agent_branch = f"algitex-agent-{result['agent']}"

            # Check for line drift before merge
            if self._detect_line_drift(agent_branch):
                # Rebase to detect drift
                subprocess.run(
                    ["git", "rebase", "HEAD", agent_branch],
                    cwd=self.root, capture_output=True
                )

            # Try merge
            merge = subprocess.run(
                ["git", "merge", "--no-ff", agent_branch, "-m",
                 f"algitex: merge agent-{result['agent']} results"],
                cwd=self.root, capture_output=True, text=True
            )

            if merge.returncode == 0:
                merge_results.append(MergeResult(
                    agent_id=str(result["agent"]),
                    ticket_id=",".join(r["ticket_id"] for r in result["results"]),
                    status="clean",
                ))
            else:
                # Conflict - try semantic resolution
                resolution = self._resolve_conflict(agent_branch)
                merge_results.append(resolution)

        return merge_results

    def _detect_line_drift(self, branch: str) -> bool:
        """Detect if line ranges have shifted due to other changes."""
        # Compare current signatures with stored ones
        extractor = RegionExtractor(str(self.root))
        current_regions = extractor.extract_all()

        # This is simplified - in practice, we'd store original signatures
        # and compare them to detect drift
        return False  # Placeholder

    def _resolve_conflict(self, branch: str) -> MergeResult:
        """Attempt semantic conflict resolution."""
        # 1. Abort current merge
        subprocess.run(["git", "merge", "--abort"], cwd=self.root, capture_output=True)

        # 2. Get conflicting files
        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", branch],
            cwd=self.root, capture_output=True, text=True
        )
        conflicting_files = [f for f in diff.stdout.strip().split('\n') if f]

        # 3. Check if changes are in different regions
        resolvable = True
        for f in conflicting_files:
            if not self._changes_are_disjoint(f, branch):
                resolvable = False
                break

        if resolvable:
            # Cherry-pick changes
            subprocess.run(
                ["git", "merge", "-X", "theirs", branch],
                cwd=self.root, capture_output=True
            )
            return MergeResult(
                agent_id=branch,
                ticket_id="",
                status="clean",
                files_changed=conflicting_files,
            )
        else:
            return MergeResult(
                agent_id=branch,
                ticket_id="",
                status="semantic_conflict",
                conflicts=conflicting_files,
            )

    def _changes_are_disjoint(self, file: str, branch: str) -> bool:
        """Check if changes in a file are in non-overlapping line ranges."""
        # Get line ranges changed in both branches
        diff_main = subprocess.run(
            ["git", "diff", "-U0", f"{branch}...HEAD", "--", file],
            cwd=self.root, capture_output=True, text=True
        )
        diff_branch = subprocess.run(
            ["git", "diff", "-U0", f"HEAD...{branch}", "--", file],
            cwd=self.root, capture_output=True, text=True
        )

        main_ranges = self._parse_diff_ranges(diff_main.stdout)
        branch_ranges = self._parse_diff_ranges(diff_branch.stdout)

        # Check for overlap
        for m_start, m_end in main_ranges:
            for b_start, b_end in branch_ranges:
                if m_start <= b_end and b_start <= m_end:
                    return False
        return True

    def _parse_diff_ranges(self, diff_output: str) -> List[Tuple[int, int]]:
        """Extract line ranges from unified diff."""
        ranges = []
        for match in re.finditer(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', diff_output):
            start = int(match.group(3))
            count = int(match.group(4) or 1)
            ranges.append((start, start + count - 1))
        return ranges

    def _cleanup_worktrees(self):
        """Remove all agent worktrees and branches."""
        try:
            subprocess.run(
                ["git", "worktree", "prune"],
                cwd=self.root, capture_output=True
            )

            # Remove worktree directories
            if self.worktrees_dir.exists():
                shutil.rmtree(self.worktrees_dir)

            # Remove agent branches
            for i in range(self.max_agents):
                branch = f"algitex-agent-{i}"
                subprocess.run(
                    ["git", "branch", "-D", branch],
                    cwd=self.root, capture_output=True
                )
        except Exception:
            pass  # Best effort cleanup
