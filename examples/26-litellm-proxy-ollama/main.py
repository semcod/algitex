#!/usr/bin/env python3
"""
Example 26: LiteLLM Proxy + Ollama - Main setup script.
Checks prerequisites and configures the proxy.
"""

import os
import sys
import subprocess


def check_litellm():
    """Check if litellm is installed."""
    try:
        result = subprocess.run(
            ["which", "litellm"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except:
        return False


def list_ollama_models():
    """List available Ollama models."""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            models = r.json().get('models', [])
            return [m['name'] for m in models]
    except:
        pass
    return []


def test_proxy():
    """Test if liteLLM proxy is running."""
    try:
        import requests
        r = requests.get("http://localhost:4000/v1/models", timeout=2)
        if r.status_code == 200:
            models = r.json().get('data', [])
            return True, [m['id'] for m in models]
        return False, []
    except:
        return False, []


def main():
    print("=" * 60)
    print("Example 26: LiteLLM Proxy + Ollama")
    print("=" * 60)
    print()
    
    # Check liteLLM
    if check_litellm():
        print("✅ litellm installed")
    else:
        print("❌ litellm not found")
        print("   Install: pip install litellm")
        return 1
    
    # Check Ollama
    if check_ollama():
        models = list_ollama_models()
        print(f"✅ Ollama running ({len(models)} models)")
        
        # Check for recommended models
        recommended = ["qwen2.5-coder:7b", "qwen2.5-coder:3b", "llama3:8b"]
        found_recommended = [m for m in models if any(r in m for r in recommended)]
        if found_recommended:
            print(f"   Recommended models found: {', '.join(found_recommended[:3])}")
        else:
            print(f"   ⚠️  No recommended models found")
            print(f"   Pull: ollama pull qwen2.5-coder:7b")
    else:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    print()
    
    # Check proxy
    proxy_ok, proxy_models = test_proxy()
    if proxy_ok:
        print(f"✅ LiteLLM proxy running on :4000")
        print(f"   Available models: {', '.join(proxy_models)}")
    else:
        print("⚠️  LiteLLM proxy not running")
        print("   Start: make proxy")
    
    print()
    print("=" * 60)
    print("Next steps:")
    print("=" * 60)
    print()
    print("1. Start proxy:")
    print("   make proxy")
    print()
    print("2. In another terminal, analyze code:")
    print("   prefact -a")
    print()
    print("3. Fix issues:")
    print("   python auto_fix.py --limit 5")
    print()
    print("Or run full demo:")
    print("   make run")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
