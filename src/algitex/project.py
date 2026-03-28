"""Project — backward compatibility shim.

This module re-exports from the new project package for backward compatibility.
New code should import directly from algitex.project.
"""

# Re-export everything from the new package
from algitex.project import (
    Project,
)
from algitex.project.services import ServiceMixin
from algitex.project.autofix import AutoFixMixin
from algitex.project.ollama import OllamaMixin
from algitex.project.batch import BatchMixin
from algitex.project.benchmark import BenchmarkMixin
from algitex.project.ide import IDEMixin
from algitex.project.config import ConfigMixin
from algitex.project.mcp import MCPMixin

__all__ = [
    "Project",
    "ServiceMixin",
    "AutoFixMixin",
    "OllamaMixin",
    "BatchMixin",
    "BenchmarkMixin",
    "IDEMixin",
    "ConfigMixin",
    "MCPMixin",
]
