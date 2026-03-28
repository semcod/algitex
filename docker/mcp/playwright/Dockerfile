# docker/mcp/playwright/Dockerfile
# Wrapper dla gotowego MCP Playwright server z Docker Hub
# Source: mcp/playwright

FROM mcp/playwright:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/playwright"
LABEL description="MCP Playwright server - browser automation, E2E testing"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Playwright requires Chromium/Chrome dependencies included in base image
