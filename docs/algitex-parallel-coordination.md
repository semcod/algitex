# algitex — Stan, refaktoryzacja, koordynacja równoległa

> **Data:** 2026-03-28
> **Stan:** 61 plików, 12,551L, CC̄=3.3, 22 critical (fan-out), 0 cycles
> **Wzrost:** 3,048L → 12,551L (+312%) od ostatniej sesji
> **Nowe moduły:** docker MCP servers (8), batch, benchmark, cicd, ide, mcp,
> ollama, services, workspace, feedback, context, telemetry, todo_*, autofix

---

## 1. Aktualny stan — diagnostyka

### Co przybyło (nowe moduły vs ostatnia sesja)

| Moduł | LOC | Rola | Status |
|-------|-----|------|--------|
| `docker/` (8 serwerów MCP) | 2,313L | proxym, vallm, code2llm, planfile, aider | Gotowe Docker images |
| `tools/benchmark.py` | 461L | Benchmark modeli LLM na zadaniach | Nowy |
| `tools/mcp.py` | 448L | MCP client/server framework | Nowy |
| `tools/ide.py` | 430L | IDE integration (VSCode, Cursor) | Nowy |
| `tools/services.py` | 413L | Service discovery + health | Nowy |
| `tools/cicd.py` | 405L | GitHub Actions / GitLab CI generation | Nowy |
| `tools/config.py` | 386L | Zaawansowana konfiguracja | Nowy |
| `tools/ollama.py` | 383L | Ollama model management | Nowy |
| `tools/batch.py` | 364L | Batch processing z rate limiting | Nowy |
| `tools/todo_runner.py` | 363L | Task execution (local + Docker) | Nowy |
| `tools/workspace.py` | 338L | Multi-repo workspace | Nowy |
| `tools/autofix/` | 450L | Autofix backends (aider, ollama, proxym) | Nowy |
| `tools/feedback.py` | 252L | Retry/replan/escalate | Nowy |
| `tools/context.py` | 206L | RAG context builder | Nowy |
| `tools/telemetry.py` | 152L | Cost/token tracking | Nowy |
| `cli/` (split) | 648L | Modularny CLI (7 submodułów) | Refaktor |

### Metryki zdrowia

```
CC̄ = 3.3        ← stabilne (cel: ≤2.3)
critical = 22    ← głównie fan-out (nie CC)
cycles = 0       ← czysto
dups = 2         ← do zbadania
max-CC = 14      ← benchmark.py (OK, <15)
evolution: NEXT[0] = no refactoring needed
```

### Top 5 hotspotów (fan-out)

| Hotspot | Fan | Problem | Fix |
|---------|-----|---------|-----|
| `Project.status` | 18 | Agreguje 18 źródeł danych | Split na `_health()`, `_tickets()`, `_budget()`, `_algo()` |
| `call_stdio` | 17 | JSON-RPC + timeout + retry | Extract `_send_request()`, `_read_response()` |
| `BatchProcessor.process` | 17 | 17-stage pipeline | Extract `_prepare()`, `_execute()`, `_collect()` |
| `DockerToolManager.get_capabilities` | 16 | Dispatch na 4 transporty | Strategy pattern per transport |
| `Project.__init__` | 16 | Inicjalizuje 16 komponentów | Lazy init + registry pattern |

---

## 2. Refaktoryzacja — 5 zadań dla LLM

### Task 1: Split `Project.status` (fan=18 → fan≤6)

```python
# PRZED: Project.status() robi 18 rzeczy
def status(self):
    health = self.analyze()
    tickets = self.tickets.list()
    budget = self.proxy.budget()
    algo = self.loop.report()
    docker = self.docker_mgr.list_running()
    # ... 13 więcej

# PO: 4 sub-metody + agregacja
def status(self):
    return {
        "health": self._status_health(),      # fan=4
        "tickets": self._status_tickets(),    # fan=3
        "infra": self._status_infra(),        # fan=5
        "algo": self._status_algo(),          # fan=4
    }

def _status_health(self):
    return {"cc": self.analyze().cc, "criticals": ..., "vallm": ...}

def _status_tickets(self):
    return {"open": ..., "sprint": ..., "gates": ...}

def _status_infra(self):
    return {"docker": self.docker_mgr.list_running(), "models": ..., "cost": ...}

def _status_algo(self):
    return {"rules": ..., "coverage": ..., "savings": ...}
```

