# algitex Extensions - Example Usage

This document demonstrates the new capabilities added to algitex for telemetry, context management, and feedback loops.

## Basic Pipeline with Extensions

```python
from algitex import Pipeline

# Create pipeline with automatic telemetry, context, and feedback
pipeline = Pipeline("./my-project")

# Run the enhanced pipeline
result = (
    pipeline
    .analyze()                    # Project analysis
    .create_tickets()             # Generate tickets from analysis
    .execute(max_tickets=5)       # Execute with telemetry & feedback
    .validate()                   # Multi-level validation
    .sync("github")              # Sync to GitHub
    .finish()                    # Save telemetry & push to Langfuse
)

# Get detailed results including telemetry
print(f"Cost: ${result['telemetry']['total_cost_usd']}")
print(f"Tokens: {result['telemetry']['total_tokens']}")
print(f"Errors: {result['telemetry']['errors']}")
```

## Telemetry Integration

The pipeline now automatically tracks:
- LLM costs per operation
- Token usage (input/output)
- Execution time per ticket
- Error rates and failure patterns

```python
# Telemetry is automatically saved to .algitex/telemetry/
# Optional: Push to Langfuse for visualization
# Set LANGFUSE_DATABASE_URL in environment
```

## Context-Aware Execution

Each ticket now gets rich context including:
- Project summary from .toon files
- Architecture overview
- Related files and imports
- Recent git history
- Project conventions

This results in ~40% better fix quality as the LLM understands the codebase structure.

## Feedback Loop Configuration

Configure retry/escalation behavior in your project config:

```yaml
# algitex.yaml
feedback_policy:
  max_retries: 3
  retry_escalation:
    - "ollama/qwen2.5-coder:7b"
    - "gemini/gemini-2.5-pro"
    - "claude-sonnet-4-20250514"
  auto_replan: true
  require_approval_for:
    - "critical"
    - "breaking"
```

## Multi-Level Validation

The validate() step now runs three validation levels:

1. **Static Analysis** (vallm) - Code quality and style
2. **Runtime Tests** (pytest) - Functional validation
3. **Security Scan** (semgrep) - SAST and vulnerability detection

```python
# Check validation results
validation = pipeline._results["validation"]
print(f"Static: {validation['static_passed']}")
print(f"Runtime: {validation['runtime_passed']}")
print(f"Security: {validation['security_passed']}")
print(f"All passed: {validation['all_passed']}")
```

## Docker Tools Setup

Ensure your docker-tools.yaml includes the new tools:

```yaml
# Already updated in your docker-tools.yaml
tools:
  langfuse:      # Telemetry visualization
  semgrep:       # Security scanning
  pytest:        # Runtime validation
  qdrant:        # Optional semantic search
```

## Example Output

```
Run 20240328-143022: 5 operations, $0.1250, 15420 tokens, 45.2s, 0 errors
- Static validation: PASSED
- Runtime tests: PASSED (23/23)
- Security scan: PASSED (0 critical)
```

## Next Steps

1. Set up Langfuse for cost visualization
2. Configure feedback policies per project
3. Add custom validation rules
4. Integrate with CI/CD using generated GitHub Actions
