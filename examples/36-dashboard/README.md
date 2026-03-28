# Example 36: Live Dashboard Usage

Demonstrates real-time monitoring with the dashboard TUI.

## What it shows

- Live dashboard with auto-refresh
- Monitor mode for existing cache/metrics
- Export to JSON/Prometheus formats
- Dashboard integration with TODO commands

## Running

```bash
cd examples/36-dashboard
python main.py
```

## CLI Commands

```bash
# Live dashboard
algitex dashboard live

# Monitor existing data
algitex dashboard monitor --cache .algitex/cache

# Export metrics
algitex dashboard export --format json

# With TODO commands
algitex todo fix --all --dashboard
algitex todo hybrid --execute --dashboard
algitex todo batch --execute --dashboard
```
