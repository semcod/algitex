# algitex


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.64-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$11.69-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-13.4h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $11.6877 (67 commits)
- 👤 **Human dev:** ~$1345 (13.4h @ $100/h, 30min dedup)

Generated on 2026-04-20 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---



**Progressive algorithmization toolchain — from LLM to deterministic code, from proxy to tickets.**

> The only framework that automates the path from "LLM handles everything"
> to "most traffic runs deterministically, LLM only for edge cases."

```
pip install algitex
algitex init ./my-app
algitex go
```

## Why "algitex"?

The name reflects the core cycle: **analyze → plan → execute → validate → repeat**. Each iteration makes your codebase healthier and your LLM usage cheaper. The progressive algorithmization loop gradually replaces LLM calls with deterministic rules.

**Algitex = Algorithmic + Intelligence + Execution + Engine**

Semantically:
- **Alg-** → algorithms, logic, determinism
- **-i-** → intelligence layer
- **-tex** → texture / system / framework / execution layer

Algitex is the **intelligence compilation engine** that transforms LLM-driven behavior into deterministic, cost-efficient algorithmic systems. It enables progressive algorithmization from probabilistic AI reasoning to structured, deterministic logic.

### Progressive Algorithmization

The 5-stage transition from LLM to deterministic:

```
Stage 1: Discovery    → LLM performs tasks, collect traces
Stage 2: Extraction   → Identify recurring patterns
Stage 3: Rules        → Generate deterministic replacements
Stage 4: Hybrid       → Route by confidence: rules vs LLM
Stage 5: Optimization → Minimize LLM dependency, reduce costs
```

**Result:** Systems that start with LLM flexibility but evolve into efficient, deterministic engines—maintaining AI reasoning benefits with traditional software performance.

## Name alternatives considered

| Name | Why it works | Why we picked algitex |
|------|-------------|----------------------|
| **algitex** | Core concept: the continuous improvement loop | Clear, memorable, tech-neutral |
| prollama | "progressive" + llama vibes | Ties too much to one model family |
| codefact | Code + factory/fact | Sounds like a trivia app |
| algopact | Algorithm + Propact | Hard to pronounce |
| loopcode | Loop + code | Reverse reads awkward |
| prodev | Progressive + dev | Too generic, SEO nightmare |

### Layer 1: Code Quality Loop
```python
from algitex import Project

p = Project("./my-app")
p.analyze()    # code2llm + vallm + redup → health report
p.plan()       # auto-generate tickets from analysis
p.execute()    # LLM handles tasks via proxym
p.status()     # health + tickets + budget + cost ledger
```

### Layer 2: Progressive Algorithmization
```python
from algitex import Loop

loop = Loop("./my-app")
loop.discover()        # Stage 1: collect all LLM traces
loop.extract()         # Stage 2: find repeating patterns
loop.generate_rules()  # Stage 3: AI writes its own replacement
loop.route()           # Stage 4: rules vs LLM by confidence
loop.optimize()        # Stage 5: monitor, minimize LLM usage
print(loop.report())   # "42% deterministic, $12.50 saved"
```

### Layer 3: Propact Workflows
```python
from algitex import Workflow

wf = Workflow("./refactor-v1.md")
wf.execute()   # runs propact:shell, propact:rest, propact:llm blocks
```

# Core loop
algitex init ./my-app         # initialize project
algitex analyze               # health check
algitex plan --sprints 3      # generate sprint strategy + tickets
algitex go                    # full pipeline
algitex status                # dashboard

# Progressive algorithmization
algitex algo discover         # start trace collection
algitex algo extract          # find patterns in traces
algitex algo rules            # generate deterministic replacements
algitex algo report           # show % deterministic vs LLM

# Propact workflows
algitex workflow run fix.md   # execute Markdown workflow
algitex workflow validate f.md

# Tickets
algitex ticket add "Fix auth" --priority high
algitex ticket list
algitex ticket board
algitex sync                  # push to GitHub/Jira

# Quick queries
algitex ask "Explain this race condition" --tier premium
algitex tools                 # show installed tools
```

## Parallel TODO Task Processing

Execute TODO tasks from prefact analysis in parallel with automatic categorization and fix strategies:

```bash
# Verify which TODO tasks are still valid vs already fixed
algitex todo verify-prefact

# Remove outdated tasks from TODO.md
algitex todo verify-prefact --prune