**Effort:** 1h | **Impact:** fan 18→6, CC bez zmian

---

### Task 2: Split `BatchProcessor.process` (fan=17 → fan≤6)

```python
# PRZED: process() ma 17 stages inline
def process(self, items):
    # validate, filter, rate-limit, group, execute, retry, collect,
    # aggregate, report, save, notify...

# PO: 3-stage pipeline
def process(self, items):
    prepared = self._prepare(items)     # validate, filter, group
    results = self._execute(prepared)   # rate-limit, execute, retry
    return self._collect(results)       # aggregate, report, save
```

**Effort:** 2h | **Impact:** fan 17→6

---

### Task 3: Extract `call_stdio` transport logic

```python
# PRZED: call_stdio robi send + read + parse + error handling + retry (fan=17)

# PO: StdioTransport class
class StdioTransport:
    def send(self, process, request: dict) -> dict:
        raw = self._serialize(request)
        self._write(process.stdin, raw)
        response = self._read_with_timeout(process.stdout)
        return self._parse(response)

    def _serialize(self, request): ...
    def _write(self, stdin, data): ...
    def _read_with_timeout(self, stdout, timeout=30): ...
    def _parse(self, raw): ...
```

**Effort:** 1.5h | **Impact:** fan 17→5, wyłonienie reusable transport

---

### Task 4: Lazy init `Project.__init__` (fan=16 → fan≤4)

```python
# PRZED: __init__ inicjalizuje 16 komponentów od razu
def __init__(self, path, config):
    self.analyzer = Analyzer(path)
    self.tickets = Tickets(path)
    self.proxy = Proxy(config)
    self.docker_mgr = DockerToolManager(config)
    # ... 12 więcej

# PO: lazy properties
def __init__(self, path, config):
    self._path = path
    self._config = config
    self._components = {}

@property
def analyzer(self):
    if "analyzer" not in self._components:
        self._components["analyzer"] = Analyzer(self._path)
    return self._components["analyzer"]

@property
def docker_mgr(self):
    if "docker" not in self._components:
        self._components["docker"] = DockerToolManager(self._config)
    return self._components["docker"]
```

**Effort:** 1.5h | **Impact:** fan 16→4, szybszy startup

---

### Task 5: Deduplikacja todo_* (4 moduły, ~1091L)

```
todo_parser.py     206L — parsuje TODO pliki
todo_executor.py   240L — wykonuje tasks przez Docker MCP
todo_runner.py     363L — wykonuje tasks z local fallback
todo_actions.py    200L — dispatch na narzędzia
todo_local.py      282L — lokalna implementacja
```

**Problem:** `todo_executor` i `todo_runner` robią to samo z różnymi backendami.

**Fix:** Merge do `todo/runner.py` + `todo/parser.py` + `todo/actions.py` (~600L, -490L).

**Effort:** 3h | **Impact:** -490L, czysta odpowiedzialność

---

## 3. GŁÓWNY TEMAT: Koordynacja równoległa zadań LLM

### Problem

Kiedy `algitex go --parallel 4` uruchamia 4 agentów (aider-mcp / claude-code)
na tym samym repo, każdy agent modyfikuje pliki. Jeśli dwa agenty edytują
ten sam plik — merge conflict. Jeśli edytują różne pliki, które importują
ten sam moduł — semantic conflict.

### Stan wiedzy (marzec 2026)

| Podejście | Kto | Mechanizm | Wady |
|-----------|-----|-----------|------|
| **Git worktrees** | Codex CLI | Osobny worktree per agent | Merge na końcu — konflikty |
| **CodeCRDT** | arxiv 2510.18893 | CRDT + observation-driven | 5-10% semantic conflicts |
| **Fan-out/Fan-in** | Azure Agent Patterns | Niezależne agenty + agregacja | Wymaga disjoint tasks |
| **Lockfile** | klasyczny | Mutex per plik | Zbyt gruboziarniste |

### Rozwiązanie algitex: **Region-Based Parallel Execution**

Łączymy 3 podejścia:

1. **AST-level region locking** — nie lockujemy plików, lockujemy *funkcje/klasy*
2. **Git worktree isolation** — każdy agent ma swoją kopię roboczą
3. **Semantic merge** — `code2llm` analizuje diff pod kątem konfliktów przed merge

