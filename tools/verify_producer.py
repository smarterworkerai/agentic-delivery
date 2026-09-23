#!/usr/bin/env python3
"""Required, portable producer checks for PR and main revisions.

The Hermes-runtime plugin doctor is a separate integration check; this command
covers only checks that run in a clean Python checkout without Hermes installed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    for args in (
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
        [sys.executable, "tools/validate_adw_skills.py"],
    ):
        subprocess.run(args, cwd=ROOT, check=True)

    sys.path.insert(0, str(ROOT / "tools"))
    import validate_adw_plugin_package as plugin

    plugin.validate_manifest_and_entrypoint()
    plugin.validate_registry_and_skills()
    plugin.validate_router_behavior()
    print("Direct root plugin package tests OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
