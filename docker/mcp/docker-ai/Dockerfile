# docker/mcp/docker-ai/Dockerfile
# Wrapper dla gotowego MCP Docker-AI server z Docker Hub
# Source: mcp/docker-ai

FROM mcp/docker-ai:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/docker-ai"
LABEL description="MCP Docker-AI server - AI-powered container orchestration"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Docker socket access (mount at runtime)
ENV DOCKER_HOST="unix:///var/run/docker.sock"

VOLUME ["/var/run/docker.sock"]
