#!/usr/bin/env python3
"""
Install script for LiteLLM Proxy + Ollama dependencies.
"""

import subprocess
import sys


def install_litellm():
    """Install litellm with proxy dependencies."""
    print("Installing litellm[proxy]...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "litellm[proxy]"],
            check=True
        )
        print("✅ litellm[proxy] installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install litellm[proxy]: {e}")
        return False


def check_litellm():
    """Check if litellm is installed and working."""
    try:
        result = subprocess.run(
            ["litellm", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def main():
    print("=" * 60)
    print("LiteLLM Proxy + Ollama - Setup")
    print("=" * 60)
    print()
    
    if check_litellm():
        print("✅ litellm is already installed")
        print()
        print("You can now run:")
        print("  make proxy  # Start the proxy server")
        return 0
    
    print("❌ litellm not found")
    print()
    print("Installing litellm[proxy]...")
    print("This may take a few minutes...")
    print()
    
    if install_litellm():
        print()
        print("✅ Installation complete!")
        print()
        print("Next steps:")
        print("  1. make proxy    # Start proxy in Terminal 1")
        print("  2. make fix      # Run auto_fix in Terminal 2")
        return 0
    else:
        print()
        print("❌ Installation failed")
        print()
        print("Try manual installation:")
        print("  pip install 'litellm[proxy]'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
