# docker/mcp/filesystem/Dockerfile
# Wrapper dla gotowego MCP Filesystem server z Docker Hub
# Source: mcp/filesystem

FROM mcp/filesystem:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/filesystem"
LABEL description="MCP Filesystem server - safe file operations"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Configure allowed directories (set at runtime)
ENV ALLOW_DIRS="/workspace"

# Mount workspace as volume
VOLUME ["/workspace"]
