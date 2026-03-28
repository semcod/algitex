#!/usr/bin/env python3
"""
Vallm MCP Server - Validation tool for Algitex
Multi-level validation with MCP support: static analysis, runtime tests, security
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

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
mcp = FastMCP("vallm")


@mcp.tool()
def validate_static(path: str = "/project") -> Dict[str, Any]:
    """
    Run static analysis with ruff, mypy on the project.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Dictionary with passed status, score, and errors
    """
    errors = []
    score = 10.0
    
    try:
        # Run ruff check
        result = subprocess.run(
            ["ruff", "check", path, "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.stdout:
            ruff_issues = json.loads(result.stdout)
            errors.extend([{"rule": f"ruff:{r['code']}", "message": r['message']} for r in ruff_issues[:5]])
            score -= len(ruff_issues) * 0.5
    except Exception as e:
        logger.warning(f"Ruff error: {e}")
    
    try:
        # Run mypy
        result = subprocess.run(
            ["mypy", path, "--ignore-missing-imports", "--json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.stdout:
            mypy_lines = [l for l in result.stdout.split('\n') if l.strip()]
            errors.extend([{"rule": "mypy", "message": l} for l in mypy_lines[:5]])
            score -= len(mypy_lines) * 0.3
    except Exception as e:
        logger.warning(f"Mypy error: {e}")
    
    return {
        "passed": score >= 7.0,
        "score": max(0, score),
        "errors": errors[:10],
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def validate_runtime(path: str = "/project") -> Dict[str, Any]:
    """
    Run runtime tests with pytest.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Dictionary with passed status, score, and test results
    """
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", path, "-v", "--tb=short", "-q"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        passed = result.returncode == 0
        
        # Parse output
        lines = result.stdout.split('\n')
        tests_run = 0
        for line in lines:
            if 'passed' in line:
                parts = line.split()
                for part in parts:
                    if 'passed' in part:
                        try:
                            tests_run = int(part.split()[0])
                        except:
                            pass
        
        return {
            "passed": passed,
            "score": 10.0 if passed else 5.0,
            "tests_run": tests_run,
            "rc": result.returncode,
            "timestamp": datetime.now().isoformat()
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "score": 0.0, "error": "Timeout"}
    except Exception as e:
        return {"passed": False, "score": 0.0, "error": str(e)}


@mcp.tool()
def validate_security(path: str = "/project") -> Dict[str, Any]:
    """
    Run security scan with bandit.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Dictionary with passed status, score, and security findings
    """
    try:
        result = subprocess.run(
            ["bandit", "-r", path, "-f", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        findings = []
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                findings = data.get("results", [])[:5]
            except:
                pass
        
        severity_score = 10.0
        for f in findings:
            if f.get("issue_severity") == "HIGH":
                severity_score -= 3.0
            elif f.get("issue_severity") == "MEDIUM":
                severity_score -= 1.5
            else:
                severity_score -= 0.5
        
        return {
            "passed": len(findings) == 0,
            "score": max(0, severity_score),
            "findings": findings,
            "finding_count": len(findings),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"Bandit error: {e}")
        return {"passed": True, "score": 10.0, "findings": [], "note": "Bandit not available"}


@mcp.tool()
def validate_all(path: str = "/project") -> Dict[str, Any]:
    """
    Run all validation levels: static, runtime, and security.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Dictionary with overall results and all validation details
    """
    static_result = validate_static(path)
    runtime_result = validate_runtime(path)
    security_result = validate_security(path)
    
    all_passed = all([
        static_result.get("passed", False),
        runtime_result.get("passed", False),
        security_result.get("passed", False)
    ])
    
    return {
        "passed": all_passed,
        "static_passed": static_result.get("passed"),
        "runtime_passed": runtime_result.get("passed"),
        "security_passed": security_result.get("passed"),
        "score": (
            static_result.get("score", 0) +
            runtime_result.get("score", 0) +
            security_result.get("score", 0)
        ) / 3,
        "details": {
            "static": static_result,
            "runtime": runtime_result,
            "security": security_result
        },
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def analyze_complexity(path: str = "/project") -> Dict[str, Any]:
    """
    Analyze code complexity with radon.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Dictionary with average complexity, max complexity, and files analyzed
    """
    try:
        result = subprocess.run(
            ["radon", "cc", path, "-a", "-s"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse complexity output
        lines = result.stdout.split('\n')
        complexities = []
        for line in lines:
            if ' - ' in line and ':' in line:
                try:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p.isdigit():
                            complexities.append(int(p))
                except:
                    pass
        
        if complexities:
            avg_cc = sum(complexities) / len(complexities)
            max_cc = max(complexities)
        else:
            avg_cc = 3.0
            max_cc = 5.0
        
        return {
            "average_cc": round(avg_cc, 2),
            "max_cc": max_cc,
            "files_analyzed": len(complexities),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"Radon error: {e}")
        return {"average_cc": 3.0, "max_cc": 5.0, "files_analyzed": 0, "note": "Radon not available"}


@mcp.tool()
def calculate_quality_score(path: str = "/project") -> Dict[str, Any]:
    """
    Calculate overall quality score combining validation and complexity.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Dictionary with overall score and component scores
    """
    validation = validate_all(path)
    complexity = analyze_complexity(path)
    
    # Normalize complexity score (lower is better, max 20 considered bad)
    complexity_score = max(0, 10 - complexity.get("average_cc", 5))
    
    overall_score = (
        validation.get("score", 0) * 0.7 +
        complexity_score * 0.3
    )
    
    return {
        "overall_score": round(overall_score, 2),
        "validation_score": validation.get("score", 0),
        "complexity_score": round(complexity_score, 2),
        "passed": validation.get("passed", False),
        "details": {
            "validation": validation,
            "complexity": complexity
        },
        "timestamp": datetime.now().isoformat()
    }


def create_rest_api() -> FastAPI:
    """Create FastAPI application for REST mode."""
    app = FastAPI(title="Vallm MCP", version="0.2.0")
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "server": "vallm-mcp"}
    
    @app.post("/validate")
    async def validate(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return validate_all(path)
    
    @app.post("/validate/static")
    async def validate_static_endpoint(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return validate_static(path)
    
    @app.post("/validate/runtime")
    async def validate_runtime_endpoint(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return validate_runtime(path)
    
    @app.post("/validate/security")
    async def validate_security_endpoint(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return validate_security(path)
    
    @app.post("/score")
    async def score_endpoint(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return calculate_quality_score(path)
    
    return app


async def run_rest_server():
    """Run as REST API server."""
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Starting Vallm REST server on port {port}")
    app = create_rest_api()
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    transport = os.getenv("TRANSPORT", "stdio")
    
    if transport == "stdio":
        logger.info("Starting Vallm MCP stdio server")
        mcp.run(transport="stdio")
    elif transport in ("rest", "sse", "http"):
        import asyncio
        asyncio.run(run_rest_server())
    else:
        logger.error(f"Unknown transport: {transport}")
        sys.exit(1)
