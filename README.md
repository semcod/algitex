# algitex

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

## Three layers, one command

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

## CLI

```bash
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

## The 5-Stage Progressive Algorithmization

```
Stage 1: Discovery     → LLM handles 100%, collect traces
Stage 2: Extraction    → identify hot paths + repeating patterns
Stage 3: Rules         → AI generates deterministic replacements
Stage 4: Hybrid        → confidence-based: known patterns → rules, unknown → LLM
Stage 5: Optimization  → most traffic deterministic, LLM for edge cases only
```

No existing framework automates this path. DSPy goes LLM→smaller LLM. algitex goes LLM→algorithm.

## Propact: Markdown as Workflow

```markdown
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

## Examples

```bash
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
- `run.sh` — executable script
- `Makefile` — `make run`, `make setup`, `make clean`
- `.env.example` — configuration template (where applicable)

## Additional Documentation

- [README2.md](./README2.md) — Detailed conceptual overview of Algitex as intelligence compilation engine

## Architecture

```
src/algitex/
├── __init__.py           # Project, Loop, Workflow, Config, Pipeline
├── config.py             # Unified config (env + YAML)
├── project.py            # Main Project class (expanded)
├── cli.py                # Typer CLI (all commands)
├── algo/                 # Progressive algorithmization
│   ├── __init__.py       # Loop, TraceEntry, Pattern, Rule, LoopState
│   └── loop.py           # Re-export
├── propact/              # Markdown workflow engine
│   ├── __init__.py       # Workflow, WorkflowStep, WorkflowResult
│   └── workflow.py       # Re-export
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


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.


Licensed under Apache-2.0.

## Author

Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Tom Sapletta


Created by **Tom Sapletta** — [tom@sapletta.com](mailto:tom@sapletta.com)

Part of the [semcod](https://github.com/semcod) / [wronai](https://github.com/wronai) ecosystem.
