# docker/mcp/security-lint/Dockerfile
# Wrapper dla gotowego MCP Security/Lint server z Docker Hub
# Source: mcp/security

FROM mcp/security:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/security-lint"
LABEL description="MCP Security-Lint server - vulnerability scanning, linting"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Mount workspace for code scanning
VOLUME ["/workspace"]
