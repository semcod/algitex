#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "========================================"
echo "Self-Hosted Pipeline Example"
echo "========================================"
echo ""

# Check if running from repo root or example dir
if [ -f "../../docker-compose.yml" ]; then
    COMPOSE_DIR="../.."
elif [ -f "docker-compose.yml" ]; then
    COMPOSE_DIR="."
else
    echo "⚠️  Cannot find docker-compose.yml"
    echo "   Run from repo root or examples/20-self-hosted-pipeline/"
    exit 1
fi

echo "Checking stack status..."
echo ""

# Count running services
RUNNING=$(docker ps --filter "name=-mcp\|proxym\|redis" --format "{{.Names}}" 2>/dev/null | wc -l)

if [ "$RUNNING" -eq 0 ]; then
    echo "🔴 No services running"
    echo ""
    echo "To start the full stack:"
    echo "  cd $COMPOSE_DIR"
    echo "  make up"
    echo "  # or: docker compose --profile tools up -d"
    echo ""
else
    echo "🟢 $RUNNING services running"
    echo ""
    docker ps --filter "name=-mcp\|proxym\|redis" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || true
    echo ""
fi

echo "Running Python demo..."
python3 main.py

echo ""
echo "========================================"
echo "Quick commands:"
echo "  make up     - Start all services"
echo "  make down   - Stop all services"
echo "  make status - Check status"
echo "========================================"
