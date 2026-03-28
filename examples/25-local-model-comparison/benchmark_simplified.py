#!/usr/bin/env python3
"""
Model benchmark script: Simplified version using algitex library.
Compares different Ollama models on standardized tasks.

Usage:
    python benchmark_simplified.py
    python benchmark_simplified.py --models qwen2.5-coder:7b llama3:8b
"""

import sys
import argparse
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Ollama models using algitex"
    )
    parser.add_argument(
        "--models", "-m",
        nargs="+",
        help="Models to benchmark (default: auto-detect)"
    )
    parser.add_argument(
        "--tasks", "-t",
        nargs="+",
        help="Tasks to run (default: all)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["table", "summary", "detailed"],
        default="table",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Model Benchmark with Algitex")
    print("=" * 60)
    
    # Initialize project
    p = Project(".")
    
    # Check Ollama
    ollama_status = p.check_ollama()
    if not ollama_status["healthy"]:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    # Get models to test
    if args.models:
        models = args.models
    else:
        # Auto-detect suitable models
        all_models = ollama_status["details"]["models"]
        preferred = ["qwen2.5-coder:3b", "qwen2.5-coder:7b", "llama3:8b", "codellama:7b"]
        models = [m for m in preferred if any(m in model for model in all_models)]
    
    if not models:
        print("❌ No models found to benchmark")
        return 1
    
    print(f"Models to test: {', '.join(models)}")
    print()
    
    # Add custom task example
    p.add_benchmark_task(
        "python_optimization",
        "Python Optimization",
        "Optimize this Python code for better performance:\n\ndef sum_squares(n):\n    total = 0\n    for i in range(n):\n        total += i * i\n    return total",
        ["sum", "range", "comprehension", "optimized"]
    )
    
    # Run benchmark
    print("Running benchmark...")
    results = p.benchmark_models(models, args.tasks)
    
    # Print results
    p.print_benchmark_results(results, args.format)
    
    # Save results
    from algitex.tools.benchmark import ModelBenchmark
    benchmark = ModelBenchmark(p.ollama.client)
    
    # Convert back to BenchmarkResults for saving
    from algitex.tools.benchmark import BenchmarkResults, TaskResult
    benchmark_results = BenchmarkResults()
    benchmark_results.timestamp = results["timestamp"]
    
    for r in results["results"]:
        result = TaskResult(
            model=r["model"],
            task_id=r["task_id"],
            success=r["success"],
            time_seconds=r["time_seconds"],
            tokens_estimated=r["tokens_estimated"],
            quality_score=r["quality_score"],
            response=r.get("response_preview", ""),
            error=r.get("error")
        )
        benchmark_results.results.append(result)
    
    benchmark.save_results(benchmark_results)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
