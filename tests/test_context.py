"""Unit tests for algitex context module."""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from algitex.tools.context import ContextBuilder, CodeContext, SemanticCache


class TestCodeContext:
    """Test the CodeContext class."""
    
    def test_code_context_creation(self):
        """Test creating a code context."""
        context = CodeContext(
            project_summary="Test project",
            architecture="Module A -> Module B",
            target_files=["file1.py"],
            related_files=["test_file1.py"],
            conventions="PEP8 style",
            recent_changes="Commit 1: Fix bug",
            ticket_context="Ticket #123: Fix issue"
        )
        
        assert context.project_summary == "Test project"
        assert context.architecture == "Module A -> Module B"
        assert context.target_files == ["file1.py"]
        assert context.related_files == ["test_file1.py"]
    
    def test_to_prompt(self):
        """Test converting context to prompt."""
        context = CodeContext(
            project_summary="Test project with CC̄=2.5",
            architecture="M[core, utils]",
            target_files=["main.py"],
            related_files=["test_main.py"],
            conventions="Use type hints",
            recent_changes="Recent commit",
            ticket_context="Ticket #1"
        )
        
        prompt = context.to_prompt("Fix the bug in main.py")
        
        assert "## Project context" in prompt
        assert "Test project with CC̄=2.5" in prompt
        assert "## Architecture" in prompt
        assert "M[core, utils]" in prompt
        assert "## Task" in prompt
        assert "Fix the bug in main.py" in prompt
        assert "## Files to modify" in prompt
        assert "- main.py" in prompt
        assert "## Related files" in prompt
        assert "- test_main.py" in prompt


