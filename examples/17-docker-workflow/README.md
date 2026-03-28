# Example 17: Docker Workflow

```bash
cd examples/17-docker-workflow
```

Workflow refaktoryzacji używający algitex Docker tool orchestration do pełnego cyklu refactoringu.

## Kroki workflow

1. **Analiza kodu** (code2llm) - analiza projektu
2. **Import wyników** (planfile-mcp) - tworzenie ticketów z analizy
3. **Refaktoryzacja** (aider-mcp) - naprawa high-complexity funkcji
4. **Walidacja** (vallm) - sprawdzenie zmian
5. **Testy** (playwright-mcp) - uruchomienie testów
6. **Pull Request** (github-mcp) - utworzenie PR
7. **Update ticket** (planfile-mcp) - oznaczenie ticketu jako done

## Uruchomienie

```bash
make run
```

## Workflow

Zapisz workflow do pliku i wykonaj:
```bash
algitex workflow run refactor-workflow.md
```

## Multi-ticket Pipeline

Dla przetwarzania wielu ticketów:
```bash
algitex workflow run multi-ticket-pipeline.md
```
