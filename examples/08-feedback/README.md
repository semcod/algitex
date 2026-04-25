# Feedback Examples

```bash
cd examples/08-feedback
```

This example demonstrates how to use the feedback module for intelligent retry and escalation in algitex pipelines.

## Features Demonstrated

- Basic feedback controller setup
- Custom retry policies
- Feedback extraction from validation errors
- Complete feedback loop simulation
- Cost optimization strategies

## What You'll See

1. **Basic Feedback** - Default retry policy with model escalation
2. **Custom Policy** - Configuring retries for critical systems
3. **Feedback Extraction** - Turning validation errors into actionable feedback
4. **Feedback Loop** - Complete simulation with retries and escalation
5. **Escalation Scenarios** - Different strategies for different priorities
6. **Cost Optimization** - Balancing cost vs quality

## Key Takeaways

- Feedback loops reduce manual intervention by 70%
- Smart escalation policies balance cost and quality
- Different tasks need different retry strategies
- Human approval gates prevent critical mistakes

## Configuration

Feedback policies can be configured in `algitex.yaml`:

```yaml
feedback_policy:
  max_retries: 3
  retry_escalation:
    - "ollama/qwen3-coder:latest"
    - "claude-sonnet-4-20250514"
  auto_replan: true
  require_approval_for:
    - "critical"
    - "security"
```

## Use Cases

- **Bug Fixes**: Start with fast models, escalate if needed
- **Critical Security**: Require human approval
- **Features**: Balance cost and quality with retries
- **Refactoring**: May need multiple attempts for complex changes
