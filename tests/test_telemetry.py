"""Unit tests for algitex telemetry module."""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from algitex.tools.telemetry import Telemetry, TraceSpan


class TestTraceSpan:
    """Test the TraceSpan class."""
    
    def test_span_creation(self):
        """Test creating a new span."""
        span = TraceSpan(name="test", tool="test-tool")
        assert span.name == "test"
        assert span.tool == "test-tool"
        assert span.status == "running"
        assert span.started > 0
        assert span.ended == 0
    
    def test_span_finish(self):
        """Test finishing a span."""
        span = TraceSpan(name="test", tool="test-tool")
        time.sleep(0.01)  # Small delay
        span.finish(status="ok", tokens_in=100, tokens_out=50, cost_usd=0.01)
        
        assert span.status == "ok"
        assert span.ended > span.started
        assert span.duration_s > 0
        assert span.tokens_in == 100
        assert span.tokens_out == 50
        assert span.cost_usd == 0.01


class TestTelemetry:
    """Test the Telemetry class."""
    
    def test_telemetry_creation(self):
        """Test creating telemetry with default run ID."""
        tel = Telemetry("test-project")
        assert tel.project == "test-project"
        assert len(tel.run_id) == 15  # YYYYMMDD-HHMMSS format
        assert len(tel.spans) == 0
    
    def test_telemetry_custom_run_id(self):
        """Test creating telemetry with custom run ID."""
        tel = Telemetry("test-project", run_id="custom-run")
        assert tel.run_id == "custom-run"
    
    def test_create_span(self):
        """Test creating a span."""
        tel = Telemetry("test-project")
        span = tel.span("test-operation", "test-tool")
        
        assert isinstance(span, TraceSpan)
        assert span.name == "test-operation"
        assert span.tool == "test-tool"
        assert len(tel.spans) == 1
    
    def test_aggregates(self):
        """Test telemetry aggregate calculations."""
        tel = Telemetry("test-project")
        
        # Create multiple spans
        span1 = tel.span("op1", "tool1")
        span1.finish(tokens_in=100, tokens_out=50, cost_usd=0.01)
        
        span2 = tel.span("op2", "tool2")
        span2.finish(tokens_in=200, tokens_out=100, cost_usd=0.02, status="error")
        
        span3 = tel.span("op3", "tool1")
        span3.finish(tokens_in=150, tokens_out=75, cost_usd=0.015)
        
        # Check aggregates
        assert tel.total_cost == 0.045
        assert tel.total_tokens == 675  # (100+50) + (200+100) + (150+75)
        assert tel.error_count == 1
        assert tel.total_duration > 0
    
    def test_summary(self):
        """Test telemetry summary generation."""
        tel = Telemetry("test-project", run_id="test-run")
        
        span1 = tel.span("op1", "tool1")
        span1.finish(model="gpt-4")
        
        span2 = tel.span("op2", "tool2")
        span2.finish(model="claude-3")
        
        summary = tel.summary()
        
        assert summary["run_id"] == "test-run"
        assert summary["project"] == "test-project"
        assert summary["spans"] == 2
        assert summary["total_cost_usd"] == 0.0
        assert summary["total_tokens"] == 0
        assert summary["errors"] == 0
        assert set(summary["models_used"]) == {"gpt-4", "claude-3"}
        assert set(summary["tools_used"]) == {"tool1", "tool2"}
    
    def test_save(self, tmp_path):
        """Test saving telemetry to file."""
        tel = Telemetry("test-project", run_id="test-save")
        
        span = tel.span("test", "tool")
        span.finish(tokens_in=100, tokens_out=50, cost_usd=0.01)
        
        # Save to temporary directory
        tel.save(str(tmp_path))
        
        # Check file exists and has correct content
        file_path = tmp_path / "telemetry" / "test-save.json"
        assert file_path.exists()
        
        data = json.loads(file_path.read_text())
        assert data["summary"]["run_id"] == "test-save"
        assert data["summary"]["spans"] == 1
        assert len(data["spans"]) == 1
        assert data["spans"][0]["name"] == "test"
    
    def test_report(self):
        """Test generating human-readable report."""
        tel = Telemetry("test-project", run_id="test-report")
        
        span = tel.span("test", "tool")
        span.finish(tokens_in=100, tokens_out=50, cost_usd=0.01)
        
        report = tel.report()
        
        assert "test-report" in report
        assert "1 operations" in report
        assert "$0.01" in report
        assert "150 tokens" in report
        assert "0 errors" in report
    
    def test_push_to_langfuse(self):
        """Test pushing telemetry to Langfuse."""
        tel = Telemetry("test-project")
        
        span = tel.span("test", "tool")
        span.finish(model="gpt-4", tokens_in=100, tokens_out=50)
        
        # Just test that it doesn't crash - actual Langfuse testing requires integration
        tel.push_to_langfuse()
    
    def test_push_to_langfuse_optional(self):
        """Test that missing Langfuse is handled gracefully."""
        tel = Telemetry("test-project")
        
        # Just test that it doesn't crash when Langfuse is not available
        tel.push_to_langfuse()
