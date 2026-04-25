# Example 14: Docker MCP - Container Management

```bash
cd examples/14-docker-mcp
```

Demonstruje użycie docker-mcp przez algitex Docker tool orchestration do zarządzania kontenerami.

## Możliwości

- Listowanie kontenerów
- Uruchamianie nowych kontenerów
- Build obrazów Docker
- Zatrzymywanie i usuwanie kontenerów
- Inspekcja zasobów kontenera
- Zarządzanie sieciami
- Zarządzanie wolumenami
- Logi kontenerów

## Wymagania

- Docker socket zamontowany w `/var/run/docker.sock`
- Uprawnienia do Docker

## Uruchomienie

```bash
make run
```

# Spawn docker-mcp
algitex docker spawn docker-mcp

# List containers
algitex docker call docker-mcp docker_list_containers -i '{
  "all": true
}'

# Run container
algitex docker call docker-mcp docker_run_container -i '{
  "image": "nginx:latest",
  "name": "test-nginx",
  "ports": ["8080:80"],
  "detach": true
}'

# Teardown
algitex docker teardown docker-mcp
```
