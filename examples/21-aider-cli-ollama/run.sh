#!/usr/bin/env bash
set -e

echo "=============================================="
echo "Example 21: Aider CLI + Ollama"
echo "=============================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
python main.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Prerequisites not satisfied"
    exit 1
fi

echo ""
echo "=============================================="
echo "Step 1: Create TODO.md with prefact -a"
echo "=============================================="

if [ -f "TODO.md" ]; then
    echo "TODO.md already exists. Skipping prefact -a"
else
    echo "Running: prefact -a"
    prefact -a
fi

echo ""
echo "=============================================="
echo "Step 2: Review TODO.md (first 20 lines)"
echo "=============================================="

head -20 TODO.md

echo ""
echo "=============================================="
echo "Step 3: Run auto_fix.py --dry-run"
echo "=============================================="
echo ""
echo "This shows what would be fixed without making changes:"
echo ""

python auto_fix.py --dry-run --limit 3

echo ""
echo "=============================================="
echo "✅ Demo Complete!"
echo "=============================================="
echo ""
echo "To actually fix code:"
echo "  python auto_fix.py           # Fix all issues"
echo "  python auto_fix.py --limit 5 # Fix first 5 only"
echo "  python auto_fix.py --dry-run # Preview changes"
echo ""
echo "Requirements:"
echo "  - Ollama running: ollama serve"
echo "  - Model pulled: ollama pull qwen2.5-coder:7b"
echo "  - aider installed: pip install aider-chat"
echo ""
