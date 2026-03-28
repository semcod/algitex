#!/usr/bin/env python3
"""
Example 24: Ollama Batch Processing - Main demo.
"""

import os
import sys


def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except:
        return False


def main():
    print("=" * 60)
    print("Example 24: Ollama Batch Processing")
    print("=" * 60)
    print()
    
    if check_ollama():
        print("✅ Ollama running")
    else:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    print()
    print("Available commands:")
    print("  python batch_analyze.py --dir . --pattern '*.py'")
    print()
    print("Features:")
    print("  - Parallel processing (4 workers default)")
    print("  - Rate limiting (2 req/s)")
    print("  - Retry logic (3 attempts)")
    print("  - Progress tracking")
    print("  - Results saved to JSON")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
