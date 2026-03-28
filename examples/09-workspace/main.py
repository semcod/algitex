"""Example: Using workspace module for multi-repo orchestration.

This example demonstrates how to:
1. Create a workspace configuration
2. Manage multiple repositories with dependencies
3. Execute pipelines across the ecosystem
4. Track progress across all projects
"""

import tempfile
import shutil
from pathlib import Path
from algitex.tools.workspace import Workspace, RepoConfig, init_workspace


def create_sample_workspace():
    """Create a sample workspace configuration."""
    print("=== Creating Sample Workspace ===\n")
    
    # Define repositories for a microservices ecosystem
    repos = [
        {
            "name": "shared-utils",
            "path": "./shared-utils",
            "git_url": "https://github.com/company/shared-utils",
            "priority": 1,
            "tags": ["library", "core"]
        },
        {
            "name": "auth-service",
            "path": "./auth-service",
            "git_url": "https://github.com/company/auth-service",
            "priority": 2,
            "depends_on": ["shared-utils"],
            "tags": ["service", "security"]
        },
        {
            "name": "user-service",
            "path": "./user-service",
            "git_url": "https://github.com/company/user-service",
            "priority": 2,
            "depends_on": ["shared-utils"],
            "tags": ["service"]
        },
        {
            "name": "api-gateway",
            "path": "./api-gateway",
            "git_url": "https://github.com/company/api-gateway",
            "priority": 3,
            "depends_on": ["auth-service", "user-service"],
            "tags": ["service", "gateway"]
        },
        {
            "name": "web-frontend",
            "path": "./web-frontend",
            "git_url": "https://github.com/company/web-frontend",
            "priority": 4,
            "depends_on": ["api-gateway"],
            "tags": ["frontend"]
        }
    ]
    
    # Create workspace config
    workspace_dir = Path("sample-workspace")
    workspace_dir.mkdir(exist_ok=True)
    
    config_path = workspace_dir / "workspace.yaml"
    init_workspace("microservices-ecosystem", str(config_path))
    
    # Update with our repos
    import yaml
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    config["workspace"]["repos"] = repos
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Created workspace config: {config_path}")
    print("\nRepository dependency graph:")
    print("shared-utils (priority 1)")
    print("├── auth-service (priority 2)")
    print("└── user-service (priority 2)")
    print("    └── api-gateway (priority 3)")
    print("        └── web-frontend (priority 4)")
    
    return str(config_path)


def workspace_management_example():
    """Example of workspace management operations."""
    print("\n=== Workspace Management Example ===\n")
    
    # Create sample workspace
    config_path = create_sample_workspace()
    
    # Load workspace
    workspace = Workspace(config_path)
    
    # Get status
    print("1. Workspace status:")
    status = workspace.status()
    print(f"   Name: {status['workspace']['name']}")
    print(f"   Repositories: {status['workspace']['repos']}")
    
    # Get execution plan
    print("\n2. Execution order (dependency-resolved):")
    plan = workspace.get_execution_plan()
    for i, repo_name in enumerate(plan, 1):
        repo = workspace.repos[repo_name]
        deps = f" (depends on: {', '.join(repo.depends_on)})" if repo.depends_on else ""
        print(f"   {i}. {repo_name}{deps}")
    
    # Find repos by tag
    print("\n3. Repositories by tag:")
    for tag in ["service", "core"]:
        repos = workspace.find_repos_by_tag(tag)
        print(f"   {tag}: {[r.name for r in repos]}")
    
    # Get dependency graph
    print("\n4. Dependency graph:")
    graph = workspace.get_dependency_graph()
    for repo, deps in graph.items():
        print(f"   {repo} -> {deps}")
    
    return workspace


