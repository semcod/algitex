"""Context management — build optimal prompts for LLM coding tools."""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import subprocess

import yaml


@dataclass
class CodeContext:
    """Assembled context for an LLM coding task."""
    project_summary: str     # Z analysis.toon — CC̄, alerts, hotspots
    architecture: str        # Z map.toon — moduły, zależności
    target_files: List[str]  # Pliki do modyfikacji
    related_files: List[str] # Pliki powiązane (imports, tests)
    conventions: str         # Z .editorconfig, pyproject.toml, CLAUDE.md
    recent_changes: str      # Z git log --oneline -10
    ticket_context: str      # Z planfile ticket
    total_tokens: int = 0

    def to_prompt(self, task: str) -> str:
        """Convert context to a formatted prompt."""
        return f"""## Project context
{self.project_summary}

## Architecture
{self.architecture}

## Conventions
{self.conventions}

## Recent changes
{self.recent_changes}

## Task
{task}

## Ticket context
{self.ticket_context}

## Files to modify
{chr(10).join(f'- {f}' for f in self.target_files)}

## Related files (read-only context)
{chr(10).join(f'- {f}' for f in self.related_files)}
"""


class ContextBuilder:
    """Build rich context for LLM coding tasks from .toon files + git + planfile."""

    def __init__(self, project_path: str):
        self.root = Path(project_path).resolve()

    def build(self, ticket: Optional[Dict[str, Any]] = None, max_tokens: int = 8000) -> CodeContext:
        """Assemble context from all available sources."""
        return CodeContext(
            project_summary=self._load_toon_summary(),
            architecture=self._load_architecture(),
            target_files=self._resolve_targets(ticket),
            related_files=self._find_related(ticket),
            conventions=self._load_conventions(),
            recent_changes=self._git_recent(),
            ticket_context=self._format_ticket(ticket),
        )

    def _load_toon_summary(self) -> str:
        """Extract key metrics from analysis.toon and project.toon."""
        for name in ["project.toon.yaml", "analysis.toon.yaml", "project_toon.yaml"]:
            path = self.root / name
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        lines = f.readlines()[:15]
                    return "\n".join(lines)
                except Exception:
                    continue
        return "No .toon diagnostics found."

    def _load_architecture(self) -> str:
        """Extract module list from map.toon."""
        for name in ["map.toon.yaml", "map_toon.yaml"]:
            path = self.root / name
            if path.exists():
                try:
                    text = path.read_text()
                    # Extract M[...] section
                    if "M[" in text:
                        start = text.index("M[")
                        end = text.index("\nD:", start) if "\nD:" in text[start:] else len(text)
                        return text[start:start+500]
                except Exception:
                    continue
        return ""

    def _resolve_targets(self, ticket: Optional[Dict[str, Any]]) -> List[str]:
        """Get files to modify from ticket hints."""
        if not ticket:
            return []
        return ticket.get("llm_hints", {}).get("files_to_modify", [])

    def _find_related(self, ticket: Optional[Dict[str, Any]]) -> List[str]:
        """Find related files via imports + test files."""
        targets = self._resolve_targets(ticket)
        related = set()
        
        for target in targets:
            path = self.root / target
            if path.exists():
                try:
                    # Find imports
                    content = path.read_text()
                    for line in content.splitlines():
                        if line.startswith(("from ", "import ")):
                            related.add(line)
                    
                    # Find test file
                    test = self.root / "tests" / f"test_{path.name}"
                    if test.exists():
                        related.add(str(test.relative_to(self.root)))
                except Exception:
                    continue
                    
        return list(related)[:10]

    def _load_conventions(self) -> str:
        """Load project conventions from config files."""
        conventions = []
        for name in ["CLAUDE.md", "AGENTS.md", ".editorconfig", "pyproject.toml"]:
            path = self.root / name
            if path.exists():
                try:
                    text = path.read_text()[:500]
                    conventions.append(f"### {name}\n{text}")
                except Exception:
                    continue
        return "\n".join(conventions[:3]) or "No conventions files found."

    def _git_recent(self) -> str:
        """Get recent git history."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.root, capture_output=True, text=True, timeout=5,
            )
            return result.stdout.strip() or "No git history."
        except Exception:
            return "Git not available."

    def _format_ticket(self, ticket: Optional[Dict[str, Any]]) -> str:
        """Format ticket information."""
        if not ticket:
            return ""
        return (
            f"ID: {ticket.get('id', 'N/A')}\n"
            f"Title: {ticket.get('title', '')}\n"
            f"Priority: {ticket.get('priority', 'normal')}\n"
            f"Description: {ticket.get('description', '')}\n"
        )


class SemanticCache:
    """Optional semantic caching using Qdrant for context retrieval."""
    
    def __init__(self, project_path: str, qdrant_url: str = "http://localhost:6333"):
        self.root = Path(project_path).resolve()
        self.qdrant_url = qdrant_url
        self._client = None
        
    def _get_client(self):
        """Lazy initialize Qdrant client."""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
                self._client = QdrantClient(url=self.qdrant_url)
            except ImportError:
                return None
        return self._client
    
    def search_similar_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar previous contexts."""
        client = self._get_client()
        if not client:
            return []
            
        try:
            # This would require embedding generation - placeholder for now
            # In a real implementation, you'd use an embedding model
            return []
        except Exception:
            return []
    
    def store_context(self, context: CodeContext, task: str, result: Dict[str, Any]) -> None:
        """Store context with its result for future retrieval."""
        client = self._get_client()
        if not client:
            return
            
        try:
            # Store in Qdrant with embeddings - placeholder
            pass
        except Exception:
            pass
