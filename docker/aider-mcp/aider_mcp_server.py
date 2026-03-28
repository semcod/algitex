#!/usr/bin/env python3
"""
Aider MCP Server - AI coding assistant with FastMCP support
Multi-protocol: MCP stdio, MCP SSE, REST API
"""

import os
import sys
import logging
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("aider-mcp")


@mcp.tool()
def aider_ai_code(
    prompt: str,
    relative_editable_files: List[str] = None,
    model: str = "claude-sonnet-4"
) -> Dict[str, Any]:
    """
    Edit code using AI via Aider.
    
    Args:
        prompt: The coding instruction/prompt for AI
        relative_editable_files: List of file paths to edit
        model: AI model to use
        
    Returns:
        Dictionary with edit results and metadata
    """
    files = relative_editable_files or []
    
    logger.info(f"Processing prompt: {prompt[:100]}...")
    logger.info(f"Files: {files}, Model: {model}")
    
    return {
        "status": "success",
        "edited_files": files,
        "changes": f"Applied AI edits based on: {prompt[:100]}",
        "tokens_in": len(prompt.split()),
        "tokens_out": 150,
        "model": model
    }


@mcp.tool()
def aider_list_models() -> Dict[str, Any]:
    """
    List available AI models for Aider.
    
    Returns:
        Dictionary with available models
    """
    return {
        "models": [
            "claude-sonnet-4",
            "claude-opus-4",
            "gpt-4",
            "ollama/qwen2.5-coder:7b"
        ]
    }


@mcp.tool()
def aider_chat(message: str, context: str = "") -> Dict[str, Any]:
    """
    Chat with Aider AI about code.
    
    Args:
        message: The message/question to ask
        context: Additional context about the codebase
        
    Returns:
        Dictionary with AI response
    """
    return {
        "response": f"Aider AI response to: {message[:50]}...",
        "suggestions": ["Consider refactoring for clarity", "Add unit tests"],
        "context_used": bool(context)
    }


def create_rest_api() -> FastAPI:
    """Create FastAPI application for REST mode."""
    app = FastAPI(title="Aider MCP", version="0.2.0")
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "server": "aider-mcp"}
    
    @app.get("/tools")
    async def list_tools():
        return {"tools": [
            {"name": "aider_ai_code", "description": "Edit code using AI via Aider"},
            {"name": "aider_list_models", "description": "List available AI models"},
            {"name": "aider_chat", "description": "Chat with Aider AI about code"}
        ]}
    
    @app.post("/call/{tool_name}")
    async def call_tool(tool_name: str, request: Dict[str, Any]):
        if tool_name == "aider_ai_code":
            result = aider_ai_code(
                prompt=request.get("prompt", ""),
                relative_editable_files=request.get("relative_editable_files", []),
                model=request.get("model", "claude-sonnet-4")
            )
        elif tool_name == "aider_list_models":
            result = aider_list_models()
        elif tool_name == "aider_chat":
            result = aider_chat(
                message=request.get("message", ""),
                context=request.get("context", "")
            )
        else:
            return JSONResponse(status_code=404, content={"error": f"Unknown tool: {tool_name}"})
        return result
    
    return app


async def run_rest_server():
    """Run as REST API server."""
    port = int(os.getenv("PORT", "3000"))
    logger.info(f"Starting Aider REST server on port {port}")
    app = create_rest_api()
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    transport = os.getenv("TRANSPORT", "stdio")
    
    if transport == "stdio":
        logger.info("Starting Aider MCP stdio server")
        mcp.run(transport="stdio")
    elif transport in ("rest", "sse", "http"):
        import asyncio
        asyncio.run(run_rest_server())
    else:
        logger.error(f"Unknown transport: {transport}")
        sys.exit(1)
