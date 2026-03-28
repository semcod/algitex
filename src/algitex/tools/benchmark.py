"""Model benchmarking — compare LLM models on standardized tasks.

Usage:
    from algitex.tools.benchmark import ModelBenchmark
    
    # Create benchmark
    benchmark = ModelBenchmark(ollama_client)
    
    # Add tasks
    benchmark.add_task("code_completion", prompt, expected_keywords)
    
    # Run comparison
    results = benchmark.compare_models(["model1", "model2"])
    
    # Print results
    benchmark.print_results(results)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    from tabulate import tabulate  # Optional, for nice tables
except ImportError:
    tabulate = None


@dataclass
class Task:
    """Benchmark task definition."""
    id: str
    name: str
    prompt: str
    expected_keywords: List[str]
    max_tokens: int = 300
    temperature: float = 0.3
    
    def evaluate_quality(self, response: str) -> float:
        """Evaluate response quality (0-5 scale)."""
        score = 0
        for keyword in self.expected_keywords:
            if keyword.lower() in response.lower():
                score += 1
        return min(5.0, (score / len(self.expected_keywords)) * 5)


@dataclass
class TaskResult:
    """Result for a single model on a single task."""
    model: str
    task_id: str
    success: bool
    time_seconds: float
    tokens_estimated: int
    quality_score: float
    response: str
    error: Optional[str] = None
    
    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second."""
        return self.tokens_estimated / self.time_seconds if self.time_seconds > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "task_id": self.task_id,
            "success": self.success,
            "time_seconds": self.time_seconds,
            "tokens_estimated": self.tokens_estimated,
            "quality_score": self.quality_score,
            "tokens_per_second": self.tokens_per_second,
            "error": self.error,
            "response_preview": self.response[:200] + "..." if len(self.response) > 200 else self.response
        }


@dataclass
class BenchmarkResults:
    """Complete benchmark results."""
    results: List[TaskResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: time.strftime("%Y%m%d_%H%M%S"))
    
    def get_model_results(self, model: str) -> List[TaskResult]:
        """Get all results for a model."""
        return [r for r in self.results if r.model == model]
    
    def get_task_results(self, task_id: str) -> List[TaskResult]:
        """Get all results for a task."""
        return [r for r in self.results if r.task_id == task_id]
    
    def get_best_model(self, task_id: str, metric: str = "quality") -> Optional[str]:
        """Get best model for a task by metric."""
        task_results = self.get_task_results(task_id)
        task_results = [r for r in task_results if r.success]
        
        if not task_results:
            return None
        
        if metric == "quality":
            best = max(task_results, key=lambda r: r.quality_score)
        elif metric == "speed":
            best = min(task_results, key=lambda r: r.time_seconds)
        elif metric == "throughput":
            best = max(task_results, key=lambda r: r.tokens_per_second)
        else:
            # Combined score: quality / time
            best = max(task_results, key=lambda r: r.quality_score / max(r.time_seconds, 0.1))
        
        return best.model
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "results": [r.to_dict() for r in self.results],
            "summary": self.get_summary()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        models = list(set(r.model for r in self.results))
        tasks = list(set(r.task_id for r in self.results))
        
        summary = {
            "models": models,
            "tasks": tasks,
            "total_runs": len(self.results),
            "successful_runs": sum(1 for r in self.results if r.success),
            "failed_runs": sum(1 for r in self.results if not r.success)
        }
        
        # Per-model stats
        summary["by_model"] = {}
        for model in models:
            model_results = self.get_model_results(model)
            successful = [r for r in model_results if r.success]
            
            if successful:
                avg_quality = sum(r.quality_score for r in successful) / len(successful)
                avg_time = sum(r.time_seconds for r in successful) / len(successful)
                avg_throughput = sum(r.tokens_per_second for r in successful) / len(successful)
                
                summary["by_model"][model] = {
                    "successful_tasks": len(successful),
                    "total_tasks": len(model_results),
                    "avg_quality": avg_quality,
                    "avg_time_seconds": avg_time,
                    "avg_tokens_per_second": avg_throughput
                }
            else:
                summary["by_model"][model] = {
                    "successful_tasks": 0,
                    "total_tasks": len(model_results),
                    "error": "All tasks failed"
                }
        
        return summary


