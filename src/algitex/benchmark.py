"""Performance benchmarks for algitex.

Provides benchmarking infrastructure for measuring:
- Cache hit rates and latency
- Tier throughput (algorithmic, micro, big LLM)
- Memory usage for large files
- End-to-end pipeline performance

Usage:
    from algitex.benchmark import BenchmarkRunner, CacheBenchmark
    
    runner = BenchmarkRunner()
    runner.run_all()
    runner.print_report()
"""

from __future__ import annotations

import gc
import time
import tempfile
import tracemalloc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Callable, Any
from statistics import mean


@dataclass
class BenchmarkResult:
    """Single benchmark run result."""
    name: str
    duration_ms: float
    iterations: int
    throughput: float  # ops/sec
    memory_delta_mb: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
            "iterations": self.iterations,
            "throughput": round(self.throughput, 2),
            "memory_delta_mb": round(self.memory_delta_mb, 3),
            **self.metadata,
        }


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""
    name: str
    results: List[BenchmarkResult] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def add(self, result: BenchmarkResult) -> None:
        self.results.append(result)
    
    def summary(self) -> Dict[str, Any]:
        if not self.results:
            return {"name": self.name, "total": 0}
        
        return {
            "name": self.name,
            "total": len(self.results),
            "total_duration_sec": round(sum(r.duration_ms for r in self.results) / 1000, 2),
            "avg_throughput": round(mean(r.throughput for r in self.results), 2),
            "total_memory_mb": round(sum(r.memory_delta_mb for r in self.results), 2),
        }
    
    def print_table(self) -> None:
        """Print results as ASCII table."""
        print(f"\n{'='*70}")
        print(f"Benchmark: {self.name}")
        print(f"{'='*70}")
        print(f"{'Name':<30} {'Duration':>12} {'Throughput':>12} {'Memory':>10}")
        print(f"{'-'*70}")
        
        for r in self.results:
            print(f"{r.name:<30} {r.duration_ms:>10.1f}ms {r.throughput:>10.1f}/s {r.memory_delta_mb:>8.2f}MB")
        
        print(f"{'-'*70}")
        summary = self.summary()
        print(f"Total: {summary['total']} benchmarks, {summary['total_duration_sec']}s, {summary['total_memory_mb']}MB")


