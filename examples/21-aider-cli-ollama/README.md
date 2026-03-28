# Example 21: Aider CLI + Ollama - Local Code Refactoring

Kompletny workflow refaktoryzacji kodu używający **aider CLI** z **lokalnym Ollama** (bez API keys).

Czyta zadania z `TODO.md` (stworzone przez `prefact -a`) i naprawia kod automatycznie.

## Workflow

```
prefact -a                    # Analiza kodu + tworzenie TODO.md
python auto_fix.py            # Naprawa wszystkich zadań przez aider + ollama
python auto_fix.py -l 5       # Naprawa pierwszych 5 zadań
```

## Wymagania

- **Ollama** zainstalowany i uruchomiony: `ollama serve`
- **Model** `qwen2.5-coder:7b` pobrany: `ollama pull qwen2.5-coder:7b`
- **aider**: `pip install aider-chat`
- **prefact**: `pip install prefact`
- **git** (wymagane przez aider): `sudo apt-get install git` lub `brew install git`

## Instalacja

```bash
make setup    # Sprawdź zależności
```

## Użycie

### Krok 1: Analiza kodu i stworzenie TODO.md

```bash
prefact -a
```

To stworzy `TODO.md` z listą problemów (unused imports, complex functions, etc.).

### Krok 2: Auto-fix przez aider + ollama

```bash
# Napraw wszystko
python auto_fix.py

# Napraw tylko pierwsze 5 zadań
python auto_fix.py --limit 5

# Dry-run (pokaż co by zrobił, bez zmian)
python auto_fix.py --dry-run

# Użyj innego modelu
python auto_fix.py --model ollama/codellama:7b
```

### Ręczne użycie aider z ollama

```bash
# Bezpośrednie użycie aider CLI
aider --model ollama/qwen2.5-coder:7b \
      --message "Add type hints to this function" \
      buggy_code.py
```

## Co się dzieje pod spodem

1. `auto_fix.py` czyta `TODO.md` z sekcji "Current Issues"
2. Dla każdego zadania wywołuje:
   ```bash
   aider --model ollama/qwen2.5-coder:7b \
         --no-git --yes \
         --message "Fix: {description}" \
         {file_path}
   ```
3. Aider komunikuje się z lokalnym Ollama (port 11434)
4. Kod jest modyfikowany bezpośrednio w plikach

## Przykładowe błędy w `buggy_code.py`

- Niepotrzebne importy
- Brak type hints
- Magic numbers
- String concatenation zamiast f-stringów
- Brak obsługi błędów

## Zalety tego podejścia

- 🔒 **100% offline** - kod nigdy nie opuszcza maszyny
- 💰 **Zero kosztów** - brak API keys
- ⚡ **Szybkie** - lokalny model, brak latency
- 📝 **Przejrzyste** - każda zmiana widoczna w git diff

## Komendy

| Komenda | Opis |
|---------|------|
| `make run` | Pełny demo workflow |
| `make setup` | Sprawdź zależności |
| `make todo` | Uruchom `prefact -a` |
| `make fix` | Uruchom `auto_fix.py` |
| `make clean` | Wyczyść zmiany |

## Troubleshooting

**Problem**: `aider: command not found`
**Rozwiązanie**: `pip install aider-chat`

**Problem**: `Ollama not responding`
**Rozwiązanie**: `ollama serve` w osobnym terminalu

**Problem**: `Model not found`
**Rozwiązanie**: `ollama pull qwen2.5-coder:7b`

**Problem**: Timeout przy naprawie
**Rozwiązanie**: Użyj mniejszego modelu (3B zamiast 7B) lub zwiększ timeout w `auto_fix.py`

**Problem**: Aider wyświetla warningi "Unknown context window size and token costs"
**Rozwiązanie**: To normalne - aider nie zna domyślnie modeli Ollama, ale działa z nimi poprawnie. Warningi są teraz filtrowane w `auto_fix.py`.

**Problem**: `Did you mean one of these?` lub `Missing environment variables`
**Rozwiązanie**: Te warningi są normalne przy użyciu Ollama. Aider działa poprawnie mimo nich.

## Porównanie z Example 11 (Aider MCP)

| | Example 11 | Example 21 (ten) |
|---|---|---|
| **Interfejs** | Docker MCP | CLI shell |
| **Model** | Gemini/Anthropic API | Ollama lokalnie |
| **Koszt** | Płatny | Darmowy |
| **Offline** | ❌ | ✅ |
| **TODO.md** | ❌ | ✅ |
| **Autonomous** | ❌ | ✅ (loop) |

## Next Steps

1. Sprawdź zmiany: `git diff`
2. Uruchom testy: `python -m pytest`
3. Zaakceptuj zmiany: `git add . && git commit -m 'Refactor via aider + ollama'`
