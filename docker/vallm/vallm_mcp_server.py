#!/usr/bin/env python3
"""
Vallm MCP Server - Validation tool for Algitex
Multi-level validation with MCP support: static analysis, runtime tests, security
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
import uvicorn


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

mcp = FastMCP("vallm")

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
}


def _resolve_root(path: str | None) -> Path:
    raw = (path or ".").strip() or "."
    root = Path(raw).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {root}")
    return root


def _count_python_files(root: Path) -> int:
    count = 0
    for path in root.rglob("*.py"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        count += 1
    return count


def _empty_result(*, path: str, reason: str) -> Dict[str, Any]:
    return {
        "passed": False,
        "success": False,
        "score": 0.0,
        "files_analyzed": 0,
        "tests_run": 0,
        "empty": True,
        "path": path,
        "message": reason,
        "timestamp": datetime.now().isoformat(),
    }


def _path_error(exc: Exception) -> Dict[str, Any]:
    return {
        "passed": False,
        "success": False,
        "score": 0.0,
        "files_analyzed": 0,
        "tests_run": 0,
        "empty": True,
        "error": str(exc),
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def validate_static(path: str = ".") -> Dict[str, Any]:
    """Run static analysis with ruff/mypy when available."""
    try:
        root = _resolve_root(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return _path_error(exc)

    files = _count_python_files(root)
    if files == 0:
        return _empty_result(path=str(root), reason="No Python files found for static analysis")

    errors: List[Dict[str, str]] = []
    score = 10.0
    tools_run: List[str] = []

    try:
        result = subprocess.run(
            ["ruff", "check", str(root), "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        tools_run.append("ruff")
        if result.stdout.strip():
            ruff_issues = json.loads(result.stdout)
            errors.extend(
                [{"rule": f"ruff:{item.get('code')}", "message": item.get("message", "")}
                 for item in ruff_issues[:5]]
            )
            score -= len(ruff_issues) * 0.5
    except FileNotFoundError:
        logger.warning("ruff not installed")
    except Exception as exc:
        logger.warning("Ruff error: %s", exc)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(root), "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        tools_run.append("mypy")
        mypy_lines = [line for line in result.stdout.splitlines() if line.strip()]
        if mypy_lines:
            errors.extend([{"rule": "mypy", "message": line} for line in mypy_lines[:5]])
            score -= len(mypy_lines) * 0.3
    except Exception as exc:
        logger.warning("Mypy error: %s", exc)

    if not tools_run:
        return _empty_result(path=str(root), reason="No static analyzers available (ruff/mypy)")

    return {
        "passed": score >= 7.0 and not errors,
        "success": True,
        "score": max(0.0, score),
        "errors": errors[:10],
        "files_analyzed": files,
        "tools_run": tools_run,
        "path": str(root),
        "empty": False,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def validate_runtime(path: str = ".") -> Dict[str, Any]:
    """Run runtime tests with pytest."""
    try:
        root = _resolve_root(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return _path_error(exc)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(root), "-q", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "success": False, "score": 0.0, "tests_run": 0, "error": "Timeout"}
    except Exception as exc:
        return {"passed": False, "success": False, "score": 0.0, "tests_run": 0, "error": str(exc)}

    output = f"{result.stdout}\n{result.stderr}"
    tests_run = 0
    # pytest summary examples: "3 passed", "1 failed, 2 passed"
    import re

    match = re.search(r"(\d+)\s+passed", output)
    if match:
        tests_run += int(match.group(1))
    match = re.search(r"(\d+)\s+failed", output)
    if match:
        tests_run += int(match.group(1))
    match = re.search(r"no tests ran", output, re.I)
    no_tests = bool(match) or tests_run == 0

    if no_tests:
        return {
            "passed": False,
            "success": False,
            "score": 0.0,
            "tests_run": 0,
            "empty": True,
            "path": str(root),
            "message": "No pytest tests ran",
            "rc": result.returncode,
            "timestamp": datetime.now().isoformat(),
        }

    passed = result.returncode == 0
    return {
        "passed": passed,
        "success": True,
        "score": 10.0 if passed else 5.0,
        "tests_run": tests_run,
        "empty": False,
        "path": str(root),
        "rc": result.returncode,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def validate_security(path: str = ".") -> Dict[str, Any]:
    """Run security scan with bandit."""
    try:
        root = _resolve_root(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return _path_error(exc)

    files = _count_python_files(root)
    if files == 0:
        return _empty_result(path=str(root), reason="No Python files found for security scan")

    try:
        result = subprocess.run(
            ["bandit", "-r", str(root), "-f", "json"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        return {
            "passed": False,
            "success": False,
            "score": 0.0,
            "findings": [],
            "finding_count": 0,
            "files_analyzed": files,
            "message": "Bandit not available",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        return _path_error(exc)

    findings = []
    if result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            findings = data.get("results", [])[:5]
        except json.JSONDecodeError:
            pass

    severity_score = 10.0
    for item in findings:
        severity = item.get("issue_severity")
        if severity == "HIGH":
            severity_score -= 3.0
        elif severity == "MEDIUM":
            severity_score -= 1.5
        else:
            severity_score -= 0.5

    return {
        "passed": len(findings) == 0,
        "success": True,
        "score": max(0.0, severity_score),
        "findings": findings,
        "finding_count": len(findings),
        "files_analyzed": files,
        "empty": False,
        "path": str(root),
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def validate_all(path: str = ".") -> Dict[str, Any]:
    """Run static, runtime, and security validation without inventing coverage."""
    try:
        root = _resolve_root(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return _path_error(exc)

    static_result = validate_static(str(root))
    runtime_result = validate_runtime(str(root))
    security_result = validate_security(str(root))

    analyzed = max(
        int(static_result.get("files_analyzed") or 0),
        int(security_result.get("files_analyzed") or 0),
    )
    tests_run = int(runtime_result.get("tests_run") or 0)
    empty = analyzed == 0 and tests_run == 0

    scores = [
        float(static_result.get("score") or 0),
        float(runtime_result.get("score") or 0),
        float(security_result.get("score") or 0),
    ]
    score = sum(scores) / 3 if not empty else 0.0
    all_passed = (not empty) and all(
        [
            static_result.get("passed", False),
            runtime_result.get("passed", False),
            security_result.get("passed", False),
        ]
    )

    return {
        "passed": all_passed,
        "success": not empty,
        "empty": empty,
        "files_analyzed": analyzed,
        "tests_run": tests_run,
        "static_passed": static_result.get("passed"),
        "runtime_passed": runtime_result.get("passed"),
        "security_passed": security_result.get("passed"),
        "score": score,
        "path": str(root),
        "message": "No analyzable Python sources or tests found" if empty else None,
        "details": {
            "static": static_result,
            "runtime": runtime_result,
            "security": security_result,
        },
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def analyze_complexity(path: str = ".") -> Dict[str, Any]:
    """Analyze code complexity with radon; fail closed when nothing is analyzed."""
    try:
        root = _resolve_root(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return _path_error(exc)

    files = _count_python_files(root)
    if files == 0:
        return _empty_result(path=str(root), reason="No Python files found for complexity analysis")

    try:
        result = subprocess.run(
            ["radon", "cc", str(root), "-a", "-s", "-j"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        return {
            **_empty_result(path=str(root), reason="Radon not available"),
            "files_analyzed": 0,
        }
    except Exception as exc:
        return _path_error(exc)

    complexities: list[float] = []
    files_analyzed = 0
    if result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                files_analyzed = len(data)
                for entries in data.values():
                    if not isinstance(entries, list):
                        continue
                    for entry in entries:
                        if isinstance(entry, dict) and "complexity" in entry:
                            complexities.append(float(entry["complexity"]))
        except json.JSONDecodeError:
            # Fallback for non-JSON radon output.
            for line in result.stdout.splitlines():
                parts = line.split()
                for token in parts:
                    if token.replace(".", "", 1).isdigit():
                        complexities.append(float(token))
                        break

    if not complexities:
        return {
            "passed": False,
            "success": False,
            "average_cc": 0.0,
            "max_cc": 0.0,
            "files_analyzed": files_analyzed or 0,
            "empty": True,
            "path": str(root),
            "message": "Radon produced no complexity records",
            "timestamp": datetime.now().isoformat(),
        }

    avg_cc = sum(complexities) / len(complexities)
    return {
        "passed": True,
        "success": True,
        "average_cc": round(avg_cc, 2),
        "max_cc": max(complexities),
        "files_analyzed": files_analyzed or files,
        "empty": False,
        "path": str(root),
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def calculate_quality_score(path: str = ".") -> Dict[str, Any]:
    """Calculate overall quality score without inventing coverage."""
    validation = validate_all(path)
    complexity = analyze_complexity(path)

    if validation.get("empty") and complexity.get("empty"):
        return {
            "overall_score": 0.0,
            "validation_score": 0.0,
            "complexity_score": 0.0,
            "passed": False,
            "success": False,
            "empty": True,
            "files_analyzed": 0,
            "tests_run": 0,
            "message": validation.get("message") or complexity.get("message"),
            "details": {"validation": validation, "complexity": complexity},
            "timestamp": datetime.now().isoformat(),
        }

    complexity_score = max(0.0, 10.0 - float(complexity.get("average_cc") or 5))
    overall_score = float(validation.get("score") or 0) * 0.7 + complexity_score * 0.3
    return {
        "overall_score": round(overall_score, 2),
        "validation_score": validation.get("score", 0),
        "complexity_score": round(complexity_score, 2),
        "passed": bool(validation.get("passed")) and not validation.get("empty"),
        "success": True,
        "empty": False,
        "files_analyzed": validation.get("files_analyzed", 0),
        "tests_run": validation.get("tests_run", 0),
        "details": {"validation": validation, "complexity": complexity},
        "timestamp": datetime.now().isoformat(),
    }


def create_rest_api() -> FastAPI:
    """Create FastAPI application for REST mode."""
    app = FastAPI(title="Vallm MCP", version="0.3.0")

    @app.get("/health")
    async def health():
        return {"status": "healthy", "server": "vallm-mcp"}

    @app.post("/validate")
    async def validate(request: Dict[str, Any]):
        return validate_all(request.get("path", "."))

    @app.post("/validate/static")
    async def validate_static_endpoint(request: Dict[str, Any]):
        return validate_static(request.get("path", "."))

    @app.post("/validate/runtime")
    async def validate_runtime_endpoint(request: Dict[str, Any]):
        return validate_runtime(request.get("path", "."))

    @app.post("/validate/security")
    async def validate_security_endpoint(request: Dict[str, Any]):
        return validate_security(request.get("path", "."))

    @app.post("/score")
    async def score_endpoint(request: Dict[str, Any]):
        return calculate_quality_score(request.get("path", "."))

    return app


async def run_rest_server():
    """Run as REST API server."""
    port = int(os.getenv("PORT", "8080"))
    logger.info("Starting Vallm REST server on port %s", port)
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
        logger.error("Unknown transport: %s", transport)
        sys.exit(1)
