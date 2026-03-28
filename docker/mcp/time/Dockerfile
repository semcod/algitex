# docker/mcp/time/Dockerfile
# Wrapper dla gotowego MCP Time server z Docker Hub
# Source: mcp/time

FROM mcp/time:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/time"
LABEL description="MCP Time server - timezone operations, scheduling"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# No auth required
