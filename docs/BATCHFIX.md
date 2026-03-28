# BatchFix — Grupowanie i Optymalizacja Fixów

BatchFix to funkcjonalność która grupuje podobne zadania z TODO.md i wykonuje je za jednym razem, znacznie przyspieszając proces naprawy kodu.

## Jak to działa?

### Problem
Tradycyjne podejście:
```
10 zadań "String concatenation" → 10 × 30s = 300s (5 minut!)
```

### BatchFix
```
10 zadań "String concatenation" → 1 × 60s = 60s (5× szybciej!)
```

## Komenda

```bash
# Symulacja (dry-run)
algitex todo batch --dry-run

# Wykonaj fixy
algitex todo batch --execute

# Konfiguracja
algitex todo batch -b ollama -s 5 --execute
```

## Opcje

| Flaga | Opis | Domyślnie |
|-------|------|-----------|
| `-b, --backend` | Backend: ollama, litellm-proxy | ollama |
| `-m, --model` | Model Ollama (np. qwen2.5-coder:7b, qwen3:8b) | qwen3:8b |
| `-s, --batch-size` | Max plików w batchu | 5 |
| `-p, --parallel` | Równoległe grupy (workers) | 3 |
| `--execute` | Wykonaj naprawdę (domyślnie dry-run) | False |
| `--prune` | Usuń nieaktualne zadania przed batch | False |
| `-l, --limit` | Limit liczby zadań (0 = wszystkie) | 0 |
| `--no-log` | Wyłącz generowanie logów markdown | False |
| `-v, --verbose` | Szczegółowe logi | False |
| `-f, --file` | Ścieżka do TODO.md | TODO.md |

## Grupowanie Zadań

BatchFix automatycznie grupuje zadania według typu:

| Kategoria | Wzorce | Przykład |
|-----------|--------|----------|
| `string_concat` | "f-string", "string concatenation" | `"hello" + name` → `f"hello {name}"` |
| `magic_number` | "magic number", "use named constant" | `timeout=30` → `timeout=DEFAULT_TIMEOUT` |
| `unused_import` | "unused import" | `import os` (nieużywane) |
| `missing_return` | "missing return type" | `def foo():` → `def foo() -> None:` |
| `docstring` | "llm-style docstring" | Konwersja na standardowe docstrings |
| `module_block` | "module execution block" | `if __name__ == "__main__":` |

## Przykład Użycia

```bash
# 1. Wygeneruj TODO.md
prefact generate

# 2. Weryfikacja - sprawdź które zadania są nadal aktualne
algitex todo verify-prefact

# 3. Wyczyść nieaktualne zadania z TODO.md
algitex todo verify-prefact --prune

# 4. Zobacz co zostanie zbatchowane
algitex todo batch --dry-run

# 5. Wykonaj fixy (dry-run z limitem i równoległością)
algitex todo batch --limit 10 --parallel 2

# 6. Wykonaj naprawdę z czyszczeniem nieaktualnych zadań
algitex todo batch --execute --prune

# 7. Sprawdź wynik
cat TODO.md  # Zadania oznaczone jako [x]
```

## Logi Markdown

BatchFix automatycznie generuje logi w formacie markdown:

```bash
# Logi zapisywane domyślnie w .algitex/logs/
algitex todo batch --dry-run
# Log zapisany: .algitex/logs/batch_YYYYMMDD_HHMMSS.md

# Wyłączenie logowania
algitex todo batch --execute --no-log
```

### Format logu

```markdown
# BatchFix Session Log

**Started:** 2026-03-28 14:46:36
**Ended:** 2026-03-28 14:46:36

## Configuration
| Parameter | Value |
|-----------|-------|
| Backend | ollama |
| Batch Size | 2 |

## Summary
| Metric | Count |
|--------|-------|
| Total Entries | 3 |
| Successful | 0 |
| Failed | 0 |
| Dry Run | 3 |
```

```
📦 BatchFix: 50 zadań → 12 grup
  🔧 string_concat: 15 plików
     • file1.py
     • file2.py
     ... i 13 więcej
     ✓ Batch fix: 15 plików w 45.2s
  
  🔧 magic_number: 10 plików
     ...

✓ BatchFix zakończony: 50 wyników w 180.5s
```

## Porównanie

| Metoda | Czas dla 50 zadań | Koszt API |
|--------|-------------------|-----------|
| Pojedyncze fixy | ~1500s (25 min) | 50 calls |
| BatchFix (5 plików) | ~300s (5 min) | 10 calls |
| **Oszczędność** | **80%** | **80%** |

## Ograniczenia

- BatchFix działa tylko z **Ollama** (lokalnym modelem)
- Maksymalny rozmiar batch: 5 plików (konfigurowalne)
- Niektóre zadania wymagają indywidualnego podejścia

## Pliki

- `src/algitex/tools/autofix/batch_backend.py` — Backend
- `src/algitex/cli/todo.py:batch` — CLI command
- `examples/34-batch-fix/` — Przykład użycia
