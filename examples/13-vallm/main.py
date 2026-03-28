#!/usr/bin/env python3
"""Example 13: Vallm - Code Validation Demo.

Demonstrates using vallm through algitex's Docker tool orchestration
for code validation and quality assessment.
"""

import os
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


def demo_validation_examples():
    """Show example vallm validation operations."""
    
    examples = [
        {
            "title": "1. Basic Code Validation",
            "action": "validate",
            "description": "Validate Python files recursively",
            "input": {
                "path": "/project/src",
                "recursive": True,
                "format": "json"
            }
        },
        {
            "title": "2. Batch Validation with Error Reporting",
            "action": "batch",
            "description": "Full project validation with error-only output",
            "input": {
                "path": "/project",
                "format": "json",
                "errors_only": True,
                "output_file": "/project/validation_report.json"
            }
        },
        {
            "title": "3. Scoring Code Quality",
            "action": "score",
            "description": "Score code on multiple metrics",
            "input": {
                "path": "/project/src/algitex",
                "threshold": 0.8,
                "metrics": ["complexity", "maintainability", "readability"]
            }
        },
        {
            "title": "4. Comprehensive Analysis",
            "action": "analyze",
            "description": "Full analysis with custom metrics",
            "input": {
                "path": "/project",
                "output_format": "toon",
                "include_metrics": [
                    "cyclomatic_complexity",
                    "lines_of_code",
                    "test_coverage",
                    "duplication"
                ]
            }
        },
        {
            "title": "5. Evolution Export",
            "action": "evolution-export",
            "description": "Track code quality changes over time",
            "input": {
                "path": "/project",
                "baseline_file": "/project/baseline.json",
                "compare_with": "last_commit"
            }
        }
    ]
    
    print("\n=== Vallm Code Validation Examples ===\n")
    
    for ex in examples:
        print(f"\n{ex['title']}")
        print(f"   Description: {ex['description']}")
        print(f"   Action: {ex['action']}")
    
    print("\n\n=== CLI Usage Examples ===\n")
    print("Spawn vallm:")
    print("  algitex docker spawn vallm")
    print("\nBasic validation:")
    print('  algitex docker call vallm validate -i \'{"path": "/project/src", "recursive": true}\'')
    print("\nBatch analysis:")
    print('  algitex docker call vallm batch -i \'{"path": "/project", "errors_only": true}\'')
    print("\nTeardown:")
    print("  algitex docker teardown vallm")


def demo_with_docker_tools():
    """Demonstrate Docker tool usage if available."""
    try:
        from algitex.tools.docker import DockerToolManager
        from algitex.config import Config
        
        config = Config.load()
        mgr = DockerToolManager(config)
        
        print("\n=== Docker Tools Status ===\n")
        
        tools = mgr.list_tools()
        print(f"Available: {len(tools)} tools")
        for tool in tools:
            print(f"  - {tool}")
        
        if "vallm" in tools:
            print("\n✅ vallm is available!")
        else:
            print("\n⚠️  vallm not found in docker-tools.yaml")
            
    except ImportError as e:
        print(f"⚠️  Docker tools not available: {e}")


if __name__ == "__main__":
    load_env()
    demo_validation_examples()
    
    try:
        demo_with_docker_tools()
    except Exception as e:
        print(f"\n⚠️  Could not load Docker tools: {e}")
