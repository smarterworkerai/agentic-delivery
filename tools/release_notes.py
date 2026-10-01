#!/usr/bin/env python3
"""Print the CHANGELOG.md section for one version.

The release workflow uses this to build GitHub Release notes. It is a Python
tool rather than shell text processing so the extraction is portable (the
Ubuntu runner's default awk is mawk) and unit-tested.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def section(changelog: str, version: str) -> str:
    """Return the body under `## [<version>]` (optionally dated), up to the next release heading."""
    heading = re.compile(rf"^## \[{re.escape(version)}\](?: - \d{{4}}-\d{{2}}-\d{{2}})?\s*$")
    lines = changelog.splitlines()
    for index, line in enumerate(lines):
        if not heading.match(line):
            continue
        body: list[str] = []
        for item in lines[index + 1:]:
            if item.startswith("## ["):
                break
            body.append(item)
        text = "\n".join(body).strip("\n")
        if not text.strip():
            raise ValueError(f"changelog section for {version} is empty")
        return text + "\n"
    raise ValueError(f"changelog has no section for {version}")


def main(argv: list[str]) -> int:
    version = argv[1] if len(argv) > 1 else (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    try:
        sys.stdout.write(section((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), version))
    except (OSError, ValueError) as exc:
        print(f"release-notes: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
