"""LLM Cache layer for OllamaClient — deduplicates identical prompts.

Usage:
    from algitex.tools.ollama_cache import CachedOllamaClient
    
    client = CachedOllamaClient(cache_dir=".algitex/cache")
    # Same prompt + model = cached response, no LLM call
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any, List
import time

from algitex.tools.ollama import OllamaClient, OllamaResponse


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""
    prompt_hash: str
    model: str
    response: str
    timestamp: float
    tokens_prompt: int
    tokens_response: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_hash": self.prompt_hash,
            "model": self.model,
            "response": self.response,
            "timestamp": self.timestamp,
            "tokens_prompt": self.tokens_prompt,
            "tokens_response": self.tokens_response,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        return cls(**data)


class LLMCache:
    """Disk-based cache for LLM responses."""
    
    def __init__(self, cache_dir: str = ".algitex/cache", ttl_hours: float = 24.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def _hash_prompt(self, prompt: str, model: str, **kwargs) -> str:
        """Create deterministic hash from prompt + model + params."""
        content = json.dumps({
            "prompt": prompt,
            "model": model,
            "params": {k: v for k, v in kwargs.items() if k not in ("stream",)}
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def _cache_path(self, prompt_hash: str) -> Path:
        """Get path to cache file for hash."""
        return self.cache_dir / f"{prompt_hash}.json"
    
    def get(self, prompt: str, model: str, **kwargs) -> Optional[CacheEntry]:
        """Get cached response if available and not expired."""
        prompt_hash = self._hash_prompt(prompt, model, **kwargs)
        cache_path = self._cache_path(prompt_hash)
        
        if not cache_path.exists():
            self._stats["misses"] += 1
            return None
        
        try:
            data = json.loads(cache_path.read_text())
            entry = CacheEntry.from_dict(data)
            
            # Check TTL
            if time.time() - entry.timestamp > self.ttl_seconds:
                cache_path.unlink()
                self._stats["evictions"] += 1
                return None
            
            self._stats["hits"] += 1
            return entry
            
        except (json.JSONDecodeError, KeyError):
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(
        self,
        prompt: str,
        model: str,
        response: str,
        tokens_prompt: int = 0,
        tokens_response: int = 0,
        **kwargs
    ) -> None:
        """Cache a response."""
        prompt_hash = self._hash_prompt(prompt, model, **kwargs)
        entry = CacheEntry(
            prompt_hash=prompt_hash,
            model=model,
            response=response,
            timestamp=time.time(),
            tokens_prompt=tokens_prompt,
            tokens_response=tokens_response,
            metadata={"params": kwargs},
        )
        
        cache_path = self._cache_path(prompt_hash)
        cache_path.write_text(json.dumps(entry.to_dict(), indent=2))
    
    def clear(self) -> int:
        """Clear all cache entries, return count removed."""
        count = 0
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
            count += 1
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}
        return count
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0.0
        
        entries = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in entries)
        
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate,
            "entries": len(entries),
            "size_bytes": total_size,
        }
    
    def list_entries(self) -> List[Dict[str, Any]]:
        """List all cache entries with metadata."""
        entries = []
        for f in sorted(self.cache_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text())
                age_hours = (time.time() - data["timestamp"]) / 3600
                entries.append({
                    "hash": data["prompt_hash"],
                    "model": data["model"],
                    "age_hours": round(age_hours, 1),
                    "tokens": data["tokens_prompt"] + data["tokens_response"],
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return entries


class CachedOllamaClient(OllamaClient):
    """OllamaClient with automatic response caching."""
    
    def __init__(
        self,
        host: str = "http://localhost:11434",
        timeout: float = 120.0,
        default_model: Optional[str] = None,
        cache_dir: str = ".algitex/cache",
        cache_ttl_hours: float = 24.0,
        enable_cache: bool = True,
    ):
        super().__init__(host=host, timeout=timeout, default_model=default_model)
        self.cache = LLMCache(cache_dir, cache_ttl_hours) if enable_cache else None
        self._metrics = {"calls": 0, "cached": 0, "tokens_in": 0, "tokens_out": 0}
    
    def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> OllamaResponse:
        """Generate with automatic caching."""
        model = model or self.default_model
        if not model:
            raise ValueError("No model specified")
        
        self._metrics["calls"] += 1
        
        # Check cache
        if self.cache:
            cached = self.cache.get(prompt, model, **kwargs)
            if cached:
                self._metrics["cached"] += 1
                return OllamaResponse(
                    content=cached.response,
                    model=model,
                    done=True,
                    prompt_eval_count=cached.tokens_prompt,
                    eval_count=cached.tokens_response,
                )
        
        # Call Ollama
        response = super().generate(prompt, model=model, **kwargs)
        
        # Cache successful response
        if self.cache and response.done and not response.content.startswith("[Ollama error"):
            self.cache.set(
                prompt=prompt,
                model=model,
                response=response.content,
                tokens_prompt=response.prompt_eval_count or 0,
                tokens_response=response.eval_count or 0,
                **kwargs
            )
            self._metrics["tokens_in"] += response.prompt_eval_count or 0
            self._metrics["tokens_out"] += response.eval_count or 0
        
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics including cache stats."""
        cache_stats = self.cache.stats() if self.cache else {"disabled": True}
        return {
            "calls": self._metrics["calls"],
            "cached_responses": self._metrics["cached"],
            "cache_hit_rate": self._metrics["cached"] / self._metrics["calls"] if self._metrics["calls"] else 0,
            "tokens_prompt": self._metrics["tokens_in"],
            "tokens_response": self._metrics["tokens_out"],
            "cache": cache_stats,
        }
    
    def clear_cache(self) -> int:
        """Clear cache and return number of entries removed."""
        return self.cache.clear() if self.cache else 0


# Backwards compatibility alias
OllamaCache = LLMCache
