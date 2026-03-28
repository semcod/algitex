# Example 02: Progressive Algorithmization Loop

Demonstruje 5-etapową podróż od "LLM obsługuje wszystko" do "większość ruchu działa deterministycznie".

Ten przykład symuluje zbieranie trace'ów i ekstrakcję wzorców bez potrzeby posiadania live proxym.

## Konfiguracja (opcjonalna)

Jeśli masz proxym, skopiuj `.env.example` do `.env`:

```bash
cp .env.example .env
```

## Uruchomienie

```bash
./run.sh
```

## 5 Etapów Progressive Algorithmization

1. **Discovery** — zbieranie trace'ów z interakcji LLM
2. **Extraction** — znajdowanie powtarzających się wzorców
3. **Rule Generation** — tworzenie deterministycznych handlerów
4. **Hybrid Routing** — routing po confidence: znane → reguła, nieznane → LLM
5. **Optimization** — monitoring i minimalizacja użycia LLM

## Wynik

Pokaże:
- Ile trace'ów zebrano
- Jakie wzorce znaleziono
- Ile reguł wygenerowano
- Potencjalne oszczędności kosztów

## W produkcji

Trace'y przychodzą automatycznie z proxym:

```bash
algitex algo discover    # włącz zbieranie
algitex algo extract     # znajdź wzorce
algitex algo rules       # generuj reguły
algitex algo report      # pokaż postęp
```
