#!/usr/bin/env python3
"""Main entry for model comparison example."""

import sys


def main():
    print("=" * 60)
    print("Example 25: Local Model Comparison")
    print("=" * 60)
    print()
    print("This example compares different Ollama models on coding tasks.")
    print()
    print("Commands:")
    print("  make setup       # Check available models")
    print("  make benchmark   # Run comparison")
    print("  make results     # Show latest results")
    print()
    print("Models tested:")
    print("  - qwen2.5-coder:3b  (fast)")
    print("  - qwen2.5-coder:7b  (balanced)")
    print("  - llama3:8b         (general)")
    print("  - codellama:7b      (code-specific)")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
