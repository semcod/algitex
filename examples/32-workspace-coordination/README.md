# Multi-Repo Workspace Coordination

```bash
cd examples/32-workspace-coordination
```

This example demonstrates algitex's ability to orchestrate analysis and fixes across multiple repositories simultaneously, with dependency-aware scheduling.

## Key Concepts

- **Cross-Repo Analysis**: Parallel analysis of multiple repositories
- **Dependency Graph**: Respect inter-repo dependencies during execution
- **One Agent Per Repo**: Natural parallelism with zero conflict risk
- **Unified Planning**: Coordinated refactoring across ecosystem

## Files

- `main.py` - Main workspace coordination demo
- `workspace_parallel.py` - Multi-repo parallel execution
- `workspace.yaml` - Workspace configuration
- `Makefile` - Build and run commands

## Workspace Configuration

The `workspace.yaml` defines:

```yaml
workspace:
  name: wronai-ecosystem
  description: "Python developer toolchain for LLM-assisted code analysis"

repos:
  - name: code2llm
    priority: 1
    role: "Static analysis → .toon diagnostics"
    
  - name: vallm
    priority: 1
    role: "LLM-generated code validator"
    
  - name: planfile
    depends_on: [code2llm, vallm]
    priority: 2
    role: "Local-first ticket management"
```

## Execution Phases

1. **Phase 1** (parallel): code2llm, vallm, redup (no deps)
2. **Phase 2** (parallel): planfile (deps: code2llm, vallm)
3. **Phase 3** (parallel): llx (deps: planfile)
4. **Phase 4** (parallel): proxym (deps: llx, planfile)
5. **Phase 5** (parallel): algitex (deps: all)

## Example Output

```
Analyzing all repositories...

  Repo              CC̄  Crit     LOC  Files
  ─────────────── ───── ───── ─────── ──────
  algitex           3.3    22   12551     61
  code2llm          4.8    52   18340    102
  vallm             3.5    12    8604     56
  ...

Planning cross-repo refactoring (2 sprints)...
  Total tickets: 47
  algitex: 12 tickets
  code2llm: 8 tickets
  ...

Executing (parallel — one agent per repo)...

  Repo            Status       Tickets   Cost
  ─────────────── ─────────── ──────── ───────
  code2llm        done              8   $2.34
  vallm           done              5   $1.67
  planfile        done              6   $2.10
  ...
```

## Benefits

- **Zero Conflict Risk**: Each agent works in separate repository
- **Dependency Awareness**: Automatic topological sort of execution
- **Parallel by Default**: Maximize parallelism while respecting deps
- **Unified View**: Single dashboard for entire ecosystem
