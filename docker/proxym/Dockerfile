# proxym-mcp - LLM proxy with MCP support
# Routes requests to multiple LLM providers with budget tracking
# Multi-protocol: MCP stdio, MCP SSE, REST API

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with MCP SDK
RUN pip install --no-cache-dir \
    "mcp[fastmcp]>=1.0.0,<2" \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    pydantic>=2.0.0 \
    httpx>=0.27.0 \
    pyyaml>=6.0 \
    tiktoken>=0.7.0

# Copy MCP server implementation
COPY docker/mcp_security.py /app/
COPY docker/proxym/proxym_mcp_server.py /app/
COPY docker/proxym/proxym_server.py /app/

# Environment configuration
ENV TRANSPORT=stdio
ENV PORT=4000
ENV LOG_LEVEL=info
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=stdio

# API keys must be injected at runtime (prefer Docker secrets in production).
ENV DEFAULT_MODEL="claude-sonnet-4"
ENV ALGITEX_MCP_ALLOW_NETWORK=false
ENV ALGITEX_MCP_MAX_PROMPT_BYTES=1048576
ENV ALGITEX_MCP_MAX_OUTPUT_TOKENS=16384

# Expose port for REST/SSE mode
EXPOSE 4000

# Run as non-root
RUN useradd -m -u 1000 proxym && chown -R proxym:proxym /app
USER proxym

# Default: MCP stdio mode
CMD ["python", "-u", "proxym_mcp_server.py"]
