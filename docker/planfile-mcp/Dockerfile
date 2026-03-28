# planfile-mcp-server - Ticket management hub with MCP support
# Multi-protocol: MCP stdio, MCP SSE, REST API
# Uses FastMCP SDK for standardized tool interfaces

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies with MCP SDK
RUN pip install --no-cache-dir \
    "mcp[fastmcp]>=1.0.0" \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    pydantic>=2.0.0 \
    pyyaml>=6.0 \
    httpx>=0.27.0

# Copy server implementation
COPY planfile_mcp_server.py /app/

# Environment configuration
ENV TRANSPORT=stdio
ENV PORT=8201
ENV DATA_DIR=/data
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=stdio

# Create data directory
RUN mkdir -p /data && chmod 777 /data

# Expose port for REST/SSE mode
EXPOSE 8201

# Run as non-root
RUN useradd -m -u 1000 planfile && chown -R planfile:planfile /app /data
USER planfile

# Default: MCP stdio mode
CMD ["python", "-u", "planfile_mcp_server.py"]
