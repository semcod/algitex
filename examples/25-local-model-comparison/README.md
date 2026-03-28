# Example 25: Local Model Comparison

```bash
cd examples/25-local-model-comparison
```

Porównanie różnych modeli **Ollama** na tym samym zadaniu.

## Problem

Masz do wyboru wiele modeli lokalnych:
- qwen3-coder:latest
- qwen2.5-coder:3b
- llama3:8b
- codellama:7b
- gemma2:9b

Ale który jest najlepszy do **Twojego** zadania?

## Rozwiązanie

Ten przykład uruchamia to samo zadanie na wielu modelach i porównuje:
- **Jakość** - jak dobrą generuje odpowiedź
- **Szybkość** - czas odpowiedzi
- **Koszt** - zużycie RAM/CPU (dla lokalnych = prąd)
- **Tokeny** - ile tokenów wygenerował

## Użycie

```bash
# 1. Upewnij się że masz zainstalowane modele
make setup

# 2. Uruchom benchmark
make benchmark

# 3. Zobacz wyniki
make results
```

## Modele do testowania

```bash
# Pobierz modele (zajmie ~20GB)
ollama pull qwen3-coder:latest
ollama pull qwen3-coder:latest
ollama pull llama3:8b
ollama pull codellama:7b
ollama pull gemma2:9b
```

## Zadania testowe

1. **Code Completion** - dokończ funkcję
2. **Bug Fix** - napraw błąd
3. **Documentation** - wygeneruj docstring
4. **Refactoring** - uprość kod
5. **Test Generation** - wygeneruj testy

## Przykładowe wyniki

```
Model Comparison Report
==================================================
Task: Code Completion
Input tokens: 150

Results:
┌─────────────────────┬──────────┬───────────┬─────────┬────────────┐
│ Model               │ Time     │ Tokens    │ Quality │ Tok/sec    │
├─────────────────────┼──────────┼───────────┼─────────┼────────────┤
│ qwen2.5-coder:3b    │ 2.3s     │ 45        │ ⭐⭐⭐    │ 19.6       │
│ qwen3-coder:latest    │ 4.1s     │ 52        │ ⭐⭐⭐⭐   │ 12.7       │
│ llama3:8b           │ 5.2s     │ 48        │ ⭐⭐⭐⭐   │ 9.2        │
│ codellama:7b        │ 4.8s     │ 55        │ ⭐⭐⭐⭐⭐  │ 11.5       │
│ gemma2:9b           │ 6.1s     │ 50        │ ⭐⭐⭐⭐   │ 8.2        │
└─────────────────────┴──────────┴───────────┴─────────┴────────────┘

Recommendation:
  Speed: qwen2.5-coder:3b (19.6 tok/s)
  Quality: codellama:7b (⭐⭐⭐⭐⭐)
  Balanced: qwen3-coder:latest (good quality, decent speed)
```

## Wnioski

| Model | Best For | Avoid For |
|-------|----------|-------------|
| qwen2.5-coder:3b | Fast autocomplete, prototyping | Complex logic |
| qwen3-coder:latest | Daily coding, balance | Large batch jobs |
| codellama:7b | Complex refactoring | Quick queries |
| llama3:8b | General purpose | Code-specific tasks |
| gemma2:9b | Documentation | Speed-critical tasks |

## Użycie w praktyce

```python
# W algitex CLI możesz wybrać model per-task

# Szybki autocomplete
export DEFAULT_MODEL=ollama/qwen3-coder:latest

# Dokładny refactor
export DEFAULT_MODEL=ollama/codellama:7b

# Codzienna praca
export DEFAULT_MODEL=ollama/qwen3-coder:latest
```

## Generowanie własnych benchmarków

```bash
# Dodaj własne zadanie
python benchmark.py --custom-task ./my_task.py

# Porównaj tylko wybrane modele
python benchmark.py --models qwen3-coder:latest

# Zapisz wyniki do CSV
python benchmark.py --output-format csv
```

## Troubleshooting

**Błąd**: `model not found`
**Fix**: `ollama pull <model_name>`

**Błąd**: `out of memory`
**Fix**: Testuj mniejsze modele (3B zamiast 7B/9B)

**Błąd**: `timeout`
**Fix**: Zwiększ timeout w config.json
