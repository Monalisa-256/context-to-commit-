#!/usr/bin/env python3
"""Create a new, intentionally failing reading queue exercise repository."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
FILES = {
    "harness.py": HERE / "harness.py",
    "reading_queue.py": HERE / "fixtures" / "reading_queue_buggy.py",
    "tests/test_reading_queue.py": HERE / "tests" / "test_reading_queue.py",
    ".gitignore": HERE / ".gitignore",
}


def git(destination: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args], cwd=destination, capture_output=True, text=True,
        check=False, timeout=30,
    )
    if result.returncode:
        details = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {details}")


def create_lab(destination: Path) -> Path:
    """Create a fresh Git repository. Never overwrite an existing path."""
    destination = destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Destination already exists: {destination}")
    if not destination.parent.is_dir():
        raise FileNotFoundError(f"Parent directory does not exist: {destination.parent}")

    destination.mkdir(mode=0o700)
    try:
        for name, source in FILES.items():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        git(destination, "init", "-q")
        git(destination, "add", ".")
        git(destination, "-c", "user.name=Local Exercise",
            "-c", "user.email=exercise@example.invalid", "commit", "-qm",
            "Record deliberately failing reading queue baseline")
    except Exception:
        print(f"Setup failed. Inspect the new directory: {destination}",
              file=sys.stderr)
        raise
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path,
                        help="new directory for the standalone Git exercise")
    args = parser.parse_args()
    try:
        destination = create_lab(args.destination)
    except (OSError, RuntimeError) as exc:
        print(f"Cannot create exercise: {exc}", file=sys.stderr)
        return 1
    print(f"Created {destination}")
    print("The baseline contains one intentional defect.")
    print("Next: cd into the directory, then run Python unittest discovery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
