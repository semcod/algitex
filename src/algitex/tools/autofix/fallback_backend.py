"""Fallback LLM backend service with automatic failover.

Tries multiple backends in order:
1. LiteLLM Proxy (primary)
2. Ollama (local fallback)
3. Aider (cli fallback)

Usage:
    from algitex.tools.autofix.fallback_backend import FallbackBackend
    
    backend = FallbackBackend(
        primary="litellm-proxy",
        fallbacks=["ollama", "aider"],
        proxy_url="http://localhost:4000"
    )
    result = backend.fix(task)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from algitex.tools.autofix.base import AutoFixBackend, Task, FixResult
from algitex.tools.autofix.proxy_backend import ProxyBackend
from algitex.tools.autofix.ollama_backend import OllamaBackend
from algitex.tools.autofix.aider_backend import AiderBackend
from algitex.tools.logging import verbose, verbose_print


@dataclass
class BackendStatus:
    """Status of a backend."""
    name: str
    healthy: bool = True
    last_error: Optional[str] = None
    last_used: float = field(default_factory=time.time)
    success_count: int = 0
    fail_count: int = 0


class FallbackBackend(AutoFixBackend):
    """Backend with automatic failover to alternative LLM services."""
    
    def __init__(
        self,
        primary: str = "litellm-proxy",
        fallbacks: List[str] = None,
        proxy_url: str = "http://localhost:4000",
        ollama_url: str = "http://localhost:11434",
        model: str = "qwen3-coder:latest",
        timeout: float = 30.0,
        retry_attempts: int = 2,
        dry_run: bool = True
    ):
        self.primary = primary
        self.fallbacks = fallbacks or ["ollama", "aider"]
        self.proxy_url = proxy_url
        self.ollama_url = ollama_url
        self.model = model
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.dry_run = dry_run
        
        # Track backend status
        self.backends: Dict[str, BackendStatus] = {
            name: BackendStatus(name=name)
            for name in [primary] + self.fallbacks
        }
        
        # Initialize backends on demand
        self._backend_instances: Dict[str, AutoFixBackend] = {}
        
        verbose_print(f"FallbackBackend initialized: primary={primary}, fallbacks={self.fallbacks}")
    
    def _get_backend(self, name: str) -> AutoFixBackend:
        """Get or create backend instance."""
        if name not in self._backend_instances:
            verbose_print(f"Creating backend instance: {name}")
            if name == "litellm-proxy":
                self._backend_instances[name] = ProxyBackend(
                    proxy_url=self.proxy_url,
                    dry_run=self.dry_run
                )
            elif name == "ollama":
                self._backend_instances[name] = OllamaBackend(
                    base_url=self.ollama_url,
                    model=self.model,
                    dry_run=self.dry_run
                )
            elif name == "aider":
                self._backend_instances[name] = AiderBackend(
                    dry_run=self.dry_run
                )
            else:
                raise ValueError(f"Unknown backend: {name}")
        
        return self._backend_instances[name]
    
    def _mark_success(self, name: str):
        """Mark backend as successful."""
        status = self.backends[name]
        status.healthy = True
        status.success_count += 1
        status.last_used = time.time()
        status.last_error = None
        verbose_print(f"Backend '{name}' marked as SUCCESS")
    
    def _mark_failure(self, name: str, error: str):
        """Mark backend as failed."""
        status = self.backends[name]
        status.healthy = False
        status.fail_count += 1
        status.last_used = time.time()
        status.last_error = error
        verbose_print(f"Backend '{name}' marked as FAILED: {error[:50]}")
    
    @verbose
    def _try_backend(self, name: str, task: Task) -> Optional[FixResult]:
        """Try to fix with a specific backend."""
        verbose_print(f"Attempting fix with backend '{name}' for task {task.id}")
        
        try:
            backend = self._get_backend(name)
            result = backend.fix(task)
            
            if result.success:
                self._mark_success(name)
                print(f"   ✓ Backend '{name}' succeeded")
                return result
            else:
                self._mark_failure(name, f"Fix returned failure: {result.error or 'Unknown'}")
                print(f"   ✗ Backend '{name}' failed (returned failure)")
                return None
                
        except Exception as e:
            self._mark_failure(name, str(e))
            print(f"   ✗ Backend '{name}' error: {e}")
            return None
    
    @verbose
    def fix(self, task: Task) -> FixResult:
        """Try to fix task with automatic fallback."""
        verbose_print(f"FallbackBackend.fix() called for task {task.id}")
        
        # Try primary backend first
        print(f"   🔧 Trying primary backend: {self.primary}")
        for attempt in range(self.retry_attempts):
            verbose_print(f"Primary attempt {attempt + 1}/{self.retry_attempts}")
            result = self._try_backend(self.primary, task)
            if result and result.success:
                return result
            if attempt < self.retry_attempts - 1:
                print(f"   ↻ Retrying {self.primary} (attempt {attempt + 2}/{self.retry_attempts})")
                time.sleep(1)
        
        # Try fallbacks in order
        for fallback in self.fallbacks:
            print(f"   🔧 Fallback to: {fallback}")
            for attempt in range(self.retry_attempts):
                verbose_print(f"Fallback '{fallback}' attempt {attempt + 1}/{self.retry_attempts}")
                result = self._try_backend(fallback, task)
                if result and result.success:
                    return result
                if attempt < self.retry_attempts - 1:
                    print(f"   ↻ Retrying {fallback} (attempt {attempt + 2}/{self.retry_attempts})")
                    time.sleep(1)
        
        # All backends failed
        print(f"   ✗ All backends failed for {task.id}")
        verbose_print(f"All backends exhausted for task {task.id}")
        return FixResult(
            task_id=task.id,
            task_description=task.description,
            success=False,
            error="All backends failed"
        )
    
    def print_status(self):
        """Print status of all backends."""
        print("\n" + "=" * 60)
        print("BACKEND STATUS")
        print("=" * 60)
        
        for name, status in self.backends.items():
            health = "✓" if status.healthy else "✗"
            print(f"  {health} {name}: {status.success_count} OK, {status.fail_count} FAIL")
            if status.last_error:
                print(f"    Last error: {status.last_error[:50]}")
        
        print("=" * 60)
