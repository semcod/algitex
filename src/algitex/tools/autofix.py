"""AutoFix — automated code fixing from TODO items.

Usage:
    from algitex.tools.autofix import AutoFix
    
    autofix = AutoFix()
    autofix.fix_all(limit=5)
    autofix.fix_issue("TASK-001")
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import requests
except ImportError:
    requests = None

from algitex.tools.todo_parser import TodoParser, Task
from algitex.tools.ollama import OllamaClient, OllamaService
from algitex.tools.services import ServiceChecker
from algitex.tools.proxy import Proxy


@dataclass
class FixResult:
    """Result of fixing an issue."""
    task: Task
    success: bool
    method: str  # "ollama", "aider", "litellm-proxy"
    time_ms: Optional[float] = None
    error: Optional[str] = None
    diff: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task.id,
            "task_description": self.task.description,
            "success": self.success,
            "method": self.method,
            "time_ms": self.time_ms,
            "error": self.error,
            "file_path": self.task.file_path
        }


class AutoFix:
    """Automated code fixing using various backends."""
    
    def __init__(
        self,
        todo_file: str = "TODO.md",
        backend: str = "auto",  # "auto", "ollama", "aider", "litellm-proxy"
        ollama_model: Optional[str] = None,
        proxy_url: str = "http://localhost:4000",
        dry_run: bool = False
    ):
        self.todo_file = Path(todo_file)
        self.backend = backend
        self.ollama_model = ollama_model
        self.proxy_url = proxy_url
        self.dry_run = dry_run
        
        # Initialize components
        self.parser = TodoParser(str(self.todo_file))
        self.service_checker = ServiceChecker()
        
        # Lazy initialization of backends
        self._ollama_service: Optional[OllamaService] = None
        self._proxy: Optional[Proxy] = None
    
    @property
    def ollama_service(self) -> OllamaService:
        """Get Ollama service instance."""
        if self._ollama_service is None:
            client = OllamaClient(default_model=self.ollama_model)
            self._ollama_service = OllamaService(client)
        return self._ollama_service
    
    @property
    def proxy(self) -> Proxy:
        """Get proxy instance."""
        if self._proxy is None:
            from algitex.config import ProxyConfig
            config = ProxyConfig(url=self.proxy_url, api_key="dummy-key")
            self._proxy = Proxy(config)
        return self._proxy
    
    def check_backends(self) -> Dict[str, bool]:
        """Check which backends are available."""
        available = {}
        
        # Check Ollama
        ollama_status = self.service_checker.check_ollama()
        available["ollama"] = ollama_status.healthy
        
        # Check Aider
        aider_status = self.service_checker.check_command_exists("aider", "aider")
        available["aider"] = aider_status.healthy
        
        # Check LiteLLM proxy
        proxy_status = self.service_checker.check_litellm_proxy(self.proxy_url)
        available["litellm-proxy"] = proxy_status.healthy
        
        return available
    
    def choose_backend(self) -> str:
        """Choose the best available backend."""
        if self.backend != "auto":
            return self.backend
        
        available = self.check_backends()
        
        # Priority: Ollama > LiteLLM proxy > Aider
        if available.get("ollama"):
            return "ollama"
        elif available.get("litellm-proxy"):
            return "litellm-proxy"
        elif available.get("aider"):
            return "aider"
        else:
            raise RuntimeError("No fixing backend available")
    
    def mark_task_done(self, task: Task) -> bool:
        """Mark a task as done in TODO.md."""
        try:
            content = self.todo_file.read_text(encoding='utf-8')
            
            # Find and replace the task line
            if task.file_path and task.line_number:
                # Prefact format: file.py:line - description
                search_line = f"- [ ] {task.file_path}:{task.line_number} - {task.description}"
                replace_line = f"- [x] {task.file_path}:{task.line_number} - {task.description}"
            else:
                # Generic format
                search_line = f"- [ ] {task.description}"
                replace_line = f"- [x] {task.description}"
            
            if search_line in content:
                content = content.replace(search_line, replace_line, 1)
                self.todo_file.write_text(content, encoding='utf-8')
                return True
            
            # Try more flexible matching
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if task.description in line and "- [ ]" in line:
                    lines[i] = line.replace("- [ ]", "- [x]", 1)
                    self.todo_file.write_text('\n'.join(lines), encoding='utf-8')
                    return True
            
            return False
        except Exception as e:
            print(f"Warning: Could not mark task as done: {e}")
            return False
    
    def fix_with_ollama(self, task: Task) -> FixResult:
        """Fix using Ollama."""
        import time
        start_time = time.time()
        
        if not task.file_path:
            return FixResult(
                task=task,
                success=False,
                method="ollama",
                error="No file path specified"
            )
        
        try:
            # Ensure we have a model
            if not self.ollama_model:
                models = self.ollama_service.get_recommended_models()
                if not models:
                    return FixResult(
                        task=task,
                        success=False,
                        method="ollama",
                        error="No suitable model found"
                    )
                self.ollama_model = models[0]
            
            # Fix the code
            success = self.ollama_service.auto_fix_file(
                task.file_path,
                task.description,
                task.line_number,
                self.ollama_model
            )
            
            elapsed = (time.time() - start_time) * 1000
            
            return FixResult(
                task=task,
                success=success,
                method="ollama",
                time_ms=elapsed,
                error=None if success else "Failed to fix code"
            )
        except Exception as e:
            return FixResult(
                task=task,
                success=False,
                method="ollama",
                time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    def fix_with_aider(self, task: Task) -> FixResult:
        """Fix using Aider CLI."""
        import time
        start_time = time.time()
        
        if not task.file_path:
            return FixResult(
                task=task,
                success=False,
                method="aider",
                error="No file path specified"
            )
        
        # Ensure git repo exists
        if not Path(".git").exists():
            subprocess.run(["git", "init"], capture_output=True)
            subprocess.run(["git", "config", "user.email", "autofix@local"], capture_output=True)
            subprocess.run(["git", "config", "user.name", "AutoFix"], capture_output=True)
        
        # Build prompt
        prompt = f"Fix this issue in {task.file_path}"
        if task.line_number:
            prompt += f" at line {task.line_number}"
        prompt += f":\n{task.description}\n\nMake minimal changes to fix only this specific issue."
        
        # Build command
        cmd = [
            "aider",
            "--model", "ollama/qwen2.5-coder:7b",
            "--openai-api-key", "dummy",
            "--no-git",
            "--no-commit",
            "--yes",
            "--no-check-version",
            "--message", prompt,
            task.file_path
        ]
        
        try:
            if self.dry_run:
                return FixResult(
                    task=task,
                    success=True,
                    method="aider",
                    time_ms=(time.time() - start_time) * 1000,
                    error="[DRY RUN]"
                )
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            elapsed = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                return FixResult(
                    task=task,
                    success=True,
                    method="aider",
                    time_ms=elapsed
                )
            else:
                return FixResult(
                    task=task,
                    success=False,
                    method="aider",
                    time_ms=elapsed,
                    error=result.stderr[:200] if result.stderr else "Aider failed"
                )
        except subprocess.TimeoutExpired:
            return FixResult(
                task=task,
                success=False,
                method="aider",
                time_ms=(time.time() - start_time) * 1000,
                error="Timeout (5min)"
            )
        except Exception as e:
            return FixResult(
                task=task,
                success=False,
                method="aider",
                time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    def fix_with_proxy(self, task: Task) -> FixResult:
        """Fix using LiteLLM proxy."""
        import time
        start_time = time.time()
        
        if not task.file_path:
            return FixResult(
                task=task,
                success=False,
                method="litellm-proxy",
                error="No file path specified"
            )
        
        if requests is None:
            return FixResult(
                task=task,
                success=False,
                method="litellm-proxy",
                error="requests module not installed. Install with: pip install requests"
            )
        
        try:
            # Read file content
            with open(task.file_path, 'r') as f:
                file_content = f.read()
            
            # Build prompt
            prompt = f"""Fix this specific issue in the code.

