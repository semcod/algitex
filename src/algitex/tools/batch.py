"""Batch processing — parallel LLM operations with rate limiting and retries.

Usage:
    from algitex.tools.batch import BatchProcessor
    
    # Define processing function
    def process_file(file_path):
        with open(file_path) as f:
            content = f.read()
        return ollama.generate(f"Analyze: {content}")
    
    # Create processor
    processor = BatchProcessor(
        worker_func=process_file,
        parallelism=4,
        rate_limit=2.0,  # requests per second
        max_retries=3
    )
    
    # Process files
    results = processor.process(file_list)
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

try:
    import tqdm  # Optional, for progress bars
    HAS_TQDM = True
except ImportError:
    tqdm = None
    HAS_TQDM = False


@dataclass
class BatchResult:
    """Result from batch processing."""
    item: Any
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    attempt: int = 1
    time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "item": self.item,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "attempt": self.attempt,
            "time_ms": self.time_ms
        }


@dataclass
class BatchStats:
    """Statistics for batch processing."""
    total: int = 0
    successful: int = 0
    failed: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    throughput: float = 0.0  # items per second
    
    def update(self, results: List[BatchResult]):
        """Update stats from results."""
        self.total = len(results)
        self.successful = sum(1 for r in results if r.success)
        self.failed = self.total - self.successful
        self.total_time_ms = sum(r.time_ms for r in results)
        self.avg_time_ms = self.total_time_ms / self.total if self.total > 0 else 0
        self.throughput = 1000 / self.avg_time_ms if self.avg_time_ms > 0 else 0


class BatchProcessor:
    """Generic batch processor with rate limiting and retries."""
    
    def __init__(
        self,
        worker_func: Callable[[Any], Any],
        parallelism: int = 4,
        rate_limit: float = 2.0,  # requests per second
        max_retries: int = 3,
        timeout: float = 300.0,
        backoff_factor: float = 2.0,
        progress: bool = True,
        save_results: bool = True,
        output_dir: str = ".batch_results"
    ):
        self.worker_func = worker_func
        self.parallelism = parallelism
        self.rate_limit = rate_limit
        self.rate_limit_delay = 1.0 / rate_limit if rate_limit > 0 else 0
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_factor = backoff_factor
        self.progress = progress
        self.save_results = save_results
        self.output_dir = Path(output_dir)
        
        # Rate limiting state
        self.last_request_time = 0.0
        self._rate_lock = None
        
        # Results
        self.results: List[BatchResult] = []
        self.stats = BatchStats()
    
    def _rate_limit(self):
        """Apply rate limiting."""
        if self.rate_limit_delay <= 0:
            return
        
        import threading
        if self._rate_lock is None:
            self._rate_lock = threading.Lock()
        
        with self._rate_lock:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
            self.last_request_time = time.time()
    
    def _process_item(self, item: Any, attempt: int = 1) -> BatchResult:
        """Process single item with retry logic."""
        start_time = time.time()
        
        try:
            # Apply rate limiting
            self._rate_limit()
            
            # Call worker function
            result = self.worker_func(item)
            
            elapsed = (time.time() - start_time) * 1000
            
            return BatchResult(
                item=item,
                success=True,
                result=result,
                attempt=attempt,
                time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            
            # Retry logic
            if attempt < self.max_retries:
                # Exponential backoff
                backoff = self.backoff_factor ** (attempt - 1)
                time.sleep(backoff)
                return self._process_item(item, attempt + 1)
            
            return BatchResult(
                item=item,
                success=False,
                error=str(e),
                attempt=attempt,
                time_ms=elapsed
            )
    
    def process(
        self,
        items: List[Any],
        progress_callback: Optional[Callable[[BatchResult], None]] = None
    ) -> List[BatchResult]:
        """Process items in parallel."""
        print(f"Processing {len(items)} items with {self.parallelism} workers")
        print(f"Rate limit: {self.rate_limit} req/s, Max retries: {self.max_retries}")
        print()
        
        self.results = []
        start_time = time.time()
        
        # Progress bar
        pbar = None
        if self.progress and HAS_TQDM:
            pbar = tqdm.tqdm(total=len(items), desc="Processing")
        elif self.progress and not HAS_TQDM:
            print("Install tqdm for progress bars: pip install tqdm")
            self.progress = False
        
        # Process in parallel
        with ThreadPoolExecutor(max_workers=self.parallelism) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(self._process_item, item): item
                for item in items
            }
            
            # Collect results
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    # Update progress
                    if pbar:
                        pbar.update(1)
                        status = "✅" if result.success else "❌"
                        pbar.set_postfix_str(f"{status} {self.results[-1].successful}/{len(self.results)}")
                    
                    # Custom callback
                    if progress_callback:
                        progress_callback(result)
                        
                except Exception as e:
                    item = future_to_item[future]
                    error_result = BatchResult(
                        item=item,
                        success=False,
                        error=str(e),
                        time_ms=0
                    )
                    self.results.append(error_result)
                    if pbar:
                        pbar.update(1)
        
        if pbar:
            pbar.close()
        
        # Update stats
        self.stats.update(self.results)
        total_time = (time.time() - start_time) * 1000
        
        # Print summary
        print()
        print(f"Completed in {total_time/1000:.1f}s")
        print(f"✅ Successful: {self.stats.successful}")
        print(f"❌ Failed: {self.stats.failed}")
        print(f"Throughput: {self.stats.throughput:.2f} items/s")
        
        # Save results
        if self.save_results:
            self._save_results()
        
        return self.results
    
    def _save_results(self):
        """Save results to JSON file."""
        self.output_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"batch_{timestamp}.json"
        
        # Prepare data for JSON serialization
        serializable_results = []
        for r in self.results:
            data = r.to_dict()
            # Handle non-serializable items
            if isinstance(data["item"], Path):
                data["item"] = str(data["item"])
            serializable_results.append(data)
        
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "stats": {
                    "total": self.stats.total,
                    "successful": self.stats.successful,
                    "failed": self.stats.failed,
                    "total_time_ms": self.stats.total_time_ms,
                    "avg_time_ms": self.stats.avg_time_ms,
                    "throughput": self.stats.throughput
                },
                "config": {
                    "parallelism": self.parallelism,
                    "rate_limit": self.rate_limit,
                    "max_retries": self.max_retries,
                    "timeout": self.timeout
                },
                "results": serializable_results
            }, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
    
    def get_successful(self) -> List[BatchResult]:
        """Get only successful results."""
        return [r for r in self.results if r.success]
    
    def get_failed(self) -> List[BatchResult]:
        """Get only failed results."""
        return [r for r in self.results if not r.success]
    
    def filter_by_error(self, error_pattern: str) -> List[BatchResult]:
        """Get results with specific error pattern."""
        import re
        pattern = re.compile(error_pattern, re.IGNORECASE)
        return [r for r in self.results if r.error and pattern.search(r.error)]


class FileBatchProcessor(BatchProcessor):
    """Specialized batch processor for files."""
    
    def __init__(
        self,
        ollama_client,
        model: str = None,
        prompt_template: str = None,
        max_file_size: int = 10000,  # characters
        **kwargs
    ):
        self.ollama_client = ollama_client
        self.model = model
        self.prompt_template = prompt_template or (
            "Analyze this Python code and provide brief feedback:\n"
            "1. Complexity (low/medium/high)\n"
            "2. Main issues (if any)\n"
            "3. Quick improvement suggestions\n\n"
            "Code:\n```python\n{content}\n```\n\nBe concise."
        )
        self.max_file_size = max_file_size
        
        # Default worker function for file processing
        def analyze_file(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Truncate large files
            if len(content) > self.max_file_size:
                content = content[:self.max_file_size] + "\n... (truncated)"
            
            prompt = self.prompt_template.format(content=content)
            response = self.ollama_client.generate(prompt, model=self.model)
            return str(response)
        
        super().__init__(worker_func=analyze_file, **kwargs)
    
    def find_files(
        self,
        directory: Union[str, Path],
        pattern: str = "*.py",
        exclude_patterns: List[str] = None
    ) -> List[Path]:
        """Find files matching pattern."""
        directory = Path(directory)
        files = []
        exclude_patterns = exclude_patterns or ["__pycache__", ".git", "venv"]
        
        for path in directory.rglob(pattern):
            if path.is_file():
                # Check exclusions
                if not any(excl in str(path) for excl in exclude_patterns):
                    files.append(path)
        
        return sorted(files)
    
    def process_directory(
        self,
        directory: Union[str, Path],
        pattern: str = "*.py",
        **kwargs
    ) -> List[BatchResult]:
        """Process all files in directory."""
        files = self.find_files(directory, pattern)
        return self.process(files, **kwargs)
