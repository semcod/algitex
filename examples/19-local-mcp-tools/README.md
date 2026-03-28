# Example 19: Local MCP Tools

Self-hosted MCP tools działające lokalnie przez Docker.

## Wymagania

- Docker i Docker Compose
- Porty: 8080, 8081, 8201 wolne

## Szybki Start

```bash
make setup    # Utwórz .env
make up       # Uruchom MCP services
make run      # Uruchom przykład
make down     # Zatrzymaj services
```

## Dostępne Usługi

| Usługa | Port | Opis |
|--------|------|------|
| code2llm-mcp | 8081 | Analiza kodu |
| vallm-mcp | 8080 | Walidacja |
| planfile-mcp | 8201 | Zarządzanie ticketami |

## Użycie

```bash
# Analiza kodu
curl -X POST http://localhost:8081/analyze \
  -d '{"path": "/workspace"}'

# Walidacja
curl -X POST http://localhost:8080/validate \
  -d '{"path": "/workspace"}'

# Tworzenie ticketu
curl -X POST http://localhost:8201/tickets \
  -d '{"title": "Fix bug", "priority": "high"}'
```
