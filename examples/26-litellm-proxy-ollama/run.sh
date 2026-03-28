#!/usr/bin/env bash
set -e

echo "============================================================"
echo "Example 26: LiteLLM Proxy + Ollama"
echo "============================================================"
echo ""

# Check if litellm is installed, if not offer to install
if ! command -v litellm &> /dev/null; then
    echo "⚠️  litellm not found"
    echo ""
    echo "Installing litellm[proxy]..."
    pip install 'litellm[proxy]' --break-system-packages 2>/dev/null || pip install 'litellm[proxy]'
    echo "✅ litellm installed"
fi

# Check for apscheduler (common missing dependency)
python3 -c "import apscheduler" 2>/dev/null || {
    echo "⚠️  Missing apscheduler dependency"
    echo "Reinstalling litellm[proxy]..."
    pip install 'litellm[proxy]' --break-system-packages 2>/dev/null || pip install 'litellm[proxy]'
}

echo "✅ litellm found"
echo ""

python3 main.py
