"""Tests for ollama_cache module."""

import json
import tempfile
from pathlib import Path

import pytest

from algitex.tools.ollama_cache import CacheEntry, LLMCache, CachedOllamaClient


class TestCacheEntry:
    def test_cache_entry_creation(self):
        entry = CacheEntry(
            prompt_hash="abc123",
            model="qwen2.5-coder:7b",
            response="Test response",
            timestamp=1234567890.0,
            tokens_prompt=100,
            tokens_response=50,
            metadata={"param": "value"},
        )
        assert entry.prompt_hash == "abc123"
        assert entry.tokens_prompt == 100
    
    def test_cache_entry_to_dict(self):
        entry = CacheEntry(
            prompt_hash="abc123",
            model="qwen2.5-coder:7b",
            response="Test response",
            timestamp=1234567890.0,
            tokens_prompt=100,
            tokens_response=50,
            metadata={},
        )
        d = entry.to_dict()
        assert d["prompt_hash"] == "abc123"
        assert d["model"] == "qwen2.5-coder:7b"
    
    def test_cache_entry_from_dict(self):
        data = {
            "prompt_hash": "abc123",
            "model": "qwen2.5-coder:7b",
            "response": "Test",
            "timestamp": 1234567890.0,
            "tokens_prompt": 100,
            "tokens_response": 50,
            "metadata": {},
        }
        entry = CacheEntry.from_dict(data)
        assert entry.prompt_hash == "abc123"


class TestLLMCache:
    def test_cache_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir, ttl_hours=24.0)
            assert cache.cache_dir == Path(tmpdir)
            assert cache.ttl_seconds == 24.0 * 3600
    
    def test_cache_set_and_get(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir, ttl_hours=24.0)
            
            cache.set(
                prompt="Test prompt",
                model="qwen2.5-coder:7b",
                response="Test response",
                tokens_prompt=100,
                tokens_response=50,
            )
            
            entry = cache.get(prompt="Test prompt", model="qwen2.5-coder:7b")
            assert entry is not None
            assert entry.response == "Test response"
            assert entry.tokens_prompt == 100
    
    def test_cache_miss(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir)
            
            entry = cache.get(prompt="Nonexistent", model="qwen2.5-coder:7b")
            assert entry is None
            
            stats = cache.stats()
            assert stats["misses"] == 1
    
    def test_cache_hit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir)
            
            cache.set("Test prompt", "qwen2.5-coder:7b", "Response", 100, 50)
            cache.get("Test prompt", "qwen2.5-coder:7b")
            
            stats = cache.stats()
            assert stats["hits"] == 1
            assert stats["misses"] == 0
    
    def test_cache_ttl_expiration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Very short TTL
            cache = LLMCache(cache_dir=tmpdir, ttl_hours=0.0001)  # 0.36 seconds
            
            cache.set("Test", "model", "Response", 10, 10)
            
            import time
            time.sleep(0.5)  # Wait for expiration
            
            entry = cache.get("Test", "model")
            assert entry is None  # Expired
    
    def test_cache_clear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir)
            
            cache.set("Test1", "model", "Response1", 10, 10)
            cache.set("Test2", "model", "Response2", 10, 10)
            
            count = cache.clear()
            assert count == 2
            
            stats = cache.stats()
            assert stats["entries"] == 0
    
    def test_cache_deduplication_same_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir)
            
            # Same prompt, same model
            cache.set("Test prompt", "qwen2.5-coder:7b", "Response1", 100, 50)
            cache.set("Test prompt", "qwen2.5-coder:7b", "Response2", 100, 50)
            
            entry = cache.get("Test prompt", "qwen2.5-coder:7b")
            assert entry.response == "Response2"  # Overwritten
    
    def test_cache_different_models(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir)
            
            # Same prompt, different models
            cache.set("Test", "model1", "Response1", 10, 10)
            cache.set("Test", "model2", "Response2", 10, 10)
            
            assert cache.get("Test", "model1").response == "Response1"
            assert cache.get("Test", "model2").response == "Response2"
    
    def test_cache_with_parameters(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir)
            
            # Same prompt/model but different params should be different entries
            cache.set("Test", "model", "Response1", 10, 10, temperature=0.7)
            cache.set("Test", "model", "Response2", 10, 10, temperature=0.9)
            
            entry1 = cache.get("Test", "model", temperature=0.7)
            entry2 = cache.get("Test", "model", temperature=0.9)
            
            assert entry1.response == "Response1"
            assert entry2.response == "Response2"
    
    def test_stats_calculation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir)
            
            cache.set("A", "model", "R", 100, 50)
            cache.set("B", "model", "R", 100, 50)
            
            cache.get("A", "model")  # Hit
            cache.get("A", "model")  # Hit
            cache.get("X", "model")  # Miss
            
            stats = cache.stats()
            assert stats["hits"] == 2
            assert stats["misses"] == 1
            assert stats["hit_rate"] == 2/3
            assert stats["entries"] == 2
    
    def test_list_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = LLMCache(cache_dir=tmpdir)
            
            cache.set("Test", "qwen2.5-coder:7b", "Response", 100, 50)
            entries = cache.list_entries()
            
            assert len(entries) == 1
            assert entries[0]["model"] == "qwen2.5-coder:7b"
            assert "hash" in entries[0]


class TestCachedOllamaClient:
    @pytest.mark.skip(reason="Requires Ollama server")
    def test_client_with_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            client = CachedOllamaClient(
                host="http://localhost:11434",
                cache_dir=tmpdir,
                enable_cache=True,
            )
            
            # Mock or test with real server
            assert client.cache is not None
    
    def test_client_metrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            client = CachedOllamaClient(
                cache_dir=tmpdir,
                enable_cache=True,
            )
            
            metrics = client.get_metrics()
            assert "calls" in metrics
            assert "cached_responses" in metrics
            assert "cache" in metrics
    
    def test_client_clear_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            client = CachedOllamaClient(
                cache_dir=tmpdir,
                enable_cache=True,
            )
            
            # Add something to cache
            client.cache.set("Test", "model", "Response", 10, 10)
            
            count = client.clear_cache()
            assert count == 1
    
    def test_client_disabled_cache(self):
        client = CachedOllamaClient(enable_cache=False)
        assert client.cache is None
