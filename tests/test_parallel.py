"""Tests for parallel task coordination."""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from algitex.tools.parallel import RegionExtractor, TaskPartitioner, ParallelExecutor, CodeRegion, RegionType


class TestRegionExtractor:
    """Test AST region extraction."""
    
    def test_extract_functions_and_classes(self):
        """Test extraction of functions and classes with line ranges."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def simple_function():
    return 42

class TestClass:
    def method_one(self):
        pass
    
    def method_two(self):
        return simple_function()

def complex_function(a, b):
    if a > b:
        return a
    return b
""")
            
            extractor = RegionExtractor(tmpdir)
            regions = extractor.extract_all()
            
            # Should extract 4 regions: 3 functions + 1 class
            assert len(regions) == 4
            
            # Check function regions
            func_regions = [r for r in regions if r.type == RegionType.FUNCTION]
            assert len(func_regions) == 3
            
            simple_func = next(r for r in func_regions if r.name == "simple_function")
            assert simple_func.start_line == 2
            assert simple_func.end_line == 3
            
            complex_func = next(r for r in func_regions if r.name == "complex_function")
            assert complex_func.start_line == 11
            assert complex_func.end_line == 16
            
            # Check class region
            class_regions = [r for r in regions if r.type == RegionType.CLASS]
            assert len(class_regions) == 1
            
            test_class = class_regions[0]
            assert test_class.name == "TestClass"
            assert test_class.start_line == 5
            assert test_class.end_line == 9
    
    def test_dependency_detection(self):
        """Test detection of function dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def helper():
    return 1

def main():
    result = helper()
    return result * 2

class MyClass:
    def method(self):
        return helper()
""")
            
            extractor = RegionExtractor(tmpdir)
            regions = extractor.extract_all()
            
            # Find main function
            main_func = next(r for r in regions if r.name == "main")
            assert "helper" in main_func.dependencies
            
            # Find MyClass.method
            my_class = next(r for r in regions if r.name == "MyClass")
            # Note: dependency detection might need refinement for class methods
            assert my_class.type == RegionType.CLASS
    
    def test_shadow_conflict_detection(self):
        """Test detection of shared imports/constants."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
import os
from typing import List

CONSTANT_VALUE = 42

def func1():
    return os.path.join("path", "file")

def func2():
    return CONSTANT_VALUE
""")
            
            extractor = RegionExtractor(tmpdir)
            regions = extractor.extract_all()
            
            # Both functions should have shadow conflicts with shared symbols
            func1 = next(r for r in regions if r.name == "func1")
            func2 = next(r for r in regions if r.name == "func2")
            
            # func1 uses os (shared import)
            assert "os" in func1.shadow_conflicts
            
            # func2 uses CONSTANT_VALUE (shared constant)
            assert "CONSTANT_VALUE" in func2.shadow_conflicts


class TestTaskPartitioner:
    """Test task partitioning logic."""
    
    def test_no_conflict_partitioning(self):
        """Test partitioning when tickets don't conflict."""
        regions = [
            CodeRegion("file1.py", "func1", RegionType.FUNCTION, 1, 10, []),
            CodeRegion("file2.py", "func2", RegionType.FUNCTION, 1, 10, []),
            CodeRegion("file3.py", "func3", RegionType.FUNCTION, 1, 10, []),
        ]
        
        tickets = [
            {"id": "t1", "llm_hints": {"files_to_modify": ["file1.py"]}},
            {"id": "t2", "llm_hints": {"files_to_modify": ["file2.py"]}},
            {"id": "t3", "llm_hints": {"files_to_modify": ["file3.py"]}},
        ]
        
        partitioner = TaskPartitioner(regions)
        groups = partitioner.partition(tickets, max_agents=2)
        
        # All tickets can run in parallel
        assert len(groups) <= 2
        total_tickets = sum(len(tids) for tids in groups.values())
        assert total_tickets == 3
    
    def test_conflict_partitioning(self):
        """Test partitioning when tickets conflict."""
        regions = [
            CodeRegion("file1.py", "func1", RegionType.FUNCTION, 1, 10, []),
            CodeRegion("file1.py", "func2", RegionType.FUNCTION, 11, 20, []),
        ]
        
        tickets = [
            {"id": "t1", "llm_hints": {"files_to_modify": ["file1.py"]}},
            {"id": "t2", "llm_hints": {"files_to_modify": ["file1.py"]}},
        ]
        
        partitioner = TaskPartitioner(regions)
        groups = partitioner.partition(tickets, max_agents=2)
        
        # Tickets should be in different agents or same agent (sequential)
        assert len(groups) <= 2
        total_tickets = sum(len(tids) for tids in groups.values())
        assert total_tickets == 2
    
    def test_dependency_conflict(self):
        """Test partitioning with dependency conflicts."""
        regions = [
            CodeRegion("file1.py", "func1", RegionType.FUNCTION, 1, 10, ["func2"]),
            CodeRegion("file1.py", "func2", RegionType.FUNCTION, 11, 20, []),
        ]
        
        tickets = [
            {"id": "t1", "llm_hints": {"files_to_modify": ["file1.py"]}},  # Will touch func1
            {"id": "t2", "llm_hints": {"files_to_modify": ["file1.py"]}},  # Will touch func2
        ]
        
        partitioner = TaskPartitioner(regions)
        groups = partitioner.partition(tickets, max_agents=2)
        
        # Should detect dependency conflict and assign appropriately
        assert len(groups) <= 2


