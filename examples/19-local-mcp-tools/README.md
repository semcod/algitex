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

## Użycie z przykładowym kodem

```bash
# Analiza kodu z błędami
curl -X POST http://localhost:8081/analyze \
  -d '{"path": "/workspace", "files": ["buggy_code.py"]}'

# Walidacja kodu
curl -X POST http://localhost:8080/validate \
  -d '{"path": "/workspace", "files": ["buggy_code.py"]}'

# Utwórz ticket z wykrytymi błędami
curl -X POST http://localhost:8201/tickets \
  -d '{"title": "Fix buggy_code.py issues", "priority": "high"}'
```

### Przykładowe błędy do naprawy w `buggy_code.py`:

- Modyfikacja listy podczas iteracji
- Mutable default arguments w klasie
- Brak walidacji w `parse_date`
- Code injection przez `eval()`
- Race conditions
- Infinite recursion

## Użycie ogólne

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