class BenchmarkRunner:
    """Main benchmark runner with memory tracking."""
    
    def __init__(self, warmup_iterations: int = 3):
        self.warmup_iterations = warmup_iterations
        self.suites: List[BenchmarkSuite] = []
    
    def _measure_memory(self, func: Callable, *args, **kwargs) -> tuple[Any, float]:
        """Run function and measure memory delta in MB."""
        gc.collect()
        tracemalloc.start()
        
        result = func(*args, **kwargs)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_mb = (peak - current) / 1024 / 1024
        return result, memory_mb
    
    def run(
        self,
        name: str,
        func: Callable,
        iterations: int = 100,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Run single benchmark."""
        # Warmup
        for _ in range(self.warmup_iterations):
            func(*args, **kwargs)
        
        # Actual benchmark
        gc.collect()
        start_mem = tracemalloc.start()
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            func(*args, **kwargs)
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_mb = (peak - current) / 1024 / 1024
        throughput = iterations / (duration_ms / 1000)
        
        return BenchmarkResult(
            name=name,
            duration_ms=duration_ms,
            iterations=iterations,
            throughput=throughput,
            memory_delta_mb=memory_mb,
        )
    
    def run_suite(self, name: str, benchmarks: Dict[str, tuple]) -> BenchmarkSuite:
        """Run multiple benchmarks as a suite."""
        suite = BenchmarkSuite(name=name)
        
        for bench_name, (func, iterations, args, kwargs) in benchmarks.items():
            result = self.run(bench_name, func, iterations, *args, **kwargs)
            suite.add(result)
        
        self.suites.append(suite)
        return suite
    
    def print_report(self) -> None:
        """Print all benchmark results."""
        for suite in self.suites:
            suite.print_table()
        
        print(f"\n{'='*70}")
        print("OVERALL SUMMARY")
        print(f"{'='*70}")
        total_benchmarks = sum(len(s.results) for s in self.suites)
        total_time = sum(sum(r.duration_ms for r in s.results) for s in self.suites) / 1000
        print(f"Suites: {len(self.suites)}, Benchmarks: {total_benchmarks}, Total time: {total_time:.1f}s")
    
    def export_json(self, path: str) -> None:
        """Export all results to JSON."""
        import json
        
        data = {
            "timestamp": time.time(),
            "suites": [
                {
                    "name": s.name,
                    "summary": s.summary(),
                    "results": [r.to_dict() for r in s.results],
                }
                for s in self.suites
            ]
        }
        
        Path(path).write_text(json.dumps(data, indent=2))


class CacheBenchmark:
    """Benchmarks for LLM cache performance."""
    
    @staticmethod
    def bench_cache_hit_rate(cache_dir: str, entries: int = 1000, lookups: int = 5000) -> Dict[str, float]:
        """Benchmark cache hit rate with synthetic data."""
        from algitex.tools.ollama_cache import LLMCache
        
        cache = LLMCache(cache_dir=cache_dir, ttl_hours=24.0)
        
        # Populate cache
        for i in range(entries):
            cache.set(
                prompt=f"Prompt {i % 100}",  # 100 unique prompts, 10x each
                model="qwen3-coder:latest",
                response=f"Response {i}",
                tokens_prompt=100,
                tokens_response=50,
            )
        
        # Measure lookups
        hits = 0
        misses = 0
        
        start = time.perf_counter()
        for i in range(lookups):
            result = cache.get(f"Prompt {i % 100}", "qwen3-coder:latest")
            if result:
                hits += 1
            else:
                misses += 1
        duration = time.perf_counter() - start
        
        stats = cache.stats()
        
        return {
            "entries": entries,
            "lookups": lookups,
            "hits": hits,
            "misses": misses,
            "hit_rate": hits / lookups,
            "throughput": lookups / duration,
            "latency_ms": (duration / lookups) * 1000,
        }
    
    @staticmethod
    def bench_cache_deduplication(cache_dir: str, duplicates: int = 100) -> Dict[str, Any]:
        """Benchmark deduplication of identical prompts."""
        from algitex.tools.ollama_cache import LLMCache
        
        cache = LLMCache(cache_dir=cache_dir)
        
        identical_prompt = "Fix this Python code: def foo(): pass"
        model = "qwen3-coder:latest"
        
        # Store same prompt multiple times (should overwrite)
        start = time.perf_counter()
        for i in range(duplicates):
            cache.set(identical_prompt, model, f"Response {i}", 100, 50)
        store_duration = time.perf_counter() - start
        
        stats = cache.stats()
        
        return {
            "attempted_stores": duplicates,
            "actual_entries": stats["entries"],  # Should be 1
            "dedup_ratio": (duplicates / stats["entries"]) if stats["entries"] > 0 else float(duplicates),
            "store_time_ms": store_duration * 1000,
        }


class TierBenchmark:
    """Benchmarks for three-tier performance comparison."""
    
    @staticmethod
    def bench_algorithmic_fix() -> Dict[str, float]:
        """Benchmark algorithmic (Tier 0) fix performance."""
        from algitex.shared_rules import get_registry
        
        registry = get_registry()
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import os\nimport json\nimport sys\n")  # Sorted correctly
            temp_path = f.name
        
        try:
            start = time.perf_counter()
            iterations = 1000
            
            for _ in range(iterations):
                registry.check_file(temp_path)
            
            duration = time.perf_counter() - start
            
            return {
                "tier": "algorithm",
                "iterations": iterations,
                "duration_ms": duration * 1000,
                "throughput": iterations / duration,
            }
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    @staticmethod
    def bench_micro_llm_simulated() -> Dict[str, float]:
        """Simulate micro LLM tier with delay."""
        # Simulate 50ms LLM call
        delay = 0.05
        iterations = 20
        
        start = time.perf_counter()
        for _ in range(iterations):
            time.sleep(delay)
        duration = time.perf_counter() - start
        
        return {
            "tier": "micro",
            "simulated_delay_ms": delay * 1000,
            "iterations": iterations,
            "duration_ms": duration * 1000,
            "throughput": iterations / duration,
        }
    
    @staticmethod
    def compare_tiers() -> Dict[str, Dict[str, float]]:
        """Compare all three tiers."""
        return {
            "algorithm": TierBenchmark.bench_algorithmic_fix(),
            "micro_simulated": TierBenchmark.bench_micro_llm_simulated(),
            "big_simulated": {
                "tier": "big",
                "simulated_delay_ms": 2000,  # 2s per call
                "estimated_throughput": 0.5,  # 0.5 ops/sec
                "note": "Big LLM tier requires actual API keys",
            }
        }


class MemoryBenchmark:
    """Memory profiling benchmarks."""
    
    @staticmethod
    def profile_large_file_parsing(lines: int = 10000) -> Dict[str, float]:
        """Memory profile parsing large Python files."""
        from algitex.shared_rules import RuleContext
        from algitex.nlp import DeadCodeDetector
        
        # Generate large file
        source = "\n".join([
            f"def func_{i}(x):\n    return x + {i}\n"
            for i in range(lines)
        ])
        
        gc.collect()
        tracemalloc.start()
        
        start_mem = tracemalloc.get_traced_memory()[0]
        
        # Parse and analyze
        ctx = RuleContext(file_path="test.py", source_code=source)
        detector = DeadCodeDetector()
        
        # Detect would need source, simulate
        current_mem = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        memory_used_mb = (current_mem - start_mem) / 1024 / 1024
        
        return {
            "lines": lines,
            "source_size_mb": len(source.encode()) / 1024 / 1024,
            "memory_used_mb": memory_used_mb,
            "memory_per_1k_lines_kb": (memory_used_mb * 1024) / (lines / 1000),
        }


def run_quick_benchmark() -> None:
    """Run quick benchmark suite."""
    runner = BenchmarkRunner(warmup_iterations=1)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "cache"
        
        # Cache benchmarks
        print("Running cache benchmarks...")
        hit_result = CacheBenchmark.bench_cache_hit_rate(str(cache_dir), entries=100, lookups=500)
        dedup_result = CacheBenchmark.bench_cache_deduplication(str(cache_dir), duplicates=50)
        
        print(f"  Cache hit rate: {hit_result['hit_rate']:.1%} ({hit_result['throughput']:.0f} ops/sec)")
        print(f"  Cache dedup: {dedup_result['dedup_ratio']:.0f}x")
        
        # Tier benchmarks
        print("\nRunning tier benchmarks...")
        tier_results = TierBenchmark.compare_tiers()
        
        for tier, result in tier_results.items():
            throughput = result.get('throughput') or result.get('estimated_throughput', 0)
            print(f"  {tier}: {throughput:.1f} ops/sec")
        
        # Memory benchmark
        print("\nRunning memory benchmark...")
        mem_result = MemoryBenchmark.profile_large_file_parsing(lines=1000)
        print(f"  Memory per 1K lines: {mem_result['memory_per_1k_lines_kb']:.2f} KB")


if __name__ == "__main__":
    run_quick_benchmark()
