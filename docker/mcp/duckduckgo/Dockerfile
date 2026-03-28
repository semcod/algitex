# docker/mcp/duckduckgo/Dockerfile
# Wrapper dla gotowego MCP DuckDuckGo server z Docker Hub
# Source: mcp/duckduckgo

FROM mcp/duckduckgo:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/duckduckgo"
LABEL description="MCP DuckDuckGo server - web search without API keys"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# No auth required - DuckDuckGo is anonymous
