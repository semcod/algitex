"""Ollama integration mixins for Project class."""

from __future__ import annotations

from typing import List, Optional

from algitex.tools.ollama import OllamaClient, OllamaService


class OllamaMixin:
    """Ollama integration functionality for Project."""

    def __init__(self) -> None:
        self.ollama = OllamaService()

    def check_ollama(self) -> dict:
        """Check Ollama status and available models."""
        from algitex.tools.services import ServiceChecker
        status = ServiceChecker().check_ollama()
        return status.to_dict()

    def list_ollama_models(self) -> list:
        """List available Ollama models."""
        models = self.ollama.client.list_models()
        return [{"name": m.name, "size": m.size, "modified_at": m.modified_at} for m in models]

    def pull_ollama_model(self, model: str) -> bool:
        """Pull an Ollama model."""
        return self.ollama.ensure_model(model)

    def generate_with_ollama(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None
    ) -> str:
        """Generate text using Ollama."""
        response = self.ollama.client.generate(prompt, model=model, system=system)
        return str(response)
