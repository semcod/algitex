#!/usr/bin/env python3
"""
Proxym Server - LLM proxy with budget tracking and multi-provider support
REST API compatible with OpenAI format
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
import uvicorn
import httpx

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class ProxymServer:
    """LLM proxy with budget tracking."""
    
    def __init__(self):
        self.port = int(os.getenv("PORT", "4000"))
        self.name = "proxym"
        self.version = "0.1.0"
        
        # API keys from environment
        self.keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "gemini": os.getenv("GEMINI_API_KEY", ""),
        }
        
        # Budget tracking
        self.daily_budget_usd = float(os.getenv("DAILY_BUDGET", "10.0"))
        self.today_cost = 0.0
        self.requests_today = 0
        
        # Model pricing (per 1K tokens)
        self.pricing = {
            "claude-sonnet-4": {"input": 0.003, "output": 0.015},
            "claude-opus-4": {"input": 0.015, "output": 0.075},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4o": {"input": 0.005, "output": 0.015},
        }
        
        self.http_client = httpx.AsyncClient(timeout=60.0)
    
    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(title="Proxym", version=self.version)
        
        @app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "budget_remaining": self.daily_budget_usd - self.today_cost,
                "requests_today": self.requests_today
            }
        
        @app.get("/v1/models")
        async def list_models():
            """List available models."""
            return {
                "object": "list",
                "data": [
                    {"id": "claude-sonnet-4", "object": "model"},
                    {"id": "claude-opus-4", "object": "model"},
                    {"id": "gpt-4", "object": "model"},
                    {"id": "gpt-4o", "object": "model"},
                ]
            }
        
        @app.post("/v1/chat/completions")
        async def chat_completions(request: Dict[str, Any]):
            """Chat completions endpoint."""
            # Check budget
            if self.today_cost >= self.daily_budget_usd:
                raise HTTPException(429, "Daily budget exceeded")
            
            model = request.get("model", "claude-sonnet-4")
            messages = request.get("messages", [])
            
            # Route to appropriate provider
            if "claude" in model:
                response = await self._call_anthropic(model, messages)
            elif "gpt" in model:
                response = await self._call_openai(model, messages)
            else:
                response = await self._mock_response(model, messages)
            
            # Track cost
            self._track_cost(model, response)
            self.requests_today += 1
            
            return response
        
        @app.get("/budget")
        async def get_budget():
            """Get current budget status."""
            return {
                "daily_budget": self.daily_budget_usd,
                "spent_today": self.today_cost,
                "remaining": self.daily_budget_usd - self.today_cost,
                "requests_today": self.requests_today
            }
        
        return app
    
    async def _call_anthropic(self, model: str, messages: List[Dict]) -> Dict[str, Any]:
        """Call Anthropic Claude API."""
        if not self.keys["anthropic"]:
            return await self._mock_response(model, messages)
        
        try:
            headers = {
                "x-api-key": self.keys["anthropic"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            # Convert messages to Anthropic format
            system_msg = ""
            chat_messages = []
            for msg in messages:
                if msg.get("role") == "system":
                    system_msg = msg.get("content", "")
                else:
                    chat_messages.append({
                        "role": msg.get("role"),
                        "content": msg.get("content")
                    })
            
            payload = {
                "model": model,
                "messages": chat_messages,
                "max_tokens": 4096
            }
            if system_msg:
                payload["system"] = system_msg
            
            resp = await self.http_client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Convert to OpenAI format
            return {
                "id": data.get("id", "proxym-" + datetime.now().isoformat()),
                "object": "chat.completion",
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": data.get("content", [{}])[0].get("text", "")
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
                    "total_tokens": data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
                }
            }
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return await self._mock_response(model, messages)
    
    async def _call_openai(self, model: str, messages: List[Dict]) -> Dict[str, Any]:
        """Call OpenAI API."""
        if not self.keys["openai"]:
            return await self._mock_response(model, messages)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.keys['openai']}",
                "Content-Type": "application/json"
            }
            
            resp = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 4096
                }
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return await self._mock_response(model, messages)
    
    async def _mock_response(self, model: str, messages: List[Dict]) -> Dict[str, Any]:
        """Generate mock response when APIs unavailable."""
        prompt = messages[-1].get("content", "") if messages else ""
        prompt_tokens = len(prompt.split())
        completion_tokens = 150
        
        return {
            "id": f"proxym-mock-{datetime.now().isoformat()}",
            "object": "chat.completion",
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"[Mock response] Received: {prompt[:100]}..."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }
    
    def _track_cost(self, model: str, response: Dict[str, Any]):
        """Track API call cost."""
        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        pricing = self.pricing.get(model, {"input": 0.01, "output": 0.03})
        cost = (input_tokens / 1000) * pricing["input"] + (output_tokens / 1000) * pricing["output"]
        self.today_cost += cost
        
        logger.info(f"Cost: ${cost:.4f}, Total today: ${self.today_cost:.4f}")
    
    async def run(self):
        """Run the server."""
        logger.info(f"Starting Proxym on port {self.port}")
        app = self.create_fastapi_app()
        config = uvicorn.Config(app, host="0.0.0.0", port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    server = ProxymServer()
    import asyncio
    asyncio.run(server.run())
