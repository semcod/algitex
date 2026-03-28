# docker/mcp/kubernetes/Dockerfile
# Wrapper dla gotowego MCP Kubernetes server z Docker Hub
# Source: mcp/kubernetes

FROM mcp/kubernetes:latest

LABEL maintainer="algitex"
LABEL org.opencontainers.image.source="https://github.com/algitex/docker/mcp/kubernetes"
LABEL description="MCP Kubernetes server - k8s pods, deployments, debugging"

# Stdio transport for MCP
ENV MCP_TRANSPORT=stdio

# Kubernetes configuration (mount kubeconfig at runtime)
ENV KUBECONFIG="/root/.kube/config"

VOLUME ["/root/.kube"]
