"""Generate Markdown documentation from Python library source code.

Usage:
    python scripts/generate_lib_docs.py
"""

import ast
from pathlib import Path
from typing import Any


def extract_docstring(node: ast.AST) -> str | None:
    """Extract docstring from AST node."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                return node.body[0].value.value
    return None


def get_function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Build function signature string from AST node."""
    args = []
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)
    
    # Handle defaults
    defaults = node.args.defaults
    if defaults:
        for i, default in enumerate(defaults):
            idx = len(args) - len(defaults) + i
            if idx >= 0:
                args[idx] += f"={ast.unparse(default)}"
    
    # Handle *args and **kwargs
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")
    
    returns = ""
    if node.returns:
        returns = f" -> {ast.unparse(node.returns)}"
    
    sig = f"def {node.name}({', '.join(args)}){returns}"
    return sig


def _parse_function_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any] | None:
    """Extract function info from an AST node."""
    if node.name.startswith('_'):
        return None
    return {
        "name": node.name,
        "signature": get_function_signature(node),
        "docstring": extract_docstring(node),
        "lineno": node.lineno,
    }


def _parse_class_node(node: ast.ClassDef) -> dict[str, Any] | None:
    """Extract class info from an AST node."""
    if node.name.startswith('_'):
        return None
    methods = []
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not item.name.startswith('_') or item.name == '__init__':
                methods.append({
                    "name": item.name,
                    "signature": get_function_signature(item),
                    "docstring": extract_docstring(item),
                    "lineno": item.lineno,
                })
    return {
        "name": node.name,
        "docstring": extract_docstring(node),
        "lineno": node.lineno,
        "methods": methods,
        "bases": [ast.unparse(base) for base in node.bases],
    }


def _parse_import_node(node: ast.Import | ast.ImportFrom) -> str | None:
    """Extract import statement string from an AST node."""
    if isinstance(node, ast.ImportFrom) and node.module:
        names = [alias.name for alias in node.names]
        return f"from {node.module} import {', '.join(names)}"
    elif isinstance(node, ast.Import):
        names = [alias.name for alias in node.names]
        return f"import {', '.join(names)}"
    return None


def _parse_export_node(node: ast.Assign) -> list[str] | None:
    """Extract __all__ exports from an AST assign node."""
    for target in node.targets:
        if isinstance(target, ast.Name) and target.id == "__all__":
            if isinstance(node.value, (ast.List, ast.Tuple)):
                return [ast.unparse(elt).strip('"\'') for elt in node.value.elts]
    return None


# Node type → handler mapping
_NODE_HANDLERS: dict[type, callable] = {
    ast.FunctionDef: _parse_function_node,
    ast.AsyncFunctionDef: _parse_function_node,
    ast.ClassDef: _parse_class_node,
    ast.Import: _parse_import_node,
    ast.ImportFrom: _parse_import_node,
    ast.Assign: _parse_export_node,
}


def parse_file(filepath: Path) -> dict[str, Any]:
    """Parse Python file and extract documentation.

    CC: 5 (init + loop + 4 handler branches via dispatch)
    Was: CC ~24 (nested if/elif per node type)
    """
    try:
        source = filepath.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        return {"error": str(e)}

    result: dict[str, Any] = {
        "module_docstring": None,
        "functions": [],
        "classes": [],
        "imports": [],
        "exports": []
    }

    result["module_docstring"] = extract_docstring(tree)

    for node in ast.iter_child_nodes(tree):
        handler = _NODE_HANDLERS.get(type(node))
        if handler is None:
            continue

        parsed = handler(node)
        if parsed is None:
            continue

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append(parsed)
        elif isinstance(node, ast.ClassDef):
            result["classes"].append(parsed)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            result["imports"].append(parsed)
        elif isinstance(node, ast.Assign):
            result["exports"] = parsed

    return result


