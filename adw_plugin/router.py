"""Hermes slash-command router for Agentic Delivery Workflow (ADW)."""

from __future__ import annotations

import re
from typing import Any

from .prompts import build_invocation_prompt
from .registry import WORKFLOW_DEFINITIONS, parse_route


def register(ctx: Any) -> None:
    """Register the `/adw` CLI command and gateway rewrite hook."""

    def handle_adw(raw_args: str) -> str:
        route = parse_route(raw_args)
        if route is None:
            return usage()
        prompt = build_invocation_prompt(route)
        injected = False
        try:
            injected = bool(ctx.inject_message(prompt, role="user"))
        except Exception:
            injected = False
        if injected:
            return f"Queued ADW workflow `{route.workflow}` with skill `{route.skill}`."
        return (
            "ADW workflow parsed, but this surface did not support direct "
            "message injection. Send the generated prompt as a normal message "
            "or use a gateway platform with the ADW rewrite hook enabled.\n\n"
            f"{prompt}"
        )

    ctx.register_command(
        "adw",
        handle_adw,
        description="Run an Agentic Delivery Workflow",
        args_hint="<workflow> <payload>",
    )
    ctx.register_hook("pre_gateway_dispatch", gateway_rewrite_hook)


def gateway_rewrite_hook(event: Any, **_: Any) -> dict[str, str] | None:
    """Rewrite valid `/adw ...` gateway commands into a normal agent prompt.

    Invalid or incomplete `/adw` commands are left for the registered plugin
    command handler so users get a direct usage response instead of an agent turn
    containing help text.
    """

    args = extract_adw_args(event)
    if args is None:
        return None
    route = parse_route(args)
    if route is None:
        return None
    return {"action": "rewrite", "text": build_invocation_prompt(route)}


def extract_adw_args(event: Any) -> str | None:
    """Return raw ADW args from a gateway event, or None if it is not `/adw`."""

    try:
        command = event.get_command()
    except Exception:
        command = None
    if isinstance(command, str):
        normalized = command.lower().lstrip("/").split("@", 1)[0].replace("_", "-")
        if normalized == "adw":
            try:
                return event.get_command_args().strip()
            except Exception:
                return ""
        return None

    text = str(getattr(event, "text", "") or "").strip()
    match = re.match(r"^/adw(?:@[A-Za-z0-9_]+)?(?:\s+(.*))?$", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return (match.group(1) or "").strip()


def usage() -> str:
    """Return concise help for argument-less or invalid `/adw` calls."""

    workflow_lines = "\n".join(
        f"- `{definition.token}` — {definition.description}" for definition in WORKFLOW_DEFINITIONS
    )
    return (
        "Usage: `/adw <workflow> <payload>`\n\n"
        "Supported workflows:\n"
        f"{workflow_lines}\n\n"
        "Examples:\n"
        "- `/adw plan-feature invoice CSV export`\n"
        "- `/adw do-impl issue #42`\n"
        "- `/adw test-feature PR #42`\n"
        "- `/adw merge-feature main PR #42`"
    )
