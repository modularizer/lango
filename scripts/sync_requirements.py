#!/usr/bin/env python3
"""Sync requirements.txt and requirements-dev.txt to pyproject.toml."""

import re
import sys
from pathlib import Path


def parse_requirements(filepath: Path) -> list[str]:
    """Parse a requirements file and return list of dependencies."""
    if not filepath.exists():
        return []

    deps = []
    for line in filepath.read_text().splitlines():
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue
        # Skip -r includes and other flags
        if line.startswith("-"):
            continue
        deps.append(line)
    return deps


def format_dependencies(deps: list[str], indent: int = 4) -> str:
    """Format dependencies as TOML array entries."""
    if not deps:
        return ""
    lines = []
    for dep in deps:
        lines.append(f'{" " * indent}"{dep}",')
    return "\n".join(lines)


def sync_to_pyproject(
    pyproject_path: Path,
    requirements_path: Path,
    requirements_dev_path: Path,
) -> bool:
    """
    Sync requirements files to pyproject.toml.

    Returns True if changes were made, False otherwise.
    """
    content = pyproject_path.read_text()
    original_content = content

    # Parse requirements
    deps = parse_requirements(requirements_path)
    dev_deps = parse_requirements(requirements_dev_path)

    # Update main dependencies
    if deps:
        deps_str = format_dependencies(deps)
        # Match the dependencies array in [project] section
        pattern = r'(dependencies\s*=\s*\[)\s*\n(.*?)(\n\s*\])'
        replacement = f'\\1\n{deps_str}\n]'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Update dev/test dependencies
    if dev_deps:
        dev_deps_str = format_dependencies(dev_deps)
        # Match the test array in [project.optional-dependencies] section
        pattern = r'(test\s*=\s*\[)\s*\n(.*?)(\n\s*\])'
        replacement = f'\\1\n{dev_deps_str}\n]'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if content != original_content:
        pyproject_path.write_text(content)
        return True
    return False


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent

    pyproject_path = repo_root / "pyproject.toml"
    requirements_path = repo_root / "requirements.txt"
    requirements_dev_path = repo_root / "requirements-dev.txt"

    if not pyproject_path.exists():
        print("Error: pyproject.toml not found", file=sys.stderr)
        return 1

    changed = sync_to_pyproject(
        pyproject_path,
        requirements_path,
        requirements_dev_path,
    )

    if changed:
        print("Synced requirements to pyproject.toml")
        # Re-stage pyproject.toml if it was modified
        return 0
    else:
        print("pyproject.toml already in sync")
        return 0


if __name__ == "__main__":
    sys.exit(main())
