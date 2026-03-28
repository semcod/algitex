# Example 13: Vallm - Code Validation

Demonstruje użycie vallm przez algitex Docker tool orchestration do walidacji kodu.

## Możliwości

- Podstawowa walidacja kodu
- Batch validation z raportami błędów
- Scoring jakości kodu
- Kompleksowa analiza
- Export ewolucji (tracking zmian)
- Niestandardowe reguły walidacji

## Uruchomienie

```bash
make run
```

## CLI Commands

```bash
# Spawn vallm
algitex docker spawn vallm

# Basic validation
algitex docker call vallm validate -i '{
  "path": "/project/src",
  "recursive": true,
  "format": "json"
}'

# Batch analysis
algitex docker call vallm batch -i '{
  "path": "/project",
  "format": "json",
  "errors_only": true
}'

# Teardown
algitex docker teardown vallm
```
