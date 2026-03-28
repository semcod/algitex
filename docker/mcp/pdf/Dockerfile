# docker/mcp/pdf/Dockerfile
# Wrapper dla gotowego MCP PDF server z Docker Hub
# Source: mcp/pdf

FROM mcp/pdf:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/pdf"
LABEL description="MCP PDF server - parsing, text extraction, OCR"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Mount workspace for PDF files
VOLUME ["/workspace"]
