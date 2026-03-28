"""Multi-repo workspace orchestration for algitex.

Manage multiple repositories as a single workspace with dependency ordering.
"""

from __future__,annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
import yaml
from graphlib import TopologicalSorter

from algitex import Pipeline, Project


@dataclass
class RepoConfig:
    """Configuration for a single repository in the workspace."""
    name: str
    path: str
    git_url: str
    priority: int = 0
    depends_on: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        self.path = str(Path(self.path).resolve())


class Workspace:
    """Manage multiple repos as a single workspace."""
    
    def __init__(self, config_path: str = "workspace.yaml"):
        self.config_path = Path(config_path)
        self.repos: Dict[str, RepoConfig] = {}
        self.config = self._load_config()
    
    def _load_config(self):
        """Load workspace configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Workspace config not found: {self.config_path}")
        
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
        
        if "workspace" not in config:
            raise ValueError("Invalid workspace config: missing 'workspace' section")
        
        workspace_config = config["workspace"]
        
        # Load repositories
        for repo_data in workspace_config.get("repos", []):
            repo = RepoConfig(**repo_data)
            self.repos[repo.name] = repo
        
        return config
    
    def _validate_dependencies(self):
        """Validate that all dependencies exist."""
        all_names = set(self.repos.keys())
        
        for name, repo in self.repos.items():
            for dep in repo.depends_on:
                if dep not in all_names:
                    raise ValueError(f"Repo '{name}' depends on non-existent repo '{dep}'")
    
    def _topo_sort(self) -> List[RepoConfig]:
        """Get repositories in dependency order using topological sort."""
        self._validate_dependencies()
        
        # Build dependency graph
        graph = {}
        for name, repo in self.repos.items():
            graph[name] = repo.depends_on
        
        # Use TopologicalSorter for dependency ordering
        sorter = TopologicalSorter(graph)
        sorted_names = list(sorter.static_order())
        
        # Return RepoConfig objects in sorted order
        return [self.repos[name] for name in sorted_names]
    
    def clone_all(self, base_dir: str = ".") -> None:
        """Clone all repositories if they don't exist."""
        base_path = Path(base_dir).resolve()
        
        for repo in self.repos.values():
            repo_path = base_path / repo.name
            
            if not repo_path.exists():
                print(f"Cloning {repo.name} from {repo.git_url}...")
                subprocess.run(
                    ["git", "clone", repo.git_url, str(repo_path)],
                    check=True,
                    capture_output=True
                )
            else:
                print(f"{repo.name} already exists at {repo_path}")
    
    def pull_all(self) -> None:
        """Pull latest changes for all repositories."""
        for repo in self.repos.values():
            repo_path = Path(repo.path)
            
            if repo_path.exists():
                print(f"Pulling latest for {repo.name}...")
                subprocess.run(
                    ["git", "pull"],
                    cwd=repo_path,
                    check=True,
                    capture_output=True
                )
    
    def analyze_all(self, full: bool = True) -> Dict[str, dict]:
        """Run algitex analyze on each repo in dependency order."""
        results = {}
        
        for repo in self._topo_sort():
            print(f"\nAnalyzing {repo.name}...")
            
            try:
                project = Project(repo.path)
                report = project.analyze(full=full)
                results[repo.name] = {
                    "status": "success",
                    "grade": report.grade,
                    "alerts": len(report.alerts) if hasattr(report, 'alerts') else 0,
                    "hotspots": len(report.hotspots) if hasattr(report, 'hotspots') else 0
                }
            except Exception as e:
                results[repo.name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def plan_all(self, sprints: int = 2) -> Dict[str, List]:
        """Generate cross-repo plan respecting dependencies."""
        all_tickets = {}
        
        for repo in self._topo_sort():
            print(f"\nPlanning {repo.name}...")
            
            try:
                project = Project(repo.path)
                tickets = project.plan(sprints=sprints)
                
                # Convert tickets to dicts for serialization
                ticket_dicts = []
                for ticket in tickets:
                    ticket_dicts.append({
                        "id": ticket.id,
                        "title": ticket.title,
                        "priority": ticket.priority,
                        "repo": repo.name,
                        "dependencies": repo.depends_on
                    })
                
                all_tickets[repo.name] = ticket_dicts
                
            except Exception as e:
                print(f"Error planning {repo.name}: {e}")
                all_tickets[repo.name] = []
        
        return all_tickets
    
    def execute_all(self, tool: str = "aider-mcp", max_tickets: int = 5) -> Dict[str, dict]:
        """Execute tickets across repos in correct order."""
        results = {}
        
        for repo in self._topo_sort():
            print(f"\nExecuting tickets for {repo.name}...")
            
            try:
                pipeline = Pipeline(repo.path)
                result = pipeline.execute(tool=tool, max_tickets=max_tickets)
                
                results[repo.name] = {
                    "status": "success",
                    "executed": result.get("executed", 0),
                    "errors": result.get("errors", [])
                }
                
            except Exception as e:
                results[repo.name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def validate_all(self) -> Dict[str, dict]:
        """Run validation across all repositories."""
        results = {}
        
        for repo in self._topo_sort():
            print(f"\nValidating {repo.name}...")
            
            try:
                pipeline = Pipeline(repo.path)
                pipeline.validate()
                validation = pipeline._results.get("validation", {})
                
                results[repo.name] = {
                    "status": "success",
                    "static_passed": validation.get("static_passed", False),
                    "runtime_passed": validation.get("runtime_passed", False),
                    "security_passed": validation.get("security_passed", False),
                    "all_passed": validation.get("all_passed", False)
                }
                
            except Exception as e:
                results[repo.name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def status(self) -> dict:
        """Get status of all repositories."""
        status = {
            "workspace": {
                "name": self.config.get("workspace", {}).get("name", self.config_path.stem),
                "repos": len(self.repos),
                "config": str(self.config_path)
            },
            "repositories": {}
        }
        
        for repo in self.repos.values():
            repo_path = Path(repo.path)
            
            # Get git status
            git_status = "not_cloned"
            if repo_path.exists():
                try:
                    result = subprocess.run(
                        ["git", "status", "--porcelain"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        if result.stdout.strip():
                            git_status = "dirty"
                        else:
                            git_status = "clean"
                except:
                    git_status = "error"
            
            # Check for algitex files
            has_algitex = any([
                (repo_path / "algitex.yaml").exists(),
                (repo_path / "analysis.toon.yaml").exists(),
                (repo_path / "planfile.yaml").exists()
            ])
            
            status["repositories"][repo.name] = {
                "path": repo.path,
                "git_url": repo.git_url,
                "priority": repo.priority,
                "dependencies": repo.depends_on,
                "git_status": git_status,
                "has_algitex": has_algitex,
                "tags": repo.tags
            }
        
        return status
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the dependency graph for visualization."""
        graph = {}
        for name, repo in self.repos.items():
            graph[name] = repo.depends_on
        return graph
    
    def find_repos_by_tag(self, tag: str) -> List[RepoConfig]:
        """Find all repositories with a specific tag."""
        return [repo for repo in self.repos.values() if tag in repo.tags]
    
    def get_execution_plan(self) -> List[str]:
        """Get the execution order for repositories."""
        return [repo.name for repo in self._topo_sort()]


# CLI convenience functions
def create_workspace_template(name: str, repos: List[Dict]) -> str:
    """Create a workspace configuration template."""
    template = {
        "workspace": {
            "name": name,
            "repos": repos
        }
    }
    return yaml.dump(template, default_flow_style=False)


def init_workspace(name: str, config_path: str = "workspace.yaml") -> None:
    """Initialize a new workspace with template."""
    template = create_workspace_template(name, [
        {
            "name": "core",
            "path": "./core",
            "git_url": "https://github.com/example/core",
            "priority": 1,
            "tags": ["library"]
        },
        {
            "name": "api",
            "path": "./api",
            "git_url": "https://github.com/example/api",
            "priority": 2,
            "depends_on": ["core"],
            "tags": ["service"]
        },
        {
            "name": "web",
            "path": "./web",
            "git_url": "https://github.com/example/web",
            "priority": 3,
            "depends_on": ["api"],
            "tags": ["frontend"]
        }
    ])
    
    with open(config_path, "w") as f:
        f.write(template)
    
    print(f"Created workspace config: {config_path}")
    print("Edit the file to match your repositories, then run:")
    print("  algitex workspace clone")
    print("  algitex workspace analyze")
    print("  algitex workspace execute")
