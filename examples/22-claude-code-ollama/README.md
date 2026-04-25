# Example 22: Claude Code + Ollama - Local AI Assistant

```bash
cd examples/22-claude-code-ollama
```

Użycie **Claude Code** z **lokalnym Ollama** - refactoring kodu bez API keys.

## Wymagania

- **Claude Code** (anthropic-curl): `pip install anthropic-curl`
- **Ollama** uruchomiony: `ollama serve`
- **Model**: `qwen3-coder:latest` lub inny

# Ustaw Ollama jako backend dla Claude Code
export ANTHROPIC_BASE_URL=http://localhost:11434/v1
export ANTHROPIC_API_KEY=ollama  # dowolny string, Ollama nie weryfikuje
```

# 3. Ręczne użycie
anthropic-curl --model ollama/qwen3-coder:latest \
  --message "Refactor this function to use type hints" \
  buggy_code.py
```

## Różnice vs Aider

| Feature | Aider | Claude Code |
|---------|-------|-------------|
| Tryb | Edytor TUI (tryb interaktywny) | CLI one-shot |
| Git integration | ✅ Auto-commit | ❌ Manual |
| Multi-file | ✅ | ✅ |
| Best for | Complex refactoring | Quick fixes |

# Spawn interactive session
anthropic-curl --model ollama/qwen3-coder:latest

# One-shot fix
anthropic-curl --model ollama/qwen3-coder:latest \
  --message "Add error handling" \
  --file buggy_code.py

# Batch processing
make batch  # Fix all TODO.md issues
```

## Workflow

```bash
prefact -a                              # 1. Analiza
anthropic-curl --model ollama/...       # 2. Fix
python -m pytest                        # 3. Test
```

## Troubleshooting

**Błąd**: `anthropic-curl: command not found`
**Fix**: `pip install anthropic-curl`

**Błąd**: `Connection refused`
**Fix**: `ollama serve` w osobnym terminalu

**Błąd**: `Model not found`
**Fix**: `ollama pull qwen3-coder:latest`
