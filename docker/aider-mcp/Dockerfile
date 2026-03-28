# aider-mcp-server - MCP-compatible Aider integration for Algitex
# Multi-protocol support: stdio (MCP), SSE (MCP), and REST API
# Uses FastMCP SDK for standardized tool interfaces

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install aider and MCP SDK with FastMCP
RUN pip install --no-cache-dir \
    aider-chat>=0.60.0 \
    "mcp[fastmcp]>=1.0.0" \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    pydantic>=2.0.0 \
    httpx>=0.27.0

# Copy MCP server implementation
COPY aider_mcp_server.py /app/

# Environment configuration
ENV TRANSPORT=stdio
ENV PORT=3000
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=stdio

# Expose port for REST/SSE mode
EXPOSE 3000

# Run as non-root
RUN useradd -m -u 1000 aider && chown -R aider:aider /app
USER aider

# Default: MCP stdio mode
CMD ["python", "-u", "aider_mcp_server.py"]
