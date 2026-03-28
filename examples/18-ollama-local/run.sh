#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Example 18: Ollama Local ==="
echo ""

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Install from: https://ollama.com"
    exit 1
fi

echo "✅ Ollama found"

# Check if running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Start it with: ollama serve"
    exit 1
fi

echo "✅ Ollama is running"
echo ""

python3 main.py
