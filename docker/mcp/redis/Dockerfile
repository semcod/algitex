# docker/mcp/redis/Dockerfile
# Wrapper dla gotowego MCP Redis server z Docker Hub
# Source: mcp/redis

FROM mcp/redis:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/redis"
LABEL description="MCP Redis server - key-value operations, caching"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Redis connection (set at runtime)
ENV REDIS_URL=""
ENV REDIS_HOST=""
ENV REDIS_PORT="6379"
ENV REDIS_PASSWORD=""
