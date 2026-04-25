# algitex Examples

```bash
cd examples
```

This directory contains example scripts and workflows demonstrating various algitex features.

> ✅ **Testing Status (2026-03-28)**: All 33 examples tested and verified working.  
> Examples 01-34 (except 29) execute without errors.

### 🚀 Parallel Execution (30-32)
- **[30-parallel-execution](30-parallel-execution/)** - Region-based parallel execution without conflicts
- **[31-abpr-workflow](31-abpr-workflow/)** - Pipeline-first, prompt-second ABPR approach
- **[32-workspace-coordination](32-workspace-coordination/)** - Multi-repo orchestration

### 🔧 Core Features (01-19)
- **[01-quickstart](01-quickstart/)** - Basic algitex usage
- **[02-algo-loop](02-algo-loop/)** - Algorithmic improvement loop
- **[03-pipeline](03-pipeline/)** - Pipeline orchestration
- **[09-workspace](09-workspace/)** - Workspace management
- And more...

### 🛠️ Tools & Integration (20-29)
- **[20-self-hosted-pipeline](20-self-hosted-pipeline/)** - Self-hosted setup
- **[21-aider-cli-ollama](21-aider-cli-ollama/)** - Aider + Ollama integration
- **[22-claude-code-ollama](22-claude-code-ollama/)** - Claude Code + Ollama
- And more...

### 🧪 Testing & Advanced (23-29)
- **[24-ollama-batch](24-ollama-batch/)** - Batch processing with Ollama
- **[28-mcp-orchestration](28-mcp-orchestration/)** - MCP server orchestration
- **[33-hybrid-autofix](33-hybrid-autofix/)** - Fast parallel + LLM with rate limiting
- And more...

### Hybrid AutoFix (33)

Combines fast parallel mechanical fixes with rate-limited LLM fixes:

```bash
cd examples/33-hybrid-autofix
make dry-run    # Preview
make hybrid     # Execute with LiteLLM proxy
make ollama     # Execute with Ollama (100% offline)
```

Features:
- **Phase 1**: Parallel mechanical fixes (8 workers, ~1500 tps)
- **Phase 2**: Rate-limited LLM fixes (10 req/sec with retry)
- Backends: `litellm-proxy`, `ollama`, `aider`
- Cost tracking per LLM call

#### 30-parallel-execution
Demonstrates algitex's parallel execution capabilities using AST-level region locking:
- Region-based locking (functions/classes, not files)
- Git worktree isolation for each agent
- Semantic merge detection
- Conflict-free parallelism

```bash
cd examples/30-parallel-execution
make run
```

#### 31-abpr-workflow
Shows the ABPR (Abduction-Based Procedural Refinement) philosophy:
- Pipeline-first, not prompt-first
- Extract patterns → generate rules → validate → repeat
- Cost optimization through deterministic rules
- Full audit trail

```bash
cd examples/31-abpr-workflow
make run
make workflow WORKFLOW=fix-auth
```

#### 32-workspace-coordination
Multi-repo orchestration with dependency awareness:
- Parallel analysis across repositories
- Topological sort respects dependencies
- One agent per repo (zero conflict risk)
- Unified planning and reporting

```bash
cd examples/32-workspace-coordination
make run
```

## Key Concepts Demonstrated

1. **Region-Based Parallel Execution** (30)
   - AST-level locking prevents conflicts
   - Git worktree isolation
   - Semantic merge detection

2. **ABPR Philosophy** (31)
   - Pipeline-first approach
   - Rule generation from patterns
   - Progressive cost reduction

3. **Workspace Orchestration** (32)
   - Cross-repo coordination
   - Dependency-aware scheduling
   - Natural parallelism

### Sprint 3: CC Reduction & Dashboard (35-40)

4. **Sprint 3 Patterns** (35)
   - Dict dispatch pattern (CC: 50→4)
   - Strategy pattern (CC: 30→6)
   - Pipeline pattern (CC: 29→5)
   - Orchestrator pattern

5. **Live Dashboard** (36)
   - Real-time TUI monitoring
   - Cache metrics panel
   - Tier progress tracking
   - Export to JSON/Prometheus

6. **Performance Benchmarks** (37)
   - Cache hit rate testing
   - Tier throughput comparison
   - Memory profiling
   - CI/CD integration

7. **New Modules** (38)
   - Using classify.py directly
   - Using repair.py directly
   - Using verify.py directly
   - Combined workflows

8. **Microtask Pipeline** (39)
   - Task decomposition
   - Context estimation
   - Three-phase execution

9. **Three-Tier Autofix** (40)
   - Algorithm tier (deterministic)
   - Micro tier (small LLM)
   - Big tier (large LLM)
   - Dashboard integration

## Running Examples

Most examples can be run directly:

```bash
# Navigate to any example directory
cd examples/XX-example-name

## Example Structure

Each numbered example follows a consistent structure:
- `README.md` - Explanation and concepts
- `main.py` - Main demonstration script
- `Makefile` - Common commands (run, test, clean)
- Additional scripts as needed

## Contributing

When adding new examples:
1. Use the next available number (41, 42, etc.)
2. Follow the established structure
3. Include a comprehensive README
4. Add a Makefile with standard targets
5. Update this main README