# BatchFix: grupowanie i optymalizacja podobnych zadań
algitex todo batch --dry-run              # Symulacja
algitex todo batch --execute              # Wykonaj fixy
algitex todo batch --limit 10 --parallel 2  # Limit i równoległość
algitex todo batch --execute --prune      # Wykonaj + wyczyść nieaktualne
algitex todo batch --execute --no-log    # Wyłącz logowanie markdown
algitex todo batch --model qwen2.5-coder:7b  # Wybór modelu Ollama

# Auto-fix mechanical issues in parallel (dry-run)
algitex todo fix-auto --workers 8

# Actually apply fixes
algitex todo fix-auto --execute
```

## MicroTask — Atomic Tasks for Small LLMs

Pipeline for breaking down and executing atomic micro-tasks optimized for small LLMs:

```bash
# Classify tasks by complexity
algitex microtask classify

# Generate execution plan
algitex microtask plan

# Execute micro-tasks
algitex microtask run --workers 4
```

## NLP — Deterministic Refactor Helpers

Deterministic NLP-based refactoring without LLM calls:

```bash
# Fix docstrings
algitex nlp docstrings --dry-run
algitex nlp docstrings --execute

# Optimize imports
algitex nlp imports --execute

# Remove dead code
algitex nlp dead-code --execute

# Find and refactor duplicates
algitex nlp duplicates --execute
```

## Benchmark — Performance Testing

Measure and compare performance across cache, tiers, and memory usage:

```bash
# Quick benchmark (30 seconds)
algitex benchmark quick

# Test cache performance
algitex benchmark cache --entries 100 --lookups 500

# Compare tier throughput
algitex benchmark tiers

# Memory profiling for large files
algitex benchmark memory --lines 1000

# Full benchmark suite with export
algitex benchmark full --export results.json
```

## Dashboard — Real-time Monitoring

Live TUI dashboard for monitoring algitex operations:

```bash
# Live dashboard with auto-refresh
algitex dashboard live

# Dashboard for 60 seconds
algitex dashboard live --duration 60

# Monitor existing cache/metrics
algitex dashboard monitor --cache .algitex/cache --metrics .algitex/metrics.json

# Export metrics to JSON
algitex dashboard export --format json --output metrics.json --duration 60

# Export to Prometheus format
algitex dashboard export --format prometheus --output metrics.prom
```

# Live dashboard during 3-tier fix
algitex todo fix --all --dashboard

# Dashboard for hybrid autofix
algitex todo hybrid --execute --dashboard

# Dashboard for batch operations
algitex todo batch --execute --dashboard
```

### Python API

```python
from algitex.todo import verify_todos, fix_todos, benchmark_fix, compare_modes

# Verify task validity
result = verify_todos("TODO.md")
print(f"Still open: {result.still_open}, Fixed: {result.already_fixed}")

# Parallel auto-fix (mechanical tasks only)
stats = fix_todos("TODO.md", workers=8, dry_run=False)
print(f"Fixed: {stats['fixed']}, Skipped: {stats['skipped']}")

# Benchmark performance
result = benchmark_fix("TODO.md", limit=100, workers=8, mode="parallel")
result.print_report()

# Compare modes
comparison = compare_modes("TODO.md", limit=50, workers=8)
### Auto-fix Categories

| Category | Auto-fixable | Description |
|----------|--------------|-------------|
| `unused_import` | ✅ Yes | Remove unused imports (import X, from Y import X) |
| `return_type` | ✅ Yes | Add missing return type annotations |
| `fstring` | ⚠️ Partial | Convert concatenations to f-strings |
| `magic` | ✅ Yes | Suggest names for magic numbers |
| `docstring` | ✅ Yes | Rewrite verbose docstrings |
| `rename` | ✅ Yes | Improve variable names |
| `split_function` | ✅ Yes | Extract methods from large functions |
| `dependency_cycle` | ✅ Yes | Break import cycles |
| `architecture` | ✅ Yes | Reorganize module structure |
| `other` | ⚠️ Varies | Complex issues requiring reasoning |

### How Parallel Processing Works

```
┌─────────────────────────────────────────────────────────┐
│              Parallel TODO Processing                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Parse TODO.md → filter worktree duplicates          │
│  2. Categorize tasks (unused_import, return_type...)    │
│  3. Group by file (1 worker per file, zero conflicts)   │
│  4. Sort tasks bottom-up (line DESC) → preserve numbers │
│  5. Execute in ThreadPoolExecutor (8 workers default)   │
│  6. Collect results: fixed, skipped, errors             │
│                                                         │
│  Safety: Each worker touches different file.            │
│  Within file: bottom-up prevents line number shifts.    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Three Execution Paths

