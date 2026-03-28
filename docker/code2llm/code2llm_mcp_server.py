#!/usr/bin/env python3
"""
Code2LLM MCP Server - Code analysis and LLM context generation
Supports: MCP stdio, MCP SSE, and REST API via FastMCP
"""

import os
import sys
import json
import ast
import logging
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn
import radon
from radon.complexity import cc_visit

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("code2llm")


def _analyze_python_file(py_file: Path, root: Path) -> Dict[str, Any]:
    """Analyze a single Python file and extract metrics."""
    try:
        content = py_file.read_text()
        tree = ast.parse(content)
        
        rel_path = str(py_file.relative_to(root))
        
        # Extract AST information
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(f"{rel_path}:{node.name}")
            elif isinstance(node, ast.ClassDef):
                classes.append(f"{rel_path}:{node.name}")
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
        
        # Complexity analysis
        complexity_scores = []
        try:
            cc_results = cc_visit(content)
            for result in cc_results:
                complexity_scores.append({
                    "file": rel_path,
                    "name": result.name,
                    "complexity": result.complexity
                })
        except:
            pass
        
        return {
            "file": rel_path,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "complexity_scores": complexity_scores
        }
    except Exception as e:
        logger.warning(f"Error analyzing {py_file}: {e}")
        return None


def _calculate_complexity_metrics(complexity_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate complexity metrics from scores."""
    if not complexity_scores:
        return {"avg_cc": 0, "max_cc": 0, "hotspots": []}
    
    avg_cc = sum(c["complexity"] for c in complexity_scores) / len(complexity_scores)
    max_cc = max(c["complexity"] for c in complexity_scores)
    
    # Hotspots (high complexity)
    hotspots = [
        f"{h['file']}: {h['name']}() CC={h['complexity']}"
        for h in complexity_scores
        if h["complexity"] > 10
    ][:10]
    
    return {
        "avg_cc": round(avg_cc, 2),
        "max_cc": max_cc,
        "hotspots": hotspots
    }


def _collect_project_metrics(root: Path) -> Dict[str, Any]:
    """Collect all metrics for the project."""
    files = []
    all_functions = []
    all_classes = []
    all_imports = []
    all_complexity_scores = []
    
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        result = _analyze_python_file(py_file, root)
        if result:
            files.append(result["file"])
            all_functions.extend(result["functions"])
            all_classes.extend(result["classes"])
            all_imports.extend(result["imports"])
            all_complexity_scores.extend(result["complexity_scores"])
    
    return {
        "files": files,
        "functions": all_functions,
        "classes": all_classes,
        "imports": all_imports,
        "complexity_scores": all_complexity_scores
    }


@mcp.tool()
def analyze_project(path: str = "/project") -> Dict[str, Any]:
    """
    Analyze a Python project and return metrics.
    
    Args:
        path: Path to the project directory to analyze
        
    Returns:
        Dictionary with project metrics including file count, complexity, dependencies
    """
    root = Path(path)
    
    # Collect all project metrics
    metrics = _collect_project_metrics(root)
    
    # Calculate complexity metrics
    complexity_metrics = _calculate_complexity_metrics(metrics["complexity_scores"])
    
    # Dependencies (unique, limited to 20)
    unique_imports = sorted(set(metrics["imports"]))[:20]
    
    return {
        "total_files": len(metrics["files"]),
        "total_functions": len(metrics["functions"]),
        "total_classes": len(metrics["classes"]),
        "average_cc": complexity_metrics["avg_cc"],
        "max_cc": complexity_metrics["max_cc"],
        "hotspots": complexity_metrics["hotspots"],
        "dependencies": unique_imports,
        "modules": metrics["files"][:20],
        "complexity_scores": metrics["complexity_scores"][:20],
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
def generate_toon(path: str = "/project") -> str:
    """
    Generate Toon notation report for a project.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Toon notation formatted report as string
    """
    analysis = analyze_project(path)
    
    lines = [
        "# Code2LLM Analysis Report",
        f"CC̄={analysis.get('average_cc', 0)}",
        f"Max: {analysis.get('max_cc', 0)}",
        "",
        f"Files: {analysis.get('total_files', 0)}",
        f"Functions: {analysis.get('total_functions', 0)}",
        f"Classes: {analysis.get('total_classes', 0)}",
        "",
        "Hotspots:",
    ]
    
    for hotspot in analysis.get("hotspots", []):
        lines.append(f"  - {hotspot}")
    
    if not analysis.get("hotspots"):
        lines.append("  - None")
    
    lines.extend(["", "Dependencies:"])
    for dep in analysis.get("dependencies", [])[:10]:
        lines.append(f"  - {dep}")
    
    return "\n".join(lines)


@mcp.tool()
def generate_readme(path: str = "/project") -> Dict[str, str]:
    """
    Generate README.md content from code analysis.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Dictionary with content and filename
    """
    analysis = analyze_project(path)
    
    content = f"""# Project Analysis

Generated by Code2LLM

## Metrics

- **Files**: {analysis.get('total_files', 0)}
- **Functions**: {analysis.get('total_functions', 0)}
- **Classes**: {analysis.get('total_classes', 0)}
- **Average Complexity**: {analysis.get('average_cc', 0)}
- **Max Complexity**: {analysis.get('max_cc', 0)}

## Hotspots (High Complexity)

{chr(10).join(['- ' + h for h in analysis.get('hotspots', [])[:5]] or ['- None'])}

## Dependencies

{chr(10).join(['- ' + d for d in analysis.get('dependencies', [])[:10]])}

---
*Generated: {datetime.now().isoformat()}*
"""
    
    return {
        "content": content,
        "filename": "README.md"
    }


@mcp.tool()
def evolution_export(path: str = "/project") -> Dict[str, Any]:
    """
    Export evolution report with modules, dependencies, and hotspots.
    
    Args:
        path: Path to the project directory
        
    Returns:
        Dictionary with evolution data
    """
    analysis = analyze_project(path)
    
    return {
        "modules": analysis.get("modules", []),
        "dependencies": analysis.get("dependencies", []),
        "hotspots": analysis.get("hotspots", []),
        "timestamp": datetime.now().isoformat()
    }


def create_rest_api() -> FastAPI:
    """Create FastAPI application for REST mode."""
    app = FastAPI(title="Code2LLM MCP", version="0.2.0")
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "server": "code2llm-mcp"}
    
    @app.post("/analyze")
    async def analyze(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return analyze_project(path)
    
    @app.post("/toon-export")
    async def toon_export(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return {"toon": generate_toon(path), "format": "yaml"}
    
    @app.post("/evolution-export")
    async def evolution_export_endpoint(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return evolution_export(path)
    
    @app.post("/generate-readme")
    async def generate_readme_endpoint(request: Dict[str, Any]):
        path = request.get("path", "/project")
        return generate_readme(path)
    
    return app


async def run_rest_server():
    """Run as REST API server."""
    port = int(os.getenv("PORT", "8081"))
    logger.info(f"Starting Code2LLM REST server on port {port}")
    app = create_rest_api()
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    transport = os.getenv("TRANSPORT", "stdio")
    
    if transport == "stdio":
        # Run as MCP stdio server
        logger.info("Starting Code2LLM MCP stdio server")
        mcp.run(transport="stdio")
    elif transport in ("rest", "sse", "http"):
        # Run as REST API server
        import asyncio
        asyncio.run(run_rest_server())
    else:
        logger.error(f"Unknown transport: {transport}")
        sys.exit(1)
