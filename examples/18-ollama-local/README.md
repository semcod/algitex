# Example 18: Ollama Local

Lokalne modele LLM przez Ollama - 100% offline, zero kosztów API.

## Wymagania

- Ollama zainstalowany: https://ollama.com
- Minimum 8GB RAM (16GB rekomendowane)
- Model `qwen2.5-coder:7b` pobrany

## Szybki Start

```bash
make setup    # Sprawdź Ollama i utwórz .env
make run      # Uruchom przykład
```

## Instalacja Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Pobierz model
dollama pull qwen2.5-coder:7b
```

## Użycie

```python
# Użyj lokalnego modelu z Algitex
export DEFAULT_MODEL=ollama/qwen2.5-coder:7b

algitex analyze --model ollama/qwen2.5-coder:7b
algitex ask "Refactor this function" --model ollama/qwen2.5-coder:7b
```

## Zalety

- 🔒 Prywatność kodu
- 💰 Zero kosztów
- 🌐 Działa offline
