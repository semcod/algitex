#!/usr/bin/env python3
"""Example 18: Ollama Local - Local LLM Integration"""

import os
import sys
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def check_ollama():
    """Check if Ollama is running."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except:
        return False


def list_models():
    """List available local models."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if r.status_code == 200:
            data = r.json()
            models = [m['name'] for m in data.get('models', [])]
            return models
    except Exception as e:
        print(f"Error: {e}")
    return []


def main():
    print("=" * 60)
    print("Example 18: Ollama Local - Local LLM Integration")
    print("=" * 60)
    print()
    
    if not check_ollama():
        print("❌ Ollama is not running")
        print("   Start it with: ollama serve")
        return 1
    
    print("✅ Ollama is running")
    
    models = list_models()
    if models:
        print(f"\n📦 Available models: {', '.join(models[:5])}")
        print(f"   (and {len(models) - 5} more...)" if len(models) > 5 else "")
    else:
        print("\n⚠️  No models found. Pull one with:")
        print("   ollama pull qwen2.5-coder:7b")
    
    print("\n" + "=" * 60)
    print("Key benefits of local LLMs:")
    print("  1. 🔒 Code privacy - nothing leaves your machine")
    print("  2. 💰 Zero API costs")
    print("  3. 🌐 Works offline")
    print("  4. ⚡ No network latency")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
