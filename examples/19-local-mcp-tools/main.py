#!/usr/bin/env python3
"""Example 19: Local MCP Tools - Self-Hosted Analysis Demo.

Demonstrates using locally-built MCP tools without external API dependencies.
"""

import os
import subprocess
from pathlib import Path


def load_env():
    """Load .env file if present."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = val


def check_docker_tools():
    """Check if local Docker tools are available."""
    tools = {
        "code2llm-mcp": 8081,
        "vallm-mcp": 8080,
        "planfile-mcp": 8201,
        "aider-mcp": 3000,
    }
    
    available = []
    for tool, port in tools.items():
        # Check if container is running
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={tool}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        if tool in result.stdout:
            available.append((tool, port))
    
    return available


def demo_code2llm():
    """Demonstrate code2llm local analysis."""
    print("\n=== 1. Local Code Analysis (code2llm) ===\n")
    
    print("Analyzing current project structure...")
    print()
    print("📁 Files that would be analyzed:")
    
    # Simulate analysis output
    files = [
        ("src/algitex/project.py", "Grade A", "Low complexity"),
        ("src/algitex/cli.py", "Grade B", "Medium complexity"),
        ("src/algitex/config.py", "Grade A", "Clean code"),
    ]
    
    print(f"{'File':<35} {'Grade':<10} {'Status':<20}")
    print("-" * 65)
    for file, grade, status in files:
        print(f"{file:<35} {grade:<10} {status:<20}")
    
    print("\n📝 Generated outputs:")
    print("   - analysis.toon (diagnostics)")
    print("   - analysis.evolution (metrics over time)")
    print("   - analysis.json (machine readable)")


def demo_vallm():
    """Demonstrate vallm local validation."""
    print("\n=== 2. Local Validation (vallm) ===\n")
    
    checks = [
        ("Syntax validation", "✅ Pass", "All files parse correctly"),
        ("Import checks", "✅ Pass", "No missing dependencies"),
        ("Type consistency", "⚠️  Warn", "3 files need type hints"),
        ("Test coverage", "✅ Pass", "82% coverage"),
        ("Code style", "✅ Pass", "PEP 8 compliant"),
    ]
    
    print(f"{'Check':<25} {'Status':<10} {'Details':<30}")
    print("-" * 65)
    for check, status, details in checks:
        print(f"{check:<25} {status:<10} {details:<30}")
    
    print("\n📊 Quality Score: 0.85/1.0")
    print("   Grade: B (Good)")


def demo_planfile():
    """Demonstrate planfile local ticket management."""
    print("\n=== 3. Local Ticket Management (planfile) ===\n")
    
    # Simulate ticket generation
    tickets = [
        {"id": "LOC-001", "title": "Add type hints to cli.py", "priority": "medium", "status": "open"},
        {"id": "LOC-002", "title": "Refactor complex function", "priority": "high", "status": "open"},
        {"id": "LOC-003", "title": "Add docstrings", "priority": "low", "status": "done"},
    ]
    
    print("Generated tickets from analysis:")
    print()
    print(f"{'ID':<10} {'Priority':<10} {'Status':<10} {'Title':<30}")
    print("-" * 60)
    for t in tickets:
        print(f"{t['id']:<10} {t['priority']:<10} {t['status']:<10} {t['title']:<30}")
    
    print("\n📁 Local storage:")
    print("   - .algitex/tickets.json")
    print("   - .algitex/sprints/")
    print("   - .algitex/backlog.md")


def demo_full_pipeline():
    """Demonstrate complete local pipeline."""
    print("\n=== 4. Complete Local Pipeline ===\n")
    
    steps = [
        ("1. code2llm analyze", "Generate diagnostics", "30s", "✅"),
        ("2. vallm validate", "Check code quality", "15s", "✅"),
        ("3. planfile create", "Generate tickets", "5s", "✅"),
        ("4. aider-mcp fix", "Refactor issues", "2m", "⏳"),
        ("5. vallm verify", "Validate fixes", "15s", "⏳"),
    ]
    
    print(f"{'Step':<20} {'Action':<25} {'Time':<10} {'Status':<10}")
    print("-" * 70)
    for step, action, time, status in steps:
        print(f"{step:<20} {action:<25} {time:<10} {status:<10}")
    
    print("\n⏱️  Total pipeline time: ~3 minutes")
    print("💰 Total cost: $0.00 (all local)")


def show_docker_commands():
    """Show useful Docker commands."""
    print("\n=== Docker Commands ===\n")
    
    commands = [
        ("Build all tools", "docker compose --profile tools build"),
        ("Start tools", "docker compose --profile tools up -d"),
        ("Check status", "docker compose --profile tools ps"),
        ("View logs", "docker compose logs -f code2llm-mcp"),
        ("Stop all", "docker compose --profile tools down"),
    ]
    
    for desc, cmd in commands:
        print(f"{desc}:")
        print(f"  {cmd}")
        print()


def show_comparison():
    """Compare local vs cloud setup."""
    print("\n=== Local vs Cloud Comparison ===\n")
    
    comparison = [
        ("API Keys", "None needed", "Multiple required"),
        ("Privacy", "100% private", "Sent to cloud"),
        ("Offline work", "✅ Yes", "❌ No"),
        ("Cost", "$0 forever", "$0.01-0.10 per task"),
        ("Speed", "Depends on hardware", "Fast (cloud GPUs)"),
        ("Setup", "Docker build (5 min)", "API signup + billing"),
    ]
    
    print(f"{'Aspect':<20} {'Local Setup':<25} {'Cloud Setup':<25}")
    print("-" * 70)
    for aspect, local, cloud in comparison:
        print(f"{aspect:<20} {local:<25} {cloud:<25}")


if __name__ == "__main__":
    load_env()
    
    print("=" * 70)
    print("Example 19: Local MCP Tools - Self-Hosted Analysis")
    print("=" * 70)
    
    # Check available tools
    tools = check_docker_tools()
    if tools:
        print(f"\n✅ Running Docker tools ({len(tools)} found):")
        for name, port in tools:
            print(f"   - {name} (port {port})")
    else:
        print("\n⚠️  No Docker tools running")
        print("   Start with: docker compose --profile tools up -d")
    
    # Run demos
    demo_code2llm()
    demo_vallm()
    demo_planfile()
    demo_full_pipeline()
    show_docker_commands()
    show_comparison()
    
    print("\n" + "=" * 70)
    print("🎯 Full development workflow without external dependencies!")
    print("=" * 70)
