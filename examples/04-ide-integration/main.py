#!/usr/bin/env python3
"""Example 04: IDE Integration.

Shows how to configure popular IDEs/agents to work with algitex + proxym.
Generates config snippets for Roo Code, Cline, Continue.dev, Aider, Cursor.

Setup:
    cp .env.example .env
    # Edit .env with your actual values

Run:
    python main.py
"""

import json
import os
from pathlib import Path


def load_env() -> None:
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


# Load .env before setting defaults
load_env()

PROXY_URL = os.getenv("PROXY_URL", "http://localhost:4000")
API_KEY = os.getenv("API_KEY", "sk-proxy-local-dev")


def roo_code_config() -> None:
    """Settings for Roo Code (VS Code extension)."""
    return {
        "roo-code.provider": "openai-compatible",
        "roo-code.apiBase": f"{PROXY_URL}/v1",
        "roo-code.apiKey": API_KEY,
        "roo-code.models": {
            "architect": "free",       # planning → Gemini free tier
            "code": "balanced",        # implementation → Gemini Flash
            "debug": "cheap",          # debugging → Haiku
            "custom-opus": "premium",  # complex tasks → Opus
        },
    }


def cline_config():
    """Settings for Cline (VS Code extension)."""
    return {
        "cline.provider": "openai-compatible",
        "cline.openaiBaseUrl": f"{PROXY_URL}/v1",
        "cline.openaiApiKey": API_KEY,
        "cline.openaiModelId": "balanced",
    }


def continuedev_config():
    """~/.continue/config.json for Continue.dev."""
    return {
        "models": [
            {
                "title": "algitex balanced",
                "provider": "openai",
                "model": "balanced",
                "apiBase": f"{PROXY_URL}/v1",
                "apiKey": API_KEY,
            },
            {
                "title": "algitex premium",
                "provider": "openai",
                "model": "premium",
                "apiBase": f"{PROXY_URL}/v1",
                "apiKey": API_KEY,
            },
        ],
        "tabAutocompleteModel": {
            "title": "algitex local",
            "provider": "openai",
            "model": "local",
            "apiBase": f"{PROXY_URL}/v1",
            "apiKey": API_KEY,
        },
    }


def aider_env():
    """Environment variables for Aider."""
    return {
        "OPENAI_API_BASE": PROXY_URL,
        "OPENAI_API_KEY": API_KEY,
        "AIDER_MODEL": "balanced",
        "AIDER_WEAK_MODEL": "cheap",
    }


def cursor_config():
    """Settings for Cursor / Windsurf."""
    return {
        "note": "Use OpenAI-compatible provider",
        "apiBase": f"{PROXY_URL}/v1",
        "apiKey": API_KEY,
        "model": "balanced",
    }


def claude_code_env():
    """Environment variables for Claude Code."""
    return {
        "ANTHROPIC_BASE_URL": PROXY_URL,
        "ANTHROPIC_API_KEY": API_KEY,
    }


def main():
    print("=== IDE Integration Configs ===\n")

    configs = [
        ("Roo Code (VS Code)", roo_code_config()),
        ("Cline (VS Code)", cline_config()),
        ("Continue.dev", continuedev_config()),
        ("Cursor / Windsurf", cursor_config()),
    ]

    for name, config in configs:
        print(f"── {name} ──")
        print(json.dumps(config, indent=2))
        print()

    print("── Aider (shell env) ──")
    for key, val in aider_env().items():
        print(f"export {key}={val}")

    print("\n── Claude Code (shell env) ──")
    for key, val in claude_code_env().items():
        print(f"export {key}={val}")

    print("\n── Model aliases ──")
    print("  cheap     → Haiku 4.5     (debug, validation)")
    print("  balanced  → Gemini Flash  (default coding)")
    print("  premium   → Opus 4.6     (architecture, complex refactoring)")
    print("  free      → Gemini 2.5   (planning, analysis)")
    print("  local     → Qwen 3B      (offline, autocomplete)")

    print(f"\n✅ All IDEs point at {PROXY_URL}")
    print("   proxym routes to the optimal model per-request.")
    print("   Start proxym: docker compose up -d  OR  proxym serve")


if __name__ == "__main__":
    main()
