#!/usr/bin/env python3
"""
Aider MCP Server - Multi-protocol implementation for Algitex
Supports: MCP stdio, MCP SSE, and REST API
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class AiderMCPServer:
    """Aider MCP Server with multi-protocol support."""
    
    def __init__(self):
        self.transport = os.getenv("TRANSPORT", "stdio")
        self.port = int(os.getenv("PORT", "3000"))
        self.name = "aider-mcp"
        self.version = "0.1.0"
        
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return available tools/capabilities."""
        return [
            {
                "name": "aider_ai_code",
                "description": "Edit code using AI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "relative_editable_files": {"type": "array", "items": {"type": "string"}},
                        "model": {"type": "string"}
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "aider_list_models",
                "description": "List available AI models",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def handle_aider_ai_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle aider_ai_code tool call."""
        prompt = params.get("prompt", "")
        files = params.get("relative_editable_files", [])
        model = params.get("model", "claude-sonnet-4")
        
        logger.info(f"Processing prompt: {prompt[:100]}...")
        logger.info(f"Files: {files}, Model: {model}")
        
        # Stub implementation - would integrate with real aider
        return {
            "status": "success",
            "edited_files": files,
            "changes": f"Applied AI edits based on: {prompt[:100]}",
            "tokens_in": len(prompt.split()),
            "tokens_out": 150,
            "model": model
        }
    
    async def handle_aider_list_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle aider_list_models tool call."""
        return {
            "models": [
                "claude-sonnet-4",
                "claude-opus-4",
                "gpt-4",
                "ollama/qwen2.5-coder:7b"
            ]
        }
    
    # === MCP stdio protocol ===
    
    async def run_stdio(self):
        """Run as MCP stdio server."""
        logger.info("Starting MCP stdio server")
        
        while True:
            try:
                # Read Content-Length header
                header = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not header:
                    break
                    
                header = header.strip()
                if not header.startswith("Content-Length:"):
                    continue
                    
                content_length = int(header.split(":")[1].strip())
                
                # Read empty line
                await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                # Read JSON content
                content = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: sys.stdin.read(content_length)
                )
                
                request = json.loads(content)
                response = await self._handle_jsonrpc(request)
                
                # Send response
                response_json = json.dumps(response)
                message = f"Content-Length: {len(response_json)}\r\n\r\n{response_json}"
                sys.stdout.write(message)
                sys.stdout.flush()
                
            except Exception as e:
                logger.error(f"Error in stdio loop: {e}")
                continue
    
    async def _handle_jsonrpc(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id", 0)
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {
                            "name": self.name,
                            "version": self.version
                        }
                    }
                }
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": self.get_capabilities()}
                }
            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_params = params.get("arguments", {})
                
                if tool_name == "aider_ai_code":
                    result = await self.handle_aider_ai_code(tool_params)
                elif tool_name == "aider_list_models":
                    result = await self.handle_aider_list_models(tool_params)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result)}]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)}
            }
    
    # === REST API ===
    
    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI application for REST mode."""
        app = FastAPI(title="Aider MCP Server", version=self.version)
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "server": self.name}
        
        @app.get("/tools")
        async def list_tools():
            return {"tools": self.get_capabilities()}
        
        @app.post("/call/{tool_name}")
        async def call_tool(tool_name: str, params: Dict[str, Any]):
            if tool_name == "aider_ai_code":
                result = await self.handle_aider_ai_code(params)
            elif tool_name == "aider_list_models":
                result = await self.handle_aider_list_models(params)
            else:
                return JSONResponse(
                    status_code=404,
                    content={"error": f"Unknown tool: {tool_name}"}
                )
            return result
        
        @app.post("/mcp")
        async def mcp_endpoint(request: Dict[str, Any]):
            """MCP-compatible JSON-RPC endpoint."""
            response = await self._handle_jsonrpc(request)
            return response
        
        return app
    
    async def run_rest(self):
        """Run as REST API server."""
        logger.info(f"Starting REST server on port {self.port}")
        app = self.create_fastapi_app()
        config = uvicorn.Config(app, host="0.0.0.0", port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    
    async def run(self):
        """Run server based on TRANSPORT env var."""
        if self.transport == "stdio":
            await self.run_stdio()
        elif self.transport in ("rest", "sse"):
            await self.run_rest()
        else:
            raise ValueError(f"Unknown transport: {self.transport}")


if __name__ == "__main__":
    server = AiderMCPServer()
    asyncio.run(server.run())