class TestContextBuilder:
    """Test the ContextBuilder class."""
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        # Create some files
        (project_dir / "main.py").write_text("""
from utils import helper

def main():
    return helper()
""")
        
        (project_dir / "utils.py").write_text("""
def helper():
    return 42
""")
        
        # Create test directory
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_main(): pass")
        
        # Create config files
        (project_dir / "pyproject.toml").write_text("""
[tool.black]
line-length = 88
""")
        
        (project_dir / ".editorconfig").write_text("""
[*.py]
indent_size = 4
""")
        
        return str(project_dir)
    
    def test_context_builder_creation(self, temp_project):
        """Test creating context builder."""
        builder = ContextBuilder(temp_project)
        assert builder.root == Path(temp_project).resolve()
    
    def test_build_basic_context(self, temp_project):
        """Test building basic context."""
        builder = ContextBuilder(temp_project)
        context = builder.build()
        
        assert isinstance(context, CodeContext)
        assert context.project_summary  # Should have some content
        assert isinstance(context.target_files, list)
        assert isinstance(context.related_files, list)
    
    def test_load_toon_summary_missing(self, temp_project):
        """Test loading toon summary when file doesn't exist."""
        builder = ContextBuilder(temp_project)
        summary = builder._load_toon_summary()
        assert summary == "No .toon diagnostics found."
    
    def test_load_toon_summary_exists(self, temp_project):
        """Test loading toon summary when file exists."""
        toon_file = Path(temp_project) / "analysis.toon.yaml"
        toon_file.write_text("CC̄=3.2\nAlerts: 5\nHotspots: main.py")
        
        builder = ContextBuilder(temp_project)
        summary = builder._load_toon_summary()
        assert "CC̄=3.2" in summary
        assert "Alerts: 5" in summary
    
    def test_load_architecture_missing(self, temp_project):
        """Test loading architecture when file doesn't exist."""
        builder = ContextBuilder(temp_project)
        arch = builder._load_architecture()
        assert arch == ""
    
    def test_load_architecture_exists(self, temp_project):
        """Test loading architecture when file exists."""
        map_file = Path(temp_project) / "map.toon.yaml"
        map_file.write_text("""
M[core, utils, api]
D[core -> utils]
D[utils -> api]
""")
        
        builder = ContextBuilder(temp_project)
        arch = builder._load_architecture()
        assert "M[core, utils, api]" in arch
    
    def test_resolve_targets(self, temp_project):
        """Test resolving target files from ticket."""
        builder = ContextBuilder(temp_project)
        
        # No ticket
        targets = builder._resolve_targets(None)
        assert targets == []
        
        # Ticket with files
        ticket = {"llm_hints": {"files_to_modify": ["main.py", "utils.py"]}}
        targets = builder._resolve_targets(ticket)
        assert targets == ["main.py", "utils.py"]
    
    def test_find_related_files(self, temp_project):
        """Test finding related files."""
        builder = ContextBuilder(temp_project)
        
        # Ticket with target files
        ticket = {"llm_hints": {"files_to_modify": ["main.py"]}}
        related = builder._find_related(ticket)
        
        # Should find imports and test files
        assert any("from utils import helper" in str(r) for r in related)
        assert "tests/test_main.py" in related
    
    def test_load_conventions(self, temp_project):
        """Test loading project conventions."""
        builder = ContextBuilder(temp_project)
        conventions = builder._load_conventions()
        
        assert "pyproject.toml" in conventions
        assert ".editorconfig" in conventions
        assert "line-length = 88" in conventions
        assert "indent_size = 4" in conventions
    
    def test_git_recent(self, temp_project):
        """Test getting recent git history."""
        builder = ContextBuilder(temp_project)
        
        # Mock git command
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "abc123 Fix bug\ndef456 Add feature\n"
            history = builder._git_recent()
            assert "Fix bug" in history
            assert "Add feature" in history
    
    def test_git_recent_error(self, temp_project):
        """Test git history when git is not available."""
        builder = ContextBuilder(temp_project)
        
        with patch('subprocess.run', side_effect=Exception("Git not found")):
            history = builder._git_recent()
            assert history == "Git not available."
    
    def test_format_ticket(self, temp_project):
        """Test formatting ticket information."""
        builder = ContextBuilder(temp_project)
        
        ticket = {
            "id": "123",
            "title": "Fix bug",
            "priority": "high",
            "description": "Critical issue in main"
        }
        
        formatted = builder._format_ticket(ticket)
        assert "ID: 123" in formatted
        assert "Title: Fix bug" in formatted
        assert "Priority: high" in formatted
        assert "Critical issue in main" in formatted
    
    def test_format_ticket_empty(self, temp_project):
        """Test formatting empty ticket."""
        builder = ContextBuilder(temp_project)
        formatted = builder._format_ticket(None)
        assert formatted == ""
    
    def test_build_with_ticket(self, temp_project):
        """Test building context with a ticket."""
        builder = ContextBuilder(temp_project)
        
        ticket = {
            "id": "123",
            "title": "Fix import error",
            "llm_hints": {"files_to_modify": ["main.py"]},
            "description": "Import statement is broken"
        }
        
        context = builder.build(ticket)
        
        assert context.target_files == ["main.py"]
        assert "tests/test_main.py" in context.related_files
        assert "ID: 123" in context.ticket_context
        assert "Fix import error" in context.ticket_context


class TestSemanticCache:
    """Test the SemanticCache class."""
    
    def test_cache_creation(self):
        """Test creating semantic cache."""
        cache = SemanticCache("/test/project", "http://localhost:6334")
        assert cache.root == Path("/test/project").resolve()
        assert cache.qdrant_url == "http://localhost:6334"
        assert cache._client is None
    
    def test_get_client_import_error(self):
        """Test handling missing Qdrant dependency."""
        cache = SemanticCache("/test/project")
        client = cache._get_client()
        assert client is None
    
    def test_search_similar_context(self):
        """Test searching for similar contexts."""
        cache = SemanticCache("/test/project")
        results = cache.search_similar_context("fix import error")
        assert results == []
    
    def test_store_context(self):
        """Test storing context in cache."""
        cache = SemanticCache("/test/project")
        context = CodeContext(
            project_summary="Test",
            architecture="Simple",
            target_files=["main.py"],
            related_files=[],
            conventions="PEP8",
            recent_changes="",
            ticket_context=""
        )
        
        # Should not raise an exception (placeholder implementation)
        cache.store_context(context, "Fix bug", {"status": "success"})
