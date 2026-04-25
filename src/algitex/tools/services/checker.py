from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from .http_checks import HTTPServiceChecks
from .local_checks import LocalSystemChecks
from .models import ServiceStatus


class ServiceChecker(HTTPServiceChecks, LocalSystemChecks):
    """Checker for various services used by algitex."""

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
        HTTPServiceChecks.__init__(self, self._client)
        LocalSystemChecks.__init__(self, timeout)

    def check_all(self, services: Optional[Dict[str, Any]] = None) -> List[ServiceStatus]:
        """Check all known services."""
        if services is None:
            services = {
                "ollama": {"host": "http://localhost:11434"},
                "litellm-proxy": {"url": "http://localhost:4000"},
                "code2llm": {"url": "http://localhost:8000"},
            }

        statuses: List[ServiceStatus] = []
        for name, config in services.items():
            if name == "ollama":
                statuses.append(self.check_ollama(config.get("host", "http://localhost:11434")))
            elif name == "litellm-proxy":
                statuses.append(self.check_litellm_proxy(config.get("url", "http://localhost:4000")))
            else:
                url = config.get("url")
                if url:
                    statuses.append(self.check_http_service(name, url))
                else:
                    port = config.get("port")
                    if port is not None:
                        statuses.append(self.check_mcp_service(name, int(port)))
        return statuses
