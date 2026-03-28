#!/usr/bin/env python3
"""
Example 25: Local Model Comparison
Demonstrates model benchmarking with algitex.tools.benchmark.
"""

import sys
import argparse
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex.tools.benchmark import ModelBenchmark
from algitex.tools.ollama import OllamaClient


def main():
    parser = argparse.ArgumentParser(description="Compare Ollama models on coding tasks")
    parser.add_argument("--models", "-m", nargs="+", default=None, help="Models to test")
    parser.add_argument("--tasks", "-t", nargs="+", default=None, help="Tasks to run")
    parser.add_argument("--format", "-f", choices=["table", "summary", "detailed"], default="table", help="Output format")
    parser.add_argument("--save", "-s", action="store_true", help="Save results to file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Example 25: Local Model Comparison")
    print("=" * 60)
    print()
    
    # Initialize Ollama client
    client = OllamaClient()
    
    # Check Ollama
    if not client.health():
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    print(f"✅ Ollama running")
    
    # Get available models
    available_models = [m.name for m in client.list_models()]
    
    if not available_models:
        print("❌ No models available")
        print("   Pull a model: ollama pull qwen2.5-coder:7b")
        return 1
    
    print(f"✅ Found {len(available_models)} models")
    
    # Select models to test
    if args.models:
        # Validate requested models
        models = []
        for model in args.models:
            if any(model in m for m in available_models):
                models.append(m for m in available_models if model in m)[0]
            else:
                print(f"⚠️  Model {model} not found, skipping")
    else:
        # Default to coding models
        coding_models = [m for m in available_models if any(x in m for x in ["coder", "code", "llama"])]
        models = coding_models[:4] if coding_models else available_models[:4]
    
    if not models:
        print("❌ No suitable models found")
        return 1
    
    print(f"\nTesting models: {', '.join(models)}")
    
    # Create benchmark
    benchmark = ModelBenchmark(client, default_tasks=True)
    
    # Add custom tasks if specified
    if args.tasks:
        # For demo, we'll use default tasks
        print(f"Note: Using default benchmark tasks")
    
    # Run benchmark
    print(f"\nRunning benchmark...")
    results = benchmark.compare_models(models, progress=True)
    
    # Show results
    print()
    benchmark.print_results(results, format=args.format)
    
    # Save results if requested
    if args.save:
        benchmark.save_results(results)
    
    # Show example usage
    print("\n" + "=" * 60)
    print("Advanced Usage")
    print("=" * 60)
    print("""
For custom benchmarks, use algitex.tools.benchmark directly:

```python
from algitex.tools.benchmark import ModelBenchmark, Task
from algitex.tools.ollama import OllamaClient

# Create benchmark
client = OllamaClient()
benchmark = ModelBenchmark(client, default_tasks=False)

# Add custom task
benchmark.add_custom_task(
    "my_task",
    "My Custom Task",
    "Write a function that...",
    expected_keywords=["def", "return", "function"]
)

# Run comparison
results = benchmark.compare_models(["model1", "model2"])

# Get best model
best = results.get_best_model("my_task", "quality")
```
""")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
