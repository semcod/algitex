# Example 12: Filesystem MCP - File Operations

```bash
cd examples/12-filesystem-mcp
```

Demonstruje użycie filesystem-mcp przez algitex Docker tool orchestration do operacji na plikach.

## Możliwości

- Odczyt zawartości plików
- Listowanie katalogów
- Wyszukiwanie plików
- Zapisywanie nowych plików
- Batch processing plików
- Tworzenie struktury katalogów

## Uruchomienie

```bash
make run
```

# Spawn filesystem-mcp
algitex docker spawn filesystem-mcp

# Read file
algitex docker call filesystem-mcp read_file -i '{
  "path": "/workspace/README.md"
}'

# List directory
algitex docker call filesystem-mcp list_directory -i '{
  "path": "/workspace",
  "recursive": false
}'

# Teardown
algitex docker teardown filesystem-mcp
```