```
┌─────────────────────────────────────────────────────────────┐
│  algitex parallel orchestrator                              │
│                                                             │
│  1. Analizuj codebase → map.toon (AST regions)             │
│  2. Podziel tickety na disjoint regions                     │
│  3. Utwórz git worktree per agent                           │
│  4. Przydziel tickety → agenty (region-aware)               │
│  5. Uruchom agenty równolegle                               │
│  6. Waliduj każdy worktree (vallm)                          │
│  7. Merge: fast-forward jeśli disjoint, 3-way jeśli overlap │
│  8. Final validation na merged result                       │
└─────────────────────────────────────────────────────────────┘
```

### Implementacja: `tools/parallel.py` (~350L)

```python
"""Parallel task coordination for algitex — region-based conflict-free execution."""
import subprocess
import json
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Models ───────────────────────────────────────────

class RegionType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    BLOCK = "block"       # top-level statements

@dataclass
class CodeRegion:
    """An AST-level lockable region within a file."""
    file: str
    name: str             # e.g. "Project.status" or "parse_token"
    type: RegionType
    start_line: int
    end_line: int
    dependencies: list = field(default_factory=list)  # regions this one imports/calls

    @property
    def key(self) -> str:
        return f"{self.file}::{self.name}"

@dataclass
class TaskAssignment:
    """A ticket assigned to a specific agent with locked regions."""
    ticket_id: str
    agent_id: str
    worktree: str
    regions: list         # CodeRegion list — locked exclusively
    status: str = "pending"  # pending | running | done | conflict

@dataclass
class MergeResult:
    """Result of merging agent worktrees back to main."""
    agent_id: str
    ticket_id: str
    status: str           # clean | conflict | semantic_conflict
    files_changed: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)


# ─── Region Extractor ─────────────────────────────────

class RegionExtractor:
    """Extract lockable AST regions from Python files using map.toon."""

    def __init__(self, project_path: str):
        self.root = Path(project_path)

    def extract_all(self) -> list:
        """Parse map.toon to get all function/class regions with line ranges."""
        toon_path = self.root / "map_toon.yaml"
        if not toon_path.exists():
            # Fallback: run code2llm
            subprocess.run(
                ["code2llm", str(self.root), "-f", "map"],
                capture_output=True,
            )

        # Parse map.toon D: section for function/class definitions
        regions = []
        for py_file in self.root.rglob("*.py"):
            regions.extend(self._extract_from_file(py_file))
        return regions

    def _extract_from_file(self, path: Path) -> list:
        """Use AST to extract function/class regions with line numbers."""
        import ast
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            return []

        regions = []
        rel_path = str(path.relative_to(self.root))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                regions.append(CodeRegion(
                    file=rel_path,
                    name=node.name,
                    type=RegionType.FUNCTION,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    dependencies=self._find_calls(node),
                ))
            elif isinstance(node, ast.ClassDef):
                regions.append(CodeRegion(
                    file=rel_path,
                    name=node.name,
                    type=RegionType.CLASS,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    dependencies=self._find_calls(node),
                ))
        return regions

    def _find_calls(self, node) -> list:
        """Find function/method calls within a node."""
        import ast
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return calls


# ─── Task Partitioner ─────────────────────────────────

class TaskPartitioner:
    """Partition tickets into non-conflicting groups for parallel execution."""

    def __init__(self, regions: list):
        self.regions = {r.key: r for r in regions}
        self._region_by_file = {}
        for r in regions:
            self._region_by_file.setdefault(r.file, []).append(r)

    def partition(self, tickets: list, max_agents: int = 4) -> list:
        """Assign tickets to agents ensuring no region overlap.

        Algorithm:
        1. For each ticket, compute its "region footprint" (files + functions)
        2. Build conflict graph: tickets overlap if they touch same regions
        3. Graph-color with max_agents colors → assignments
        4. Same color = same agent (sequential within agent, parallel across)
        """
        # Step 1: compute footprints
        footprints = {}
        for ticket in tickets:
            files = ticket.get("llm_hints", {}).get("files_to_modify", [])
            touched_regions = set()
            for f in files:
                for r in self._region_by_file.get(f, []):
                    touched_regions.add(r.key)
                    # Also add dependencies (transitive conflict)
                    for dep in r.dependencies:
                        for r2 in self.regions.values():
                            if r2.name == dep:
                                touched_regions.add(r2.key)
            footprints[ticket["id"]] = touched_regions

        # Step 2: build conflict graph
        ticket_ids = [t["id"] for t in tickets]
        conflicts = {tid: set() for tid in ticket_ids}
        for i, t1 in enumerate(ticket_ids):
            for t2 in ticket_ids[i+1:]:
                if footprints[t1] & footprints[t2]:  # overlapping regions
                    conflicts[t1].add(t2)
                    conflicts[t2].add(t1)

        # Step 3: greedy graph coloring
        colors = {}
        for tid in ticket_ids:
            used = {colors[c] for c in conflicts[tid] if c in colors}
            for color in range(max_agents):
                if color not in used:
                    colors[tid] = color
                    break
            else:
                colors[tid] = 0  # fallback: sequential on agent 0

        # Step 4: group by color → agent assignments
        groups = {}
        for tid, color in colors.items():
            groups.setdefault(color, []).append(tid)

        return groups  # {agent_idx: [ticket_ids]}


# ─── Parallel Executor ────────────────────────────────

class ParallelExecutor:
    """Execute tickets in parallel using git worktrees + region locking."""

    def __init__(self, project_path: str, max_agents: int = 4):
        self.root = Path(project_path)
        self.max_agents = max_agents
        self.worktrees_dir = self.root / ".algitex" / "worktrees"
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, tickets: list, tool: str = "aider-mcp") -> list:
        """Full parallel execution pipeline.

        1. Extract AST regions
        2. Partition tickets by region overlap
        3. Create git worktrees
        4. Run agents in parallel
        5. Validate each worktree
        6. Merge results
        """
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
            cwd=self.root, capture_output=True,
        )
        # Create worktree
        subprocess.run(
            ["git", "worktree", "add", wt_path, branch],
            cwd=self.root, capture_output=True,
        )
        return wt_path

    def _run_agent(self, agent_idx, worktree, tickets, tool):
        """Run an agent sequentially on its assigned tickets."""
        from algitex.workflows import Pipeline

        results = []
        for ticket in tickets:
            pipeline = Pipeline(worktree, config=None)
            result = pipeline.execute(ticket=ticket, tool=tool)
            results.append({
                "ticket_id": ticket["id"],
                "status": result.get("status", "unknown"),
            })

        return {
            "agent": agent_idx,
            "worktree": worktree,
            "results": results,
        }

    def _merge_all(self, agent_results: list) -> list:
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

            # Try merge
            merge = subprocess.run(
                ["git", "merge", "--no-ff", agent_branch, "-m",
                 f"algitex: merge agent-{result['agent']} results"],
                cwd=self.root, capture_output=True, text=True,
            )

            if merge.returncode == 0:
                merge_results.append(MergeResult(
                    agent_id=str(result["agent"]),
                    ticket_id=",".join(r["ticket_id"] for r in result["results"]),
                    status="clean",
                ))
            else:
                # Conflict — try semantic resolution
                resolution = self._resolve_conflict(agent_branch)
                merge_results.append(resolution)

        return merge_results

    def _resolve_conflict(self, branch: str) -> MergeResult:
        """Attempt semantic conflict resolution using code2llm analysis."""
        # 1. Abort current merge
        subprocess.run(["git", "merge", "--abort"], cwd=self.root, capture_output=True)

        # 2. Get conflicting files
        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", branch],
            cwd=self.root, capture_output=True, text=True,
        )
        conflicting_files = diff.stdout.strip().split("\n")

        # 3. For each file: check if changes are in different regions
        resolvable = True
        for f in conflicting_files:
            if not self._changes_are_disjoint(f, branch):
                resolvable = False
                break

        if resolvable:
            # Cherry-pick individual changes (region-safe)
            subprocess.run(
                ["git", "merge", "-X", "theirs", branch],
                cwd=self.root, capture_output=True,
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
        # Get line ranges changed in HEAD vs branch
        diff_main = subprocess.run(
            ["git", "diff", "-U0", f"{branch}...HEAD", "--", file],
            cwd=self.root, capture_output=True, text=True,
        )
        diff_branch = subprocess.run(
            ["git", "diff", "-U0", f"HEAD...{branch}", "--", file],
            cwd=self.root, capture_output=True, text=True,
        )

        main_ranges = self._parse_diff_ranges(diff_main.stdout)
        branch_ranges = self._parse_diff_ranges(diff_branch.stdout)

        # Check for overlap
        for m_start, m_end in main_ranges:
            for b_start, b_end in branch_ranges:
                if m_start <= b_end and b_start <= m_end:
                    return False
        return True

    def _parse_diff_ranges(self, diff_output: str) -> list:
        """Extract line ranges from unified diff."""
        import re
        ranges = []
        for match in re.finditer(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', diff_output):
            start = int(match.group(3))
            count = int(match.group(4) or 1)
            ranges.append((start, start + count - 1))
        return ranges

    def _cleanup_worktrees(self):
        """Remove all agent worktrees and branches."""
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=self.root, capture_output=True,
        )
        import shutil
        if self.worktrees_dir.exists():
            shutil.rmtree(self.worktrees_dir)
```

