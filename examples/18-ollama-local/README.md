# Example 18: Ollama Local - Local LLM Integration

Demonstruje użycie lokalnego LLM przez Ollama bez potrzeby zewnętrznych API keys.

## Wymagania

- Ollama zainstalowane lokalnie: https://ollama.com
- Model `qwen2.5-coder:7b` (lub podobny) pobrany:
  ```bash
  ollama pull qwen2.5-coder:7b
  ```

## Możliwości

- Lokalna analiza kodu bez wysyłania danych do chmury
- Generowanie kodu offline
- Zero kosztów API
- Prywatność kodu źródłowego

## Uruchomienie

```bash
cd examples/18-ollama-local
make setup  # Sprawdza czy Ollama jest dostępne
make run
```

## CLI Commands

```bash
# Sprawdź dostępne modele
ollama list

# Uruchom interaktywną sesję
ollama run qwen2.5-coder:7b

# Użyj przez proxym (jeśli skonfigurowany)
algitex ask "Explain this code" --model ollama/qwen2.5-coder:7b
```

## Dostępne Modele

| Model | Rozmiar | Przeznaczenie |
|-------|---------|---------------|
| qwen2.5-coder:7b | 4.7GB | Kod, refactoring |
| qwen2.5-coder:14b | 9GB | Złożone zadania |
| llama3.2:3b | 2.0GB | Szybkie odpowiedzi |
| codellama:7b | 3.8GB | Specjalizacja w kodzie |

## Konfiguracja proxym

```yaml
# proxym-config.yaml
providers:
  ollama:
    base_url: http://localhost:11434
    models:
      - qwen2.5-coder:7b
      - llama3.2:3b
```
