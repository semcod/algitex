# Example 20: Self-Hosted Pipeline - Full Local Setup

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
