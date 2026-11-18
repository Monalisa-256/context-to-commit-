#!/usr/bin/env python3
"""Check that executable examples match their published code listings."""

from __future__ import annotations

import argparse
import difflib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LISTINGS = (
    (ROOT / "MASTERPLAN.md", "### 22.3 Complete `harness.py`",
     ROOT / "examples" / "reading_queue" / "harness.py"),
    (ROOT / "TESTING.md", "## 5. Install an automated test suite",
     ROOT / "tests" / "test_reference_harness.py"),
)


def extract_listing(document: str, heading: str) -> str:
    """Read the first complete Python fence after a unique section heading."""
    if document.count(heading) != 1:
        raise ValueError(f"Expected one section named {heading!r}")
    after = document.split(heading, 1)[1]
    match = re.search(r"(?ms)^```python[ \t]*\n(.*?)^```[ \t]*$", after)
    if match is None:
        raise ValueError(f"Missing complete Python listing under {heading!r}")
    return match.group(1).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="replace executable copies with the documented listings")
    args = parser.parse_args()
    failures = 0
    for document, heading, executable in LISTINGS:
        expected = extract_listing(document.read_text(encoding="utf-8"), heading)
        if args.write:
            executable.write_text(expected, encoding="utf-8")
            print(f"Updated {executable.relative_to(ROOT)}")
            continue
        actual = executable.read_text(encoding="utf-8")
        if actual == expected:
            print(f"OK: {executable.relative_to(ROOT)} matches {document.name}")
            continue
        failures += 1
        print(f"Mismatch: {executable.relative_to(ROOT)} differs from {document.name}",
              file=sys.stderr)
        diff = difflib.unified_diff(
            expected.splitlines(keepends=True), actual.splitlines(keepends=True),
            fromfile=document.name, tofile=str(executable.relative_to(ROOT)),
        )
        sys.stderr.writelines(diff)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
