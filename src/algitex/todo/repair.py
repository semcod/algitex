"""Per-type repair functions — each handles exactly one fix category.

Implements Strategy pattern: REPAIRERS dict maps category → repair function.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from algitex.todo.classify import KNOWN_MAGIC_CONSTANTS


# ─── Type alias for repair functions ─────────────────
RepairFunc = Callable[[Path, str, int], bool]


def _find_import_insert_point(lines: list[str]) -> int:
    """Find the insert point just after the last import statement."""
    last_import = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            last_import = i + 1
    return last_import


# ─── Individual repair functions ──────────────────────


def repair_unused_import(path: Path, name: str, line_idx: int) -> bool:
    """Remove unused import from file.
    
    Args:
        path: File to modify
        name: Import name to remove
        line_idx: 0-based line index
    
    Returns:
        True if fixed, False otherwise
    """
    lines = path.read_text().splitlines()
    if line_idx >= len(lines):
        return False

    line = lines[line_idx]

    # Case 1: "import X" → remove entire line
    if re.match(rf"^import\s+{name}\s*$", line.strip()):
        lines.pop(line_idx)
        path.write_text("\n".join(lines) + "\n")
        return True

    # Case 2: "from Y import X" → remove line
    if re.match(rf"^from\s+\S+\s+import\s+{name}\s*$", line.strip()):
        lines.pop(line_idx)
        path.write_text("\n".join(lines) + "\n")
        return True

    # Case 3: "from Y import A, X, B" → remove X from list
    if "import" in line and name in line:
        new_line = re.sub(rf",?\s*{name}\s*,?", ",", line)
        new_line = re.sub(r",\s*$", "", new_line)  # trailing comma
        new_line = re.sub(r"import\s*,", "import ", new_line)  # leading comma
        lines[line_idx] = new_line
        path.write_text("\n".join(lines) + "\n")
        return True

    return False


def repair_return_type(path: Path, suggested: str, line_idx: int) -> bool:
    """Add return type annotation to function.
    
    Args:
        path: File to modify
        suggested: Return type annotation (e.g., "-> None")
        line_idx: 0-based line index
    
    Returns:
        True if fixed, False otherwise
    """
    lines = path.read_text().splitlines()
    if line_idx >= len(lines):
        return False

    line = lines[line_idx]

    # Add return type before the colon
    if "def " in line and ":" in line and " -> " not in line:
        new_line = re.sub(r"\)\s*:", f") {suggested}:", line)
        if new_line != line:
            lines[line_idx] = new_line
            path.write_text("\n".join(lines) + "\n")
            return True

    return False


def _simple_fstring_rewrite(line: str) -> str:
    """Rewrite simple string concatenation to f-string."""
    pattern = re.compile(
        r'(?P<left>["\'])(?P<prefix>[^"\']*)\1\s*\+\s*'
        r'(?P<expr>[A-Za-z_][A-Za-z0-9_\.]*)\s*\+\s*'
        r'(?P<right>["\'])(?P<tail>[^"\']*)\4'
    )

    def _replace(match: re.Match[str]) -> str:
        prefix = match.group("prefix").replace("\\", "\\\\").replace('"', '\\"').replace("{", "{{").replace("}", "}}")
        expr = match.group("expr")
        tail = match.group("tail").replace("\\", "\\\\").replace('"', '\\"').replace("{", "{{").replace("}", "}}")
        return f'f"{prefix}{{{expr}}}{tail}"'

    return pattern.sub(_replace, line, count=1)


def repair_fstring(path: Path, _unused: str = "", _unused2: int = 0) -> bool:
    """Convert string concatenations to f-strings using flynt or simple rewrite.
    
    Args:
        path: File to modify
        _unused: Unused parameter for API consistency
        _unused2: Unused parameter for API consistency
    
    Returns:
        True if any changes were made
    """
    # Try flynt first if available
    try:
        if shutil.which("flynt"):
            result = subprocess.run(
                ["flynt", str(path), "--transform-concats", "--quiet"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return True
    except Exception:
        pass

    # Fallback: simple rewrite
    lines = path.read_text().splitlines()
    changed = False
    for i, line in enumerate(lines):
        # Skip lines that can't be string concatenations
        if not line.strip() or line.strip().startswith(("#", "import", "from")):
            continue
        if '"' not in line and "'" not in line:
            continue
        if "+" not in line:
            continue
        new_line = _simple_fstring_rewrite(line)
        if new_line != line:
            lines[i] = new_line
            changed = True

    if changed:
        path.write_text("\n".join(lines) + "\n")
    return changed


def repair_magic_number(
    path: Path, 
    number: int, 
    line_idx: int,
    const_name: str | None = None
) -> bool:
    """Replace magic number with named constant.
    
    Args:
        path: File to modify
        number: Magic number to replace
        line_idx: 0-based line index
        const_name: Constant name (auto-detected if None)
    
    Returns:
        True if fixed, False otherwise
    """
    if const_name is None:
        const_name = KNOWN_MAGIC_CONSTANTS.get(number)
        if const_name is None:
            return False

    lines = path.read_text().splitlines()
    if line_idx >= len(lines):
        return False

    line = lines[line_idx]
    new_line = re.sub(
        rf'(?<!["\'])\b{number}\b(?!["\'])',
        const_name,
        line,
        count=1,
    )
    
    if new_line == line:
        return False

    lines[line_idx] = new_line

    # Check if constant needs to be defined
    existing_constants = set()
    for l in lines:
        match = re.match(r"^([A-Z][A-Z0-9_]+)\s*=\s*\d+\s*$", l.strip())
        if match:
            existing_constants.add(match.group(1))

    if const_name not in existing_constants:
        insert_at = _find_import_insert_point(lines)
        const_block = ["", "# Constants", f"{const_name} = {number}", ""]
        lines[insert_at:insert_at] = const_block

    path.write_text("\n".join(lines) + "\n")
    return True


def repair_module_block(path: Path, _unused: str = "", _unused2: int = 0) -> bool:
    """Add standard module execution block.
    
    Args:
        path: File to modify
        _unused: Unused parameter for API consistency
        _unused2: Unused parameter for API consistency
    
    Returns:
        True if block was added
    """
    text = path.read_text()
    if "if __name__ == '__main__':" in text or 'if __name__ == "__main__":' in text:
        return False

    stripped = text.rstrip()
    if not stripped:
        return False

    if stripped.endswith("main()"):
        stripped += "\n"
    else:
        stripped += "\n\n"

    stripped += "if __name__ == '__main__':\n    main()\n"
    path.write_text(stripped)
    return True


# ─── Dispatch table ────────────────────────────────────

REPAIRERS: dict[str, Callable[[Path, str, int], bool]] = {
    "unused_import": repair_unused_import,
    "return_type": repair_return_type,
    "fstring": repair_fstring,
    "magic": repair_magic_number,
    "magic_known": repair_magic_number,
    "module_block": repair_module_block,
    "exec_block": repair_module_block,
}


__all__ = [
    "REPAIRERS",
    "repair_unused_import",
    "repair_return_type",
    "repair_fstring",
    "repair_magic_number",
    "repair_module_block",
]
