#!/usr/bin/env python3
"""Example 25: Local Model Comparison - Simplified using algitex Project."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main() -> int:
    print("=" * 60)
    print("Example 25: Local Model Comparison")
    print("=" * 60)
    print()

    p = Project(".")

    # Check services
    print("Checking services...")
    p.print_service_status()

    # Check Ollama - this also initializes the ollama service needed for benchmark
    ollama_status = p.check_ollama()
    if not ollama_status["healthy"]:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1

    # Initialize ollama service for benchmark (needed for benchmark_models)
    _ = p._ollama_service

    models = ollama_status["details"]["models"]
    print(f"✅ Ollama running with {len(models)} models")

    # Select coding models for benchmark
    coding_models = [m for m in models if any(x in m for x in ["coder", "code", "llama"])]
    models_to_test = coding_models[:4] if coding_models else models[:4]

    if not models_to_test:
        print("❌ No suitable models found")
        return 1

    print(f"\nTesting models: {', '.join(models_to_test)}")

    # Run benchmark
    print("\nRunning benchmark...")
    results = p.benchmark_models(models_to_test)

    # Show results
    print(f"\nResults: {results['total']} comparisons")
    for r in results["results"]:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['model']}: {r['task_id']} ({r['time_seconds']:.1f}s)")

    print("\nNext steps:")
    print("  p.benchmark_models(['model1', 'model2'])")
    print("  p.add_benchmark_task('task_id', 'name', 'prompt', ['keyword'])")

    return 0


if __name__ == "__main__":
    sys.exit(main())