File: {task.file_path}
Line: {task.line_number or 'unknown'}
Issue: {task.description}

Current code:
```python
{file_content}
```

Provide ONLY the fixed code for this specific issue. Do not explain changes. Return the complete fixed file content."""
            
            if self.dry_run:
                return FixResult(
                    task=task,
                    success=True,
                    method="litellm-proxy",
                    time_ms=(time.time() - start_time) * 1000,
                    error="[DRY RUN]"
                )
            
            # Call proxy
            response = requests.post(
                f"{self.proxy_url}/v1/chat/completions",
                headers={
                    "Authorization": "Bearer dummy-key",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-coder",
                    "messages": [
                        {"role": "system", "content": "You are an expert Python code reviewer. Fix issues precisely."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=120
            )
            
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                fixed_code = data["choices"][0]["message"]["content"]
                
                # Extract code from markdown if present
                code_match = re.search(r'```python\n(.*?)\n```', fixed_code, re.DOTALL)
                if code_match:
                    fixed_code = code_match.group(1)
                
                # Write fixed code
                with open(task.file_path, 'w') as f:
                    f.write(fixed_code)
                
                return FixResult(
                    task=task,
                    success=True,
                    method="litellm-proxy",
                    time_ms=elapsed
                )
            else:
                return FixResult(
                    task=task,
                    success=False,
                    method="litellm-proxy",
                    time_ms=elapsed,
                    error=f"API error: {response.status_code}"
                )
        except Exception as e:
            return FixResult(
                task=task,
                success=False,
                method="litellm-proxy",
                time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    def fix_task(self, task: Task, backend: Optional[str] = None) -> FixResult:
        """Fix a single task."""
        backend = backend or self.choose_backend()
        
        if backend == "ollama":
            return self.fix_with_ollama(task)
        elif backend == "aider":
            return self.fix_with_aider(task)
        elif backend == "litellm-proxy":
            return self.fix_with_proxy(task)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def fix_all(
        self,
        limit: Optional[int] = None,
        backend: Optional[str] = None,
        filter_file: Optional[str] = None
    ) -> List[FixResult]:
        """Fix all pending tasks."""
        # Parse tasks
        tasks = self.parser.parse()
        
        # Apply filters
        if filter_file:
            tasks = [t for t in tasks if t.file_path == filter_file]
        
        if limit:
            tasks = tasks[:limit]
        
        if not tasks:
            print("No tasks found to fix.")
            return []
        
        # Choose backend
        backend = backend or self.choose_backend()
        print(f"Using backend: {backend}")
        
        # Fix tasks
        results = []
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] Fixing {task.id}: {task.description[:50]}...")
            
            result = self.fix_task(task, backend)
            results.append(result)
            
            if result.success:
                print(f"   ✅ Fixed with {result.method} ({result.time_ms:.0f}ms)")
                if not self.dry_run:
                    if self.mark_task_done(task):
                        print(f"   ✅ Marked as done in TODO.md")
            else:
                print(f"   ❌ Failed: {result.error}")
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def fix_issue(self, task_id: str, backend: Optional[str] = None) -> Optional[FixResult]:
        """Fix a specific task by ID."""
        tasks = self.parser.parse()
        task = next((t for t in tasks if t.id == task_id), None)
        
        if not task:
            print(f"Task {task_id} not found")
            return None
        
        print(f"Fixing {task_id}: {task.description}")
        
        result = self.fix_task(task, backend)
        
        if result.success:
            print(f"✅ Fixed with {result.method}")
            if not self.dry_run:
                self.mark_task_done(task)
        else:
            print(f"❌ Failed: {result.error}")
        
        return result
    
    def print_summary(self, results: List[FixResult]):
        """Print summary of fixing results."""
        print("\n" + "=" * 70)
        print("AutoFix Summary")
        print("=" * 70)
        
        total = len(results)
        fixed = sum(1 for r in results if r.success)
        failed = total - fixed
        
        print(f"Total issues: {total}")
        print(f"✅ Fixed: {fixed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\nFailed issues:")
            for r in results:
                if not r.success:
                    print(f"  - {r.task.id}: {r.error}")
        
        # Group by method
        by_method = {}
        for r in results:
            if r.success:
                by_method.setdefault(r.method, 0)
                by_method[r.method] += 1
        
        if by_method:
            print("\nFixed by method:")
            for method, count in by_method.items():
                print(f"  - {method}: {count}")
        
        if not self.dry_run and fixed > 0:
            print(f"\n📝 Review changes with: git diff")
            print(f"🚀 Commit with: git commit -m 'Fix {fixed} issues via AutoFix'")
    
    def list_tasks(self) -> List[Task]:
        """List all pending tasks."""
        return self.parser.parse()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tasks."""
        return self.parser.get_stats()
