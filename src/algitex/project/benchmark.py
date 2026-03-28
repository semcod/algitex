"""Benchmarking mixins for Project class."""

from __future__ import annotations

from typing import List, Optional

from algitex.tools.benchmark,ModelBenchmark


class BenchmarkMixin:
    """Model benchmarking functionality for Project."""

    def __init__(self, ollama_client) -> None:
        self.benchmark = ModelBenchmark(ollama_client)

    def benchmark_models(
        self,
        models: List[str],
        tasks: Optional[List[str]] = None
    ) -> dict:
        """Benchmark models on tasks."""
        results = self.benchmark.compare_models(models, tasks)
        return results.to_dict()

    def add_benchmark_task(
        self,
        task_id: str,
        name: str,
        prompt: str,
        expected_keywords: List[str]
    ):
        """Add a custom benchmark task."""
        self.benchmark.add_custom_task(
            task_id=task_id,
            name=name,
            prompt=prompt,
            expected_keywords=expected_keywords
        )

    def print_benchmark_results(self, results: dict, format: str = "table") -> None:
        """Print benchmark results from dict."""
        from algitex.tools.benchmark import BenchmarkResults, TaskResult

        benchmark_results = BenchmarkResults()
        for r in results["results"]:
            result = TaskResult(
                model=r["model"],
                task_id=r["task_id"],
                success=r["success"],
                time_seconds=r["time_seconds"],
                tokens_estimated=r["tokens_estimated"],
                quality_score=r["quality_score"],
                response=r.get("response_preview", ""),
                error=r.get("error")
            )
            benchmark_results.results.append(result)

        self.benchmark.print_results(benchmark_results, format)
