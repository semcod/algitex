#!/usr/bin/env python3
"""
Example 24: Ollama Batch Processing
Demonstrates efficient batch processing with algitex.tools.batch.
"""

import sys
import argparse
from pathlib import Path

# Add algitex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex.tools.batch import FileBatchProcessor
from algitex.tools.ollama import OllamaClient


def main():
    parser = argparse.ArgumentParser(description="Batch analyze files with Ollama")
    parser.add_argument("--dir", "-d", default=".", help="Directory to scan")
    parser.add_argument("--pattern", "-p", default="*.py", help="File pattern")
    parser.add_argument("--parallel", "-j", type=int, default=4, help="Parallelism")
    parser.add_argument("--model", "-m", default="qwen2.5-coder:7b", help="Ollama model")
    parser.add_argument("--rate-limit", "-r", type=float, default=2.0, help="Rate limit (req/s)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Example 24: Ollama Batch Processing")
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
    
    # Check model
    models = [m.name for m in client.list_models()]
    if args.model not in models:
        print(f"❌ Model {args.model} not found")
        print(f"   Pull: ollama pull {args.model}")
        return 1
    
    print(f"✅ Using model: {args.model}")
    
    # Create batch processor
    processor = FileBatchProcessor(
        ollama_client=client,
        model=args.model,
        parallelism=args.parallel,
        rate_limit=args.rate_limit,
        max_file_size=5000
    )
    
    # Find files
    print(f"\nScanning {args.dir} for {args.pattern}...")
    files = processor.find_files(args.dir, args.pattern)
    
    if not files:
        print(f"No files found matching {args.pattern}")
        return 0
    
    print(f"Found {len(files)} files")
    
    # Confirm for large batches
    if len(files) > 50:
        print(f"\nLarge batch: {len(files)} files. This will take ~{len(files) // args.rate_limit // 60} minutes.")
        print("Press Ctrl+C to cancel, or wait 3 seconds to continue...")
        import time
        time.sleep(3)
    
    # Process files
    print(f"\nProcessing with {args.parallel} workers, {args.rate_limit} req/s rate limit...")
    results = processor.process(files)
    
    # Show summary
    successful = processor.get_successful()
    failed = processor.get_failed()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total: {len(files)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if failed:
        print("\nFailed files:")
        for r in failed[:5]:
            print(f"  - {r.item}: {r.error}")
    
    # Show example usage
    print("\n" + "=" * 60)
    print("Advanced Usage")
    print("=" * 60)
    print("""
For more control, use algitex.tools.batch directly:

```python
from algitex.tools.batch import BatchProcessor, FileBatchProcessor
from algitex.tools.ollama import OllamaClient

# Custom processing function
def custom_analyze(file_path):
    with open(file_path) as f:
        content = f.read()
    # Your custom logic here
    return analysis

# Create processor
processor = BatchProcessor(
    worker_func=custom_analyze,
    parallelism=8,
    rate_limit=4.0,
    max_retries=3
)

# Process files
results = processor.process(file_list)

# Get results
successful = processor.get_successful()
failed = processor.get_failed()
```
""")
    
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
