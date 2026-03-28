# Example 16: Comprehensive Test Workflow

```bash
cd examples/16-test-workflow
```

Pełny pipeline testowy demonstrujący moc algitex Docker tool orchestration - łączy analizę, refaktoryzację, testy i deployment.

## Scenariusz: Automated Code Quality Improvement Pipeline

14 kroków od analizy do PR:
1. Analiza projektu (code2llm)
2. Tworzenie ticketów (planfile-mcp)
3. Pobranie high-priority tickets
4. Refaktoryzacja (aider-mcp)
5. Walidacja (vallm)
6. Uruchomienie testów (docker-mcp)
7. Sprawdzenie coverage (vallm)
8. Generowanie dokumentacji (aider-mcp)
9. Build Docker image (docker-mcp)
10. Security scan (docker-mcp)
11. Push do registry (docker-mcp)
12. Create PR (github-mcp)
13. Update ticket status (planfile-mcp)
14. Generate report (filesystem-mcp)

## Konfiguracja

Wymagane zmienne:
```bash
export GITHUB_PAT=your_github_token
export GEMINI_API_KEY=your_gemini_key
export ANTHROPIC_API_KEY=your_anthropic_key
export BUILD_NUMBER=123
```

## Uruchomienie

```bash
make run
```

## Workflow

Zapisz workflow do pliku i wykonaj:
```bash
algitex workflow run comprehensive-test.md
```