---

## 4. CLI integration

```python
# src/algitex/cli/parallel.py

@click.command("parallel")
@click.argument("path", default=".")
@click.option("--agents", "-n", default=4, help="Number of parallel agents")
@click.option("--tool", "-t", default="aider-mcp", help="Docker tool to use")
@click.option("--dry-run", is_flag=True, help="Show partition plan without executing")
def parallel(path, agents, tool, dry_run):
    """Execute tickets in parallel with conflict-free coordination."""
    from algitex.tools.parallel import ParallelExecutor, RegionExtractor, TaskPartitioner
    from algitex.tools.tickets import Tickets

    tickets_mgr = Tickets(path)
    open_tickets = tickets_mgr.list(status="open")

    if not open_tickets:
        click.echo("No open tickets to execute.")
        return

    # Show partition plan
    extractor = RegionExtractor(path)
    regions = extractor.extract_all()
    partitioner = TaskPartitioner(regions)
    groups = partitioner.partition(
        [t.to_dict() for t in open_tickets],
        max_agents=agents,
    )

    click.echo(f"\n  Partition plan ({len(open_tickets)} tickets → {len(groups)} agents):\n")
    for agent_idx, ticket_ids in groups.items():
        click.echo(f"  Agent {agent_idx}: {', '.join(ticket_ids)}")

    if dry_run:
        return

    click.echo(f"\n  Executing with {len(groups)} parallel agents ({tool})...\n")
    executor = ParallelExecutor(path, max_agents=agents)
    results = executor.execute([t.to_dict() for t in open_tickets], tool=tool)

    for r in results:
        icon = "✓" if r.status == "clean" else "✗" if r.status == "semantic_conflict" else "!"
        click.echo(f"  {icon} Agent {r.agent_id}: {r.status} ({', '.join(r.files_changed or [])})")
```

