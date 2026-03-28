#!/usr/bin/env python3
"""
Ollama Batch Processing - Parallel analysis of multiple files.
Demonstrates efficient batch processing with rate limiting and retries.
"""

import os
import sys
import json
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
PARALLELISM = int(os.getenv("BATCH_PARALLELISM", 4))
RATE_LIMIT = float(os.getenv("BATCH_RATE_LIMIT", 2))  # requests per second
RETRY_ATTEMPTS = int(os.getenv("BATCH_RETRY_ATTEMPTS", 3))
TIMEOUT = int(os.getenv("BATCH_TIMEOUT", 300))


class BatchProcessor:
    """Batch processor for Ollama with rate limiting and retries."""
    
    def __init__(self, model: str = None, parallelism: int = None):
        self.model = model or DEFAULT_MODEL
        self.parallelism = parallelism or PARALLELISM
        self.rate_limit_delay = 1.0 / RATE_LIMIT
        self.last_request_time = 0
        self.results = []
        self.failed = []
    
    def _rate_limited_request(self, prompt: str) -> Dict[str, Any]:
        """Make rate-limited request to Ollama."""
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        
        self.last_request_time = time.time()
        
        # Make request
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500
                    }
                },
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json().get("response", ""),
                    "model": self.model
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_file(self, file_path: str, attempt: int = 1) -> Dict[str, Any]:
        """Analyze single file with retry logic."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Limit content size
            max_chars = 5000
            if len(content) > max_chars:
                content = content[:max_chars] + "\n... (truncated)"
            
            prompt = f"""Analyze this Python code and provide brief feedback:
1. Complexity (low/medium/high)
2. Main issues (if any)
3. Quick improvement suggestions

Code:
```python
{content}
```

Be concise."""
            
            result = self._rate_limited_request(prompt)
            
            if result["success"]:
                return {
                    "file": file_path,
                    "success": True,
                    "analysis": result["response"]
                }
            else:
                # Retry logic
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    return self._analyze_file(file_path, attempt + 1)
                else:
                    return {
                        "file": file_path,
                        "success": False,
                        "error": result.get("error", "Unknown error")
                    }
        except Exception as e:
            if attempt < RETRY_ATTEMPTS:
                time.sleep(2 ** attempt)
                return self._analyze_file(file_path, attempt + 1)
            return {
                "file": file_path,
                "success": False,
                "error": str(e)
            }
    
    def process_files(self, files: List[str], progress_callback=None) -> List[Dict]:
        """Process multiple files in parallel."""
        results = []
        completed = 0
        failed = 0
        
        print(f"Processing {len(files)} files with {self.parallelism} workers...")
        print(f"Rate limit: {RATE_LIMIT} req/s, Timeout: {TIMEOUT}s")
        print()
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.parallelism) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._analyze_file, f): f for f in files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["success"]:
                        completed += 1
                        status = "✅"
                    else:
                        failed += 1
                        status = "❌"
                    
                    # Progress
                    progress = len(results) / len(files) * 100
                    elapsed = time.time() - start_time
                    eta = (elapsed / len(results)) * (len(files) - len(results)) if len(results) > 0 else 0
                    
                    print(f"{status} [{len(results)}/{len(files)}] {file_path[:50]}... ({progress:.1f}%, ETA: {eta:.0f}s)")
                    
                    if progress_callback:
                        progress_callback(result)
                        
                except Exception as e:
                    print(f"❌ Exception for {file_path}: {e}")
                    failed += 1
        
        total_time = time.time() - start_time
        
        print()
        print(f"Completed in {total_time:.1f}s")
        print(f"✅ Successful: {completed}")
        print(f"❌ Failed: {failed}")
        
        return results


def find_files(directory: str, pattern: str = "*.py") -> List[str]:
    """Find files matching pattern."""
    files = []
    for path in Path(directory).rglob(pattern):
        if path.is_file():
            files.append(str(path))
    return sorted(files)


def save_results(results: List[Dict], output_dir: str = ".batch_results"):
    """Save results to JSON."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"analysis_{timestamp}.json")
    
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "model": DEFAULT_MODEL,
            "total_files": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Batch analyze files with Ollama")
    parser.add_argument("--dir", "-d", default=".", help="Directory to scan")
    parser.add_argument("--pattern", "-p", default="*.py", help="File pattern")
    parser.add_argument("--parallel", "-j", type=int, default=PARALLELISM, help="Parallelism")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="Ollama model")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Ollama Batch Processing")
    print("=" * 60)
    print()
    
    # Check Ollama
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code != 200:
            print("❌ Ollama not responding")
            return 1
        print(f"✅ Ollama running")
    except:
        print("❌ Ollama not running. Start: ollama serve")
        return 1
    
    # Find files
    print(f"Scanning {args.dir} for {args.pattern}...")
    files = find_files(args.dir, args.pattern)
    
    if not files:
        print(f"No files found matching {args.pattern}")
        return 0
    
    print(f"Found {len(files)} files")
    print()
    
    # Confirm
    if len(files) > 50:
        print(f"Large batch: {len(files)} files. This will take ~{len(files) // RATE_LIMIT // 60} minutes.")
        print("Press Ctrl+C to cancel, or wait 3 seconds to continue...")
        time.sleep(3)
    
    # Process
    processor = BatchProcessor(model=args.model, parallelism=args.parallel)
    results = processor.process_files(files)
    
    # Save
    save_results(results)
    
    # Summary
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total: {len(files)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if failed:
        print()
        print("Failed files:")
        for r in failed[:5]:
            print(f"  - {r['file']}: {r.get('error', 'Unknown')}")
    
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
