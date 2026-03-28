#!/usr/bin/env python3
"""
Planfile MCP Server - Ticket management hub with FastMCP support
Multi-protocol: MCP stdio, MCP SSE, REST API
"""

import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import yaml
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("planfile-mcp")

# Data storage
DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
_tickets: Dict[str, Dict] = {}


def _load_tickets():
    """Load tickets from data directory."""
    global _tickets
    planfile_path = DATA_DIR / "planfile.yaml"
    if planfile_path.exists():
        try:
            with open(planfile_path) as f:
                data = yaml.safe_load(f)
                if data and "tickets" in data:
                    for ticket in data["tickets"]:
                        _tickets[ticket.get("id", str(len(_tickets)))] = ticket
        except Exception as e:
            logger.error(f"Error loading tickets: {e}")


def _save_tickets():
    """Save tickets to data directory."""
    planfile_path = DATA_DIR / "planfile.yaml"
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "tickets": list(_tickets.values()),
            "updated_at": datetime.now().isoformat()
        }
        with open(planfile_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    except Exception as e:
        logger.error(f"Error saving tickets: {e}")


@mcp.tool()
def planfile_create_ticket(
    title: str,
    description: str = "",
    priority: str = "normal",
    tags: List[str] = None
) -> Dict[str, Any]:
    """
    Create a new ticket.
    
    Args:
        title: Ticket title
        description: Ticket description
        priority: Ticket priority (low, normal, high, critical)
        tags: List of tags
        
    Returns:
        Dictionary with created ticket info
    """
    _load_tickets()
    ticket_id = str(len(_tickets) + 1)
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "open",
        "tags": tags or [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    _tickets[ticket_id] = ticket
    _save_tickets()
    logger.info(f"Created ticket {ticket_id}: {ticket['title']}")
    return {"ticket_id": ticket_id, "status": "created", "ticket": ticket}


@mcp.tool()
def planfile_list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all tickets with optional filtering.
    
    Args:
        status: Filter by status (open, in_progress, done, skipped)
        priority: Filter by priority (low, normal, high, critical)
        
    Returns:
        Dictionary with tickets list and count
    """
    _load_tickets()
    tickets = list(_tickets.values())
    
    if status:
        tickets = [t for t in tickets if t.get("status") == status]
    if priority:
        tickets = [t for t in tickets if t.get("priority") == priority]
    
    return {"tickets": tickets, "count": len(tickets)}


@mcp.tool()
def planfile_update_ticket(
    ticket_id: str,
    status: Optional[str] = None,
    resolution: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Update ticket status or properties.
    
    Args:
        ticket_id: ID of the ticket to update
        status: New status (open, in_progress, done, skipped)
        resolution: Resolution details
        
    Returns:
        Dictionary with updated ticket info
    """
    _load_tickets()
    if ticket_id not in _tickets:
        return {"error": f"Ticket {ticket_id} not found"}
    
    ticket = _tickets[ticket_id]
    
    if status:
        ticket["status"] = status
    if resolution:
        ticket["resolution"] = resolution
    
    ticket["updated_at"] = datetime.now().isoformat()
    _save_tickets()
    logger.info(f"Updated ticket {ticket_id}")
    return {"ticket_id": ticket_id, "status": "updated", "ticket": ticket}


@mcp.tool()
def planfile_create_tickets_bulk(tickets: List[Dict]) -> Dict[str, Any]:
    """
    Create multiple tickets at once.
    
    Args:
        tickets: List of ticket data dictionaries
        
    Returns:
        Dictionary with created ticket IDs
    """
    created = []
    for ticket_data in tickets:
        result = planfile_create_ticket(
            title=ticket_data.get("title", "Untitled"),
            description=ticket_data.get("description", ""),
            priority=ticket_data.get("priority", "normal"),
            tags=ticket_data.get("tags", [])
        )
        if "ticket_id" in result:
            created.append(result["ticket_id"])
    return {"created": created, "count": len(created)}


@mcp.tool()
def planfile_sprint_status() -> Dict[str, Any]:
    """
    Get sprint status overview.
    
    Returns:
        Dictionary with sprint statistics
    """
    _load_tickets()
    tickets = list(_tickets.values())
    by_status = {}
    for t in tickets:
        status = t.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    
    return {
        "total": len(tickets),
        "by_status": by_status,
        "completion_rate": by_status.get("done", 0) / len(tickets) if tickets else 0
    }


@mcp.tool()
def planfile_sync() -> Dict[str, Any]:
    """
    Sync tickets with storage.
    
    Returns:
        Dictionary with sync status
    """
    _save_tickets()
    return {"synced": len(_tickets), "status": "success"}


def create_rest_api() -> FastAPI:
    """Create FastAPI application for REST mode."""
    app = FastAPI(title="Planfile MCP", version="0.2.0")
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "server": "planfile-mcp"}
    
    @app.get("/tickets")
    async def list_tickets():
        return planfile_list_tickets()
    
    @app.post("/tickets")
    async def create_ticket(request: Dict[str, Any]):
        return planfile_create_ticket(
            title=request.get("title", "Untitled"),
            description=request.get("description", ""),
            priority=request.get("priority", "normal"),
            tags=request.get("tags", [])
        )
    
    @app.patch("/tickets/{ticket_id}")
    async def update_ticket(ticket_id: str, request: Dict[str, Any]):
        return planfile_update_ticket(
            ticket_id=ticket_id,
            status=request.get("status"),
            resolution=request.get("resolution")
        )
    
    @app.get("/sprint")
    async def sprint():
        return planfile_sprint_status()
    
    return app


async def run_rest_server():
    """Run as REST API server."""
    port = int(os.getenv("PORT", "8201"))
    logger.info(f"Starting Planfile REST server on port {port}")
    app = create_rest_api()
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    transport = os.getenv("TRANSPORT", "stdio")
    
    if transport == "stdio":
        logger.info("Starting Planfile MCP stdio server")
        mcp.run(transport="stdio")
    elif transport in ("rest", "sse", "http"):
        import asyncio
        asyncio.run(run_rest_server())
    else:
        logger.error(f"Unknown transport: {transport}")
        sys.exit(1)
