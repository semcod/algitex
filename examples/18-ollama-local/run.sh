#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Ollama Local Example ==="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found!"
    echo "Install from: https://ollama.com"
    echo ""
    echo "Quick install:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    exit 1
fi

# Check if Ollama is running
if ! ollama list &> /dev/null; then
    echo "⚠️  Ollama is not running!"
    echo "Start with: ollama serve"
    echo ""
    exit 1
fi

echo "✅ Ollama is installed and running"
echo ""
echo "Available models:"
ollama list | tail -n +2 | while read line; do
    if [ -n "$line" ]; then
        model=$(echo $line | awk '{print $1}')
        echo "  - $model"
    fi
done

echo ""
echo "Running Python demo..."
python3 main.py