---

## 5. Przykłady użycia

### `examples/parallel_refactoring.py`

```python
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
    print(f"CC̄ after parallel refactoring: {p.status()['health']['cc']}")


if __name__ == "__main__":
    main()
```

### `examples/abpr_pipeline.py`

```python
"""Example: ABPR-style pipeline (Abduction-Based Procedural Refinement).

Instead of: "fix this bug" (prompt-first)
We do: analyze → localize → generate rule → validate → repeat (pipeline-first)

This is the core algitex philosophy: pipeline-first, prompt-second.
"""
from algitex import Project, Loop, Workflow

def main():
    p = Project("./my-app")
    loop = Loop("./my-app")

    # Stage 1: Execute — collect traces from LLM interactions
    loop.discover()

    # Stage 2: Build trace — structural analysis (not imagined state)
    health = p.analyze()
    print(f"CC̄={health.cc}, criticals={health.criticals}")

    # Stage 3: Find conflict — pattern extraction
    patterns = loop.extract(min_frequency=3)
    print(f"Found {len(patterns)} recurring patterns")

    # Stage 4: Apply rule — local fix, not global rewrite
    for pattern in patterns:
        rules = loop.generate_rules(pattern)
        for rule in rules:
            print(f"  Generated rule: {rule.name} (confidence: {rule.confidence})")

    # Stage 5: Route — deterministic if possible, LLM if not
    for request in get_incoming_requests():
        result = loop.route(request)
        if result.used_rule:
            print(f"  Handled by rule: {result.rule_name} (no LLM cost)")
        else:
            print(f"  Handled by LLM: {result.model} (${result.cost})")

    # Stage 6: Optimize — report savings
    report = loop.report()
    print(f"Rules cover {report.rule_coverage}% of requests")
    print(f"Cost savings: ${report.cost_saved}")


if __name__ == "__main__":
    main()
```

### `examples/parallel_multi_tool.py`

