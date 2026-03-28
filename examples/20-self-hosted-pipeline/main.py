#!/usr/bin/env python3
"""Example 20: Self-Hosted Pipeline - Full Local Setup Demo.

Demonstrates a complete CI/CD pipeline running 100% locally.
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


def check_stack_status():
    """Check status of self-hosted stack."""
    services = {
        "code2llm-mcp": 8081,
        "vallm-mcp": 8080,
        "planfile-mcp": 8201,
        "aider-mcp": 3000,
        "proxym": 4000,
    }
    
    status = []
    for service, port in services.items():
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={service}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        is_running = service in result.stdout
        status.append((service, port, is_running))
    
    return status


def demo_full_pipeline():
    """Demonstrate complete local pipeline."""
    print("\n" + "=" * 70)
    print("SELF-HOSTED PIPELINE - Full Local CI/CD")
    print("=" * 70)
    
    steps = [
        {
            "phase": "1. Source Analysis",
            "tool": "code2llm",
            "action": "Static analysis",
            "input": "src/",
            "output": "analysis.toon",
            "time": "30s",
        },
        {
            "phase": "2. Quality Validation",
            "tool": "vallm",
            "action": "Code validation",
            "input": "analysis.toon",
            "output": "quality_report.json",
            "time": "15s",
        },
        {
            "phase": "3. Ticket Generation",
            "tool": "planfile",
            "action": "Create tickets",
            "input": "quality_report.json",
            "output": "tickets/",
            "time": "5s",
        },
        {
            "phase": "4. Code Refactoring",
            "tool": "aider-mcp",
            "action": "Apply fixes",
            "input": "tickets/high-priority.md",
            "output": "src/ (modified)",
            "time": "2m",
        },
        {
            "phase": "5. Verification",
            "tool": "vallm",
            "action": "Validate fixes",
            "input": "src/",
            "output": "validation.json",
            "time": "15s",
        },
        {
            "phase": "6. Documentation",
            "tool": "code2llm",
            "action": "Generate docs",
            "input": "src/",
            "output": "docs/",
            "time": "20s",
        },
    ]
    
    print("\n📊 Pipeline Steps:\n")
    print(f"{'Phase':<25} {'Tool':<12} {'Action':<20} {'Time':<8}")
    print("-" * 70)
    
    total_time = 0
    for step in steps:
        print(f"{step['phase']:<25} {step['tool']:<12} {step['action']:<20} {step['time']:<8}")
        # Rough time calculation
        if 'm' in step['time']:
            total_time += int(step['time'].replace('m', '')) * 60
        else:
            total_time += int(step['time'].replace('s', ''))
    
    print("-" * 70)
    print(f"Total pipeline time: ~{total_time // 60}m {total_time % 60}s")
    print(f"Total cost: $0.00 (self-hosted)")


def demo_workflow_scenarios():
    """Show different workflow scenarios."""
    print("\n" + "=" * 70)
    print("WORKFLOW SCENARIOS")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Daily Development",
            "trigger": "git commit",
            "steps": ["validate", "quick-fix"],
            "time": "1m",
        },
        {
            "name": "Code Review",
            "trigger": "pull request",
            "steps": ["analyze", "validate", "generate-tickets"],
            "time": "3m",
        },
        {
            "name": "Release Preparation",
            "trigger": "tag push",
            "steps": ["full-analysis", "validate", "refactor", "docs", "verify"],
            "time": "10m",
        },
        {
            "name": "Legacy Refactoring",
            "trigger": "manual",
            "steps": ["analyze", "batch-refactor", "validate", "docs"],
            "time": "30m",
        },
    ]
    
    print()
    for s in scenarios:
        print(f"📋 {s['name']}")
        print(f"   Trigger: {s['trigger']}")
        print(f"   Steps: {' → '.join(s['steps'])}")
        print(f"   Time: {s['time']}")
        print()


def demo_api_examples():
    """Show API usage examples."""
    print("\n" + "=" * 70)
    print("API EXAMPLES")
    print("=" * 70)
    
    examples = [
        {
            "desc": "Analyze project",
            "cmd": "curl -X POST http://localhost:8081/analyze \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"path\": \"/workspace\", \"format\": \"toon\"}'"
        },
        {
            "desc": "Validate code",
            "cmd": "curl -X POST http://localhost:8080/validate \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"path\": \"/workspace/src\", \"recursive\": true}'"
        },
        {
            "desc": "Create ticket",
            "cmd": "curl -X POST http://localhost:8201/tickets \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"title\": \"Refactor\", \"priority\": \"high\"}'"
        },
        {
            "desc": "Check health",
            "cmd": "curl http://localhost:8081/health"
        },
    ]
    
    for ex in examples:
        print(f"\n{ex['desc']}:")
        print(f"  {ex['cmd']}")


def show_resource_usage():
    """Show estimated resource usage."""
    print("\n" + "=" * 70)
    print("RESOURCE USAGE (Estimated)")
    print("=" * 70)
    
    resources = [
        ("code2llm-mcp", "512MB", "Low", "Analysis"),
        ("vallm-mcp", "512MB", "Low", "Validation"),
        ("planfile-mcp", "256MB", "Minimal", "Tickets"),
        ("aider-mcp", "1GB", "High", "Refactoring"),
        ("proxym", "512MB", "Medium", "LLM Gateway"),
        ("Redis", "256MB", "Minimal", "Cache"),
    ]
    
    print(f"\n{'Service':<20} {'Memory':<10} {'CPU':<10} {'Purpose':<20}")
    print("-" * 70)
    total_ram = 0
    for service, mem, cpu, purpose in resources:
        print(f"{service:<20} {mem:<10} {cpu:<10} {purpose:<20}")
        # Parse memory
        if 'GB' in mem:
            total_ram += int(mem.replace('GB', '')) * 1024
        else:
            total_ram += int(mem.replace('MB', ''))
    
    print("-" * 70)
    print(f"Total RAM needed: ~{total_ram}MB ({total_ram/1024:.1f}GB)")
    print(f"Disk space: ~5GB (images)")


def show_deployment_options():
    """Show deployment options."""
    print("\n" + "=" * 70)
    print("DEPLOYMENT OPTIONS")
    print("=" * 70)
    
    options = [
        {
            "name": "Local Dev Machine",
            "specs": "16GB RAM, 4 cores",
            "best_for": "Development, testing",
            "pros": "Simple, fast",
            "cons": "Resource limited",
        },
        {
            "name": "Homelab Server",
            "specs": "32GB RAM, 8 cores",
            "best_for": "Team of 5-10",
            "pros": "Always on, shared",
            "cons": "Setup complexity",
        },
        {
            "name": "VPS Cloud",
            "specs": "4 vCPU, 16GB RAM",
            "best_for": "Remote access",
            "pros": "Accessible anywhere",
            "cons": "~$40/month",
        },
        {
            "name": "Bare Metal",
            "specs": "64GB RAM, GPU",
            "best_for": "Large teams",
            "pros": "Maximum performance",
            "cons": "High upfront cost",
        },
    ]
    
    for opt in options:
        print(f"\n🏠 {opt['name']}")
        print(f"   Specs: {opt['specs']}")
        print(f"   Best for: {opt['best_for']}")
        print(f"   Pros: {opt['pros']}")
        print(f"   Cons: {opt['cons']}")


if __name__ == "__main__":
    load_env()
    
    print("\n" + "=" * 70)
    print("Example 20: Self-Hosted Pipeline - Full Local Setup")
    print("=" * 70)
    
    # Check stack
    status = check_stack_status()
    running = sum(1 for _, _, r in status if r)
    total = len(status)
    
    print(f"\n📊 Stack Status: {running}/{total} services running")
    for service, port, is_running in status:
        icon = "🟢" if is_running else "🔴"
        print(f"   {icon} {service} (port {port})")
    
    if running == 0:
        print("\n⚠️  No services running!")
        print("   Start with: make up (from repo root)")
    elif running < total:
        print("\n⚠️  Some services not running")
        print("   Check: make status")
    else:
        print("\n✅ All services running!")
    
    # Run demos
    demo_full_pipeline()
    demo_workflow_scenarios()
    demo_api_examples()
    show_resource_usage()
    show_deployment_options()
    
    print("\n" + "=" * 70)
    print("🎯 Complete autonomy - no external dependencies!")
    print("=" * 70)
