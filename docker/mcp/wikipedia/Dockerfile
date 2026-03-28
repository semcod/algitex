# docker/mcp/wikipedia/Dockerfile
# Wrapper dla gotowego MCP Wikipedia server z Docker Hub
# Source: mcp/wikipedia-mcp

FROM mcp/wikipedia-mcp:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/wikipedia"
LABEL description="MCP Wikipedia server - knowledge fetching"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# No auth required for Wikipedia
