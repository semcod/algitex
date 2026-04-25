from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import httpx

from .models import ServiceStatus


class HTTPServiceChecks:
    """HTTP-based checks for external services."""

    def __init__(self, client: httpx.Client):
        self._client = client

    def check_http_service(
        self,
        name: str,
        url: str,
        health_path: str = "/health",
        expected_status: int = 200,
    ) -> ServiceStatus:
        """Check an HTTP service."""
        full_url = url.rstrip("/") + health_path
        start_time = time.time()
        try:
            response = self._client.get(full_url)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == expected_status:
                details: Dict[str, Any] = {}
                try:
                    if response.content:
                        details = response.json()
                except json.JSONDecodeError:
                    pass

                return ServiceStatus(
                    name=name,
                    healthy=True,
                    url=url,
                    response_time_ms=response_time,
                    details=details,
                )

            return ServiceStatus(
                name=name,
                healthy=False,
                url=url,
                response_time_ms=response_time,
                error=f"HTTP {response.status_code}",
            )
        except httpx.RequestError as e:
            return ServiceStatus(name=name, healthy=False, url=url, error=str(e))

    def check_ollama(self, host: str = "http://localhost:11434") -> ServiceStatus:
        """Check Ollama service."""
        start_time = time.time()
        try:
            response = self._client.get(f"{host}/api/tags")
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                return ServiceStatus(
                    name="ollama",
                    healthy=True,
                    url=host,
                    response_time_ms=response_time,
                    details={
                        "models_count": len(models),
                        "models": models[:10],
                        "total_models": len(models),
                    },
                )

            return ServiceStatus(
                name="ollama",
                healthy=False,
                url=host,
                error=f"HTTP {response.status_code}",
            )
        except Exception as e:
            return ServiceStatus(name="ollama", healthy=False, url=host, error=str(e))

    def check_litellm_proxy(self, url: str = "http://localhost:4000") -> ServiceStatus:
        """Check LiteLLM proxy."""
        start_time = time.time()
        try:
            response = self._client.get(f"{url}/v1/models")
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                models = [m["id"] for m in data.get("data", [])]
                return ServiceStatus(
                    name="litellm-proxy",
                    healthy=True,
                    url=url,
                    response_time_ms=response_time,
                    details={
                        "models_count": len(models),
                        "models": models[:10],
                        "total_models": len(models),
                    },
                )

            return ServiceStatus(
                name="litellm-proxy",
                healthy=False,
                url=url,
                error=f"HTTP {response.status_code}",
            )
        except Exception as e:
            return ServiceStatus(
                name="litellm-proxy", healthy=False, url=url, error=str(e)
            )

    def check_mcp_service(self, name: str, port: int) -> ServiceStatus:
        """Check an MCP service by port."""
        url = f"http://localhost:{port}"
        return self.check_http_service(name, url, "/health")
