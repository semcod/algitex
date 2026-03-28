# docker/mcp/slack/Dockerfile
# Wrapper dla gotowego MCP Slack server z Docker Hub
# Source: mcp/slack

FROM mcp/slack:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/slack"
LABEL description="MCP Slack server - notifications, messaging, channels"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Slack credentials (set at runtime)
ENV SLACK_TOKEN=""
ENV SLACK_CHANNEL=""