```python
"""Example: Parallel execution with different tools per ticket.

Some tickets are best handled by aider (code edits),
others by ollama (local, cheap), others by Claude Code (complex).
algitex assigns the right tool per ticket based on complexity.
"""
from algitex import Project
from algitex.tools.parallel import ParallelExecutor

def main():
    p = Project("./my-app")

    tickets = [
        {
            "id": "PLF-010",
            "title": "Fix import order",
            "priority": "low",
            "llm_hints": {
                "model_tier": "cheap",
                "files_to_modify": ["src/utils.py"],
            },
        },
        {
            "id": "PLF-011",
            "title": "Refactor auth middleware (CC=25)",
            "priority": "high",
            "llm_hints": {
                "model_tier": "premium",
                "files_to_modify": ["src/auth/middleware.py"],
            },
        },
        {
            "id": "PLF-012",
            "title": "Add input validation",
            "priority": "normal",
            "llm_hints": {
                "model_tier": "balanced",
                "files_to_modify": ["src/api/handlers.py"],
            },
        },
        {
            "id": "PLF-013",
            "title": "Update error messages",
            "priority": "low",
            "llm_hints": {
                "model_tier": "cheap",
                "files_to_modify": ["src/api/errors.py"],
            },
        },
    ]

    # All 4 tickets touch different files → all can run in parallel
    executor = ParallelExecutor("./my-app", max_agents=4)
    results = executor.execute(tickets)

    # Tool selection per agent based on model_tier:
    # Agent 0 (PLF-010): ollama/qwen2.5-coder:7b (cheap, local)
    # Agent 1 (PLF-011): claude-sonnet-4 (premium, complex task)
    # Agent 2 (PLF-012): gemini-2.5-pro (balanced)
    # Agent 3 (PLF-013): ollama/qwen2.5-coder:7b (cheap, local)

    for r in results:
        print(f"  {r.status}: {r.ticket_id}")


if __name__ == "__main__":
    main()
```

### `examples/workspace_parallel.py`

```python
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
        print(f"  {name}: CC̄={health['cc']}, criticals={health['criticals']}")

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
```

### `examples/todo_pipeline.md`

```markdown
# Example: Fix job queue deadlocks (pipeline-first)

## 1. Analyze current state
```propact:shell
code2llm ./src/jobs/queue.py --toon --json > queue.toon
```

## 2. Reproduce test failure
```propact:shell
pytest tests/jobs/queue_test.py --run-flaky --maxfail=3
```

## 3. Localize root cause (LLM as heuristic)
```propact:llm
{
  "model": "balanced",
  "messages": [
    {
      "role": "system",
      "content": "From queue.toon find minimal deadlock cause. Return JSON with error type and location."
    }
  ]
}
```

## 4. Generate fix (LLM generates rule, not rewrite)
```propact:docker
tool: aider-mcp
action: aider_ai_code
input:
  prompt: "Based on the localized cause, add minimal fix: timeout/retry/lock"
  relative_editable_files: ["src/jobs/queue.py"]
```

## 5. Validate
```propact:shell
vallm file ./src/jobs/queue.py --level 3
pytest tests/jobs/queue_test.py
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 6. If failed → retry with escalated model
```propact:shell
if [ "$?" != "0" ]; then
    algitex algo feedback --ticket QJ-2026-05 --retry
fi
```
```

---

## 6. Impact na codebase

| Zmiana | Pliki | LOC | CC̄ | Effort |
|--------|-------|-----|-----|--------|
| `tools/parallel.py` | +1 | ~350L | 3.0 | 6h |
| `cli/parallel.py` | +1 | ~40L | 2.0 | 1h |
| Split `Project.status` | refactor | 0 | -0.1 | 1h |
| Split `BatchProcessor.process` | refactor | 0 | -0.1 | 2h |
| Extract `StdioTransport` | refactor | 0 | -0.1 | 1.5h |
| Lazy init `Project.__init__` | refactor | 0 | -0.1 | 1.5h |
| Merge todo_* | refactor | -490L | 0 | 3h |
| `examples/` (5 plików) | +5 | ~250L | n/a | 2h |
| **Total** | +7, refactor 5 | +150L netto | CC̄→3.0 | **18h** |

### Rekomendowana kolejność

1. **parallel.py** (6h) — największa dźwignia, odblokuje `algitex go --parallel`
2. **Split fan-out hotspotów** (6h) — 4 zadania, każde niezależne (mogą iść równolegle!)
3. **Merge todo_*** (3h) — cleanup, -490L
4. **Examples** (2h) — dokumentacja przez przykłady
5. **CLI parallel** (1h) — expose to user
