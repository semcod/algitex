#!/usr/bin/env python3
"""
Example 20: Self-Hosted Pipeline - Full Local CI/CD

Kompletny pipeline działający w 100% lokalnie z wykorzystaniem:
- code2llm-mcp: analiza kodu
- vallm-mcp: walidacja
- planfile-mcp: zarządzanie ticketami
- proxym-mcp (opcjonalnie): proxy do Ollama
"""

import os
import sys
import requests
from typing import Dict, Any

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Configuration
CODE2LLM_URL = os.getenv("CODE2LLM_URL", "http://localhost:8081")
VALLM_URL = os.getenv("VALLM_URL", "http://localhost:8080")
PLANFILE_URL = os.getenv("PLANFILE_URL", "http://localhost:8201")


def check_services() -> Dict[str, bool]:
    """Check if all MCP services are running."""
    services = {
        "code2llm": False,
        "vallm": False,
        "planfile": False,
    }
    
    try:
        r = requests.get(f"{CODE2LLM_URL}/health", timeout=2)
        services["code2llm"] = r.status_code == 200
    except:
        pass
    
    try:
        r = requests.get(f"{VALLM_URL}/health", timeout=2)
        services["vallm"] = r.status_code == 200
    except:
        pass
    
    try:
        r = requests.get(f"{PLANFILE_URL}/health", timeout=2)
        services["planfile"] = r.status_code == 200
    except:
        pass
    
    return services


def demo_code_analysis():
    """Demonstrate code analysis with code2llm."""
    print("\n📊 Step 1: Code Analysis (code2llm-mcp)")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{CODE2LLM_URL}/analyze",
            json={"path": "/app", "format": "toon"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis complete")
            print(f"   Files: {data.get('total_files', 'N/A')}")
            print(f"   Functions: {data.get('total_functions', 'N/A')}")
            print(f"   Avg Complexity: {data.get('average_cc', 'N/A')}")
            if data.get('hotspots'):
                print(f"   Hotspots: {len(data['hotspots'])} high-complexity areas")
        else:
            print(f"⚠️  Analysis returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")


def demo_validation():
    """Demonstrate validation with vallm."""
    print("\n🔍 Step 2: Validation (vallm-mcp)")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{VALLM_URL}/validate",
            json={"path": "/app"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Validation complete")
            print(f"   Static: {'✅' if data.get('static_passed') else '❌'}")
            print(f"   Runtime: {'✅' if data.get('runtime_passed') else '❌'}")
            print(f"   Security: {'✅' if data.get('security_passed') else '❌'}")
            print(f"   Overall Score: {data.get('score', 'N/A'):.1f}/10")
        else:
            print(f"⚠️  Validation returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Validation failed: {e}")


def demo_ticket_management():
    """Demonstrate ticket management with planfile-mcp."""
    print("\n🎫 Step 3: Ticket Management (planfile-mcp)")
    print("-" * 50)
    
    try:
        # Create a ticket
        response = requests.post(
            f"{PLANFILE_URL}/tickets",
            json={
                "title": "Demo: Refactor main.py",
                "description": "Example ticket from self-hosted pipeline demo",
                "priority": "normal",
                "tags": ["demo", "refactor"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            ticket_id = data.get('ticket_id', 'N/A')
            print(f"✅ Created ticket: {ticket_id}")
        else:
            print(f"⚠️  Ticket creation returned: {response.status_code}")
        
        # List tickets
        response = requests.get(f"{PLANFILE_URL}/tickets", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Total tickets: {data.get('count', 0)}")
    except Exception as e:
        print(f"❌ Ticket management failed: {e}")


def demo_sprint_status():
    """Demonstrate sprint status."""
    print("\n📈 Step 4: Sprint Status")
    print("-" * 50)
    
    try:
        response = requests.get(f"{PLANFILE_URL}/sprint", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sprint status")
            print(f"   Total tickets: {data.get('total', 0)}")
            print(f"   By status: {data.get('by_status', {})}")
            print(f"   Completion: {data.get('completion_rate', 0)*100:.1f}%")
    except Exception as e:
        print(f"❌ Sprint status failed: {e}")


def main():
    """Main demo function."""
    print("=" * 60)
    print("Example 20: Self-Hosted Pipeline - Full Local CI/CD")
    print("=" * 60)
    print()
    print("This example demonstrates a complete local pipeline using:")
    print("  • code2llm-mcp  :8081 - Code analysis")
    print("  • vallm-mcp     :8080 - Validation")
    print("  • planfile-mcp  :8201 - Ticket management")
    print()
    
    # Check services
    print("Checking services...")
    services = check_services()
    
    for name, status in services.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    
    if not all(services.values()):
        print("\n⚠️  Some services are not running!")
        print("   Start them with: make up")
        return 1
    
    print("\n✅ All services ready!")
    
    # Run demo steps
    demo_code_analysis()
    demo_validation()
    demo_ticket_management()
    demo_sprint_status()
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run auto-fix workflow:")
    print("     python auto_fix_todos.py")
    print()
    print("  2. Use CLI with local model:")
    print("     export DEFAULT_MODEL=ollama/qwen2.5-coder:7b")
    print("     algitex analyze --model ollama/qwen2.5-coder:7b")
    print()
    print("  3. Stop services:")
    print("     make down")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
