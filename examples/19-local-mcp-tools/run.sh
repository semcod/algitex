#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Example 19: Local MCP Tools ==="
echo ""

# Check services
echo "Checking MCP services..."
CODE2LLM_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health 2>/dev/null || echo "000")
VALLM_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null || echo "000")
PLANFILE_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8201/health 2>/dev/null || echo "000")

if [ "$CODE2LLM_OK" != "200" ] || [ "$VALLM_OK" != "200" ] || [ "$PLANFILE_OK" != "200" ]; then
    echo "❌ Some MCP services are not running"
    echo "   Start them with: make up"
    echo ""
    echo "Status:"
    echo "  code2llm: $CODE2LLM_OK"
    echo "  vallm: $VALLM_OK"
    echo "  planfile: $PLANFILE_OK"
    exit 1
fi

echo "✅ All MCP services are running"
echo ""

python3 main.py
