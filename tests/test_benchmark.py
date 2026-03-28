"""Tests for benchmark module."""

import tempfile
from pathlib import Path

import pytest

from algitex.benchmark import (
    BenchmarkResult,
    BenchmarkSuite,
    BenchmarkRunner,
    CacheBenchmark,
    TierBenchmark,
    MemoryBenchmark,
    run_quick_benchmark,
)


class TestBenchmarkResult:
    def test_result_creation(self):
        result = BenchmarkResult(
            name="test_bench",
            duration_ms=100.0,
            iterations=1000,
            throughput=10000.0,
            memory_delta_mb=1.5,
            metadata={"key": "value"},
        )
        assert result.name == "test_bench"
        assert result.throughput == 10000.0
    
    def test_result_to_dict(self):
        result = BenchmarkResult(
            name="test",
            duration_ms=100.0,
            iterations=1000,
            throughput=10000.0,
            memory_delta_mb=1.5,
        )
        d = result.to_dict()
        assert d["name"] == "test"
        assert d["throughput"] == 10000.0


class TestBenchmarkSuite:
    def test_suite_creation(self):
        suite = BenchmarkSuite(name="test_suite")
        assert suite.name == "test_suite"
        assert len(suite.results) == 0
    
    def test_suite_add_result(self):
        suite = BenchmarkSuite(name="test")
        result = BenchmarkResult("bench1", 100.0, 1000, 10000.0, 1.0)
        suite.add(result)
        assert len(suite.results) == 1
    
    def test_suite_summary_empty(self):
        suite = BenchmarkSuite(name="empty")
        summary = suite.summary()
        assert summary["name"] == "empty"
        assert summary["total"] == 0
    
    def test_suite_summary_with_results(self):
        suite = BenchmarkSuite(name="test")
        suite.add(BenchmarkResult("bench1", 100.0, 1000, 10000.0, 1.0))
        suite.add(BenchmarkResult("bench2", 200.0, 2000, 10000.0, 2.0))
        
        summary = suite.summary()
        assert summary["total"] == 2
        assert summary["total_duration_sec"] == 0.3  # 100ms + 200ms = 300ms = 0.3s
        assert summary["total_memory_mb"] == 3.0


class TestBenchmarkRunner:
    def test_runner_creation(self):
        runner = BenchmarkRunner(warmup_iterations=5)
        assert runner.warmup_iterations == 5
    
    def test_run_simple_benchmark(self):
        runner = BenchmarkRunner(warmup_iterations=1)
        
        def test_func():
            return sum(range(100))
        
        result = runner.run("test_sum", test_func, iterations=100)
        
        assert result.name == "test_sum"
        assert result.iterations == 100
        assert result.duration_ms > 0
        assert result.throughput > 0
    
    def test_run_suite(self):
        runner = BenchmarkRunner(warmup_iterations=1)
        
        def func1(): pass
        def func2(): pass
        
        benchmarks = {
            "bench1": (func1, 10, [], {}),
            "bench2": (func2, 10, [], {}),
        }
        
        suite = runner.run_suite("test_suite", benchmarks)
        
        assert len(suite.results) == 2
        assert suite.name == "test_suite"
    
    def test_export_json(self):
        runner = BenchmarkRunner(warmup_iterations=1)
        
        def test_func(): pass
        
        # Create suite and run benchmark
        suite = runner.run_suite("test_suite", {
            "test": (test_func, 10, [], {})
        })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "results.json"
            runner.export_json(str(export_path))
            
            assert export_path.exists()
            content = export_path.read_text()
            assert "test_suite" in content


class TestCacheBenchmark:
    def test_cache_hit_rate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = CacheBenchmark.bench_cache_hit_rate(
                cache_dir=tmpdir,
                entries=50,
                lookups=100,
            )
            
            assert "hit_rate" in result
            assert "throughput" in result
            assert "latency_ms" in result
            assert 0 <= result["hit_rate"] <= 1
            assert result["throughput"] > 0
    
    def test_cache_deduplication(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = CacheBenchmark.bench_cache_deduplication(
                cache_dir=tmpdir,
                duplicates=10,
            )
            
            assert result["attempted_stores"] == 10
            assert result["actual_entries"] == 1  # Should dedup to 1
            assert result["dedup_ratio"] >= 10


class TestTierBenchmark:
    def test_algorithmic_fix(self):
        result = TierBenchmark.bench_algorithmic_fix()
        
        assert result["tier"] == "algorithm"
        assert "throughput" in result
        assert result["throughput"] > 0
    
    def test_micro_llm_simulated(self):
        result = TierBenchmark.bench_micro_llm_simulated()
        
        assert result["tier"] == "micro"
        assert result["simulated_delay_ms"] == 50
        assert result["throughput"] > 0
    
    def test_compare_tiers(self):
        results = TierBenchmark.compare_tiers()
        
        assert "algorithm" in results
        assert "micro_simulated" in results
        assert "big_simulated" in results


class TestMemoryBenchmark:
    def test_profile_large_file_small(self):
        result = MemoryBenchmark.profile_large_file_parsing(lines=100)
        
        assert result["lines"] == 100
        assert result["memory_used_mb"] >= 0
        assert result["memory_per_1k_lines_kb"] >= 0
    
    def test_profile_large_file_medium(self):
        result = MemoryBenchmark.profile_large_file_parsing(lines=500)
        
        assert result["lines"] == 500
        assert result["source_size_mb"] > 0


class TestRunQuickBenchmark:
    def test_quick_benchmark_runs(self, capsys):
        # Should run without error
        run_quick_benchmark()
        
        captured = capsys.readouterr()
        assert "cache" in captured.out.lower() or "tier" in captured.out.lower()
