# docker/mcp/git/Dockerfile
# Wrapper dla gotowego MCP Git server z Docker Hub
# Source: mcp/git

FROM mcp/git:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/git"
LABEL description="MCP Git server - git operations, diff, log"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Mount workspace with git repos
VOLUME ["/workspace"]
