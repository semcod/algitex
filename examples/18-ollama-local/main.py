#!/usr/bin/env python3
"""Example 18: Ollama Local - Local LLM Integration with practical demo"""

import os
import sys
import requests
import json

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen2.5-coder:7b")


def check_ollama() -> Any:
    """Check if Ollama is running."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except:
        return False


def list_models() -> Any:
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


def generate_code(prompt: str, model: str = None) -> str:
    """Generate code using local Ollama model."""
    model = model or DEFAULT_MODEL
    
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": f"You are a Python expert. Write clean, well-documented code.\n\nTask: {prompt}\n\nCode:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            },
            timeout=60
        )
        
        if r.status_code == 200:
            data = r.json()
            return data.get('response', '')
        else:
            return f"Error: {r.status_code}"
    except Exception as e:
        return f"Error generating code: {e}"


def analyze_code(code: str, model: str = None) -> dict:
    """Analyze code using local Ollama model."""
    model = model or DEFAULT_MODEL
    
    prompt = f"""Analyze this Python code and provide feedback in JSON format.
Focus on: complexity, issues, and suggestions.

Code:
```python
{code}
```

Respond with JSON only:
{{
    "complexity": "low/medium/high",
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"]
}}"""
    
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 300
                }
            },
            timeout=60
        )
        
        if r.status_code == 200:
            data = r.json()
            response = data.get('response', '{}')
            try:
                return json.loads(response)
            except:
                return {"raw_response": response[:200]}
        else:
            return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def demo_code_generation() -> None:
    """Demo: Generate a function using local LLM."""
    print("\n📝 Demo 1: Code Generation")
    print("-" * 60)
    print(f"Generating Python function using {DEFAULT_MODEL}...")
    print()
    
    prompt = "Write a Python function to calculate Fibonacci numbers with memoization"
    code = generate_code(prompt)
    
    print("Generated code:")
    print("```python")
    print(code[:500] if len(code) > 500 else code)
    print("```")
    if len(code) > 500:
        print(f"... ({len(code)} characters total)")


def demo_code_analysis():
    """Demo: Analyze code using local LLM."""
    print("\n🔍 Demo 2: Code Analysis")
    print("-" * 60)
    print(f"Analyzing code sample using {DEFAULT_MODEL}...")
    print()
    
    sample_code = '''
def process_data(data):
    result = []
    for item in data:
        if item.active:
            result.append(transform(item))
    return result
'''
    
    print("Code to analyze:")
    print("```python")
    print(sample_code)
    print("```")
    print()
    
    analysis = analyze_code(sample_code)
    
    if "error" in analysis:
        print(f"⚠️  Analysis error: {analysis['error']}")
    else:
        print("Analysis results:")
        for key, value in analysis.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value[:3]:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")


def demo_cost_comparison():
    """Demo: Compare local vs cloud costs."""
    print("\n💰 Demo 3: Cost Comparison")
    print("-" * 60)
    
    scenarios = [
        ("Small refactor", 1000, 0.003),
        ("Batch analysis", 10000, 0.030),
        ("Full project", 100000, 0.300),
    ]
    
    print(f"{'Scenario':<25} {'Cloud Cost':>12} {'Local Cost':>12} {'Savings':>12}")
    print("-" * 60)
    
    for name, tokens, cloud_cost in scenarios:
        local_cost = 0.0
        savings = cloud_cost
        print(f"{name:<25} ${cloud_cost:>11.4f} ${local_cost:>11.4f} ${savings:>11.4f}")
    
    print()
    print("💡 Local LLM = Zero API costs, full privacy")


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
        
        if DEFAULT_MODEL not in models and not any(DEFAULT_MODEL in m for m in models):
            print(f"\n⚠️  Default model '{DEFAULT_MODEL}' not found.")
            print(f"   Available: {', '.join(models[:3])}...")
            print(f"   Pull with: ollama pull {DEFAULT_MODEL}")
    else:
        print("\n⚠️  No models found. Pull one with:")
        print("   ollama pull qwen2.5-coder:7b")
        return 1
    
    demo_code_generation()
    demo_code_analysis()
    demo_cost_comparison()
    
    print("\n" + "=" * 60)
    print("Key benefits of local LLMs:")
    print("  1. 🔒 Code privacy - nothing leaves your machine")
    print("  2. 💰 Zero API costs")
    print("  3. 🌐 Works offline")
    print("  4. ⚡ No network latency")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Use with Algitex CLI:")
    print("     export DEFAULT_MODEL=ollama/qwen2.5-coder:7b")
    print("     algitex analyze --model ollama/qwen2.5-coder:7b")
    print()
    print("  2. Try local MCP pipeline:")
    print("     cd ../19-local-mcp-tools && make run")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
