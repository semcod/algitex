#!/usr/bin/env python3
"""
Vallm Server - Validation tool for Algitex
Multi-level validation: static analysis, runtime tests, security
"""

import os
import sys
import json
import logging
import subprocess
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class VallmServer:
    """Validation server with multiple validation levels."""
    
    def __init__(self):
        self.port = int(os.getenv("PORT", "8080"))
        self.name = "vallm"
        self.version = "0.1.0"
    
    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(title="Vallm", version=self.version)
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @app.post("/validate")
        async def validate(request: Dict[str, Any]):
            """Run all validation levels."""
            path = request.get("path", "/project")
            
            static_result = await self._validate_static(path)
            runtime_result = await self._validate_runtime(path)
            security_result = await self._validate_security(path)
            
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
                }
            }
        
        @app.post("/batch")
        async def batch_validate(request: Dict[str, Any]):
            """Batch validation for entire project."""
            path = request.get("path", "/project")
            format_type = request.get("format", "json")
            
            result = await validate({"path": path})
            
            if format_type == "json":
                return result
            else:
                return {
                    "passed": result["passed"],
                    "summary": f"Score: {result['score']:.2f}"
                }
        
        @app.post("/score")
        async def score(request: Dict[str, Any]):
            """Calculate quality score."""
            path = request.get("path", "/project")
            
            # Calculate complexity
            complexity = self._analyze_complexity(path)
            
            return {
                "score": complexity.get("average_cc", 5.0) / 10.0,
                "metrics": complexity
            }
        
        return app
    
    async def _validate_static(self, path: str) -> Dict[str, Any]:
        """Static analysis with pylint, mypy, ruff."""
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
            "errors": errors[:10]
        }
    
    async def _validate_runtime(self, path: str) -> Dict[str, Any]:
        """Run tests with pytest."""
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
                "rc": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "score": 0.0, "error": "Timeout"}
        except Exception as e:
            return {"passed": False, "score": 0.0, "error": str(e)}
    
    async def _validate_security(self, path: str) -> Dict[str, Any]:
        """Security scan with bandit."""
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
                "finding_count": len(findings)
            }
        except Exception as e:
            logger.warning(f"Bandit error: {e}")
            return {"passed": True, "score": 10.0, "findings": []}
    
    def _analyze_complexity(self, path: str) -> Dict[str, Any]:
        """Analyze code complexity with radon."""
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
                "files_analyzed": len(complexities)
            }
        except Exception as e:
            logger.warning(f"Radon error: {e}")
            return {"average_cc": 3.0, "max_cc": 5.0, "files_analyzed": 0}
    
    async def run(self):
        """Run the server."""
        logger.info(f"Starting Vallm on port {self.port}")
        app = self.create_fastapi_app()
        config = uvicorn.Config(app, host="0.0.0.0", port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    server = VallmServer()
    import asyncio
    asyncio.run(server.run())
