#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Local MCP Tools Example ==="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found!"
    echo "Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check docker compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found!"
    exit 1
fi

echo "✅ Docker is available"
echo ""

# Check if tools are running
TOOLS=$(docker ps --filter "name=-mcp" --format "{{.Names}}" 2>/dev/null || true)

if [ -z "$TOOLS" ]; then
    echo "⚠️  No MCP tools are running"
    echo ""
    echo "To start local tools:"
    echo "  cd ../.."
    echo "  docker compose --profile tools up -d"
    echo ""
    echo "This will build and start:"
    echo "  - code2llm-mcp (port 8081)"
    echo "  - vallm-mcp (port 8080)"
    echo "  - planfile-mcp (port 8201)"
    echo "  - aider-mcp (port 3000)"
    echo ""
else
    echo "✅ Running MCP tools:"
    echo "$TOOLS" | while read tool; do
        echo "  - $tool"
    done
    echo ""
fi

echo "Running Python demo..."
python3 main.py
