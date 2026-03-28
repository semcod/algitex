# Example 01: Quickstart

Pokazuje trzy główne obiekty: Project, Loop, Workflow.
Działa nawet bez zainstalowanych narzędzi — gracefully degrades.

## Uruchomienie

```bash
./run.sh
```

lub bezpośrednio:

```bash
python main.py
```

## Co robi ten przykład

1. Sprawdza dostępne narzędzia (`discover_tools()`)
2. Tworzy projekt (`Project`)
3. Analizuje kod (`analyze()`)
4. Tworzy plan z ticketami (`plan()`)
5. Pokazuje status (`status()`)
6. Dodaje ticket ręcznie (`add_ticket()`)

## Następne kroki

```bash
algitex go                # pełny pipeline
algitex algo discover     # zacznij zbierać trace'y
algitex ask "question"    # szybkie zapytanie do LLM
```
