# docker/mcp/postgres/Dockerfile
# Wrapper dla gotowego MCP PostgreSQL server z Docker Hub
# Source: mcp/postgres

FROM mcp/postgres:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/postgres"
LABEL description="MCP PostgreSQL server - database operations"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Database connection (set at runtime)
ENV POSTGRES_URL=""
ENV POSTGRES_HOST=""
ENV POSTGRES_PORT="5432"
ENV POSTGRES_DB=""
ENV POSTGRES_USER=""
ENV POSTGRES_PASSWORD=""