def cross_repo_analysis_example():
    """Example of analyzing multiple repositories."""
    print("\n=== Cross-Repository Analysis ===\n")
    
    config_path = create_sample_workspace()
    workspace = Workspace(config_path)
    
    print("Analyzing all repositories in dependency order...")
    
    # Simulate analysis results
    results = {}
    for repo_name in workspace.get_execution_plan():
        # Mock analysis result
        results[repo_name] = {
            "status": "success",
            "grade": "B" if repo_name != "api-gateway" else "C",
            "alerts": 3 if repo_name == "api-gateway" else 1,
            "hotspots": 2 if repo_name == "auth-service" else 0
        }
    
    print("\nAnalysis Results:")
    print("-" * 60)
    print(f"{'Repository':<15} {'Grade':<8} {'Alerts':<8} {'Hotspots':<10}")
    print("-" * 60)
    
    total_alerts = 0
    total_hotspots = 0
    
    for repo_name, result in results.items():
        print(f"{repo_name:<15} {result['grade']:<8} {result['alerts']:<8} {result['hotspots']:<10}")
        total_alerts += result['alerts']
        total_hotspots += result['hotspots']
    
    print("-" * 60)
    print(f"{'TOTAL':<15} {'':<8} {total_alerts:<8} {total_hotspots:<10}")
    
    # Identify critical issues
    print("\nCritical Issues:")
    for repo_name, result in results.items():
        if result['grade'] == 'C' or result['alerts'] > 2:
            print(f"   ⚠️  {repo_name}: Grade {result['grade']} with {result['alerts']} alerts")
    
    return results


def cross_repo_planning_example():
    """Example of planning across repositories."""
    print("\n=== Cross-Repository Planning ===\n")
    
    config_path = create_sample_workspace()
    workspace = Workspace(config_path)
    
    print("Generating tickets for all repositories...")
    
    # Simulate ticket generation
    all_tickets = {}
    execution_plan = workspace.get_execution_plan()
    
    for repo_name in execution_plan:
        # Mock tickets based on repo type
        repo = workspace.repos[repo_name]
        
        if "service" in repo.tags:
            tickets = [
                {"id": f"{repo_name}-001", "title": f"Add health check endpoint", "priority": "high"},
                {"id": f"{repo_name}-002", "title": f"Implement request logging", "priority": "medium"}
            ]
        elif "frontend" in repo.tags:
            tickets = [
                {"id": f"{repo_name}-001", "title": f"Add error boundary components", "priority": "high"},
                {"id": f"{repo_name}-002", "title": f"Optimize bundle size", "priority": "medium"}
            ]
        else:  # library/core
            tickets = [
                {"id": f"{repo_name}-001", "title": f"Add type hints to public API", "priority": "medium"},
                {"id": f"{repo_name}-002", "title": f"Improve test coverage", "priority": "low"}
            ]
        
        all_tickets[repo_name] = tickets
    
    print("\nGenerated Tickets by Repository:")
    for repo_name, tickets in all_tickets.items():
        print(f"\n{repo_name}:")
        for ticket in tickets:
            print(f"   - [{ticket['id']}] {ticket['title']} ({ticket['priority']})")
    
    # Show dependency-aware scheduling
    print("\nDependency-Aware Scheduling:")
    print("Week 1 (Core libraries):")
    print("   - shared-utils tickets")
    print("\nWeek 2 (Foundational services):")
    print("   - auth-service tickets")
    print("   - user-service tickets")
    print("\nWeek 3 (Integration layer):")
    print("   - api-gateway tickets")
    print("\nWeek 4 (Frontend):")
    print("   - web-frontend tickets")
    
    return all_tickets


