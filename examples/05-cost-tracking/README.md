# Example 05: Cost Tracking & Budget

Pokazuje jak algitex śledzi koszty LLM per-ticket
i jak algo loop redukuje wydatki w czasie.

## Uruchomienie

```bash
./run.sh
```

## Co pokazuje

### 1. Cost ledger per ticket

Każdy ticket ma metadane:
- `cost_usd` — koszt LLM
- `model` — użyty model
- `tier` — poziom (cheap/balanced/premium/free)

### 2. Cost by tier

Wizualizacja rozkładu kosztów:
```
deep:      $0.1820 ████████████████████
standard:  $0.0450 ████
cheap:     $0.0030
free:      $0.0000
trivial:   $0.0004
```

### 3. Progressive Algorithmization Savings

Symulacja oszczędności:
- Ile trace'ów zebrano
- Jakie wzorce znaleziono
- Potencjalne miesięczne oszczędności

## W produkcji

```bash
algitex status           # pokaż cost ledger
algitex algo report      # pokaż % deterministic
```

Proxym loguje koszt/model/latency **per ticket**.
Cost ledger pokazuje dokładnie ile kosztuje każde zadanie.
