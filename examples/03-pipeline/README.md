# Example 03: Composable Pipeline

Łączenie kroków fluentnie: analyze → tickets → execute → validate → sync.
Każdy krok jest opcjonalny — pomijaj to, czego nie potrzebujesz.

## Konfiguracja (opcjonalna)

Jeśli masz proxym, skopiuj `.env.example` do `.env`:

```bash
cp .env.example .env
```

## Uruchomienie

```bash
./run.sh
```

## Trzy wzorce użycia

### Wzorzec A: Pełny pipeline

```python
result = (
    Pipeline(".")
    .analyze(full=False)     # szybki health check
    .create_tickets()        # auto-generuj z analizy
    .report()
)
```

### Wzorzec B: Tylko analiza

```python
result = (
    Pipeline(".")
    .analyze()
    .report()
)
```

### Wzorzec C: Niestandardowe tickety

Ręczne dodawanie ticketów z tagami i metadanymi.

## CLI equivalent

```bash
algitex go      # pełny zautomatyzowany cykl
```
