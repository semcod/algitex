#!/usr/bin/env python3
"""
Batch processing script: Simplified version using algitex library.
Analyzes multiple files in parallel with rate limiting and retries.

Usage:
    python batch_simplified.py --directory . --pattern "*.py"
    python batch_simplified.py --parallelism 8 --rate-limit 5
"""

import sys
import argparse
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main():
    parser = argparse.ArgumentParser(
        description="Batch analyze files using algitex"
    )
    parser.add_argument(
        "--directory", "-d",
        default=".",
        help="Directory to scan"
    )
    parser.add_argument(
        "--pattern", "-p",
        default="*.py",
        help="File pattern"
    )
    parser.add_argument(
        "--parallel", "-j",
        type=int,
        default=4,
        help="Number of parallel workers"
    )
    parser.add_argument(
        "--rate-limit", "-r",
        type=float,
        default=2.0,
        help="Rate limit (requests per second)"
    )
    parser.add_argument(
        "--model", "-m",
        help="Ollama model to use"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Batch Processing with Algitex")
    print("=" * 60)
    print(f"Directory: {args.directory}")
    print(f"Pattern: {args.pattern}")
    print(f"Workers: {args.parallel}")
    print(f"Rate limit: {args.rate_limit} req/s")
    print()
    
    # Initialize project
    p = Project(".")
    
    # Check Ollama
    ollama_status = p.check_ollama()
    if not ollama_status["healthy"]:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    # Set model if specified
    if args.model:
        p.batch.model = args.model
    
    # Run batch analysis
    print("Starting batch analysis...")
    result = p.batch_analyze(
        directory=args.directory,
        pattern=args.pattern,
        parallelism=args.parallel,
        rate_limit=args.rate_limit
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total files: {result['total']}")
    print(f"✅ Successful: {result['successful']}")
    print(f"❌ Failed: {result['failed']}")
    
    # Show failed files if any
    if result['failed'] > 0:
        print("\nFailed files:")
        for r in result['results']:
            if not r['success']:
                print(f"  - {r['item']}: {r.get('error', 'Unknown')}")
    
    print(f"\nResults saved to: .batch_results/")
    
    return 0 if result['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
