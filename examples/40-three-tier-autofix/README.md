# Example 40: Three-Tier Autofix System

Demonstrates the complete 3-tier autofix workflow.

## What it shows

- Tier 1: Algorithm (deterministic fixes)
- Tier 2: Micro (small LLM fixes)
- Tier 3: Big (large LLM fixes)
- Dashboard integration

## Running

```bash
cd examples/40-three-tier-autofix
python main.py


# Algorithm tier only
algitex todo fix --algo

# Micro tier only
algitex todo fix --micro

# All three tiers
algitex todo fix --all

# With dashboard
algitex todo fix --all --dashboard
```

## Tier Characteristics

| Tier | Speed | Success Rate | LLM Calls |
|------|-------|--------------|-----------|
| Algorithm | Fast (>40/s) | >95% | None |
| Micro | Medium (~3/s) | ~80% | Small |
| Big | Slow (~1/s) | ~60% | Large |
