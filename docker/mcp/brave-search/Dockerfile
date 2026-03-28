# docker/mcp/brave-search/Dockerfile
# Wrapper dla gotowego MCP Brave Search server z Docker Hub
# Source: mcp/brave-search

FROM mcp/brave-search:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/brave-search"
LABEL description="MCP Brave Search server - web, image, news search"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# API key (set at runtime)
ENV BRAVE_API_KEY=""
