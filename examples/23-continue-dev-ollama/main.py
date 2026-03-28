#!/usr/bin/env python3
"""
Continue.dev + Ollama configuration generator.
Creates ~/.continue/config.json with Ollama settings.
"""

import os
import sys
import json


def generate_continue_config():
    """Generate Continue.dev config for Ollama."""
    config = {
        "models": [
            {
                "title": "Qwen Coder 7B (Local)",
                "provider": "ollama",
                "model": "qwen2.5-coder:7b",
                "apiBase": "http://localhost:11434"
            },
            {
                "title": "Llama 3 8B (Local)",
                "provider": "ollama",
                "model": "llama3:8b",
                "apiBase": "http://localhost:11434"
            },
            {
                "title": "CodeLlama 7B (Local)",
                "provider": "ollama",
                "model": "codellama:7b",
                "apiBase": "http://localhost:11434"
            }
        ],
        "tabAutocompleteModel": {
            "title": "Qwen Autocomplete",
            "provider": "ollama",
            "model": "qwen2.5-coder:7b",
            "apiBase": "http://localhost:11434"
        },
        "customCommands": [
            {
                "name": "refactor",
                "prompt": "Refactor this code to be more readable, efficient, and maintainable. Add type hints, docstrings, and improve variable names.",
                "description": "Refactor selected code"
            },
            {
                "name": "fix",
                "prompt": "Find and fix any bugs, issues, or code smells in this code. Explain what was wrong and how you fixed it.",
                "description": "Fix code issues"
            },
            {
                "name": "test",
                "prompt": "Write comprehensive unit tests for this code using pytest. Include edge cases and error scenarios.",
                "description": "Generate unit tests"
            },
            {
                "name": "document",
                "prompt": "Add comprehensive documentation to this code. Include docstrings, inline comments, and type hints.",
                "description": "Add documentation"
            },
            {
                "name": "optimize",
                "prompt": "Optimize this code for better performance. Explain the optimizations made.",
                "description": "Optimize performance"
            }
        ]
    }
    return config


def install_config():
    """Install config to ~/.continue/config.json."""
    home = os.path.expanduser("~")
    continue_dir = os.path.join(home, ".continue")
    config_path = os.path.join(continue_dir, "config.json")
    
    # Create directory if needed
    if not os.path.exists(continue_dir):
        os.makedirs(continue_dir)
        print(f"Created: {continue_dir}")
    
    # Backup existing config
    if os.path.exists(config_path):
        backup_path = config_path + ".backup"
        os.rename(config_path, backup_path)
        print(f"Backup: {backup_path}")
    
    # Write new config
    config = generate_continue_config()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created: {config_path}")
    return True


def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except:
        return False


def list_models():
    """List available Ollama models."""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            models = r.json().get('models', [])
            return [m['name'] for m in models]
    except:
        pass
    return []


def main():
    print("=" * 60)
    print("Example 23: Continue.dev + Ollama Setup")
    print("=" * 60)
    print()
    
    # Check Ollama
    if check_ollama():
        models = list_models()
        print(f"✅ Ollama running ({len(models)} models)")
        for m in models:
            print(f"   - {m}")
    else:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    print()
    
    # Install config
    print("Installing Continue.dev config...")
    if install_config():
        print("✅ Config installed")
    else:
        print("❌ Failed to install config")
        return 1
    
    print()
    print("=" * 60)
    print("Next steps:")
    print()
    print("1. Open VS Code")
    print("2. Install Continue.dev extension (if not installed)")
    print("3. Press Ctrl+L to open Continue panel")
    print("4. Select 'Qwen Coder 7B (Local)' from dropdown")
    print()
    print("Usage:")
    print("  Ctrl+L      - Open chat panel")
    print("  Ctrl+I      - Inline edit (select code first)")
    print("  Tab         - Autocomplete")
    print()
    print("Custom commands (type in chat):")
    print("  /refactor   - Refactor selected code")
    print("  /fix        - Fix issues")
    print("  /test       - Generate tests")
    print("  /document   - Add documentation")
    print("  /optimize   - Optimize performance")
    print()
    print("Config location: ~/.continue/config.json")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
