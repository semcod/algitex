# Example 21: Aider CLI + Ollama - Local Code Refactoring

```bash
cd examples/21-aider-cli-ollama
```

Kompletny workflow refaktoryzacji kodu używający **aider CLI** z **lokalnym Ollama** (bez API keys).

Czyta zadania z `TODO.md` (stworzone przez `algitex analyze`) i naprawia kod automatycznie.

## Workflow

```
algitex analyze               # Analiza kodu + tworzenie TODO.md
python main.py                # Sprawdź status i wygeneruj TODO
algitex todo fix              # Naprawa wszystkich zadań
```

## Wymagania

- **Ollama** zainstalowany i uruchomiony: `ollama serve`
- **Model** `qwen2.5-coder:7b` pobrany: `ollama pull qwen2.5-coder:7b`
- **aider**: `pip install aider-chat`
- **algitex**: `pip install -e ../../`
- **git** (wymagane przez aider): `sudo apt-get install git` lub `brew install git`

## Instalacja

```bash
make setup    # Sprawdź zależności
```

## Użycie

### Krok 1: Analiza kodu i stworzenie TODO.md

```bash
algitex analyze
# lub
python -c "from algitex import Project; p = Project('.'); p.generate_todo()"
```

To stworzy `TODO.md` z listą problemów (unused imports, complex functions, etc.).

### Krok 2: Auto-fix przez algitex

```bash
# Napraw wszystko
algitex todo fix

# Napraw tylko pierwsze 5 zadań
algitex todo fix --limit 5

# Użyj Python API
python -c "from algitex import Project; p = Project('.'); p.fix_issues()"
```

### Ręczne użycie aider z ollama

```bash
# Bezpośrednie użycie aider CLI
aider --model ollama/qwen2.5-coder:7b \
      --message "Add type hints to this function" \
      buggy_code.py
```

## Co się dzieje pod spodem

1. `main.py` używa `algitex.Project` do sprawdzenia usług
2. `p.generate_todo()` tworzy `TODO.md` z wyników analizy
3. `p.fix_issues()` lub `algitex todo fix` naprawiają automatycznie
4. Algitex wybiera najlepszy backend (Ollama, Aider, lub LiteLLM)

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
| `make run` | Sprawdź status usług |
| `make setup` | Sprawdź zależności |
| `make todo` | Wygeneruj TODO.md |
| `make fix` | Napraw przez algitex |
| `make clean` | Wyczyść zmiany |

## Troubleshooting

**Problem**: `aider: command not found`
**Rozwiązanie**: `pip install aider-chat`

**Problem**: `Ollama not responding`
**Rozwiązanie**: `ollama serve` w osobnym terminalu

**Problem**: `Model not found`
**Rozwiązanie**: `ollama pull qwen2.5-coder:7b`

**Problem**: Timeout przy naprawie
**Rozwiązanie**: Użyj mniejszego modelu (3B zamiast 7B) lub zmniejsz limit w `p.fix_issues(limit=3)`

**Problem**: Aider wyświetla warningi "Unknown context window size and token costs"
**Rozwiązanie**: To normalne - aider nie zna domyślnie modeli Ollama, ale działa z nimi poprawnie.

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
