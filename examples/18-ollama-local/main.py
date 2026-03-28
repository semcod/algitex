#!/usr/bin/env python3
"""Example 18: Ollama Local - Local LLM Integration Demo.

Demonstrates using local LLMs through Ollama without external API keys.
All processing happens locally - no code sent to cloud.
"""

import os
import subprocess
import json
from pathlib import Path


def load_env():
    """Load .env file if present."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = val


def check_ollama():
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, "Ollama installed but not running"
    except FileNotFoundError:
        return False, "Ollama not found. Install from https://ollama.com"
    except subprocess.TimeoutExpired:
        return False, "Ollama timeout - service may be starting"


def list_local_models():
    """List downloaded models."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        models = []
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if parts:
                    models.append(parts[0])
        return models
    except Exception:
        return []


def demo_local_analysis():
    """Demonstrate local code analysis."""
    print("\n=== Local Code Analysis ===\n")
    
    # Sample code to analyze
    sample_code = '''
def process_data(data):
    result = []
    for item in data:
        if item.active:
            result.append(transform(item))
    return result
'''
    
    models = list_local_models()
    
    if not models:
        print("⚠️  No local models found")
        print("Download a model with: ollama pull qwen2.5-coder:7b")
        return
    
    print(f"Available models: {', '.join(models)}")
    print(f"\nAnalyzing code sample...")
    print(f"Code:\n{sample_code}")
    
    # Simulate what would happen with local model
    print("\n📋 What Ollama would analyze:")
    print("   - Function complexity")
    print("   - Potential optimizations")
    print("   - Type hint suggestions")
    print("   - Docstring recommendations")
    
    if "qwen2.5-coder:7b" in models:
        print("\n✅ qwen2.5-coder:7b is ready for code tasks")
    else:
        print("\n⚠️  Recommended: ollama pull qwen2.5-coder:7b")


def demo_cost_comparison():
    """Compare costs: local vs cloud."""
    print("\n=== Cost Comparison: Local vs Cloud ===\n")
    
    scenarios = [
        ("Small refactor (1K tokens)", 1),
        ("Batch analysis (10K tokens)", 10),
        ("Full project (100K tokens)", 100),
    ]
    
    cloud_cost_per_1k = 0.003  # $0.003 per 1K tokens (GPT-4 mini)
    
    print(f"{'Scenario':<25} {'Cloud Cost':<15} {'Local Cost':<15} {'Savings':<15}")
    print("-" * 70)
    
    for name, tokens_k in scenarios:
        cloud = tokens_k * cloud_cost_per_1k
        local = 0  # Local is free (electricity negligible)
        savings = cloud
        print(f"{name:<25} ${cloud:>10.4f}    ${local:>10.4f}    ${savings:>10.4f}")
    
    print("-" * 70)
    print("\n💡 Local LLM = Zero API costs, full privacy")


def demo_offline_workflow():
    """Show offline workflow capabilities."""
    print("\n=== Offline Workflow ===\n")
    
    workflow = [
        ("1. Code Analysis", "Analyze local files with code2llm", "✅ Offline"),
        ("2. Generate Tickets", "Create tickets from analysis", "✅ Offline"),
        ("3. Refactor Code", "Use aider-mcp with local model", "✅ Offline"),
        ("4. Validate", "Run vallm validation", "✅ Offline"),
        ("5. Documentation", "Generate docs locally", "✅ Offline"),
    ]
    
    for step, desc, status in workflow:
        print(f"{step}")
        print(f"   {desc}")
        print(f"   Status: {status}")
        print()
    
    print("🎯 Entire pipeline works without internet connection!")


def demo_integration():
    """Show integration with algitex."""
    print("\n=== Integration with Algitex ===\n")
    
    print("CLI commands with local model:")
    print()
    print("  # Use local model for all operations")
    print("  export DEFAULT_MODEL=ollama/qwen2.5-coder:7b")
    print()
    print("  # Initialize project")
    print("  algitex init .")
    print()
    print("  # Run analysis (local)")
    print("  algitex analyze --model ollama/qwen2.5-coder:7b")
    print()
    print("  # Ask questions (local)")
    print("  algitex ask 'Refactor this function' --model ollama/qwen2.5-coder:7b")
    print()
    print("  # Run workflow (local)")
    print("  algitex workflow run refactor.md --model ollama/qwen2.5-coder:7b")


def show_requirements():
    """Show system requirements."""
    print("\n=== System Requirements ===\n")
    
    reqs = [
        ("CPU", "4+ cores recommended", "2 cores minimum"),
        ("RAM", "16GB recommended", "8GB minimum"),
        ("Disk", "10GB per 7B model", "SSD recommended"),
        ("GPU", "Optional - speeds up inference", "CPU works fine"),
    ]
    
    print(f"{'Component':<15} {'Recommended':<25} {'Minimum':<25}")
    print("-" * 65)
    for comp, rec, min_val in reqs:
        print(f"{comp:<15} {rec:<25} {min_val:<25}")
    
    print("\n💻 Models run on CPU if no GPU available (slower but works)")


if __name__ == "__main__":
    load_env()
    
    print("=" * 60)
    print("Example 18: Ollama Local - Local LLM Integration")
    print("=" * 60)
    
    # Check Ollama status
    running, msg = check_ollama()
    if running:
        print("\n✅ Ollama is running")
        models = list_local_models()
        if models:
            print(f"   Models: {', '.join(models)}")
    else:
        print(f"\n⚠️  {msg}")
        print("   This example will run in demo mode")
    
    # Run demos
    demo_local_analysis()
    demo_cost_comparison()
    demo_offline_workflow()
    demo_integration()
    show_requirements()
    
    print("\n" + "=" * 60)
    print("Key benefits of local LLMs:")
    print("  1. 🔒 Code privacy - nothing leaves your machine")
    print("  2. 💰 Zero API costs")
    print("  3. 🌐 Works offline")
    print("  4. ⚡ No network latency")
    print("=" * 60)
