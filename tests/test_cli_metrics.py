"""Integration tests for metrics CLI commands."""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from algitex.cli import app


runner = CliRunner()


class TestMetricsCLI:
    def test_metrics_help(self):
        result = runner.invoke(app, ["metrics", "--help"])
        assert result.exit_code == 0
        assert "Metrics and observability" in result.output
        assert "show" in result.output
        assert "cache" in result.output
        assert "compare" in result.output
    
    def test_metrics_show_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "metrics.json"
            
            result = runner.invoke(app, ["metrics", "show", "--storage", str(storage)])
            
            assert result.exit_code == 0
            # Should show empty metrics without error
            assert "Algitex Metrics" in result.output or "0" in result.output
    
    def test_metrics_cache_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, ["metrics", "cache", "--dir", tmpdir])
            
            assert result.exit_code == 0
            assert "Entries:" in result.output or "0" in result.output
    
    def test_metrics_cache_list_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, ["metrics", "cache", "--dir", tmpdir, "--list"])
            
            assert result.exit_code == 0
            assert "empty" in result.output.lower() or "Cache is" in result.output
    
    def test_metrics_clear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "metrics.json"
            cache_dir = Path(tmpdir) / "cache"
            cache_dir.mkdir()
            
            result = runner.invoke(app, [
                "metrics", "clear",
                "--storage", str(storage),
                "--cache", str(cache_dir)
            ])
            
            assert result.exit_code == 0
            assert "Clearing" in result.output or "Cleared" in result.output
    
    def test_metrics_compare_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "metrics.json"
            
            # Initialize with empty data
            from algitex.metrics import MetricsCollector
            collector = MetricsCollector(str(storage))
            collector.save()
            
            result = runner.invoke(app, ["metrics", "compare", "--storage", str(storage)])
            
            # Command should handle empty data gracefully
            assert result.exit_code in [0, 1]  # Either success or graceful error
            if result.exit_code == 0:
                assert "Tier" in result.output or "Algorithm" in result.output
    
    def test_metrics_export_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "metrics.json"
            csv_file = Path(tmpdir) / "export.csv"
            
            # First, record some metrics
            from algitex.metrics import MetricsCollector
            collector = MetricsCollector(str(storage))
            collector.record_llm_call("micro", "model", 100, 50, 500, True)
            collector.save()
            
            result = runner.invoke(app, [
                "metrics", "show",
                "--storage", str(storage),
                "--export", str(csv_file)
            ])
            
            assert result.exit_code == 0
            assert csv_file.exists()
            content = csv_file.read_text()
            assert "timestamp" in content or "micro" in content
    
    def test_metrics_cache_clear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            from algitex.tools.ollama_cache import LLMCache
            cache = LLMCache(tmpdir)
            cache.set("test", "model", "response", 100, 50)
            
            result = runner.invoke(app, ["metrics", "cache", "--dir", tmpdir, "--clear"])
            
            assert result.exit_code == 0
            assert "Cleared" in result.output
            
            stats = cache.stats()
            assert stats["entries"] == 0


class TestCacheCLI:
    def test_cache_stats_with_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            from algitex.tools.ollama_cache import LLMCache
            cache = LLMCache(tmpdir)
            cache.set("prompt1", "model1", "response1", 100, 50)
            cache.set("prompt2", "model2", "response2", 200, 100)
            
            result = runner.invoke(app, ["metrics", "cache", "--dir", tmpdir])
            
            assert result.exit_code == 0
            assert "2" in result.output or "entries" in result.output.lower()
    
    def test_cache_list_with_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            from algitex.tools.ollama_cache import LLMCache
            cache = LLMCache(tmpdir)
            cache.set("test prompt", "qwen2.5-coder:7b", "test response", 100, 50)
            
            result = runner.invoke(app, ["metrics", "cache", "--dir", tmpdir, "--list"])
            
            assert result.exit_code == 0
            assert "qwen2.5-coder:7b" in result.output
