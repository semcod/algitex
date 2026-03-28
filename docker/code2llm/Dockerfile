# code2llm-mcp - Code analysis with MCP support
# Multi-protocol: MCP stdio, MCP SSE, REST API
# Uses FastMCP SDK for standardized tool interfaces

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with MCP SDK
RUN pip install --no-cache-dir \
    "mcp[fastmcp]>=1.0.0" \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    pydantic>=2.0.0 \
    pyyaml>=6.0 \
    radon>=6.0 \
    ast-decompiler>=0.7.0

# Copy MCP server implementation
COPY code2llm_mcp_server.py /app/
COPY code2llm_server.py /app/

# Environment configuration
ENV TRANSPORT=stdio
ENV PORT=8081
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=stdio

# Expose port for REST/SSE mode
EXPOSE 8081

# Run as non-root
RUN useradd -m -u 1000 code2llm && chown -R code2llm:code2llm /app
USER code2llm

# Default: MCP stdio mode
CMD ["python", "-u", "code2llm_mcp_server.py"]
