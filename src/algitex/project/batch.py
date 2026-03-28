"""Batch processing mixins for Project class."""

from __future__ import annotations

from typing import Callable, Optional

from algitex.tools.batch import BatchProcessor, FileBatchProcessor


class BatchMixin:
    """Batch processing functionality for Project."""

    def __init__(self, path: str, ollama_client) -> None:
        from pathlib import Path
        self.batch = FileBatchProcessor(
            ollama_client=ollama_client,
            output_dir=str(Path(path) / ".batch_results")
        )

    def batch_analyze(
        self,
        directory: str = ".",
        pattern: str = "*.py",
        parallelism: Optional[int] = None,
        rate_limit: Optional[float] = None
    ) -> dict:
        """Batch analyze files in directory."""
        # Update processor config if provided
        if parallelism:
            self.batch.parallelism = parallelism
        if rate_limit:
            self.batch.rate_limit = rate_limit

        # Process files
        results = self.batch.process_directory(directory, pattern)

        # Convert to dict
        return {
            "total": len(results),
            "successful": len([r for r in results if r.success]),
            "failed": len([r for r in results if not r.success]),
            "results": [r.to_dict() for r in results]
        }

    def create_batch_processor(
        self,
        worker_func: Callable,
        parallelism: int = 4,
        rate_limit: float = 2.0,
        **kwargs
    ) -> BatchProcessor:
        """Create a custom batch processor."""
        from pathlib import Path
        return BatchProcessor(
            worker_func=worker_func,
            parallelism=parallelism,
            rate_limit=rate_limit,
            output_dir=str(Path(".") / ".batch_results"),
            **kwargs
        )