| Path | LLM? | Parallel? | Throughput | Use Case |
|------|------|-----------|------------|----------|
| `todo fix-auto` | ❌ No | ✅ Yes (8 workers) | ~1500 tickets/sec | Mechanical fixes: unused imports, return types |
| `todo run --tool ollama-mcp` | ✅ Yes | ❌ Sequential (queue) | ~1-10 tickets/sec | Complex fixes requiring reasoning |
| `autofix via proxy` | ✅ Yes | ⚠️ Batch | ~5-50 tickets/sec | Intelligent fixes via litellm-proxy |

**When to use which:**

**Path 1: Mechanical Fixes (`todo fix-auto`)**
- No LLM calls — pure regex/text manipulation
- 8 parallel workers, thread-safe per-file isolation
- Handles: `unused_import`, `return_type`, `fstring` (via flynt)
- Best for: bulk cleanup of 100+ simple issues

```python
from algitex.todo import fix_todos
stats = fix_todos("TODO.md", workers=8, dry_run=False)
# 2679 tasks → ~1.8 seconds total
```

**Path 2: LLM-based Fixes (`todo run`)**
- Uses Ollama/aider via Docker MCP
- Sequential execution (respects LLM rate limits)
- Handles: complex refactoring, architectural changes
- Best for: issues requiring code understanding

```bash
algitex todo run --tool ollama-mcp --limit 10
```

**Path 3: Hybrid via Proxy (`autofix`)**
- Routes through litellm-proxy with cost tracking
- Batch processing with retry logic
- Handles: smart fixes with context awareness
- Best for: production workflows with budget constraints

```python
from algitex.tools.autofix import AutoFix
autofix = AutoFix(backend="litellm-proxy", proxy_url="http://localhost:4000")
autofix.fix_all(limit=5)  # $0.12 per batch avg
```

**Path 4: Hybrid CLI (`todo hybrid`) — Fast + Parallel + LLM**
- Phase 1: Parallel mechanical fixes (no LLM)
- Phase 2: Rate-limited parallel LLM fixes
- Handles: complete TODO workflow in one command

```bash
# Dry run (preview)
algitex todo hybrid --workers 4 --rate-limit 10

# Execute with rate limiting
algitex todo hybrid --execute --backend litellm-proxy --workers 4 --rate-limit 10

# Local Ollama (100% offline)
algitex todo hybrid --execute --backend ollama --workers 2 --rate-limit 5
```

### The Missing Piece: Fast + Parallel + LLM

To achieve **szybkie + równoległe + LLM**, you need to combine `ThreadPoolExecutor` with `ProxyBackend`:

```python
from algitex.todo import HybridAutofix

# Combines parallel task distribution with LLM backend
fixer = HybridAutofix(
    backend="litellm-proxy",
    workers=4,              # Parallel workers
    rate_limit=10,          # Requests per second
    retry_attempts=3,
    timeout=30
)

# Mechanical fixes: parallel, no LLM
fixer.fix_mechanical("TODO.md")  # 1000+ tickets/sec

# Complex fixes: parallel LLM with rate limiting
fixer.fix_complex("TODO.md")     # 10-50 tickets/sec, cost-tracked
```

**Requirements for parallel LLM:**
- Rate limiting (prevent 429 errors)
- Retry logic with exponential backoff
- Cost tracking per batch
- Circuit breaker for failed requests

## The 5-Stage Progressive Algorithmization

```
Stage 1: Discovery     → LLM handles 100%, collect traces
Stage 2: Extraction    → identify hot paths + repeating patterns
Stage 3: Rules         → AI generates deterministic replacements
Stage 4: Hybrid        → confidence-based: known patterns → rules, unknown → LLM
Stage 5: Optimization  → most traffic deterministic, LLM for edge cases only
```

No existing framework automates this path. DSPy goes LLM→smaller LLM. algitex goes LLM→algorithm.

# Fix Authentication Module

Analyze current state:

```propact:shell
code2llm ./src/auth -f toon --json
```

Ask LLM for a fix plan:

```propact:rest
POST http://localhost:4000/v1/chat/completions
{"model": "balanced", "messages": [{"role": "user", "content": "Fix auth"}]}
```

Validate the result:

