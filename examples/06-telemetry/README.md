# Telemetry Examples

```bash
cd examples/06-telemetry
```

This example demonstrates how to use the telemetry module to track costs and performance in algitex pipelines.

## Features Demonstrated

- Basic telemetry tracking with spans
- Context manager usage for automatic timing
- Multi-model cost comparison
- Budget tracking and alerts
- Langfuse integration (optional)

## Running the Example

```bash
# Install dependencies
pip install algitex

# Run the telemetry example
python main.py
```

## What You'll See

1. **Basic Telemetry** - Creating spans and tracking operations
2. **Context Manager** - Automatic timing with `with` statements
3. **Model Comparison** - Cost analysis across different LLM models
4. **Budget Tracking** - Monitoring spending against limits
5. **Langfuse Push** - Optional integration for visualization

## Key Takeaways

- Telemetry provides visibility into LLM costs and usage
- Different models have vastly different cost profiles
- Budget tracking prevents overspending
- Context managers make timing operations easy

## Configuration

To enable Langfuse integration:

```bash
export LANGFUSE_DATABASE_URL="postgresql://..."
```

The telemetry data will be saved to `.algitex/telemetry/` automatically.
