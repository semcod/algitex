# docker/mcp/audio/Dockerfile
# Wrapper dla gotowego MCP Audio server z Docker Hub
# Source: mcp/audio

FROM mcp/audio:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/audio"
LABEL description="MCP Audio server - STT, TTS, audio analysis"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Mount workspace for audio files
VOLUME ["/workspace"]
