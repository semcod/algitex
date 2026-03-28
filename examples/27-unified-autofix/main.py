#!/usr/bin/env python3
"""Example 27: Unified AutoFix - Simplified using algitex Project."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from algitex import Project


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified AutoFix - Complete algitex demo")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of issues to fix")
    parser.add_argument("--backend", "-b", default="ollama", choices=["auto", "ollama", "aider", "litellm-proxy"])
    parser.add_argument("--demo", action="store_true", help="Run feature demos")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Example 27: Unified AutoFix")
    print("=" * 60)
    print()
    
    p = Project(".")
    
    # 1. Check services
    print("1. Service Health Check")
    print("-" * 60)
    p.print_service_status(show_details=True)
    
    # Check Ollama
    ollama_status = p.check_ollama()
    if ollama_status["healthy"]:
        models = ollama_status["details"]["models"]
        print(f"\n✅ Ollama: {len(models)} models available")
    
    # 2. Analyze and generate TODO
    print("\n2. Project Analysis")
    print("-" * 60)
    result = p.generate_todo()
    print(f"✅ Created {result['filename']} with {result['count']} issues")
    print(f"   Project grade: {result['grade']}")
    
    # 3. Fix issues
    print("\n3. AutoFix Execution")
    print("-" * 60)
    print(f"Backend: {args.backend}")
    
    fix_result = p.fix_issues(limit=args.limit, backend=args.backend)
    print(f"✅ Fixed: {fix_result['fixed']}/{fix_result['total']}")
    
    # 4. Optional demos
    if args.demo and ollama_status["healthy"]:
        print("\n4. Additional Features")
        print("-" * 60)
        code = p.generate_with_ollama("Write a hello world function")
        print(f"Generated code:\n{code[:200]}...")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