def workspace_execution_example():
    """Example of executing across the workspace."""
    print("\n=== Workspace Execution Example ===\n")
    
    config_path = create_sample_workspace()
    workspace = Workspace(config_path)
    
    print("Executing tickets across all repositories...")
    
    # Simulate execution results
    results = {}
    execution_plan = workspace.get_execution_plan()
    
    for repo_name in execution_plan:
        # Mock execution based on complexity
        if repo_name == "api-gateway":
            results[repo_name] = {
                "status": "success",
                "executed": 1,
                "errors": ["Integration test failed"]
            }
        elif repo_name == "web-frontend":
            results[repo_name] = {
                "status": "success",
                "executed": 2,
                "errors": []
            }
        else:
            results[repo_name] = {
                "status": "success",
                "executed": 2,
                "errors": []
            }
    
    print("\nExecution Results:")
    print("-" * 50)
    
    total_executed = 0
    total_errors = 0
    
    for repo_name, result in results.items():
        status_icon = "✅" if result["status"] == "success" else "❌"
        errors_str = f" ({len(result['errors'])} errors)" if result['errors'] else ""
        print(f"{status_icon} {repo_name}: {result['executed']} executed{errors_str}")
        
        total_executed += result['executed']
        total_errors += len(result['errors'])
    
    print("-" * 50)
    print(f"Total: {total_executed} tickets executed, {total_errors} errors")
    
    # Show error handling
    if total_errors > 0:
        print("\nError Handling:")
        print("   - Failed tickets are automatically retried with different models")
        print("   - Critical failures create escalation tickets")
        print("   - Dependencies prevent execution of downstream repos until fixed")
    
    return results


def advanced_workspace_features():
    """Example of advanced workspace features."""
    print("\n=== Advanced Workspace Features ===\n")
    
    config_path = create_sample_workspace()
    workspace = Workspace(config_path)
    
    # 1. Custom workspace queries
    print("1. Custom Queries:")
    
    # Find all services
    services = workspace.find_repos_by_tag("service")
    print(f"   Services: {[s.name for s in services]}")
    
    # Find repos without dependencies
    independent = [r for r in workspace.repos.values() if not r.depends_on]
    print(f"   Independent repos: {[r.name for r in independent]}")
    
    # Find leaf nodes (nothing depends on them)
    all_deps = set()
    for repo in workspace.repos.values():
        all_deps.update(repo.depends_on)
    leaf_nodes = [r.name for r in workspace.repos.values() if r.name not in all_deps]
    print(f"   Leaf nodes: {leaf_nodes}")
    
    # 2. Impact analysis
    print("\n2. Impact Analysis:")
    print("   If shared-utils changes, it affects:")
    for repo in workspace.repos.values():
        if "shared-utils" in repo.depends_on:
            print(f"   - {repo.name} (direct)")
    
    # 3. Parallel execution opportunities
    print("\n3. Parallel Execution Opportunities:")
    execution_plan = workspace.get_execution_plan()
    
    # Group by level
    levels = {}
    for repo_name in execution_plan:
        repo = workspace.repos[repo_name]
        level = len(repo.depends_on)
        if level not in levels:
            levels[level] = []
        levels[level].append(repo_name)
    
    for level, repos in sorted(levels.items()):
        print(f"   Level {level}: {repos} (can run in parallel)")
    
    # 4. Workspace metrics
    print("\n4. Workspace Metrics:")
    total_repos = len(workspace.repos)
    max_depth = max(len(r.depends_on) for r in workspace.repos.values())
    avg_deps = sum(len(r.depends_on) for r in workspace.repos.values()) / total_repos
    
    print(f"   Total repositories: {total_repos}")
    print(f"   Maximum dependency depth: {max_depth}")
    print(f"   Average dependencies: {avg_deps:.1f}")
    print(f"   Critical path length: {len(execution_plan)}")


def cleanup_sample_workspace():
    """Clean up the sample workspace."""
    workspace_dir = Path("sample-workspace")
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)
        print("\n✅ Cleaned up sample workspace")


if __name__ == "__main__":
    print("Algitex Workspace Examples")
    print("=" * 50)
    
    try:
        # Run all examples
        workspace_management_example()
        cross_repo_analysis_example()
        cross_repo_planning_example()
        workspace_execution_example()
        advanced_workspace_features()
        
    finally:
        cleanup_sample_workspace()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nKey takeaways:")
    print("1. Workspace manages complex repo dependencies automatically")
    print("2. Topological sorting ensures correct execution order")
    print("3. Cross-repo visibility enables better planning")
    print("4. Parallel execution opportunities are identified")
    print("5. Impact analysis helps with change management")
