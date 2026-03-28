# Example 28: MCP Service Orchestration

```bash
cd examples/28-mcp-orchestration
```

This example demonstrates how to use algitex's MCP (Model Context Protocol) service orchestration capabilities to manage multiple MCP services.

## Overview

The `MCPOrchestrator` class provides:
- Dependency-aware service startup
- Health checking
- Graceful shutdown
- Log collection
- Service management (start, stop, restart)

## Usage

```python
from algitex import Project

# Initialize project
p = Project(".")

# List available services
services = p.mcp.list_services()

# Get service info
info = p.mcp.get_service_info("code2llm")

# Start all services
p.start_mcp_services()

# Check status
p.print_mcp_status()

# Stop all services
p.stop_mcp_services()
```

## Available Services

- `aider` - Aider MCP for code editing
- `code2llm` - Code analysis MCP
- `filesystem` - Filesystem access MCP
- `github` - GitHub integration MCP
- `docker` - Docker control MCP

## Running the Example

```bash
# Run the main demo
python main.py

# Start all MCP services
python -c "from algitex import Project; p = Project('.'); p.start_mcp_services()"

# Check MCP status
python -c "from algitex import Project; p = Project('.'); p.print_mcp_status()"
```

## Requirements

- algitex installed
- Node.js (for npx-based MCP servers)
- Docker (optional, for Docker MCP)
