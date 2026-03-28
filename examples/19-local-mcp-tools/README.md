# Example 19: Local MCP Tools - Self-Hosted Analysis

Demonstruje użycie lokalnych MCP tools (code2llm, vallm, planfile) zbudowanych z lokalnych Dockerfile.

## Wymagania

- Docker i Docker Compose
- Lokalne Dockerfile w `docker/`

## Uruchomienie

```bash
# Zbuduj lokalne obrazy
docker compose --profile tools build

# Uruchom narzędzia
docker compose --profile tools up -d

# Uruchom przykład
cd examples/19-local-mcp-tools
make run
```

## Dostępne Lokalne Tools

| Tool | Port | Funkcja |
|------|------|---------|
| code2llm-mcp | 8081 | Analiza kodu, generowanie .toon |
| vallm-mcp | 8080 | Walidacja kodu, scoring |
| planfile-mcp | 8201 | Zarządzanie ticketami |
| aider-mcp | 3000 | Refaktoryzacja kodu |
| proxym | 4000 | LLM gateway (opcjonalnie) |

## Architektura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ code2llm    │────→│  vallm      │────→│  planfile   │
│  (analiza)  │     │ (walidacja) │     │  (tickets)  │
└─────────────┘     └─────────────┘     └─────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                    ┌───────▼───────┐
                    │  algitex CLI  │
                    └───────────────┘
```

Wszystko działa lokalnie - żadnych zewnętrznych API!
