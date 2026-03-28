#!/usr/bin/env python3
"""
Code2LLM Server - Code analysis and LLM context generation
Generates Toon notation and LLM-friendly code representation
"""

import os
import sys
import json
import ast
import logging
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

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


class Code2LLMServer:
    """Code analysis server for LLM context generation."""
    
    def __init__(self):
        self.port = int(os.getenv("PORT", "8081"))
        self.name = "code2llm"
        self.version = "0.1.0"
    
    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(title="Code2LLM", version=self.version)
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @app.post("/analyze")
        async def analyze(request: Dict[str, Any]):
            """Analyze code and generate Toon report."""
            path = request.get("path", "/project")
            
            analysis = self._analyze_project(path)
            
            return {
                "toon": self._generate_toon(analysis),
                "metrics": analysis,
                "timestamp": datetime.now().isoformat()
            }
        
        @app.post("/toon-export")
        async def toon_export(request: Dict[str, Any]):
            """Export Toon notation."""
            path = request.get("path", "/project")
            
            analysis = self._analyze_project(path)
            toon = self._generate_toon(analysis)
            
            return {
                "toon": toon,
                "format": "yaml"
            }
        
        @app.post("/evolution-export")
        async def evolution_export(request: Dict[str, Any]):
            """Export evolution report."""
            path = request.get("path", "/project")
            
            analysis = self._analyze_project(path)
            
            return {
                "modules": analysis.get("modules", []),
                "dependencies": analysis.get("dependencies", []),
                "hotspots": analysis.get("hotspots", [])
            }
        
        @app.post("/generate-readme")
        async def generate_readme(request: Dict[str, Any]):
            """Generate README.md from code analysis."""
            path = request.get("path", "/project")
            
            analysis = self._analyze_project(path)
            readme = self._generate_readme(analysis)
            
            return {
                "content": readme,
                "filename": "README.md"
            }
        
        return app
    
    def _analyze_python_file(self, py_file: Path, root: Path) -> Dict[str, Any]:
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

    def _calculate_complexity_metrics(self, complexity_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
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

    def _collect_project_metrics(self, root: Path) -> Dict[str, Any]:
        """Collect all metrics for the project."""
        files = []
        all_functions = []
        all_classes = []
        all_imports = []
        all_complexity_scores = []
        
        for py_file in root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            result = self._analyze_python_file(py_file, root)
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

    def _analyze_project(self, path: str) -> Dict[str, Any]:
        """Analyze Python project."""
        root = Path(path)
        
        # Collect all project metrics
        metrics = self._collect_project_metrics(root)
        
        # Calculate complexity metrics
        complexity_metrics = self._calculate_complexity_metrics(metrics["complexity_scores"])
        
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
            "complexity_scores": metrics["complexity_scores"][:20]
        }
    
    def _generate_toon(self, analysis: Dict[str, Any]) -> str:
        """Generate Toon notation."""
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
    
    def _generate_readme(self, analysis: Dict[str, Any]) -> str:
        """Generate README from analysis."""
        return f"""# Project Analysis

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
    
    async def run(self):
        """Run the server."""
        logger.info(f"Starting Code2LLM on port {self.port}")
        app = self.create_fastapi_app()
        config = uvicorn.Config(app, host="0.0.0.0", port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    server = Code2LLMServer()
    import asyncio
    asyncio.run(server.run())
