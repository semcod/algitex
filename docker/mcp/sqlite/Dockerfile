# docker/mcp/sqlite/Dockerfile
# Wrapper dla gotowego MCP SQLite server z Docker Hub
# Source: mcp/sqlite

FROM mcp/sqlite:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/sqlite"
LABEL description="MCP SQLite server - local database operations"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Mount workspace for database files
VOLUME ["/workspace"]
