# Example 18: Ollama Local

```bash
cd examples/18-ollama-local
```

Lokalne modele LLM przez Ollama - 100% offline, zero kosztów API.

## Wymagania

- Ollama zainstalowany: https://ollama.com
- Minimum 8GB RAM (16GB rekomendowane)
- Model `qwen3-coder:latest` pobrany

## Szybki Start

```bash
make setup    # Sprawdź Ollama i utwórz .env
make run      # Uruchom przykład
```

# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Pobierz model
ollama pull qwen3-coder:latest
```

# 1. Napraw przykładowy kod z błędami
algitex fix buggy_code.py --model ollama/qwen3-coder:latest

# 2. Analiza kodu
algitex analyze buggy_code.py --model ollama/qwen3-coder:latest

# 3. Wygeneruj testy dla naprawionego kodu
algitex test buggy_code.py --model ollama/qwen3-coder:latest
```

### Przykładowe błędy do naprawy w `buggy_code.py`:

- Niepotrzebne importy (np. `import json`)
- Dzielenie przez zero
- Niezamknięte pliki
- String concatenation zamiast f-stringów
- Mutable default arguments
- Path traversal vulnerability

# Użyj lokalnego modelu z Algitex
export DEFAULT_MODEL=ollama/qwen3-coder:latest

algitex analyze --model ollama/qwen3-coder:latest
algitex ask "Refactor this function" --model ollama/qwen3-coder:latest
```

## Zalety

- 🔒 Prywatność kodu
- 💰 Zero kosztów
- 🌐 Działa offline
