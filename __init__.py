"""Hermes plugin entrypoint for the Agentic Delivery Workflow router."""

from __future__ import annotations

from pathlib import Path
import sys

_PLUGIN_ROOT = Path(__file__).resolve().parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from adw_plugin.router import register

__all__ = ["register"]