class ModelBenchmark:
    """Benchmark models on standardized tasks."""
    
    def __init__(self, ollama_client, default_tasks: bool = True):
        self.client = ollama_client
        self.tasks: Dict[str, Task] = {}
        
        if default_tasks:
            self._add_default_tasks()
    
    def _add_default_tasks(self):
        """Add default benchmark tasks."""
        self.tasks["code_completion"] = Task(
            id="code_completion",
            name="Code Completion",
            prompt="Complete this Python function:\n\ndef fibonacci(n):\n    pass",
            expected_keywords=["def", "fibonacci", "return", "sequence"]
        )
        
        self.tasks["bug_fix"] = Task(
            id="bug_fix",
            name="Bug Fix",
            prompt="""Fix the bug in this code:

def divide(a, b):
    return a / b

# Test: divide(10, 0) should not crash""",
            expected_keywords=["if", "ZeroDivisionError", "try", "except"]
        )
        
        self.tasks["documentation"] = Task(
            id="documentation",
            name="Documentation",
            prompt="""Add docstring to this function:

def process_data(data, transform):
    result = []
    for item in data:
        result.append(transform(item))
    return result""",
            expected_keywords=["Args:", "Returns:", "docstring"]
        )
        
        self.tasks["refactoring"] = Task(
            id="refactoring",
            name="Refactoring",
            prompt="""Refactor this code to be more Pythonic:

items = []
for i in range(len(data)):
    items.append(data[i] * 2)""",
            expected_keywords=["list", "comprehension", "compact"]
        )
    
    def add_task(self, task: Task):
        """Add a custom task."""
        self.tasks[task.id] = task
    
    def add_custom_task(
        self,
        task_id: str,
        name: str,
        prompt: str,
        expected_keywords: List[str],
        **kwargs
    ):
        """Add a custom task by parameters."""
        task = Task(
            id=task_id,
            name=name,
            prompt=prompt,
            expected_keywords=expected_keywords,
            **kwargs
        )
        self.add_task(task)
    
    def run_single_task(self, model: str, task: Task) -> TaskResult:
        """Run a single benchmark task."""
        start_time = time.time()
        
        try:
            response = self.client.generate(
                prompt=task.prompt,
                model=model,
                temperature=task.temperature
            )
            
            elapsed = time.time() - start_time
            
            # Estimate tokens (rough approximation)
            tokens_estimated = len(str(response).split())
            
            # Evaluate quality
            quality_score = task.evaluate_quality(str(response))
            
            return TaskResult(
                model=model,
                task_id=task.id,
                success=True,
                time_seconds=elapsed,
                tokens_estimated=tokens_estimated,
                quality_score=quality_score,
                response=str(response)
            )
        except Exception as e:
            return TaskResult(
                model=model,
                task_id=task.id,
                success=False,
                time_seconds=time.time() - start_time,
                tokens_estimated=0,
                quality_score=0,
                response="",
                error=str(e)
            )
    
    def compare_models(
        self,
        models: List[str],
        tasks: Optional[List[str]] = None,
        progress: bool = True
    ) -> BenchmarkResults:
        """Compare models on all tasks."""
        tasks_to_run = tasks or list(self.tasks.keys())
        results = BenchmarkResults()
        
        print(f"Benchmarking {len(models)} models on {len(tasks_to_run)} tasks")
        print()
        
        total_runs = len(models) * len(tasks_to_run)
        current_run = 0
        
        for model in models:
            print(f"Testing: {model}")
            
            for task_id in tasks_to_run:
                if task_id not in self.tasks:
                    print(f"  ⚠️  Task {task_id} not found, skipping")
                    continue
                
                task = self.tasks[task_id]
                current_run += 1
                
                if progress:
                    print(f"  [{current_run}/{total_runs}] {task.name}...", end=" ")
                
                result = self.run_single_task(model, task)
                results.results.append(result)
                
                if progress:
                    if result.success:
                        print(f"✅ {result.time_seconds:.1f}s, quality: {result.quality_score:.1f}/5")
                    else:
                        print(f"❌ {result.error[:50]}")
        
        return results
    
    def print_results(self, results: BenchmarkResults, format: str = "table"):
        """Print benchmark results."""
        if format == "table":
            self._print_table(results)
        elif format == "summary":
            self._print_summary(results)
        else:
            self._print_detailed(results)
    
    def _print_table(self, results: BenchmarkResults):
        """Print results as table."""
        print()
        print("=" * 100)
        print("Model Comparison Results")
        print("=" * 100)
        
        for task_id in self.tasks.keys():
            task_results = results.get_task_results(task_id)
            if not task_results:
                continue
            
            task = self.tasks[task_id]
            print()
            print(f"Task: {task.name}")
            print("-" * 100)
            
            # Prepare table data
            headers = ["Model", "Time (s)", "Tokens", "Quality", "Tokens/s"]
            rows = []
            
            for result in task_results:
                if result.success:
                    quality_stars = "⭐" * int(result.quality_score)
                    rows.append([
                        result.model,
                        f"{result.time_seconds:.1f}",
                        result.tokens_estimated,
                        quality_stars,
                        f"{result.tokens_per_second:.1f}"
                    ])
                else:
                    rows.append([
                        result.model,
                        "FAILED",
                        "-",
                        "-",
                        "-"
                    ])
            
            # Try to use tabulate, fallback to simple format
            try:
                print(tabulate(rows, headers=headers, tablefmt="grid"))
            except ImportError:
                # Simple table format
                print(f"{'Model':<25} {'Time':>8} {'Tokens':>8} {'Quality':>8} {'Tok/s':>8}")
                print("-" * 100)
                for row in rows:
                    print(f"{row[0]:<25} {row[1]:>8} {row[2]:>8} {row[3]:>8} {row[4]:>8}")
            
            print("-" * 100)
    
    def _print_summary(self, results: BenchmarkResults):
        """Print summary statistics."""
        summary = results.get_summary()
        
        print()
        print("=" * 80)
        print("Benchmark Summary")
        print("=" * 80)
        print(f"Total runs: {summary['total_runs']}")
        print(f"Successful: {summary['successful_runs']}")
        print(f"Failed: {summary['failed_runs']}")
        print()
        
        print("Per-model performance:")
        for model, stats in summary["by_model"].items():
            if "error" in stats:
                print(f"  {model}: ❌ {stats['error']}")
            else:
                print(f"  {model}:")
                print(f"    Tasks: {stats['successful_tasks']}/{stats['total_tasks']}")
                print(f"    Avg quality: {stats['avg_quality']:.1f}/5")
                print(f"    Avg time: {stats['avg_time_seconds']:.1f}s")
                print(f"    Avg throughput: {stats['avg_tokens_per_second']:.1f} tok/s")
        
        print()
        print("Best models by task:")
        for task_id in self.tasks.keys():
            best = results.get_best_model(task_id, "quality")
            if best:
                print(f"  {self.tasks[task_id].name}: 🏆 {best}")
    
    def _print_detailed(self, results: BenchmarkResults):
        """Print detailed results."""
        for result in results.results:
            print()
            print(f"Model: {result.model}")
            print(f"Task: {result.tasks[result.task_id].name if result.task_id in self.tasks else result.task_id}")
            print(f"Success: {result.success}")
            
            if result.success:
                print(f"Time: {result.time_seconds:.1f}s")
                print(f"Tokens: {result.tokens_estimated}")
                print(f"Quality: {result.quality_score:.1f}/5")
                print(f"Response:")
                print(result.response)
            else:
                print(f"Error: {result.error}")
    
    def save_results(self, results: BenchmarkResults, filename: Optional[str] = None):
        """Save results to JSON file."""
        if not filename:
            filename = f"benchmark_{results.timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        
        print(f"\nResults saved to: {filename}")
    
    def load_results(self, filename: str) -> BenchmarkResults:
        """Load results from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        results = BenchmarkResults()
        results.timestamp = data.get("timestamp", results.timestamp)
        
        for result_data in data["results"]:
            result = TaskResult(
                model=result_data["model"],
                task_id=result_data["task_id"],
                success=result_data["success"],
                time_seconds=result_data["time_seconds"],
                tokens_estimated=result_data["tokens_estimated"],
                quality_score=result_data["quality_score"],
                response=result_data.get("response_preview", ""),
                error=result_data.get("error")
            )
            results.results.append(result)
        
        return results
