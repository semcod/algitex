#!/usr/bin/env python3
"""
Code2LLM MCP Server - Code analysis and LLM context generation
Supports: MCP stdio, MCP SSE, and REST API via FastMCP
"""

from __future__ import annotations

import ast
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcp_security import resolve_project_path  # noqa: E402

try:
    from radon.complexity import cc_visit
except ImportError:  # pragma: no cover - optional dependency
    cc_visit = None


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

mcp = FastMCP("code2llm")

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    "vendor",
    ".intent",
}

SOURCE_SUFFIXES = {
    ".py",
    ".php",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
}


def _resolve_root(path: str | None) -> Path:
    return resolve_project_path(path)


def _iter_source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() in SOURCE_SUFFIXES:
            files.append(path)
    return sorted(files)


def _analyze_python_file(py_file: Path, root: Path) -> Optional[Dict[str, Any]]:
    """Analyze a single Python file and extract metrics."""
    try:
        content = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
        rel_path = str(py_file.relative_to(root))

        functions: list[str] = []
        classes: list[str] = []
        imports: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(f"{rel_path}:{node.name}")
            elif isinstance(node, ast.ClassDef):
                classes.append(f"{rel_path}:{node.name}")
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)

        complexity_scores: list[dict[str, Any]] = []
        if cc_visit is not None:
            try:
                for result in cc_visit(content):
                    complexity_scores.append(
                        {
                            "file": rel_path,
                            "name": result.name,
                            "complexity": result.complexity,
                        }
                    )
            except Exception:
                pass

        return {
            "file": rel_path,
            "language": "python",
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "complexity_scores": complexity_scores,
        }
    except Exception as exc:
        logger.warning("Error analyzing %s: %s", py_file, exc)
        return None


def _analyze_text_source(path: Path, root: Path) -> Dict[str, Any]:
    """Lightweight metrics for non-Python sources (PHP/TS/JS)."""
    rel_path = str(path.relative_to(root))
    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    function_hits = 0
    class_hits = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("function ", "def ", "export function ", "async function ")):
            function_hits += 1
        if stripped.startswith(("class ", "export class ", "abstract class ")):
            class_hits += 1
        if " function(" in stripped or stripped.startswith("public function "):
            function_hits += 1
    return {
        "file": rel_path,
        "language": path.suffix.lower().lstrip(".") or "unknown",
        "functions": [f"{rel_path}:fn{i}" for i in range(function_hits)],
        "classes": [f"{rel_path}:cls{i}" for i in range(class_hits)],
        "imports": [],
        "complexity_scores": [],
        "line_count": len(lines),
    }


