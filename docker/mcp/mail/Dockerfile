# docker/mcp/mail/Dockerfile
# Wrapper dla gotowego MCP Mail server z Docker Hub
# Source: mcp/mail

FROM mcp/mail:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/mail"
LABEL description="MCP Mail server - email sending, SMTP operations"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# SMTP configuration (set at runtime)
ENV SMTP_HOST=""
ENV SMTP_PORT="587"
ENV SMTP_USER=""
ENV SMTP_PASSWORD=""
ENV SMTP_TLS="true"
