# docker/mcp/video/Dockerfile
# Wrapper dla gotowego MCP Video server z Docker Hub
# Source: mcp/video

FROM mcp/video:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/video"
LABEL description="MCP Video server - processing, slicing, caption, summarization"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Mount workspace for video files
VOLUME ["/workspace"]
