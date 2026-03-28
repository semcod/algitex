# Example 24: Ollama Batch Processing - Parallel Code Analysis

Przetwarzanie wsadowe wielu plików przez **Ollama** z **równoległością**.

## Problem

Masz 100+ plików do przeanalizowania/refactorowania:
- Analiza jeden po drugim trwa wieczność
- Chcesz wykorzystać wszystkie rdzenie CPU
- Musisz monitorować postęp

## Rozwiązanie

Ten przykład pokazuje batch processing z:
- **Równoległe przetwarzanie** (thread pool)
- **Rate limiting** (nie zalewać Ollama)
- **Retry logic** (gdy model się wykrzaczy)
- **Progress tracking** (widać co się dzieje)
- **Resume** (można przerwać i wznowić)

## Użycie

```bash
# 1. Analiza wielu plików równolegle
python batch_analyze.py --dir ./src --pattern "*.py"

# 2. Refactoring wsadowy
python batch_refactor.py --todo TODO.md --parallel 4

# 3. Generowanie dokumentacji
python batch_document.py --dir ./src --output ./docs
```

## Konfiguracja

```bash
# Ustawienia w .env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
BATCH_PARALLELISM=4      # Ile równoległych requestów
BATCH_RATE_LIMIT=2         # Requesty na sekundę
BATCH_RETRY_ATTEMPTS=3     # Ile retry przed failure
BATCH_TIMEOUT=300          # Timeout na plik (sekundy)
```

## Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                    Batch Processor                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ File Queue   │──▶│ Thread Pool  │──▶│ Ollama API   │    │
│  │ (100 files)  │   │ (4 workers)  │   │ (local)      │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
│         │                   │                  │             │
│         ▼                   ▼                  ▼             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │ Progress     │   │ Retry        │   │ Results      │    │
│  │ Tracker      │   │ Handler      │   │ DB (JSON)    │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Przykładowe wyniki

```bash
$ python batch_analyze.py --dir ./src

Batch Analysis Report
==================================================
Total files: 100
Completed: 100
Failed: 0
Time: 5m 23s

Results:
  High complexity: 12 files
  Medium complexity: 35 files
  Low complexity: 53 files

Hotspots:
  1. src/core/engine.py:42 (CC=25)
  2. src/api/routes.py:156 (CC=18)
  3. src/utils/parser.py:89 (CC=15)

Output saved to: .batch_results/analysis_20260328.json
```

## Resume przerwanej pracy

```bash
# Przerwano po 50 plikach
Ctrl+C

# Wznów od miejsca przerwania
python batch_analyze.py --resume
```

## Zalety

- ⚡ **Szybkość** - 4-8x szybciej niż sekwencyjnie
- 🔄 **Odporność** - retry na błędy
- 📊 **Widoczność** - progress bar i logi
- 💾 **Bezpieczeństwo** - wyniki zapisywane na bieżąco
- 🌐 **Offline** - 100% lokalne

## Porównanie

| Metoda | 100 plików | CPU Usage |
|--------|-----------|-----------|
| Sekwencyjna | 20 min | 25% |
| Batch (4x) | 5 min | 100% |
| Batch (8x) | 3 min | 100% |

## Troubleshooting

**Błąd**: `Connection pool exhausted`
**Fix**: Zmniejsz `BATCH_PARALLELISM` do 2

**Błąd**: `Model timeout`
**Fix**: Zwiększ `BATCH_TIMEOUT` lub zmniejsz rozmiar plików

**Błąd**: `Out of memory`
**Fix**: Zmniejsz batch size, użyj modelu 3B zamiast 7B

## Next Steps

1. Przeanalizuj kod: `python batch_analyze.py --dir ./src`
2. Zobacz wyniki: `cat .batch_results/analysis_latest.json`
3. Zrób refactor: `python batch_refactor.py --select-high-complexity`
