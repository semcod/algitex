# ABPR (Abduction-Based Procedural Refinement) Workflow

```bash
cd examples/31-abpr-workflow
```

This example demonstrates the ABPR philosophy: pipeline-first, prompt-second. Instead of "fix this bug" → LLM global rewrite, ABPR follows: analyze → localize → generate rule → validate → repeat.

## Key Concepts

- **Pipeline-First**: User designs pipelines, LLM is just one step inside
- **Rule Generation**: Extract recurring patterns into deterministic rules
- **Iterative Refinement**: Repeat until module stabilizes
- **Cost Optimization**: Rules cover common cases, LLM handles exceptions

## Files

- `main.py` - Main ABPR pipeline demonstration
- `abpr_pipeline.py` - Core ABPR implementation
- `workflows/` - Example pipeline definitions
- `Makefile` - Build and run commands

# Run with a specific workflow
make run-workflow WORKFLOW=fix-auth
```

## ABPR Stages

1. **Execute** - Collect traces from LLM interactions
2. **Trace** - Build structural analysis (not imagined state)
3. **Conflict** - Extract recurring patterns
4. **Rule** - Generate deterministic rules
5. **Validate** - Apply rules and validate
6. **Repeat** - Continue until stable

## Example Output

```
Stage 1: Discovering patterns from LLM interactions...
Stage 2: Analyzing codebase structure...
  CC̄=3.3, criticals=22
Stage 3: Extracting recurring patterns...
  Found 5 patterns
    - validate_input: 12x occurrences
    - handle_error: 8x occurrences
    - log_access: 15x occurrences
Stage 4: Generating deterministic rules...
    Rule: validate_input_rule (confidence: 85%)
    Rule: handle_error_rule (confidence: 92%)
Stage 5: Validating...
  Validation: PASSED

==================================================
Rules generated: 3
Rule coverage: 73%
Cost savings: $12.34
Iterations: 1
Module stabilized: YES
```

## Workflow Files

The `workflows/` directory contains pipeline definitions that can be run with:

```bash
algitex workflow run examples/31-abpr-workflow/workflows/fix-auth.md --ticket SEC-2026-01
```
