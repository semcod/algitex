# Example 34: BatchFix — Grupowanie i Optymalizacja

Demonstracja funkcjonalności BatchFix która grupuje podobne zadania i wykonuje je za jednym razem.

## Czym jest BatchFix?

BatchFix optymalizuje proces naprawy kodu przez:
- **Grupowanie** podobnych zadań (np. wszystkie "f-string" razem)
- **Batch processing** — jedno wywołanie LLM dla wielu plików
- **Oszczędność** — 5× szybciej, 5× taniej

## Struktura

```
examples/34-batch-fix/
├── main.py              # Przykłady użycia
├── sample_code/         # Przykładowe pliki z błędami
│   ├── file1.py        # String concatenation
│   ├── file2.py        # Magic numbers
│   └── file3.py        # Unused imports
├── TODO.md             # Wygenerowane zadania
└── README.md           # Ten plik
```

## Użycie

```bash
# Wejdź do katalogu
cd examples/34-batch-fix

# 1. Wygeneruj TODO.md z błędami
prefact generate

# 2. Zobacz co zostanie zbatchowane
algitex todo batch --dry-run

# 3. Wykonaj fixy
algitex todo batch --execute

# 4. Sprawdź wynik
algitex todo list
```

## Przykładowy Output

```
$ algitex todo batch --execute

⚡ EXECUTE — Fixy zostaną zastosowane

📋 Znaleziono 15 zadań
📦 BatchFix: 15 zadań → 3 grupy

  🔧 string_concat: 5 plików
     • file1.py
     • file2.py
     ... i 3 więcej
     ✓ Batch fix: 5 plików w 38.2s
  
  🔧 magic_number: 5 plików
     • config.py
     • main.py
     ... i 3 więcej
     ✓ Batch fix: 5 plików w 35.1s
  
  🔧 unused_import: 5 plików
     • module1.py
     • module2.py
     ... i 3 więcej
     ✓ Batch fix: 5 plików w 32.7s

════════════════════════════════════════════════════════════
  BATCH FIX SUMMARY
════════════════════════════════════════════════════════════

  ✅ Success: 15
  ❌ Failed:  0
  📊 Total:   15

✓ Zaktualizowano 15 plików
```

## Porównanie

| Metoda | Czas | Wywołań API | Efektywność |
|--------|------|-------------|-------------|
| Indywidualne | 450s (7.5 min) | 15 | Baseline |
| BatchFix (5) | 106s (1.8 min) | 3 | **76% szybciej** |

## Więcej Informacji

- [Dokumentacja BatchFix](/docs/BATCHFIX.md)
- [Główny README](/README.md)