```propact:shell
vallm batch ./src/auth --recursive
```
```

## Planfile-Aware Proxy Headers

Every LLM request through algitex carries context:

```
X-Planfile-Ref: my-project/current/DLP-0042
X-Workflow-Ref: refactor-v1.md
X-Task-Tier: complex
X-Inject-Context: true
```

Proxym logs cost/model/latency **per ticket**. The cost ledger shows exactly what each task costs.

## Installation

```bash
pip install algitex                # core
pip install algitex[all]           # + all tools
pip install algitex[proxy]         # + proxym
pip install algitex[analysis]      # + code2llm, vallm, redup
pip install algitex[tickets]       # + planfile
pip install algitex[routing]       # + llx
```

# Quickstart — three main objects (Project, Loop, Workflow)
cd examples/01-quickstart
make run

# Progressive Algorithmization — 5-stage loop
cd examples/02-algo-loop
make run

# Composable Pipeline — fluent API
cd examples/03-pipeline
make run

# IDE Integration — generate configs for Roo Code, Cline, etc.
cd examples/04-ide-integration
make setup && make run

# Cost Tracking — per-ticket cost ledger
cd examples/05-cost-tracking
make run

# Local LLM with Ollama — 100% offline, zero API costs
cd examples/18-ollama-local
make setup && make run

# Local MCP Tools — self-hosted code analysis & validation
cd examples/19-local-mcp-tools
make up && make run

# Self-Hosted Pipeline — complete local CI/CD stack
cd examples/20-self-hosted-pipeline
make build && make up && make run

# Aider CLI + Ollama — local refactoring with prefact TODO workflow
cd examples/21-aider-cli-ollama
make setup && make run

# Claude Code + Ollama — AI assistant with local LLM
cd examples/22-claude-code-ollama
make setup && make run

# Continue.dev + Ollama — VS Code extension setup
cd examples/23-continue-dev-ollama
make setup

# Ollama Batch Processing — parallel code analysis
cd examples/24-ollama-batch
python batch_analyze.py --dir ./src

# Local Model Comparison — benchmark Ollama models
cd examples/25-local-model-comparison
make benchmark

# LiteLLM Proxy + Ollama — native algitex integration (better than aider)
cd examples/26-litellm-proxy-ollama
make setup && make proxy  # Terminal 1
make fix                  # Terminal 2

# Hybrid AutoFix — fast parallel + LLM with rate limiting
cd examples/33-hybrid-autofix
make dry-run              # Preview
make hybrid               # Execute with LiteLLM proxy
make ollama               # Execute with Ollama (100% offline)

# BatchFix — grupowanie i optymalizacja podobnych zadań
cd examples/34-batch-fix
algitex todo batch --dry-run   # Symulacja
algitex todo batch --execute   # Wykonaj fixy
```

