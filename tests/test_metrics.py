"""Tests for metrics module."""

import json
import tempfile
from pathlib import Path

import pytest

from algitex.metrics import LLMCall, FixResult, MetricsCollector, MetricsReporter, get_metrics, reset_metrics


class TestLLMCall:
    def test_call_creation(self):
        call = LLMCall(
            timestamp=1234567890.0,
            tier="micro",
            model="qwen2.5-coder:7b",
            tokens_in=100,
            tokens_out=50,
            duration_ms=500.0,
            success=True,
            cached=False,
            task_category="magic",
        )
        assert call.tier == "micro"
        assert call.tokens_in == 100
    
    def test_call_to_dict(self):
        call = LLMCall(
            timestamp=1234567890.0,
            tier="micro",
            model="qwen2.5-coder:7b",
            tokens_in=100,
            tokens_out=50,
            duration_ms=500.0,
            success=True,
            cached=False,
        )
        d = call.to_dict()
        assert d["tier"] == "micro"
        assert d["model"] == "qwen2.5-coder:7b"


class TestFixResult:
    def test_result_creation(self):
        result = FixResult(
            timestamp=1234567890.0,
            tier="algorithm",
            category="unused_import",
            file="test.py",
            line=10,
            success=True,
            duration_ms=100.0,
            used_llm=False,
        )
        assert result.category == "unused_import"
        assert result.success is True


class TestMetricsCollector:
    def test_record_llm_call(self):
        collector = MetricsCollector()
        
        collector.record_llm_call(
            tier="micro",
            model="qwen2.5-coder:7b",
            tokens_in=100,
            tokens_out=50,
            duration_ms=500.0,
            success=True,
            cached=False,
        )
        
        assert len(collector.llm_calls) == 1
        assert collector.llm_calls[0].tier == "micro"
    
    def test_record_fix(self):
        collector = MetricsCollector()
        
        collector.record_fix(
            tier="algorithm",
            category="unused_import",
            file="test.py",
            line=10,
            success=True,
            duration_ms=100.0,
        )
        
        assert len(collector.fix_results) == 1
        assert collector.fix_results[0].category == "unused_import"
    
    def test_tier_stats(self):
        collector = MetricsCollector()
        
        # Add calls for different tiers
        collector.record_llm_call("micro", "model", 100, 50, 500, True)
        collector.record_llm_call("micro", "model", 100, 50, 500, True)
        collector.record_llm_call("big", "model", 500, 200, 2000, True)
        collector.record_llm_call("big", "model", 500, 200, 2000, False)
        
        stats = collector.get_tier_stats()
        
        assert stats["micro"]["calls"] == 2
        assert stats["micro"]["success"] == 2
        assert stats["big"]["calls"] == 2
        assert stats["big"]["success"] == 1
        assert stats["big"]["failure"] == 1
    
    def test_estimate_cost(self):
        collector = MetricsCollector()
        
        # Local model = free
        collector.record_llm_call("micro", "qwen2.5-coder:7b", 1000000, 500000, 500, True)
        
        # Claude = expensive
        collector.record_llm_call("big", "claude-3-5-sonnet", 1000000, 500000, 2000, True)
        
        costs = collector.estimate_cost()
        
        # Local should be free
        assert costs["micro"] == 0.0
        # Claude: $3/M input + $15/M output = $3 + $7.5 = $10.5
        assert costs["big"] == pytest.approx(10.5, rel=0.01)
        assert costs["total"] == pytest.approx(10.5, rel=0.01)
    
    def test_estimate_cost_cached(self):
        collector = MetricsCollector()
        
        # Non-cached expensive call
        collector.record_llm_call("big", "claude-3-5-sonnet", 1000000, 500000, 2000, True, cached=False)
        
        # Cached call should be free even for expensive model
        collector.record_llm_call("big", "claude-3-5-sonnet", 1000000, 500000, 2000, True, cached=True)
        
        costs = collector.estimate_cost()
        
        # First big call costs, second is free (cached)
        assert costs.get("big", 0) == pytest.approx(10.5, rel=0.01)  # Only one counted
        assert costs["total"] == pytest.approx(10.5, rel=0.01)
    
    def test_get_summary(self):
        collector = MetricsCollector()
        
        collector.record_llm_call("micro", "model", 100, 50, 500, True)
        collector.record_fix("algorithm", "unused_import", "test.py", 10, True, 100)
        
        summary = collector.get_summary()
        
        assert summary["llm_calls"] == 1
        assert summary["fix_attempts"] == 1
        assert summary["fix_success_rate"] == 1.0
        assert "session_duration_sec" in summary
    
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "metrics.json"
            
            # Save
            collector1 = MetricsCollector(str(storage))
            collector1.record_llm_call("micro", "model", 100, 50, 500, True)
            collector1.save()
            
            # Load
            collector2 = MetricsCollector(str(storage))
            collector2.load()
            
            assert len(collector2.llm_calls) == 1
            assert collector2.llm_calls[0].tier == "micro"
    
    def test_reset(self):
        collector = MetricsCollector()
        
        collector.record_llm_call("micro", "model", 100, 50, 500, True)
        collector.record_fix("algorithm", "unused_import", "test.py", 10, True, 100)
        
        collector.reset()
        
        assert len(collector.llm_calls) == 0
        assert len(collector.fix_results) == 0


class TestMetricsReporter:
    def test_print_dashboard(self, capsys):
        collector = MetricsCollector()
        collector.record_llm_call("micro", "model", 100, 50, 500, True)
        
        reporter = MetricsReporter(collector)
        
        # This should not raise
        reporter.print_dashboard()
        
        # Can't easily test Rich output, but at least verify no exception
    
    def test_export_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = MetricsCollector()
            collector.record_llm_call("micro", "qwen2.5-coder:7b", 100, 50, 500, True, cached=False, task_category="magic")
            
            reporter = MetricsReporter(collector)
            csv_path = Path(tmpdir) / "metrics.csv"
            
            reporter.export_csv(str(csv_path))
            
            assert csv_path.exists()
            content = csv_path.read_text()
            assert "micro" in content
            assert "qwen2.5-coder:7b" in content


class TestGlobalMetrics:
    def test_get_metrics(self):
        reset_metrics()
        
        metrics1 = get_metrics()
        metrics1.record_llm_call("micro", "model", 100, 50, 500, True)
        
        metrics2 = get_metrics()
        assert len(metrics2.llm_calls) == 1  # Same instance
    
    def test_reset_metrics(self):
        reset_metrics()
        
        metrics = get_metrics()
        metrics.record_llm_call("micro", "model", 100, 50, 500, True)
        
        reset_metrics()
        
        metrics2 = get_metrics()
        assert len(metrics2.llm_calls) == 0  # Fresh instance
