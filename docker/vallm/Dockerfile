# vallm-mcp - Validation tool with MCP support
# Multi-level validation: static analysis, runtime tests, security
# Multi-protocol: MCP stdio, MCP SSE, REST API

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with MCP SDK
RUN pip install --no-cache-dir \
    "mcp[fastmcp]>=1.0.0" \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    pydantic>=2.0.0 \
    pyyaml>=6.0 \
    radon>=6.0 \
    bandit>=1.7 \
    pylint>=3.0 \
    mypy>=1.8 \
    ruff>=0.3.0

# Copy MCP server implementation
COPY vallm_mcp_server.py /app/
COPY vallm_server.py /app/

# Environment configuration
ENV TRANSPORT=stdio
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=stdio

# Expose port for REST/SSE mode
EXPOSE 8080

# Run as non-root
RUN useradd -m -u 1000 vallm && chown -R vallm:vallm /app
USER vallm

# Default: MCP stdio mode
CMD ["python", "-u", "vallm_mcp_server.py"]
