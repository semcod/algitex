# Example 15: GitHub MCP - Repository Management

```bash
cd examples/15-github-mcp
```

Demonstruje użycie github-mcp przez algitex Docker tool orchestration do operacji na repozytoriach GitHub.

## Możliwości

- Tworzenie Issues
- Tworzenie Pull Requests
- Wyszukiwanie kodu
- Listowanie commitów
- Pobieranie zawartości plików
- Tworzenie i aktualizacja plików
- Bulk tworzenie Issues

## Konfiguracja

Wymagane:
```bash
export GITHUB_PAT=your_github_token
```

## Uruchomienie

```bash
make run
```

# Spawn github-mcp
algitex docker spawn github-mcp

# Create issue
algitex docker call github-mcp create_issue -i '{
  "owner": "myorg",
  "repo": "myproject",
  "title": "Bug: Fix authentication timeout",
  "body": "Users experiencing timeout after 30 seconds",
  "labels": ["bug", "authentication"]
}'

# Teardown
algitex docker teardown github-mcp
```
