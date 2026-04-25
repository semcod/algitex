# Example 11: Aider MCP - Code Refactoring

```bash
cd examples/11-aider-mcp
```

Demonstruje użycie aider-mcp przez algitex Docker tool orchestration do refaktoryzacji kodu.

## Możliwości

- Prosta refaktoryzacja funkcji
- Dodawanie type hints
- Generowanie dokumentacji
- Generowanie testów
- Optymalizacja wydajności

## Konfiguracja

Wymagane zmienne środowiskowe:
```bash
export GEMINI_API_KEY=your_key
# lub
export ANTHROPIC_API_KEY=your_key
```

## Uruchomienie

```bash
make run
```

# Spawn aider-mcp
algitex docker spawn aider-mcp

# Call refactoring
algitex docker call aider-mcp aider_ai_code -i '{
  "prompt": "Add type hints to main.py",
  "relative_editable_files": ["main.py"],
  "model": "gemini/gemini-2.5-pro"
}'

# Teardown
algitex docker teardown aider-mcp
```