Each example has:
- [01-quickstart/README.md](examples/01-quickstart/README.md) — Project, Loop, Workflow basics
- [02-algo-loop/README.md](examples/02-algo-loop/README.md) — Progressive algorithmization
- [03-pipeline/README.md](examples/03-pipeline/README.md) — Composable fluent API
- [04-ide-integration/README.md](examples/04-ide-integration/README.md) — IDE configs
- [05-cost-tracking/README.md](examples/05-cost-tracking/README.md) — Cost tracking
- [06-telemetry/README.md](examples/06-telemetry/README.md) — Telemetry & observability
- [07-context/README.md](examples/07-context/README.md) — Context building
- [08-feedback/README.md](examples/08-feedback/README.md) — Feedback loops
- [09-workspace/README.md](examples/09-workspace/README.md) — Workspace management
- [10-cicd/README.md](examples/10-cicd/README.md) — CI/CD pipelines
- [11-aider-mcp/README.md](examples/11-aider-mcp/README.md) — Aider MCP code refactoring
- [12-filesystem-mcp/README.md](examples/12-filesystem-mcp/README.md) — Filesystem operations
- [13-vallm/README.md](examples/13-vallm/README.md) — Vallm validation
- [14-docker-mcp/README.md](examples/14-docker-mcp/README.md) — Docker container management
- [15-github-mcp/README.md](examples/15-github-mcp/README.md) — GitHub repository operations
- [16-test-workflow/README.md](examples/16-test-workflow/README.md) — Comprehensive test pipeline
- [17-docker-workflow/README.md](examples/17-docker-workflow/README.md) — Refactoring workflow
- [18-ollama-local/README.md](examples/18-ollama-local/README.md) — Local LLM with Ollama (100% offline)
- [19-local-mcp-tools/README.md](examples/19-local-mcp-tools/README.md) — Self-hosted MCP tools (Docker)
- [20-self-hosted-pipeline/README.md](examples/20-self-hosted-pipeline/README.md) — Complete local CI/CD pipeline
- [21-aider-cli-ollama/README.md](examples/21-aider-cli-ollama/README.md) — Aider CLI + Ollama local refactoring
- [22-claude-code-ollama/README.md](examples/22-claude-code-ollama/README.md) — Claude Code + Ollama AI assistant
- [23-continue-dev-ollama/README.md](examples/23-continue-dev-ollama/README.md) — Continue.dev VS Code extension + Ollama
- [24-ollama-batch/README.md](examples/24-ollama-batch/README.md) — Parallel batch processing with Ollama
- [25-local-model-comparison/README.md](examples/25-local-model-comparison/README.md) — Benchmark Ollama models
- [26-litellm-proxy-ollama/README.md](examples/26-litellm-proxy-ollama/README.md) — LiteLLM Proxy + Ollama (native algitex)
- [28-mcp-orchestration/README.md](examples/28-mcp-orchestration/README.md) — MCP Service Orchestration
- [30-parallel-execution/README.md](examples/30-parallel-execution/README.md) — Parallel Execution with Region-Based Coordination
- [31-abpr-workflow/README.md](examples/31-abpr-workflow/README.md) — ABPR Workflow
- [32-workspace-coordination/README.md](examples/32-workspace-coordination/README.md) — Multi-Repo Workspace Coordination
- [33-hybrid-autofix/README.md](examples/33-hybrid-autofix/README.md) — Fast parallel + LLM with rate limiting
- [34-batch-fix/README.md](examples/34-batch-fix/README.md) — BatchFix: grupowanie i optymalizacja fixów
- [35-sprint3-patterns/README.md](examples/35-sprint3-patterns/README.md) — Sprint 3 CC Reduction Patterns
- [36-dashboard/README.md](examples/36-dashboard/README.md) — Live Dashboard TUI
- [37-benchmarks/README.md](examples/37-benchmarks/README.md) — Performance Benchmarks
- [38-new-modules/README.md](examples/38-new-modules/README.md) — New Module Usage
- [39-microtask-pipeline/README.md](examples/39-microtask-pipeline/README.md) — MicroTask Pipeline
- [40-three-tier-autofix/README.md](examples/40-three-tier-autofix/README.md) — Three-Tier AutoFix
- [41-god-module-splitting/README.md](examples/41-god-module-splitting/README.md) — God Module Splitting
- [42-duplicate-removal/README.md](examples/42-duplicate-removal/README.md) — Duplicate Code Removal
- [43-code-health/README.md](examples/43-code-health/README.md) — Code Health Monitoring
- [44-plugin-system/README.md](examples/44-plugin-system/README.md) — Plugin System Architecture
- `run.sh` — executable script
- `Makefile` — `make run`, `make setup`, `make clean`
- `.env.example` — configuration template (where applicable)

> ✅ **44 examples available** (2026-04-25). Examples 01-34 tested and verified working.

## Additional Documentation

- [README2.md](./README2.md) — Detailed conceptual overview of Algitex as intelligence compilation engine
- [docs/todo.md](./docs/todo.md) — TODO task processing and BatchFix
- [docs/BATCHFIX.md](./docs/BATCHFIX.md) — BatchFix: grupowanie i optymalizacja fixów
- [docs/MICROTASK.md](./docs/MICROTASK.md) — Atomic micro-tasks for small LLMs
- [docs/NLP.md](./docs/NLP.md) — Deterministic NLP refactor helpers
- [docs/NEW_FEATURES.md](./docs/NEW_FEATURES.md) — Overview of new modules and features
- [docs/autofix.md](./docs/autofix.md) — AutoFix module documentation
- [docs/REFACTORING_SUMMARY.md](./docs/REFACTORING_SUMMARY.md) — Codebase refactoring summary

## Architecture

