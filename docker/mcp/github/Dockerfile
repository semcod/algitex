# docker/mcp/github/Dockerfile
# Wrapper dla gotowego MCP GitHub server z Docker Hub
# Source: mcp/github

FROM mcp/github:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/github"
LABEL description="MCP GitHub server - repository, PR, issues automation"

# Environment variables (set at runtime)
ENV GITHUB_TOKEN=""
ENV GITHUB_PERSONAL_ACCESS_TOKEN=""

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# No additional configuration needed - using official image directly
# Run with: docker run -e GITHUB_TOKEN=xxx algitex/mcp-github
