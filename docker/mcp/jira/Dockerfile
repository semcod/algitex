# docker/mcp/jira/Dockerfile
# Wrapper dla gotowego MCP Jira server z Docker Hub
# Source: mcp/jira

FROM mcp/jira:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/jira"
LABEL description="MCP Jira server - ticket management, sync with planfile"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Jira credentials (set at runtime)
ENV JIRA_URL=""
ENV JIRA_USERNAME=""
ENV JIRA_API_TOKEN=""
ENV JIRA_PROJECT=""
