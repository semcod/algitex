# docker/mcp/browser/Dockerfile
# Wrapper dla gotowego MCP Browser server z Docker Hub
# Source: mcp/browser

FROM mcp/browser:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/browser"
LABEL description="MCP Browser server - simple browser automation"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio
