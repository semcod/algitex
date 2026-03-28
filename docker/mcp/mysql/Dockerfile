# docker/mcp/mysql/Dockerfile
# Wrapper dla gotowego MCP MySQL server z Docker Hub
# Source: mcp/mysql

FROM mcp/mysql:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/mysql"
LABEL description="MCP MySQL server - database operations"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Database connection (set at runtime)
ENV MYSQL_URL=""
ENV MYSQL_HOST=""
ENV MYSQL_PORT="3306"
ENV MYSQL_DATABASE=""
ENV MYSQL_USER=""
ENV MYSQL_PASSWORD=""
