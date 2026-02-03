#!/usr/bin/env python3
"""Sync __version__ in __init__.py from pyproject.toml."""

import re
import sys
from pathlib import Path


def get_pyproject_version(pyproject_path: Path) -> str | None:
    """Extract version from pyproject.toml."""
    content = pyproject_path.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    return match.group(1) if match else None


def sync_version(pyproject_path: Path, init_path: Path) -> bool:
    """Sync version from pyproject.toml to __init__.py. Returns True if changed."""
    version = get_pyproject_version(pyproject_path)
    if not version:
        print("Error: Could not find version in pyproject.toml", file=sys.stderr)
        return False

    content = init_path.read_text()
    original = content

    # Replace __version__ line (with or without comment)
    content = re.sub(
        r'^__version__\s*=\s*"[^"]+".*$',
        f'__version__ = "{version}"  # modify in pyproject.toml',
        content,
        flags=re.MULTILINE,
    )

    if content != original:
        init_path.write_text(content)
        return True
    return False


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent

    pyproject_path = repo_root / "pyproject.toml"
    init_path = repo_root / "src" / "lango" / "__init__.py"

    if not pyproject_path.exists():
        print("Error: pyproject.toml not found", file=sys.stderr)
        return 1

    if not init_path.exists():
        print("Error: src/lango/__init__.py not found", file=sys.stderr)
        return 1

    changed = sync_version(pyproject_path, init_path)

    if changed:
        print("Synced __version__ from pyproject.toml")
        return 0
    else:
        print("__version__ already in sync")
        return 0


if __name__ == "__main__":
    sys.exit(main())
