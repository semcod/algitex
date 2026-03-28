"""Ollama backend — native Ollama support for local LLMs.

Usage:
    from algitex.tools.ollama import OllamaClient
    
    client = OllamaClient()
    models = client.list_models()
    response = client.generate("Explain this code", model="qwen2.5-coder:7b")
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import httpx
from pathlib import Path


@dataclass
class OllamaModel:
    """Information about an Ollama model."""
    name: str
    size: int
    digest: str
    modified_at: str
    
    @property
    def display_name(self) -> str:
        """Get display name without tag."""
        return self.name.split(":")[0]


@dataclass
class OllamaResponse:
    """Response from Ollama API."""
    content: str
    model: str
    created_at: Optional[str] = None
    done: bool = True
    total_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None
    
    def __str__(self) -> str:
        return self.content


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(
        self,
        host: str = "http://localhost:11434",
        timeout: float = 120.0,
        default_model: Optional[str] = None
    ):
        self.host = host.rstrip("/")
        self.timeout = timeout
        self.default_model = default_model
        self._client = httpx.Client(base_url=self.host, timeout=timeout)
    
    def health(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = self._client.get("/api/tags")
            return response.status_code == 200
        except httpx.RequestError:
            return False
    
    def list_models(self) -> List[OllamaModel]:
        """List available models."""
        try:
            response = self._client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                models.append(OllamaModel(
                    name=model["name"],
                    size=model.get("size", 0),
                    digest=model.get("digest", ""),
                    modified_at=model.get("modified_at", "")
                ))
            
            return models
        except (httpx.RequestError, json.JSONDecodeError):
            return []
    
    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            response = self._client.post("/api/pull", json={"name": model})
            response.raise_for_status()
            # Stream response to show progress
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if data.get("status") == "success":
                        return True
            return True
        except (httpx.RequestError, json.JSONDecodeError):
            return False
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        format: Optional[str] = None  # "json" for structured output
    ) -> Union[OllamaResponse, List[OllamaResponse]]:
        """Generate text using Ollama."""
        model = model or self.default_model
        
        if not model:
            raise ValueError("No model specified and no default model set")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }
        
        if system:
            payload["system"] = system
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        if format:
            payload["format"] = format
        
        try:
            response = self._client.post("/api/generate", json=payload)
            response.raise_for_status()
            
            if stream:
                responses = []
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        responses.append(OllamaResponse(
                            content=data.get("response", ""),
                            model=data.get("model", model),
                            done=data.get("done", False)
                        ))
                return responses
            else:
                data = response.json()
                return OllamaResponse(
                    content=data.get("response", ""),
                    model=data.get("model", model),
                    created_at=data.get("created_at"),
                    done=data.get("done", True),
                    total_duration=data.get("total_duration"),
                    prompt_eval_count=data.get("prompt_eval_count"),
                    eval_count=data.get("eval_count")
                )
        except (httpx.RequestError, json.JSONDecodeError) as e:
            return OllamaResponse(content=f"[Ollama error: {e}]", model=model or "")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        format: Optional[str] = None
    ) -> Union[OllamaResponse, List[OllamaResponse]]:
        """Chat with Ollama using message format."""
        model = model or self.default_model
        
        if not model:
            raise ValueError("No model specified and no default model set")
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        if format:
            payload["format"] = format
        
        try:
            response = self._client.post("/api/chat", json=payload)
            response.raise_for_status()
            
            if stream:
                responses = []
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        msg = data.get("message", {})
                        responses.append(OllamaResponse(
                            content=msg.get("content", ""),
                            model=data.get("model", model),
                            done=data.get("done", False)
                        ))
                return responses
            else:
                data = response.json()
                msg = data.get("message", {})
                return OllamaResponse(
                    content=msg.get("content", ""),
                    model=data.get("model", model),
                    created_at=data.get("created_at"),
                    done=data.get("done", True),
                    total_duration=data.get("total_duration"),
                    prompt_eval_count=data.get("prompt_eval_count"),
                    eval_count=data.get("eval_count")
                )
        except (httpx.RequestError, json.JSONDecodeError) as e:
            return OllamaResponse(content=f"[Ollama error: {e}]", model=model or "")
    
    def fix_code(
        self,
        file_path: str,
        issue: str,
        line_number: Optional[int] = None,
        model: Optional[str] = None
    ) -> Optional[str]:
        """Fix code issue using Ollama."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except Exception:
            return None
        
        system_prompt = "You are an expert Python developer. Fix the specific issue described. Make minimal changes to fix only this issue. Return only the complete fixed code without explanations."
        
        user_prompt = f"""Fix this issue in {file_path}"""
        
        if line_number:
            user_prompt += f" at line {line_number}"
        
        user_prompt += f""":
        
Issue: {issue}

Current code:
```python
{code}
```

Provide the complete fixed code."""
        
        response = self.generate(
            prompt=user_prompt,
            system=system_prompt,
            model=model,
            temperature=0.3
        )
        
        # Extract code from response if wrapped in markdown
        content = response.content
        code_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
        if code_match:
            return code_match.group(1)
        
        return content
    
    def analyze_code(
        self,
        code: str,
        model: Optional[str] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Analyze code and return structured feedback."""
        system_prompt = "You are a code analysis expert. Analyze the provided code and return JSON with complexity, issues, and suggestions."
        
        prompt = f"""Analyze this Python code and provide feedback:

```python
{code}
```

Return JSON with:
{{
    "complexity": "low|medium|high",
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "score": 0.0-10.0
}}"""
        
        response = self.generate(
            prompt=prompt,
            system=system_prompt,
            model=model,
            temperature=0.3,
            format=format
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"raw_response": response.content}
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class OllamaService:
    """High-level service for Ollama operations."""
    
    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()
    
    def ensure_model(self, model: str) -> bool:
        """Ensure model is available, pull if necessary."""
        models = self.client.list_models()
        if any(m.name == model for m in models):
            return True
        
        print(f"Pulling model {model}...")
        return self.client.pull_model(model)
    
    def get_recommended_models(self) -> List[str]:
        """Get list of recommended coding models."""
        models = self.client.list_models()
        model_names = [m.name for m in models]
        
        recommended = [
            "qwen2.5-coder:7b",
            "qwen2.5-coder:3b",
            "codellama:7b",
            "deepseek-coder:6.7b",
            "llama3:8b"
        ]
        
        available = [m for m in recommended if m in model_names]
        return available
    
    def auto_fix_file(
        self,
        file_path: str,
        issue: str,
        line_number: Optional[int] = None,
        model: Optional[str] = None
    ) -> bool:
        """Fix issue in file and write back the result."""
        if not model:
            # Try to find a good coding model
            coding_models = self.get_recommended_models()
            model = coding_models[0] if coding_models else None
        
        if not model:
            print("No suitable model found for code fixing")
            return False
        
        fixed_code = self.client.fix_code(file_path, issue, line_number, model)
        if not fixed_code:
            return False
        
        try:
            with open(file_path, 'w') as f:
                f.write(fixed_code)
            return True
        except Exception:
            return False
