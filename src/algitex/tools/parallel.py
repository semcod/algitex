"""Parallel task coordination for algitex — backward compatibility shim.

This module re-exports from algitex.tools.parallel for backward compatibility.
New code should import directly from algitex.tools.parallel.
"""
# Re-export all classes from the new package location for backward compatibility
from algitex.tools.parallel.models import (
    RegionType,
    CodeRegion,
    TaskAssignment,
    MergeResult,
)

from algitex.tools.parallel.extractor import RegionExtractor

from algitex.tools.parallel.partitioner import TaskPartitioner

from algitex.tools.parallel.executor import ParallelExecutor

__all__ = [
    "RegionType",
    "CodeRegion", 
    "TaskAssignment",
    "MergeResult",
    "RegionExtractor",
    "TaskPartitioner",
    "ParallelExecutor",
]
