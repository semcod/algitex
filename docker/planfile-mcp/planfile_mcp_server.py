#!/usr/bin/env python3
"""
Planfile MCP Server - Ticket management hub for Algitex
Multi-protocol: MCP stdio, MCP SSE, REST API
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import yaml
from fastapi import FastAPI
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class PlanfileMCPServer:
    """Planfile MCP Server for ticket management."""
    
    def __init__(self):
        self.transport = os.getenv("TRANSPORT", "stdio")
        self.port = int(os.getenv("PORT", "8201"))
        self.data_dir = Path(os.getenv("DATA_DIR", "/data"))
        self.name = "planfile-mcp"
        self.version = "0.1.0"
        self._tickets: Dict[str, Dict] = {}
        self._load_tickets()
    
    def _load_tickets(self):
        """Load tickets from data directory."""
        planfile_path = self.data_dir / "planfile.yaml"
        if planfile_path.exists():
            try:
                with open(planfile_path) as f:
                    data = yaml.safe_load(f)
                    if data and "tickets" in data:
                        for ticket in data["tickets"]:
                            self._tickets[ticket.get("id", str(len(self._tickets)))] = ticket
            except Exception as e:
                logger.error(f"Error loading tickets: {e}")
    
    def _save_tickets(self):
        """Save tickets to data directory."""
        planfile_path = self.data_dir / "planfile.yaml"
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            data = {
                "tickets": list(self._tickets.values()),
                "updated_at": datetime.now().isoformat()
            }
            with open(planfile_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving tickets: {e}")
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return available tools."""
        return [
            {
                "name": "planfile_create_ticket",
                "description": "Create a new ticket",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string", "enum": ["low", "normal", "high", "critical"]},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "planfile_list_tickets",
                "description": "List all tickets",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "priority": {"type": "string"}
                    }
                }
            },
            {
                "name": "planfile_update_ticket",
                "description": "Update ticket status or properties",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["open", "in_progress", "done", "skipped"]},
                        "resolution": {"type": "object"}
                    },
                    "required": ["ticket_id"]
                }
            },
            {
                "name": "planfile_create_tickets_bulk",
                "description": "Create multiple tickets at once",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tickets": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["tickets"]
                }
            },
            {
                "name": "planfile_sprint_status",
                "description": "Get sprint status overview",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "planfile_sync",
                "description": "Sync tickets with storage",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
    
    async def handle_create_ticket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ticket."""
        ticket_id = str(len(self._tickets) + 1)
        ticket = {
            "id": ticket_id,
            "title": params.get("title", "Untitled"),
            "description": params.get("description", ""),
            "priority": params.get("priority", "normal"),
            "status": "open",
            "tags": params.get("tags", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self._tickets[ticket_id] = ticket
        self._save_tickets()
        logger.info(f"Created ticket {ticket_id}: {ticket['title']}")
        return {"ticket_id": ticket_id, "status": "created", "ticket": ticket}
    
    async def handle_list_tickets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List tickets with optional filtering."""
        tickets = list(self._tickets.values())
        
        if params.get("status"):
            tickets = [t for t in tickets if t.get("status") == params["status"]]
        if params.get("priority"):
            tickets = [t for t in tickets if t.get("priority") == params["priority"]]
        
        return {"tickets": tickets, "count": len(tickets)}
    
    async def handle_update_ticket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a ticket."""
        ticket_id = params.get("ticket_id")
        if ticket_id not in self._tickets:
            return {"error": f"Ticket {ticket_id} not found"}
        
        ticket = self._tickets[ticket_id]
        
        if "status" in params:
            ticket["status"] = params["status"]
        if "resolution" in params:
            ticket["resolution"] = params["resolution"]
        
        ticket["updated_at"] = datetime.now().isoformat()
        self._save_tickets()
        logger.info(f"Updated ticket {ticket_id}")
        return {"ticket_id": ticket_id, "status": "updated", "ticket": ticket}
    
    async def handle_create_tickets_bulk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create multiple tickets."""
        created = []
        for ticket_data in params.get("tickets", []):
            result = await self.handle_create_ticket(ticket_data)
            if "ticket_id" in result:
                created.append(result["ticket_id"])
        return {"created": created, "count": len(created)}
    
    async def handle_sprint_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get sprint status."""
        tickets = list(self._tickets.values())
        by_status = {}
        for t in tickets:
            status = t.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total": len(tickets),
            "by_status": by_status,
            "completion_rate": by_status.get("done", 0) / len(tickets) if tickets else 0
        }
    
    async def handle_sync(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sync tickets to storage."""
        self._save_tickets()
        return {"synced": len(self._tickets), "status": "success"}
    
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
                        "serverInfo": {"name": self.name, "version": self.version}
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
                
                handlers = {
                    "planfile_create_ticket": self.handle_create_ticket,
                    "planfile_list_tickets": self.handle_list_tickets,
                    "planfile_update_ticket": self.handle_update_ticket,
                    "planfile_create_tickets_bulk": self.handle_create_tickets_bulk,
                    "planfile_sprint_status": self.handle_sprint_status,
                    "planfile_sync": self.handle_sync,
                }
                
                handler = handlers.get(tool_name)
                if handler:
                    result = await handler(tool_params)
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
            logger.error(f"Error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)}
            }
    
    async def run_stdio(self):
        """Run as MCP stdio server."""
        logger.info("Starting Planfile MCP stdio server")
        while True:
            try:
                header = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not header:
                    break
                header = header.strip()
                if not header.startswith("Content-Length:"):
                    continue
                content_length = int(header.split(":")[1].strip())
                await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                content = await asyncio.get_event_loop().run_in_executor(None, lambda: sys.stdin.read(content_length))
                request = json.loads(content)
                response = await self._handle_jsonrpc(request)
                response_json = json.dumps(response)
                message = f"Content-Length: {len(response_json)}\r\n\r\n{response_json}"
                sys.stdout.write(message)
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error: {e}")
    
    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI app for REST mode."""
        app = FastAPI(title="Planfile MCP Server", version=self.version)
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @app.get("/tickets")
        async def list_tickets():
            return await self.handle_list_tickets({})
        
        @app.post("/tickets")
        async def create_ticket(params: Dict[str, Any]):
            return await self.handle_create_ticket(params)
        
        @app.patch("/tickets/{ticket_id}")
        async def update_ticket(ticket_id: str, params: Dict[str, Any]):
            params["ticket_id"] = ticket_id
            return await self.handle_update_ticket(params)
        
        @app.post("/mcp")
        async def mcp_endpoint(request: Dict[str, Any]):
            return await self._handle_jsonrpc(request)
        
        return app
    
    async def run_rest(self):
        """Run as REST server."""
        logger.info(f"Starting REST server on port {self.port}")
        app = self.create_fastapi_app()
        config = uvicorn.Config(app, host="0.0.0.0", port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    
    async def run(self):
        if self.transport == "stdio":
            await self.run_stdio()
        else:
            await self.run_rest()


if __name__ == "__main__":
    server = PlanfileMCPServer()
    asyncio.run(server.run())