```
src/algitex/
├── __init__.py           # Project, Loop, Workflow, Config, Pipeline
├── config.py             # Unified config (env + YAML)
├── project.py            # Main Project class (expanded)
├── cli.py                # Typer CLI backward compatibility shim
├── cli/                  # Modular CLI commands
│   ├── __init__.py       # Main app with all subcommands
│   ├── core.py           # init, analyze, plan, go, status
│   ├── ticket.py         # Ticket management
│   ├── algo.py           # Progressive algorithmization
│   ├── workflow.py       # Propact workflows
│   ├── docker.py         # Docker MCP tools
│   ├── todo.py           # TODO processing
│   ├── microtask.py      # Atomic micro-task pipeline
│   ├── nlp.py            # Deterministic NLP helpers
│   ├── metrics.py        # Metrics and observability
│   ├── benchmark.py      # Performance benchmarks
│   └── dashboard.py      # Real-time monitoring
├── algo/                 # Progressive algorithmization
│   ├── __init__.py       # Loop, TraceEntry, Pattern, Rule, LoopState
│   └── loop.py           # Re-export
├── propact/              # Markdown workflow engine
│   ├── __init__.py       # Workflow, WorkflowStep, WorkflowResult
│   └── workflow.py       # Re-export
├── todo/                 # TODO fixing system (Sprint 3: CC reduced)
│   ├── __init__.py       # Public API exports
│   ├── fixer.py          # Orchestrator (was 724L, now ~450L)
│   ├── classify.py       # Task classification (CC: 50→4)
│   ├── repair.py         # Repair strategies (CC: 30→6)
│   ├── verify.py         # Verification pipeline (CC: 29→5)
│   ├── micro.py          # Small LLM fixes
│   ├── hybrid.py         # Big LLM fixes
│   ├── tiering.py        # Task classification helpers
│   └── benchmark.py      # Performance benchmarking
├── microtask/            # Atomic tasks for small LLMs
│   ├── __init__.py       # MicroTask, TaskType, MicroTaskBatch
│   ├── classifier.py     # Task classification
│   ├── executor.py       # Three-phase execution
│   └── slicer.py         # Context extraction
├── nlp/                  # Deterministic NLP refactors
│   └── __init__.py       # DocstringShortener, DeadCodeDetector, etc.
├── tools/
│   ├── __init__.py       # Tool discovery
│   ├── proxy.py          # proxym wrapper + planfile headers
│   ├── analysis.py       # code2llm + vallm + redup
│   └── tickets.py        # planfile wrapper + cost ledger
└── workflows/
    ├── __init__.py        # Pipeline (composable steps)
    └── pipeline.py        # Re-export
```

## How it connects to the ecosystem

```
┌─────────────────────────────────────────────────────┐
│                     algitex                         │
│            (orchestration layer)                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  analyze()   plan()   execute()   algo.discover()   │
│     │          │         │            │             │
│  code2llm   planfile   proxym      trace →          │
│  vallm      tickets    llx         patterns →       │
│  redup      strategy   models      rules →          │
│                                    hybrid routing   │
│                                                     │
│  MicroTask Pipeline:                                │
│    microtask classify → atomic task decomposition   │
│    microtask plan     → execution strategy          │
│    microtask run      → three-phase execution       │
│                                                     │
│  NLP Helpers (deterministic):                       │
│    nlp docstrings     → shorten verbose docs        │
│    nlp imports        → sort and organize           │
│    nlp dead-code      → detect unused functions     │
│    nlp duplicates     → find repeated blocks        │
│                                                     │
│  run_workflow("fix.md")                             │
│     │                                               │
│  propact:shell → subprocess                         │
│  propact:rest  → httpx                              │
│  propact:llm   → proxym                             │
│  propact:mcp   → MCP tool call                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Tool Roles

| Tool | What | Install |
|------|------|---------|
| **proxym** | LLM gateway, 10 providers, routing, budget | `pip install proxym` |
| **planfile** | Sprint planning, tickets, GitHub/Jira sync | `pip install planfile` |
| **llx** | Metric-driven model selection, MCP server | `pip install llx` |
| **code2llm** | Static analysis → .toon diagnostics | `pip install code2llm` |
| **vallm** | 4-tier code validation | `pip install vallm` |
| **redup** | Duplication detection | `pip install redup` |

## License

Licensed under Apache-2.0.
## Status

_Last updated by [taskill](https://github.com/oqlos/taskill) at 2026-04-25 09:28 UTC_

| Metric | Value |
|---|---|
| HEAD | `6e56e90` |
| Coverage | — |
| Failing tests | — |
| Commits in last cycle | 50 |

> The project focused on extensive refactoring of documentation and examples, along with fixes and features enhancing the CLI interface and deep code analysis engine.

<!-- taskill:status:end -->
