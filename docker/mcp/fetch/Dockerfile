# docker/mcp/fetch/Dockerfile
# Wrapper dla gotowego MCP Fetch server z Docker Hub
# Source: mcp/fetch

FROM mcp/fetch:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/fetch"
LABEL description="MCP Fetch server - HTTP client, web scraping"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# No auth required for basic fetch
