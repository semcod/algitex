"""Region extraction — AST-based extraction of lockable code regions."""
import ast
from pathlib import Path
from typing import Dict, List

from algitex.tools.parallel.models import CodeRegion, RegionType


class RegionExtractor:
    """Extract lockable AST regions from Python files using map.toon."""

    def __init__(self, project_path: str):
        self.root = Path(project_path)
        self._signature_cache: Dict[str, str] = {}

    def extract_all(self) -> List[CodeRegion]:
        """Parse map.toon to get all function/class regions with line ranges."""
        regions = []

        # Try to read from map.toon if it exists
        toon_path = self.root / "map.toon"
        if toon_path.exists():
            regions.extend(self._extract_from_toon(toon_path))

        # Always extract from AST for accuracy
        for py_file in self.root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            regions.extend(self._extract_from_file(py_file))

        # Detect shadow conflicts (shared imports/constants)
        self._detect_shadow_conflicts(regions)

        return regions

    def _should_skip_file(self, path: Path) -> bool:
        """Skip generated, test, or vendor files."""
        parts = path.parts
        skip_dirs = {'.git', '__pycache__', 'venv', '.venv', 'node_modules',
                    'build', 'dist', '.tox', '.pytest_cache'}
        return any(d in skip_dirs for d in parts) or path.name.startswith('test_')

    def _extract_from_toon(self, toon_path: Path) -> List[CodeRegion]:
        """Extract regions from existing map.toon file."""
        regions = []
        try:
            import yaml
            with open(toon_path) as f:
                data = yaml.safe_load(f)

            # Extract from D: section (definitions)
            for item in data.get('D', []):
                if item.get('type') in ['function', 'class']:
                    regions.append(CodeRegion(
                        file=item['file'],
                        name=item['name'],
                        type=RegionType(item['type']),
                        start_line=item.get('start', 0),
                        end_line=item.get('end', 0),
                        signature_hash=item.get('hash', ''),
                        dependencies=item.get('deps', [])
            ))
        except Exception:
            pass  # Fallback to AST extraction

        return regions

    def _extract_from_file(self, path: Path) -> List[CodeRegion]:
        """Use AST to extract function/class regions with line numbers."""
        try:
            source = path.read_text()
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return []

        regions = []
        rel_path = str(path.relative_to(self.root))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                region = CodeRegion(
                    file=rel_path,
                    name=node.name,
                    type=RegionType.FUNCTION,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    signature_hash="",
                    dependencies=self._find_calls(node)
                )
                region.signature_hash = region.compute_signature_hash(source)
                regions.append(region)

            elif isinstance(node, ast.ClassDef):
                region = CodeRegion(
                    file=rel_path,
                    name=node.name,
                    type=RegionType.CLASS,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    signature_hash="",
                    dependencies=self._find_calls(node)
                )
                region.signature_hash = region.compute_signature_hash(source)
                regions.append(region)

        return regions

    def _find_calls(self, node) -> List[str]:
        """Find function/method calls within a node."""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # Handle method calls and attribute access
                    calls.append(child.func.attr)
                    # Also capture the full attribute chain
                    if isinstance(child.func.value, ast.Name):
                        calls.append(f"{child.func.value.id}.{child.func.attr}")
        return list(set(calls))  # Deduplicate

    def _detect_shadow_conflicts(self, regions: List[CodeRegion]):
        """Detect shared imports/constants that could cause shadow conflicts."""
        # Group regions by file
        regions_by_file = {}
        for r in regions:
            regions_by_file.setdefault(r.file, []).append(r)

        # For each file, find shared imports and module-level constants
        for file_path, file_regions in regions_by_file.items():
            full_path = self.root / file_path
            try:
                source = full_path.read_text()
                tree = ast.parse(source)

                # Find module-level imports and constants
                shared_symbols = set()
                for node in tree.body:
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        for alias in node.names:
                            shared_symbols.add(alias.name)
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if target.id.isupper():  # Constants
                                    shared_symbols.add(target.id)

                # Add shadow conflicts for regions that use shared symbols
                for region in file_regions:
                    region_deps = set(region.dependencies)
                    shadow_symbols = region_deps & shared_symbols
                    region.shadow_conflicts = list(shadow_symbols)

            except Exception:
                continue
