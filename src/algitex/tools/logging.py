"""Verbose logging utilities with decorators for algitex.

Usage:
    from algitex.tools.logging import log_calls, log_time, verbose
    
    @log_calls
    def my_function():
        pass
    
    @log_time
    def slow_function():
        pass
    
    @verbose
    def debug_function(ctx):
        pass
"""
from __future__ import annotations

import functools
import time
from typing import Callable, Any


# Global verbose flag
VERBOSE = False


def set_verbose(enabled: bool = True):
    """Enable or disable verbose logging globally."""
    global VERBOSE
    VERBOSE = enabled


def log_calls(func: Callable) -> Callable:
    """Decorator to log function calls with arguments and results."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not VERBOSE:
            return func(*args, **kwargs)
        
        func_name = func.__qualname__
        print(f"[VERBOSE] → {func_name}({format_args(args, kwargs)})")
        
        try:
            result = func(*args, **kwargs)
            print(f"[VERBOSE] ← {func_name} = {format_result(result)}")
            return result
        except Exception as e:
            print(f"[VERBOSE] ✗ {func_name} raised {type(e).__name__}: {e}")
            raise
    
    return wrapper


def log_time(func: Callable) -> Callable:
    """Decorator to log function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not VERBOSE:
            return func(*args, **kwargs)
        
        func_name = func.__qualname__
        start = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"[VERBOSE] ⏱ {func_name}: {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"[VERBOSE] ✗ {func_name}: {elapsed:.3f}s (failed)")
            raise
    
    return wrapper


def verbose(func: Callable) -> Callable:
    """Combined decorator: logs calls, time, and results."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not VERBOSE:
            return func(*args, **kwargs)
        
        func_name = func.__qualname__
        args_str = format_args(args, kwargs)
        
        print(f"[VERBOSE] → {func_name}({args_str})")
        start = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"[VERBOSE] ← {func_name} = {format_result(result)} ({elapsed:.3f}s)")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"[VERBOSE] ✗ {func_name} raised {type(e).__name__}: {e} ({elapsed:.3f}s)")
            raise
    
    return wrapper


def format_args(args, kwargs) -> str:
    """Format arguments for display."""
    parts = []
    for arg in args:
        parts.append(format_value(arg))
    for key, value in kwargs.items():
        parts.append(f"{key}={format_value(value)}")
    return ", ".join(parts[:5])  # Limit to 5 args


def format_value(value: Any) -> str:
    """Format a value for display."""
    value_str = repr(value)
    if len(value_str) > 50:
        value_str = value_str[:47] + "..."
    return value_str


def format_result(result: Any) -> str:
    """Format a result for display."""
    result_str = repr(result)
    if len(result_str) > 50:
        result_str = result_str[:47] + "..."
    return result_str


class VerboseContext:
    """Context manager for verbose logging in a block."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        if VERBOSE:
            self.start_time = time.perf_counter()
            print(f"[VERBOSE] ▶ {self.name}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if VERBOSE:
            elapsed = time.perf_counter() - self.start_time
            if exc_type:
                print(f"[VERBOSE] ✗ {self.name} failed: {exc_val} ({elapsed:.3f}s)")
            else:
                print(f"[VERBOSE] ✓ {self.name} completed ({elapsed:.3f}s)")
        return False


def verbose_print(msg: str, level: str = "INFO"):
    """Print verbose message if verbose mode is enabled."""
    if VERBOSE:
        print(f"[VERBOSE] [{level}] {msg}")
