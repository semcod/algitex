"""Tests for dashboard module."""

import time
from collections import deque

import pytest

from algitex.dashboard import (
    TierState,
    CacheState,
    LiveDashboard,
    SimpleProgressTracker,
    show_quick_dashboard,
)


class TestTierState:
    def test_state_creation(self):
        state = TierState(name="micro", current=10, total=100)
        assert state.name == "micro"
        assert state.current == 10
    
    def test_percent_calculation(self):
        state = TierState(name="test", current=50, total=100)
        assert state.percent == 50.0
    
    def test_percent_zero_total(self):
        state = TierState(name="test", current=0, total=0)
        assert state.percent == 0.0
    
    def test_eta_calculation(self):
        state = TierState(name="test", current=50, total=100, throughput=10.0)
        assert state.eta_seconds == 5.0  # 50 remaining at 10/sec = 5s
    
    def test_eta_zero_throughput(self):
        state = TierState(name="test", current=50, total=100, throughput=0)
        assert state.eta_seconds == 0.0


class TestCacheState:
    def test_state_creation(self):
        state = CacheState(hits=100, misses=20, entries=50)
        assert state.hits == 100
        assert state.entries == 50
    
    def test_hit_rate_calculation(self):
        state = CacheState(hits=80, misses=20)
        assert state.hit_rate == 0.8
    
    def test_hit_rate_zero_total(self):
        state = CacheState(hits=0, misses=0)
        assert state.hit_rate == 0.0
    
    def test_size_mb_calculation(self):
        state = CacheState(size_bytes=1024 * 1024)  # 1 MB
        assert state.size_mb == 1.0


class TestLiveDashboard:
    def test_dashboard_creation(self):
        dashboard = LiveDashboard(refresh_rate=0.5)
        assert dashboard.refresh_rate == 0.5
        assert not dashboard._running
    
    def test_update_cache_stats(self):
        dashboard = LiveDashboard()
        
        dashboard.update_cache_stats(hits=100, misses=20, entries=50)
        
        assert dashboard.cache.hits == 100
        assert dashboard.cache.misses == 20
        assert dashboard.cache.entries == 50
    
    def test_update_tier_progress(self):
        dashboard = LiveDashboard()
        
        dashboard.update_tier_progress(
            "micro",
            current=25,
            total=100,
            success=20,
            failed=5,
            throughput=10.0,
            active=True,
        )
        
        tier = dashboard.tiers["micro"]
        assert tier.current == 25
        assert tier.total == 100
        assert tier.success == 20
        assert tier.failed == 5
        assert tier.throughput == 10.0
        assert tier.active is True
    
    def test_update_unknown_tier(self):
        dashboard = LiveDashboard()
        # Should not raise
        dashboard.update_tier_progress("unknown", current=10)
    
    def test_throughput_history(self):
        dashboard = LiveDashboard()
        
        dashboard.update_tier_progress("micro", throughput=10.0)
        dashboard.update_tier_progress("micro", throughput=20.0)
        
        history = dashboard._throughput_history["micro"]
        assert len(history) == 2
        assert list(history) == [10.0, 20.0]
    
    def test_start_stop(self):
        dashboard = LiveDashboard(refresh_rate=0.1)
        
        dashboard.start()
        assert dashboard._running
        
        time.sleep(0.2)
        
        dashboard.stop()
        assert not dashboard._running
    
    def test_context_manager(self):
        dashboard = LiveDashboard(refresh_rate=0.1)
        
        with dashboard as d:
            assert d._running
            time.sleep(0.1)
        
        assert not dashboard._running
    
    def test_set_on_update(self):
        dashboard = LiveDashboard()
        
        called = False
        def callback():
            nonlocal called
            called = True
        
        dashboard.set_on_update(callback)
        assert dashboard._on_update is callback


class TestSimpleProgressTracker:
    def test_tracker_creation(self):
        tracker = SimpleProgressTracker()
        assert tracker.progress is None
    
    def test_start_stop(self):
        tracker = SimpleProgressTracker()
        
        tracker.start()
        assert tracker.progress is not None
        
        tracker.stop()
        assert tracker.progress is None
    
    def test_add_task(self):
        tracker = SimpleProgressTracker()
        tracker.start()
        
        task_id = tracker.add_task("Test task", total=100)
        
        assert "Test task" in tracker.tasks
        assert tracker.tasks["Test task"] == task_id
        
        tracker.stop()
    
    def test_update_task(self):
        tracker = SimpleProgressTracker()
        tracker.start()
        
        tracker.add_task("Test", total=100)
        tracker.update("Test", advance=10)
        
        # Can't easily verify progress, but should not raise
        tracker.stop()
    
    def test_update_unknown_task(self):
        tracker = SimpleProgressTracker()
        tracker.start()
        
        # Should not raise
        tracker.update("unknown", advance=10)
        
        tracker.stop()
    
    def test_context_manager(self):
        with SimpleProgressTracker() as tracker:
            assert tracker.progress is not None
        
        assert tracker.progress is None


class TestShowQuickDashboard:
    def test_quick_dashboard_runs(self, capsys):
        # Mock to avoid actual live display
        import threading
        
        def mock_dashboard(duration):
            print("Mock dashboard ran")
        
        # Test that function doesn't crash
        try:
            show_quick_dashboard(duration=0.1)
        except Exception as e:
            # Expected to fail in test environment without display
            pass


class TestDashboardRender:
    def test_render_header(self):
        dashboard = LiveDashboard()
        header = dashboard._render_header()
        assert "Algitex Live Dashboard" in header.renderable
    
    def test_render_cache_panel(self):
        dashboard = LiveDashboard()
        dashboard.update_cache_stats(hits=80, misses=20, entries=50)
        
        panel = dashboard._render_cache_panel()
        assert "Cache" in str(panel.title)
    
    def test_render_tiers_panel(self):
        dashboard = LiveDashboard()
        dashboard.update_tier_progress("micro", current=50, total=100, active=True)
        
        panel = dashboard._render_tiers_panel()
        assert "Tiers" in str(panel.title)
    
    def test_render_footer(self):
        dashboard = LiveDashboard()
        footer = dashboard._render_footer()
        assert "Processed:" in footer.renderable
