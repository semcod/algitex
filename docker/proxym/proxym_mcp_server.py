#!/usr/bin/env python3
"""
Proxym MCP Server - LLM proxy with MCP support
Routes requests to multiple LLM providers with budget tracking
"""

import os
import sys
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
import httpx
import tiktoken

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("proxym")

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "claude-sonnet-4")

# Simple token counter
try:
    encoding = tiktoken.get_encoding("cl100k_base")
except:
    encoding = None


def count_tokens(text: str) -> int:
    """Count tokens in text."""
    if encoding:
        return len(encoding.encode(text))
    return len(text.split())


@mcp.tool()
def list_models() -> Dict[str, Any]:
    """
    List available LLM models and their capabilities.
    
    Returns:
        Dictionary with available models and their configurations
    """
    models = []
    
    if ANTHROPIC_API_KEY:
        models.extend([
            {"id": "claude-sonnet-4", "provider": "anthropic", "context": 200000},
            {"id": "claude-opus-4", "provider": "anthropic", "context": 200000},
            {"id": "claude-haiku-3", "provider": "anthropic", "context": 48000},
        ])
    
    if OPENAI_API_KEY:
        models.extend([
            {"id": "gpt-4o", "provider": "openai", "context": 128000},
            {"id": "gpt-4o-mini", "provider": "openai", "context": 128000},
        ])
    
    if GEMINI_API_KEY:
        models.extend([
            {"id": "gemini-2.0-flash", "provider": "google", "context": 1048576},
        ])
    
    return {
        "models": models,
        "default": DEFAULT_MODEL,
        "count": len(models),
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def chat_completion(
    messages: List[Dict[str, str]],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4096
) -> Dict[str, Any]:
    """
    Send chat completion request to LLM provider.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model ID to use (defaults to system default)
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Dictionary with response content and metadata
    """
    model = model or DEFAULT_MODEL
    
    # Count input tokens
    input_text = "\n".join([m.get("content", "") for m in messages])
    input_tokens = count_tokens(input_text)
    
    # Route to appropriate provider
    if model.startswith("claude") and ANTHROPIC_API_KEY:
        return _call_anthropic(messages, model, temperature, max_tokens, input_tokens)
    elif model.startswith("gpt") and OPENAI_API_KEY:
        return _call_openai(messages, model, temperature, max_tokens, input_tokens)
    elif model.startswith("gemini") and GEMINI_API_KEY:
        return _call_gemini(messages, model, temperature, max_tokens, input_tokens)
    else:
        return {
            "error": f"Model {model} not available or API key not configured",
            "available_models": list_models()["models"]
        }


def _call_anthropic(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    input_tokens: int
) -> Dict[str, Any]:
    """Call Anthropic Claude API."""
    try:
        # Convert messages to Anthropic format
        system_msg = None
        chat_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content")
            else:
                chat_messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content")
                })
        
        payload = {
            "model": model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=120.0
        )
        
        data = response.json()
        
        if response.status_code == 200:
            content = data.get("content", [{}])[0].get("text", "")
            output_tokens = data.get("usage", {}).get("output_tokens", count_tokens(content))
            
            return {
                "content": content,
                "model": model,
                "provider": "anthropic",
                "input_tokens": data.get("usage", {}).get("input_tokens", input_tokens),
                "output_tokens": output_tokens,
                "total_tokens": data.get("usage", {}).get("input_tokens", input_tokens) + output_tokens,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "error": data.get("error", {}).get("message", "Unknown error"),
                "status_code": response.status_code
            }
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        return {"error": str(e)}


def _call_openai(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    input_tokens: int
) -> Dict[str, Any]:
    """Call OpenAI API."""
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=120.0
        )
        
        data = response.json()
        
        if response.status_code == 200:
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            return {
                "content": content,
                "model": model,
                "provider": "openai",
                "input_tokens": usage.get("prompt_tokens", input_tokens),
                "output_tokens": usage.get("completion_tokens", count_tokens(content)),
                "total_tokens": usage.get("total_tokens", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "error": data.get("error", {}).get("message", "Unknown error"),
                "status_code": response.status_code
            }
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return {"error": str(e)}


def _call_gemini(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    input_tokens: int
) -> Dict[str, Any]:
    """Call Google Gemini API."""
    try:
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg.get("role") in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })
        
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={
                "Content-Type": "application/json"
            },
            params={"key": GEMINI_API_KEY},
            json={
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            },
            timeout=120.0
        )
        
        data = response.json()
        
        if response.status_code == 200:
            content = data["candidates"][0]["content"]["parts"][0].get("text", "")
            
            return {
                "content": content,
                "model": model,
                "provider": "google",
                "input_tokens": input_tokens,
                "output_tokens": count_tokens(content),
                "total_tokens": input_tokens + count_tokens(content),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "error": data.get("error", {}).get("message", "Unknown error"),
                "status_code": response.status_code
            }
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {"error": str(e)}


@mcp.tool()
def simple_prompt(prompt: str, model: str = None) -> Dict[str, Any]:
    """
    Simple single-prompt completion.
    
    Args:
        prompt: The prompt text to send
        model: Model ID to use (defaults to system default)
        
    Returns:
        Dictionary with response content and metadata
    """
    messages = [{"role": "user", "content": prompt}]
    return chat_completion(messages, model)


@mcp.tool()
def get_budget_status() -> Dict[str, Any]:
    """
    Get current budget/usage status (placeholder for budget tracking).
    
    Returns:
        Dictionary with budget information
    """
    return {
        "daily_limit": float(os.getenv("DAILY_BUDGET", "10.0")),
        "used_today": 0.0,  # Would be tracked in persistent storage
        "remaining": float(os.getenv("DAILY_BUDGET", "10.0")),
        "timestamp": datetime.now().isoformat()
    }


def create_rest_api() -> FastAPI:
    """Create FastAPI application for REST mode."""
    app = FastAPI(title="Proxym MCP", version="0.2.0")
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "server": "proxym-mcp"}
    
    @app.get("/models")
    async def models():
        return list_models()
    
    @app.post("/chat")
    async def chat(request: Dict[str, Any]):
        messages = request.get("messages", [])
        model = request.get("model")
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", 4096)
        return chat_completion(messages, model, temperature, max_tokens)
    
    @app.post("/prompt")
    async def prompt_endpoint(request: Dict[str, Any]):
        prompt = request.get("prompt", "")
        model = request.get("model")
        return simple_prompt(prompt, model)
    
    @app.get("/budget")
    async def budget():
        return get_budget_status()
    
    return app


async def run_rest_server():
    """Run as REST API server."""
    port = int(os.getenv("PORT", "4000"))
    logger.info(f"Starting Proxym REST server on port {port}")
    app = create_rest_api()
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    transport = os.getenv("TRANSPORT", "stdio")
    
    if transport == "stdio":
        logger.info("Starting Proxym MCP stdio server")
        mcp.run(transport="stdio")
    elif transport in ("rest", "sse", "http"):
        import asyncio
        asyncio.run(run_rest_server())
    else:
        logger.error(f"Unknown transport: {transport}")
        sys.exit(1)
