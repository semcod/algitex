"""Remove repeated README boilerplate blocks."""

from __future__ import annotations

import re
from pathlib import Path


def fix_readme(path: str = "README.md") -> None:
    """Collapse repeated license and author lines in the project README."""
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    before_len = len(text)

    text = re.sub(
        r"(Licensed under Apache-2\.0\.)\s*(?:\n\s*\n\s*Licensed under Apache-2\.0\.)+",
        r"\1",
        text,
    )
    text = re.sub(
        r"(## Author\s*\n\s*Tom Sapletta\s*\n)(?:\s*Tom Sapletta\s*\n\s*)+",
        r"\1",
        text,
    )
    text = re.sub(r"\n{3,}", "\n\n", text)

    target.write_text(text, encoding="utf-8")
    after_len = len(text)
    print(f"README: {before_len} -> {after_len} chars ({before_len - after_len} removed)")


if __name__ == "__main__":
    fix_readme()