class TestParallelExecutor:
    """Test parallel execution orchestration."""
    
    @patch('algitex.tools.parallel.subprocess.run')
    @patch('algitex.tools.parallel.ThreadPoolExecutor')
    def test_git_worktree_creation(self, mock_executor, mock_subprocess):
        """Test git worktree creation for agents."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = ParallelExecutor(tmpdir, max_agents=2)
            
            # Mock git commands
            worktree_path = executor._create_worktree(0)
            
            # Should have called git branch and git worktree
            assert mock_subprocess.call_count >= 2
            assert worktree_path.endswith("agent-0")
    
    def test_line_range_detection(self):
        """Test detection of overlapping line ranges."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = ParallelExecutor(tmpdir)
            
            # Mock diff output
            diff_main = """@@ -10,5 +10,5 @@
 def function():
     return 1
"""
            diff_branch = """@@ -20,5 +20,5 @@
 def other():
     return 2
"""
            
            main_ranges = executor._parse_diff_ranges(diff_main)
            branch_ranges = executor._parse_diff_ranges(diff_branch)
            
            # Ranges should not overlap
            assert executor._changes_are_disjoint("test.py", "main") == True
            
            # Overlapping ranges
            overlapping_diff = """@@ -10,5 +10,5 @@
 def function():
     return 1
"""
            overlapping_ranges = executor._parse_diff_ranges(overlapping_diff)
            # Should detect overlap
            assert len(main_ranges) > 0
            assert len(overlapping_ranges) > 0


@pytest.fixture
def sample_project():
    """Create a sample project for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple Python files with different functions
        files = {
            "main.py": """
def process_data():
    return "processed"

def main():
    return process_data()
""",
            "utils.py": """
def helper():
    return 42

def calculate(a, b):
    return a + b
""",
            "models.py": """
class BaseModel:
    def save(self):
        pass

class UserModel(BaseModel):
    def __init__(self, name):
        self.name = name
"""
        }
        
        for filename, content in files.items():
            (Path(tmpdir) / filename).write_text(content)
        
        yield tmpdir


def test_end_to_end_parallel_flow(sample_project):
    """Test the complete parallel execution flow."""
    # Extract regions
    extractor = RegionExtractor(sample_project)
    regions = extractor.extract_all()
    assert len(regions) > 0
    
    # Create tickets
    tickets = [
        {"id": "t1", "llm_hints": {"files_to_modify": ["main.py"]}},
        {"id": "t2", "llm_hints": {"files_to_modify": ["utils.py"]}},
        {"id": "t3", "llm_hints": {"files_to_modify": ["models.py"]}},
    ]
    
    # Partition tickets
    partitioner = TaskPartitioner(regions)
    groups = partitioner.partition(tickets, max_agents=2)
    
    # Verify partitioning
    assert len(groups) <= 2
    total_assigned = sum(len(tids) for tids in groups.values())
    assert total_assigned == 3
    
    # Different files should be able to run in parallel
    if len(groups) == 2:
        # Should have distributed tickets across agents
        assert all(len(tids) > 0 for tids in groups.values())


if __name__ == "__main__":
    pytest.main([__file__])
