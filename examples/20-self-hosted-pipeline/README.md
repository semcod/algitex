# Example 20: Self-Hosted Pipeline - Full Local Setup

```bash
cd examples/20-self-hosted-pipeline
```

Kompletny pipeline CI/CD działający w 100% lokalnie bez zewnętrznych API keys.

## Wymagania

- Docker i Docker Compose
- Ollama (opcjonalnie, dla LLM)
- 8GB+ RAM
- 20GB wolnego miejsca na Docker images

## Architektura

```
┌────────────────────────────────────────────────────────────┐
│                    Self-Hosted Stack                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐  │
│  │ code2llm │──→│  vallm   │──→│ aider-mcp│──→│ planfile│  │
│  │  :8081   │   │  :8080   │   │  :3000   │   │  :8201  │  │
│  └──────────┘   └──────────┘   └──────────┘   └─────────┘  │
│        │              │               │            │       │
│        └──────────────┴───────────────┴────────────┘       │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │   algitex CLI     │                   │
│                    └───────────────────┘                   │
│                                                            │
│  Optional:                                                 │
│  ┌──────────┐   ┌──────────┐                               │
│  │  proxym  │   │  ollama  │                               │
│  │  :4000   │   │  :11434  │                               │
│  └──────────┘   └──────────┘                               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Szybki Start

```bash
# 1. Zbuduj wszystkie lokalne obrazy
make build

# 2. Uruchom cały stack
make up

# 3. Sprawdź status
make status

# 4. Uruchom przykład
cd examples/20-self-hosted-pipeline
make run
```

## Pełny Pipeline z przykładowym kodem

```bash
# 1. Analiza kodu z błędami
curl -X POST http://localhost:8081/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/workspace", "files": ["buggy_code.py"]}'

# 2. Walidacja lokalna
curl -X POST http://localhost:8080/validate \
  -H "Content-Type: application/json" \
  -d '{"path": "/workspace", "files": ["buggy_code.py"]}'

# 3. Auto-fix workflow
python auto_fix_todos.py

# 4. Naprawa konkretnego pliku
algitex fix buggy_code.py --model ollama/qwen3-coder:latest
```

### Przykładowe błędy bezpieczeństwa w `buggy_code.py`:

- SQL injection w `fetch_user_data`
- YAML deserialization vulnerability
- Timing attack w `authenticate_user`
- Hardcoded credentials
- Path traversal w `cleanup_old_files`
- Deserialization vulnerability w `generate_report`

## Pełny Pipeline Lokalny

```bash
# Analiza kodu lokalnie
curl -X POST http://localhost:8081/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/workspace", "format": "toon"}'

# Walidacja lokalna
curl -X POST http://localhost:8080/validate \
  -H "Content-Type: application/json" \
  -d '{"path": "/workspace/src"}'

# Tworzenie ticketów lokalnie
curl -X POST http://localhost:8201/tickets \
  -H "Content-Type: application/json" \
  -d '{"title": "Refactor main.py", "priority": "high"}'
```

## Koszty

| Komponent | Koszt miesięczny |
|-----------|------------------|
| Cloud API (porównanie) | $50-200 |
| **Self-hosted** | **$0** |
| Prąd (szacunek) | ~$5 |

## Zalety

- 🔒 100% prywatność kodu
- 🌐 Działa offline
- 💰 Zero kosztów API
- ⚡ Brak limitów rate-limiting
- 🎓 Pełna kontrola nad modelami
