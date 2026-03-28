#!/usr/bin/env python3
"""Example 25: Local Model Comparison - Simplified using algitex library."""

import sys
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    """Simplified version using algitex Project class."""
    print("=" * 60)
    print("Example 25: Local Model Comparison (Simplified)")
    print("=" * 60)
    print()
    
    # Initialize project
    p = Project(".")
    
    # Check Ollama
    ollama_status = p.check_ollama()
    if not ollama_status["healthy"]:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    models = ollama_status["details"]["models"]
    print(f"✅ Ollama running with {len(models)} models")
    
    # Check for benchmark models
    benchmark_models = ["qwen2.5-coder:3b", "qwen2.5-coder:7b", "llama3:8b", "codellama:7b"]
    available = [m for m in benchmark_models if any(m in model for model in models)]
    
    if available:
        print(f"   Models to test: {', '.join(available)}")
    else:
        print("   ⚠️  No benchmark models found")
        print("   Install with:")
        for model in benchmark_models:
            print(f"      ollama pull {model}")
    
    print()
    print("Available commands:")
    print("  python benchmark_simplified.py")
    print("  python benchmark_simplified.py --models qwen2.5-coder:7b llama3:8b")
    print()
    print("Features:")
    print("  - Compare models on standardized tasks")
    print("  - Quality scoring and performance metrics")
    print("  - Detailed results tables")
    print("  - JSON export for analysis")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
