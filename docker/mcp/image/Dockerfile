# docker/mcp/image/Dockerfile
# Wrapper dla gotowego MCP Image server z Docker Hub
# Source: mcp/image

FROM mcp/image:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/image"
LABEL description="MCP Image server - resize, crop, caption, analyze"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Mount workspace for image files
VOLUME ["/workspace"]
