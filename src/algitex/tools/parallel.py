"""Parallel task coordination for algitex — region-based conflict-free execution."""
import subprocess
import json
import hashlib
import ast
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set, Tuple, Optional


# ─── Models ───────────────────────────────────────────

class RegionType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    BLOCK = "block"  # top-level statements


@dataclass
class CodeRegion:
    """An AST-level lockable region within a file."""
    file: str
    name: str  # e.g. "Project.status" or "parse_token"
    type: RegionType
    start_line: int
    end_line: int
    signature_hash: str  # Hash of signature to detect line drift
    dependencies: List[str] = field(default_factory=list)  # regions this one imports/calls
    shadow_conflicts: List[str] = field(default_factory=list)  # shared imports/constants

    @property
    def key(self) -> str:
        return f"{self.file}::{self.name}"

    def compute_signature_hash(self, source: str) -> str:
        """Compute hash of function/class signature to track changes."""
        lines = source.split('\n')[self.start_line-1:self.end_line]
        signature = '\n'.join(lines[:min(5, len(lines))])  # First 5 lines as signature
        return hashlib.sha256(signature.encode()).hexdigest()[:16]


@dataclass
class TaskAssignment:
    """A ticket assigned to a specific agent with locked regions."""
    ticket_id: str
    agent_id: str
    worktree: str
    regions: List[CodeRegion]  # Locked exclusively
    status: str = "pending"  # pending | running | done | conflict


@dataclass
class MergeResult:
    """Result of merging agent worktrees back to main."""
    agent_id: str
    ticket_id: str
    status: str  # clean | conflict | semantic_conflict | shadow_conflict
    files_changed: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    line_drift_detected: bool = False


# ─── Region Extractor ─────────────────────────────────

class RegionExtractor:
    """Extract lockable AST regions from Python files using map.toon."""

    def __init__(self, project_path: str):
        self.root = Path(project_path)
        self._signature_cache: Dict[str, str] = {}

    def extract_all(self) -> List[CodeRegion]:
        """Parse map.toon to get all function/class regions with line ranges."""
        regions = []
        
        # Try to read from map.toon if it exists
        toon_path = self.root / "map.toon"
        if toon_path.exists():
            regions.extend(self._extract_from_toon(toon_path))
        
        # Always extract from AST for accuracy
        for py_file in self.root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            regions.extend(self._extract_from_file(py_file))
        
        # Detect shadow conflicts (shared imports/constants)
        self._detect_shadow_conflicts(regions)
        
        return regions

    def _should_skip_file(self, path: Path) -> bool:
        """Skip generated, test, or vendor files."""
        parts = path.parts
        skip_dirs = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', 
                    'build', 'dist', '.tox', '.pytest_cache'}
        return any(d in skip_dirs for d in parts) or path.name.startswith('test_')

    def _extract_from_toon(self, toon_path: Path) -> List[CodeRegion]:
        """Extract regions from existing map.toon file."""
        regions = []
        try:
            import yaml
            with open(toon_path) as f:
                data = yaml.safe_load(f)
            
            # Extract from D: section (definitions)
            for item in data.get('D', []):
                if item.get('type') in ['function', 'class']:
                    regions.append(CodeRegion(
                        file=item['file'],
                        name=item['name'],
                        type=RegionType(item['type']),
                        start_line=item.get('start', 0),
                        end_line=item.get('end', 0),
                        signature_hash=item.get('hash', ''),
                        dependencies=item.get('deps', [])
            ))
        except Exception:
            pass  # Fallback to AST extraction
        
        return regions

    def _extract_from_file(self, path: Path) -> List[CodeRegion]:
        """Use AST to extract function/class regions with line numbers."""
        try:
            source = path.read_text()
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return []

        regions = []
        rel_path = str(path.relative_to(self.root))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                region = CodeRegion(
                    file=rel_path,
                    name=node.name,
                    type=RegionType.FUNCTION,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    signature_hash="",
                    dependencies=self._find_calls(node)
                )
                region.signature_hash = region.compute_signature_hash(source)
                regions.append(region)
                
            elif isinstance(node, ast.ClassDef):
                region = CodeRegion(
                    file=rel_path,
                    name=node.name,
                    type=RegionType.CLASS,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    signature_hash="",
                    dependencies=self._find_calls(node)
                )
                region.signature_hash = region.compute_signature_hash(source)
                regions.append(region)

        return regions

    def _find_calls(self, node) -> List[str]:
        """Find function/method calls within a node."""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # Handle method calls and attribute access
                    calls.append(child.func.attr)
                    # Also capture the full attribute chain
                    if isinstance(child.func.value, ast.Name):
                        calls.append(f"{child.func.value.id}.{child.func.attr}")
        return list(set(calls))  # Deduplicate

    def _detect_shadow_conflicts(self, regions: List[CodeRegion]):
        """Detect shared imports/constants that could cause shadow conflicts."""
        # Group regions by file
        regions_by_file = {}
        for r in regions:
            regions_by_file.setdefault(r.file, []).append(r)
        
        # For each file, find shared imports and module-level constants
        for file_path, file_regions in regions_by_file.items():
            full_path = self.root / file_path
            try:
                source = full_path.read_text()
                tree = ast.parse(source)
                
                # Find module-level imports and constants
                shared_symbols = set()
                for node in tree.body:
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        for alias in node.names:
                            shared_symbols.add(alias.name)
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if target.id.isupper():  # Constants
                                    shared_symbols.add(target.id)
                
                # Add shadow conflicts for regions that use shared symbols
                for region in file_regions:
                    region_deps = set(region.dependencies)
                    shadow_symbols = region_deps & shared_symbols
                    region.shadow_conflicts = list(shadow_symbols)
                    
            except Exception:
                continue


# ─── Task Partitioner ─────────────────────────────────

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

        # Step 2: build conflict graph
        ticket_ids = [t["id"] for t in tickets]
        conflicts = {tid: set() for tid in ticket_ids}
        
        for i, t1 in enumerate(ticket_ids):
            for t2 in ticket_ids[i+1:]:
                if footprints[t1] & footprints[t2]:
                    conflicts[t1].add(t2)
                    conflicts[t2].add(t1)

        # Step 3: greedy graph coloring with load balancing
        colors = {}
        agent_loads = [0] * max_agents
        
        # Sort tickets by footprint size (largest first for better packing)
        sorted_tickets = sorted(ticket_ids, key=lambda tid: len(footprints[tid]), reverse=True)
        
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

        # Step 4: group by color
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


# ─── Parallel Executor ────────────────────────────────

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