def _calculate_complexity_metrics(complexity_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not complexity_scores:
        return {"avg_cc": 0, "max_cc": 0, "hotspots": []}

    avg_cc = sum(item["complexity"] for item in complexity_scores) / len(complexity_scores)
    max_cc = max(item["complexity"] for item in complexity_scores)
    hotspots = [
        f"{item['file']}: {item['name']}() CC={item['complexity']}"
        for item in complexity_scores
        if item["complexity"] > 10
    ][:10]
    return {"avg_cc": round(avg_cc, 2), "max_cc": max_cc, "hotspots": hotspots}


def _collect_project_metrics(root: Path) -> Dict[str, Any]:
    files: list[str] = []
    languages: dict[str, int] = {}
    all_functions: list[str] = []
    all_classes: list[str] = []
    all_imports: list[str] = []
    all_complexity_scores: list[dict[str, Any]] = []

    for source in _iter_source_files(root):
        if source.suffix.lower() == ".py":
            result = _analyze_python_file(source, root)
        else:
            result = _analyze_text_source(source, root)
        if not result:
            continue
        files.append(result["file"])
        languages[result["language"]] = languages.get(result["language"], 0) + 1
        all_functions.extend(result["functions"])
        all_classes.extend(result["classes"])
        all_imports.extend(result["imports"])
        all_complexity_scores.extend(result["complexity_scores"])

    return {
        "files": files,
        "languages": languages,
        "functions": all_functions,
        "classes": all_classes,
        "imports": all_imports,
        "complexity_scores": all_complexity_scores,
    }


def _analyze_with_package(root: Path) -> Optional[Dict[str, Any]]:
    """Optional compact metrics from installed code2llm (never return raw to_dict)."""
    try:
        from code2llm.core.analyzer import ProjectAnalyzer  # type: ignore
    except Exception:
        return None
    try:
        analyzer = ProjectAnalyzer(project_path=root)
        result = analyzer.analyze_project(str(root))
        files = list(getattr(result, "files", None) or [])
        if not files and hasattr(result, "to_dict"):
            # Some builds only expose dict form — keep it compact.
            data = result.to_dict()
            total = int(data.get("total_files") or data.get("file_count") or 0)
            if total <= 0:
                return None
            return {
                "total_files": total,
                "total_functions": int(data.get("total_functions") or 0),
                "total_classes": int(data.get("total_classes") or 0),
                "average_cc": float(data.get("average_cc") or 0),
                "max_cc": float(data.get("max_cc") or 0),
                "hotspots": list(data.get("hotspots") or [])[:20],
                "dependencies": list(data.get("dependencies") or [])[:20],
                "languages": {"python": total},
                "source": "code2llm-package",
            }
        if not files:
            return None
        complexities = []
        functions = 0
        classes = 0
        for item in files:
            functions += len(getattr(item, "functions", None) or [])
            classes += len(getattr(item, "classes", None) or [])
            for fn in getattr(item, "functions", None) or []:
                cc = getattr(fn, "complexity", None)
                if cc is not None:
                    complexities.append(float(cc))
        avg = round(sum(complexities) / len(complexities), 2) if complexities else 0.0
        return {
            "total_files": len(files),
            "total_functions": functions,
            "total_classes": classes,
            "average_cc": avg,
            "max_cc": max(complexities) if complexities else 0.0,
            "hotspots": [],
            "dependencies": [],
            "languages": {"python": len(files)},
            "source": "code2llm-package",
        }
    except Exception as exc:
        logger.warning("code2llm package analyze failed: %s", exc)
    return None


@mcp.tool()
def analyze_project(path: str = ".") -> Dict[str, Any]:
    """
    Analyze a project (Python/PHP/TS/JS) and return metrics.

    Args:
        path: Path to the project directory to analyze

    Returns:
        Dictionary with project metrics including file count, complexity, dependencies
    """
    try:
        root = _resolve_root(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return {
            "success": False,
            "error": str(exc),
            "total_files": 0,
            "timestamp": datetime.now().isoformat(),
        }

    # Prefer local multi-language walk (PHP/TS/JS/Py). Package path is Python-centric.
    metrics = _collect_project_metrics(root)
    complexity_metrics = _calculate_complexity_metrics(metrics["complexity_scores"])
    unique_imports = sorted(set(metrics["imports"]))[:20]
    total_files = len(metrics["files"])

    if total_files == 0:
        packaged = _analyze_with_package(root)
        if packaged and int(packaged.get("total_files") or 0) > 0:
            packaged.setdefault("success", True)
            packaged.setdefault("empty", False)
            packaged.setdefault("path", str(root))
            packaged.setdefault("timestamp", datetime.now().isoformat())
            return packaged

    return {
        "success": total_files > 0,
        "path": str(root),
        "total_files": total_files,
        "total_functions": len(metrics["functions"]),
        "total_classes": len(metrics["classes"]),
        "languages": metrics["languages"],
        "average_cc": complexity_metrics["avg_cc"],
        "max_cc": complexity_metrics["max_cc"],
        "hotspots": complexity_metrics["hotspots"],
        "dependencies": unique_imports,
        "modules": metrics["files"][:50],
        "complexity_scores": metrics["complexity_scores"][:20],
        "empty": total_files == 0,
        "message": None if total_files else "No supported source files found",
        "source": "local-walk",
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def generate_toon(path: str = ".") -> str:
    """Generate Toon notation report for a project."""
    analysis = analyze_project(path)
    if not analysis.get("success", True) and analysis.get("error"):
        return f"# Code2LLM Analysis Report\n\nERROR: {analysis['error']}\n"

    lines = [
        "# Code2LLM Analysis Report",
        f"Path: {analysis.get('path', path)}",
        f"CC̄={analysis.get('average_cc', 0)}",
        f"Max: {analysis.get('max_cc', 0)}",
        "",
        f"Files: {analysis.get('total_files', 0)}",
        f"Functions: {analysis.get('total_functions', 0)}",
        f"Classes: {analysis.get('total_classes', 0)}",
        "",
        "Languages:",
    ]
    languages = analysis.get("languages") or {}
    if languages:
        for language, count in sorted(languages.items()):
            lines.append(f"  - {language}: {count}")
    else:
        lines.append("  - None")

    lines.extend(["", "Hotspots:"])
    for hotspot in analysis.get("hotspots", []) or []:
        lines.append(f"  - {hotspot}")
    if not analysis.get("hotspots"):
        lines.append("  - None")

    lines.extend(["", "Dependencies:"])
    for dep in analysis.get("dependencies", [])[:10]:
        lines.append(f"  - {dep}")
    if not analysis.get("dependencies"):
        lines.append("  - None")

    return "\n".join(lines)


@mcp.tool()
def generate_readme(path: str = ".") -> Dict[str, str]:
    """Generate README.md content from code analysis."""
    analysis = analyze_project(path)
    content = f"""# Project Analysis

Generated by Code2LLM

## Metrics

- **Path**: {analysis.get('path', path)}
- **Files**: {analysis.get('total_files', 0)}
- **Functions**: {analysis.get('total_functions', 0)}
- **Classes**: {analysis.get('total_classes', 0)}
- **Average Complexity**: {analysis.get('average_cc', 0)}
- **Max Complexity**: {analysis.get('max_cc', 0)}

## Hotspots (High Complexity)

{chr(10).join(['- ' + h for h in analysis.get('hotspots', [])[:5]] or ['- None'])}

## Dependencies

{chr(10).join(['- ' + d for d in analysis.get('dependencies', [])[:10]] or ['- None'])}

---
*Generated: {datetime.now().isoformat()}*
"""
    return {"content": content, "filename": "README.md"}


@mcp.tool()
def evolution_export(path: str = ".") -> Dict[str, Any]:
    """Export evolution report with modules, dependencies, and hotspots."""
    analysis = analyze_project(path)
    return {
        "success": analysis.get("success", analysis.get("total_files", 0) > 0),
        "modules": analysis.get("modules", []),
        "dependencies": analysis.get("dependencies", []),
        "hotspots": analysis.get("hotspots", []),
        "metrics": {
            "files": analysis.get("total_files", 0),
            "functions": analysis.get("total_functions", 0),
            "classes": analysis.get("total_classes", 0),
            "average_cc": analysis.get("average_cc", 0),
            "max_cc": analysis.get("max_cc", 0),
            "languages": analysis.get("languages", {}),
        },
        "timestamp": datetime.now().isoformat(),
    }


def create_rest_api() -> FastAPI:
    """Create FastAPI application for REST mode."""
    app = FastAPI(title="Code2LLM MCP", version="0.3.0")

    @app.get("/health")
    async def health():
        return {"status": "healthy", "server": "code2llm-mcp"}

    @app.post("/analyze")
    async def analyze(request: Dict[str, Any]):
        return analyze_project(request.get("path", "."))

    return app


async def run_rest_server():
    """Run as REST API server."""
    port = int(os.getenv("PORT", "8080"))
    logger.info("Starting Code2LLM REST server on port %s", port)
    app = create_rest_api()
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    transport = os.getenv("TRANSPORT", "stdio")
    if transport == "stdio":
        logger.info("Starting Code2LLM MCP stdio server")
        mcp.run(transport="stdio")
    elif transport in ("rest", "sse", "http"):
        import asyncio

        asyncio.run(run_rest_server())
    else:
        logger.error("Unknown transport: %s", transport)
        sys.exit(1)
