# Workspace Examples

```bash
cd examples/09-workspace
```

This example demonstrates how to use the workspace module to orchestrate multiple repositories as a single ecosystem.

## Features Demonstrated

- Creating and managing multi-repo workspaces
- Dependency resolution with topological sorting
- Cross-repo analysis and planning
- Execute tickets across the entire ecosystem
- Advanced workspace features and queries

## Running the Example

```bash
# Install dependencies
pip install algitex

# Run the workspace example
python main.py
```

## What You'll See

1. **Workspace Creation** - Setting up a microservices ecosystem
2. **Workspace Management** - Status, execution plan, dependency graph
3. **Cross-Repo Analysis** - Analyzing all repos in dependency order
4. **Cross-Repo Planning** - Generating tickets with dependency awareness
5. **Workspace Execution** - Running tickets across the ecosystem
6. **Advanced Features** - Impact analysis, parallel execution opportunities

## Key Takeaways

- Workspace manages complex repo dependencies automatically
- Topological sorting ensures correct execution order
- Cross-repo visibility enables better planning
- Parallel execution opportunities are identified automatically
- Impact analysis helps with change management

## Configuration

Create a `workspace.yaml` file:

```yaml
workspace:
  name: "my-ecosystem"
  repos:
    - name: "core-lib"
      path: "./core-lib"
      git_url: "https://github.com/company/core-lib"
      priority: 1
      tags: ["library"]
    - name: "auth-service"
      path: "./auth-service"
      git_url: "https://github.com/company/auth-service"
      priority: 2
      depends_on: ["core-lib"]
      tags: ["service"]
```

## Use Cases

- **Microservices** - Manage service dependencies
- **Monorepos** - Organize large codebases
- **Ecosystem Updates** - Coordinate changes across projects
- **Release Management** - Ensure proper deployment order
