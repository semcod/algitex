# Example: Using docker-mcp for Container Management

This example demonstrates how to use docker-mcp through algitex's Docker tool orchestration for managing Docker containers and images.

## Prerequisites
- Docker socket mounted at /var/run/docker.sock
- Sufficient Docker permissions

## Example 1: Listing All Containers

```propact:docker
tool: docker-mcp
action: docker_list_containers
input:
  all: true  # Include stopped containers
```

## Example 2: Running a New Container

```propact:docker
tool: docker-mcp
action: docker_run_container
input:
  image: "nginx:latest"
  name: "test-nginx"
  ports:
    - "8080:80"
  environment:
    - "NGINX_HOST=localhost"
    - "NGINX_PORT=80"
  detach: true
```

## Example 3: Building an Image

```propact:docker
tool: docker-mcp
action: docker_build_image
input:
  context_path: "/workspace"
  dockerfile_path: "/workspace/Dockerfile"
  tag: "my-app:latest"
  build_args:
    - "VERSION=1.0.0"
    - "ENV=production"
```

## Example 4: Stopping and Removing Containers

```propact:docker
tool: docker-mcp
action: docker_stop_container
input:
  container_id: "test-nginx"
  remove: true
```

## Example 5: Inspecting Container Resources

```propact:docker
tool: docker-mcp
action: docker_inspect
input:
  target: "test-nginx"
  type: "container"
```

## Example 6: Managing Container Networks

```propact:docker
tool: docker-mcp
action: docker_create_network
input:
  name: "algitex-network"
  driver: "bridge"
  subnet: "172.20.0.0/16"
```

## Example 7: Volume Management

```propact:docker
tool: docker-mcp
action: docker_create_volume
input:
  name: "algitex-data"
  driver: "local"
  labels:
    - "project=algitex"
    - "environment=dev"
```

## Example 8: Container Logs

```propact:docker
tool: docker-mcp
action: docker_logs
input:
  container: "test-nginx"
  follow: false
  tail: 100
```

## Running the Examples

To run these examples:

1. Save the workflow to a file (e.g., `docker-management.md`)
2. Execute with: `algitex workflow run docker-management.md`

## Using via CLI

```bash
# Spawn docker-mcp
algitex docker spawn docker-mcp

# List containers
algitex docker call docker-mcp docker_list_containers -i '{
  "all": true
}'

# Run a container
algitex docker call docker-mcp docker_run_container -i '{
  "image": "nginx:latest",
  "name": "test-nginx",
  "ports": ["8080:80"],
  "detach": true
}'

# Stop container
algitex docker call docker-mcp docker_stop_container -i '{
  "container_id": "test-nginx",
  "remove": true
}'

# Teardown when done
algitex docker teardown docker-mcp
```

## Integration Example: CI/CD Pipeline

```markdown
# CI/CD Pipeline with Docker

## Build application image
```propact:docker
tool: docker-mcp
action: docker_build_image
input:
  context_path: "/workspace"
  dockerfile_path: "/workspace/Dockerfile"
  tag: "my-app:${BUILD_NUMBER}"
```

## Run tests in container
```propact:docker
tool: docker-mcp
action: docker_run_container
input:
  image: "my-app:${BUILD_NUMBER}"
  command: "pytest"
  volumes:
    - "/workspace/test-results:/app/test-results"
```

## Push to registry
```propact:docker
tool: docker-mcp
action: docker_push_image
input:
  image: "my-app:${BUILD_NUMBER}"
  registry: "docker.io/myuser"
```

## Deploy to staging
```propact:docker
tool: docker-mcp
action: docker_run_container
input:
  image: "my-app:${BUILD_NUMBER}"
  name: "staging-app"
  env_file: "/workspace/.env.staging"
  networks:
    - "staging-network"
```