def generate_module_doc(module_name: str, module_path: Path, parsed: dict) -> str:
    """Generate markdown documentation for a module."""
    lines = []
    
    # Header
    lines.append(f"# `{module_name}`")
    lines.append("")
    
    # Module docstring
    if parsed.get("module_docstring"):
        lines.append(parsed["module_docstring"])
        lines.append("")
    
    # Exports
    if parsed.get("exports"):
        lines.append("## Public API")
        lines.append("")
        lines.append("```python")
        lines.append(f"__all__ = {parsed['exports']}")
        lines.append("```")
        lines.append("")
    
    # Functions
    if parsed.get("functions"):
        lines.append("## Functions")
        lines.append("")
        for func in sorted(parsed["functions"], key=lambda x: x["lineno"]):
            lines.append(f"### `{func['name']}`")
            lines.append("")
            lines.append(f"```python")
            lines.append(func["signature"])
            lines.append("```")
            lines.append("")
            if func.get("docstring"):
                lines.append(func["docstring"])
                lines.append("")
    
    # Classes
    if parsed.get("classes"):
        lines.append("## Classes")
        lines.append("")
        for cls in sorted(parsed["classes"], key=lambda x: x["lineno"]):
            bases = f"({', '.join(cls['bases'])})" if cls["bases"] else ""
            lines.append(f"### `{cls['name']}{bases}`")
            lines.append("")
            if cls.get("docstring"):
                lines.append(cls["docstring"])
                lines.append("")
            
            if cls.get("methods"):
                lines.append("**Methods:**")
                lines.append("")
                for method in cls["methods"]:
                    lines.append(f"#### `{method['name']}`")
                    lines.append("")
                    lines.append(f"```python")
                    lines.append(method["signature"])
                    lines.append("```")
                    lines.append("")
                    if method.get("docstring"):
                        lines.append(method["docstring"])
                        lines.append("")
    
    return "\n".join(lines)


def scan_package(src_dir: Path, output_dir: Path) -> None:
    """Scan package and generate markdown documentation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_modules = []
    
    for pyfile in sorted(src_dir.rglob("*.py")):
        if pyfile.name.startswith("__pycache__"):
            continue
        
        # Build module name
        rel_path = pyfile.relative_to(src_dir)
        module_parts = list(rel_path.parent.parts)
        if pyfile.stem != "__init__":
            module_parts.append(pyfile.stem)
        module_name = ".".join(module_parts) if module_parts else pyfile.stem
        
        print(f"  Parsing: {module_name}")
        
        parsed = parse_file(pyfile)
        if "error" in parsed:
            print(f"    Error: {parsed['error']}")
            continue
        
        if not parsed["functions"] and not parsed["classes"] and not parsed["module_docstring"]:
            continue
        
        # Generate markdown
        md_content = generate_module_doc(module_name, pyfile, parsed)
        
        # Determine output path
        if pyfile.name == "__init__.py":
            out_file = output_dir / "/".join(rel_path.parent.parts) / "index.md"
        else:
            out_file = output_dir / "/".join(rel_path.parent.parts) / f"{pyfile.stem}.md"
        
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(md_content, encoding='utf-8')
        
        all_modules.append({
            "name": module_name,
            "path": str(out_file.relative_to(output_dir)),
            "functions": len(parsed["functions"]),
            "classes": len(parsed["classes"])
        })
    
    # Generate index
    generate_index(output_dir, all_modules)
    
    return all_modules


def generate_index(output_dir: Path, modules: list[dict]) -> None:
    """Generate index.md with module overview."""
    lines = [
        "# API Documentation",
        "",
        "Auto-generated documentation from source code.",
        "",
        "## Modules",
        "",
        "| Module | Functions | Classes |",
        "|--------|-----------|----------|"
    ]
    
    for mod in modules:
        link = f"[{mod['name']}](./{mod['path']})"
        lines.append(f"| {link} | {mod['functions']} | {mod['classes']} |")
    
    index_file = output_dir / "index.md"
    index_file.write_text("\n".join(lines), encoding='utf-8')
    print(f"\nGenerated: {index_file}")


def main():
    src_dir = Path("/home/tom/github/semcod/algitex/src/algitex")
    output_dir = Path("/home/tom/github/semcod/algitex/docs/api")
    
    print(f"Generating docs from: {src_dir}")
    print(f"Output to: {output_dir}")
    print()
    
    modules = scan_package(src_dir, output_dir)
    
    print(f"\n✅ Generated {len(modules)} module docs")
    print(f"   Location: {output_dir}")


if __name__ == "__main__":
    main()
