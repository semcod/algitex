# Example 23: Continue.dev + Ollama - VS Code Extension

```bash
cd examples/23-continue-dev-ollama
```

Konfiguracja **Continue.dev** (VS Code extension) do pracy z **lokalnym Ollama**.

## Co to jest Continue.dev?

Continue.dev to darmowe rozszerzenie VS Code/IntelliJ które:
- Pozwala czatować z LLM w panelu bocznym
- Generuje kod z poziomu edytora
- Refactoruje zaznaczony kod
- Pracuje **offline** z Ollama

## Wymagania

- VS Code lub IntelliJ
- Rozszerzenie Continue.dev
- Ollama uruchomiony lokalnie

## Konfiguracja

### 1. Zainstaluj Continue.dev

```bash
# W VS Code
# Extensions → Search "Continue" → Install
```

### 2. Skonfiguruj Ollama w Continue

Stwórz lub edytuj `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "Qwen Coder 7B",
      "provider": "ollama",
      "model": "qwen2.5-coder:7b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Llama 3 8B",
      "provider": "ollama",
      "model": "llama3:8b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen Local",
    "provider": "ollama",
    "model": "qwen2.5-coder:7b",
    "apiBase": "http://localhost:11434"
  },
  "customCommands": [
    {
      "name": "refactor",
      "prompt": "Refactor this code to be more readable and efficient. Add type hints and docstrings.",
      "description": "Refactor selected code"
    },
    {
      "name": "fix",
      "prompt": "Fix any bugs or issues in this code. Explain what was wrong.",
      "description": "Fix code issues"
    },
    {
      "name": "test",
      "prompt": "Write unit tests for this code using pytest.",
      "description": "Generate tests"
    }
  ]
}
```

### 3. Użycie w VS Code

```bash
# Skróty klawiszowe (default):
Ctrl+L          # Otwórz Continue panel
Ctrl+Shift+L    # Nowa sesja czatu
Ctrl+I          # Inline edit (zaznacz kod, potem Ctrl+I)
Tab             # Autocomplete (jeśli włączone)
```

## Workflow z algitex

```bash
# 1. Analiza kodu
algitex analyze

# 2. Otwórz VS Code z Continue
# Ctrl+L → wybierz model "Qwen Coder 7B"

# 3. Zaznacz kod z błędem w buggy_code.py
# Ctrl+I → napisz "Fix this issue"

# 4. Lub użyj custom command:
# Zaznacz kod → /refactor
```

## Generowanie config.json

```bash
make setup    # Generuje ~/.continue/config.json
```

## Różnice vs Aider/Claude Code

| Feature | Continue.dev | Aider | Claude Code |
|---------|--------------|-------|-------------|
| Interfejs | VS Code GUI | CLI TUI | CLI |
| Autocomplete | ✅ Tab | ❌ | ❌ |
| Inline edit | ✅ Ctrl+I | ✅ | ❌ |
| Chat panel | ✅ | ✅ | ❌ |
| Offline | ✅ | ✅ | ✅ |
| Best for | Daily coding | Complex refactor | Quick fixes |

## CLI Commands (Continue.dev ma też CLI)

```bash
# Install CLI
pip install continuedev

# Usage
continue --help

# W tym przykładzie używamy tylko konfiguracji
# Samo Continue.dev działa w VS Code
```

## Troubleshooting

**Problem**: `Cannot connect to Ollama`
**Fix**: Sprawdź czy `ollama serve` działa

**Problem**: `Model not found`
**Fix**: `ollama pull qwen2.5-coder:7b`

**Problem**: Autocomplete nie działa
**Fix**: Sprawdź czy `tabAutocompleteModel` jest skonfigurowany

## Przykładowe użycie

1. Otwórz `buggy_code.py` w VS Code
2. Zaznacz funkcję `calc()`
3. Naciśnij `Ctrl+I`
4. Napisz: "Add type hints and error handling"
5. Continue.dev wygeneruje poprawiony kod

## Więcej

Dokumentacja: https://docs.continue.dev
