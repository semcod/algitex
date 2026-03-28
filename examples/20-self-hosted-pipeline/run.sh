#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Self-Hosted Pipeline Example ==="
echo "Full local CI/CD pipeline using MCP tools"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env - edit with your configuration"
fi

# Check services
echo "Checking MCP services..."
CODE2LLM_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health || echo "000")
VALLM_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health || echo "000")
PLANFILE_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8201/health || echo "000")

if [ "$CODE2LLM_OK" != "200" ] || [ "$VALLM_OK" != "200" ] || [ "$PLANFILE_OK" != "200" ]; then
    echo "❌ Some MCP services are not running"
    echo "   Start them with: make up"
    echo ""
    echo "Current status:"
    echo "  code2llm: $CODE2LLM_OK"
    echo "  vallm: $VALLM_OK"
    echo "  planfile: $PLANFILE_OK"
    exit 1
fi

echo "✅ All MCP services are running"
echo ""
echo "Running pipeline demo..."
python3 main.py
