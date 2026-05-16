#!/usr/bin/env python3
"""Validate the project-local ADW Hermes plugin spike.

This is intentionally model-free: it verifies parsing, CLI injection behavior,
gateway rewrite behavior, and Hermes project-plugin discovery with a temporary
HERMES_HOME config that enables the plugin.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = REPO_ROOT / ".hermes" / "plugins" / "adw" / "__init__.py"
HERMES_SRC = Path(os.environ.get("HERMES_SRC", "/home/pupz/.hermes/hermes-agent"))


def load_plugin_module():
    spec = importlib.util.spec_from_file_location("adw_plugin_spike", PLUGIN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import plugin from {PLUGIN_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeCtx:
    def __init__(self) -> None:
        self.commands = {}
        self.hooks = {}
        self.injected = []

    def register_command(self, name, handler, description="", args_hint=""):
        self.commands[name] = {
            "handler": handler,
            "description": description,
            "args_hint": args_hint,
        }

    def register_hook(self, hook_name, callback):
        self.hooks.setdefault(hook_name, []).append(callback)

    def inject_message(self, content: str, role: str = "user") -> bool:
        self.injected.append((role, content))
        return True


class FakeEvent:
    def __init__(self, text: str) -> None:
        self.text = text

    def get_command(self):
        if not self.text.startswith("/"):
            return None
        return self.text[1:].split(maxsplit=1)[0].split("@", 1)[0]

    def get_command_args(self):
        parts = self.text.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else ""


def assert_contains(haystack: str, needle: str) -> None:
    if needle not in haystack:
        raise AssertionError(f"Expected to find {needle!r}")


def validate_direct_module() -> None:
    module = load_plugin_module()

    route = module.parse_route("plan invoice CSV export")
    assert route is not None
    assert route.workflow == "plan-feature"
    assert route.skill == "adw-plan-feature"
    assert route.payload == "invoice CSV export"

    prompt = module.build_invocation_prompt(route)
    assert_contains(prompt, "Workflow: plan-feature")
    assert_contains(prompt, "Operational skill: adw-plan-feature")
    assert_contains(prompt, "## Embedded ADW Core Skill (`adw-core`)")
    assert_contains(prompt, "## Embedded Operational Skill (`adw-plan-feature`)")
    assert_contains(prompt, "name: adw-core")
    assert_contains(prompt, "name: adw-plan-feature")

    ctx = FakeCtx()
    module.register(ctx)
    assert "adw" in ctx.commands
    assert "pre_gateway_dispatch" in ctx.hooks
    result = ctx.commands["adw"]["handler"]("bugfix login timeout")
    assert "Queued ADW workflow `plan-bugfix`" in result
    assert len(ctx.injected) == 1
    role, injected_prompt = ctx.injected[0]
    assert role == "user"
    assert_contains(injected_prompt, "Workflow: plan-bugfix")
    assert_contains(injected_prompt, "name: adw-plan-bugfix")

    gateway_result = ctx.hooks["pre_gateway_dispatch"][0](FakeEvent("/adw merge main PR #42"))
    assert gateway_result is not None
    assert gateway_result["action"] == "rewrite"
    rewritten = gateway_result["text"]
    assert not rewritten.startswith("/")
    assert_contains(rewritten, "Workflow: merge-feature")
    assert_contains(rewritten, "User payload: main PR #42")

    assert ctx.hooks["pre_gateway_dispatch"][0](FakeEvent("/adw")) is None
    assert ctx.hooks["pre_gateway_dispatch"][0](FakeEvent("hello")) is None


def hermes_python() -> str:
    hermes = shutil.which("hermes")
    if not hermes:
        return sys.executable
    try:
        first_line = Path(hermes).read_text(encoding="utf-8").splitlines()[0]
    except OSError:
        return sys.executable
    if first_line.startswith("#!"):
        candidate = first_line[2:].strip().split()[0]
        if candidate and Path(candidate).exists():
            return candidate
    return sys.executable


def validate_hermes_discovery() -> None:
    if not HERMES_SRC.exists():
        raise RuntimeError(f"Hermes source not found: {HERMES_SRC}")
    code = """
from hermes_cli.plugins import discover_plugins, get_plugin_command_handler, get_plugin_commands, invoke_hook
from types import SimpleNamespace

discover_plugins(force=True)
commands = get_plugin_commands()
assert 'adw' in commands, commands
handler = get_plugin_command_handler('adw')
assert handler is not None
assert commands['adw']['args_hint'] == '<workflow> <payload>'

class Event:
    text = '/adw test PR #99'
    def get_command(self): return 'adw'
    def get_command_args(self): return 'test PR #99'

results = invoke_hook('pre_gateway_dispatch', event=Event(), gateway=None, session_store=None)
rewrites = [r for r in results if isinstance(r, dict) and r.get('action') == 'rewrite']
assert rewrites, results
assert 'Workflow: test-feature' in rewrites[0]['text']
assert 'name: adw-test-feature' in rewrites[0]['text']
print('Hermes discovery OK: /adw command registered and gateway rewrite hook works')
"""
    with tempfile.TemporaryDirectory(prefix="adw-hermes-home-") as tmp:
        home = Path(tmp)
        (home / "config.yaml").write_text("plugins:\n  enabled:\n    - adw\n", encoding="utf-8")
        env = os.environ.copy()
        env["HERMES_HOME"] = str(home)
        env["HERMES_ENABLE_PROJECT_PLUGINS"] = "1"
        env["PYTHONPATH"] = f"{HERMES_SRC}:{env.get('PYTHONPATH', '')}"
        completed = subprocess.run(
            [hermes_python(), "-c", code],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(
                "Hermes discovery validation failed\n"
                f"STDOUT:\n{completed.stdout}\n"
                f"STDERR:\n{completed.stderr}"
            )
        print(completed.stdout.strip())


def main() -> None:
    validate_direct_module()
    print("Direct plugin tests OK: parse, CLI injection, and gateway rewrite")
    validate_hermes_discovery()
    print("ADW plugin spike validation OK")


if __name__ == "__main__":
    main()
