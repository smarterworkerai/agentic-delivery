#!/usr/bin/env python3
"""Validate the installable root ADW Hermes plugin package.

This validator is model-free. It verifies the root plugin manifest, package
entrypoint, workflow registry consistency, CLI injection behavior, gateway
rewrite behavior, and Hermes discovery from a temporary user-plugin install.
"""
from __future__ import annotations

import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
HERMES_SRC = Path(os.environ.get("HERMES_SRC", "/home/pupz/.hermes/hermes-agent"))
EXPECTED_WORKFLOWS = {
    "plan-feature": "adw-plan-feature",
    "plan-bugfix": "adw-plan-bugfix",
    "do-impl": "adw-do-impl",
    "do-impl-delegate": "adw-do-impl-delegate",
    "test-feature": "adw-test-feature",
    "merge-feature": "adw-merge-feature",
    "promote-release": "adw-promote-release",
    "rollback-deployment": "adw-rollback-deployment",
    "validate-regression": "adw-validate-regression",
    "create-adr": "adw-create-adr",
    "audit-dependencies": "adw-audit-dependencies",
    "analyze-production": "adw-analyze-production",
}


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


def parse_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def validate_manifest_and_entrypoint() -> None:
    manifest = REPO_ROOT / "plugin.yaml"
    if not manifest.exists():
        raise AssertionError("missing root plugin.yaml")
    data = parse_simple_yaml(manifest)
    assert data.get("name") == "adw", data
    assert data.get("kind") == "standalone", data
    assert_contains(manifest.read_text(encoding="utf-8"), "Agentic Delivery Workflow")

    init_file = REPO_ROOT / "__init__.py"
    if not init_file.exists():
        raise AssertionError("missing root __init__.py")
    root_text = init_file.read_text(encoding="utf-8")
    assert_contains(root_text, "from adw_plugin.router import register")

    sys.path.insert(0, str(REPO_ROOT))
    root_module = importlib.import_module("__init__")
    router = importlib.import_module("adw_plugin.router")
    assert getattr(root_module, "register") is getattr(router, "register")


def validate_registry_and_skills() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    registry = importlib.import_module("adw_plugin.registry")

    assert registry.WORKFLOWS == EXPECTED_WORKFLOWS
    for alias, canonical in registry.ALIASES.items():
        if canonical not in registry.WORKFLOWS:
            raise AssertionError(f"alias {alias!r} points to unknown workflow {canonical!r}")

    for workflow, skill_name in registry.WORKFLOWS.items():
        route = registry.parse_route(f"{workflow} payload text")
        assert route is not None
        assert route.workflow == workflow
        assert route.skill == skill_name
        skill_dir = registry.skill_dir_for_name(skill_name)
        skill_path = REPO_ROOT / "skills" / "adw" / skill_dir / "SKILL.md"
        if not skill_path.exists():
            raise AssertionError(f"registry maps {workflow} to missing {skill_path}")

    aliases_to_check = {
        "plan": "plan-feature",
        "bugfix": "plan-bugfix",
        "impl": "do-impl",
        "delegate": "do-impl-delegate",
        "test": "test-feature",
        "merge": "merge-feature",
        "rollback": "rollback-deployment",
    }
    for alias, canonical in aliases_to_check.items():
        route = registry.parse_route(f"{alias} example")
        assert route is not None
        assert route.workflow == canonical

    operational_dirs = {
        path.parent.name
        for path in (REPO_ROOT / "skills" / "adw").glob("*/SKILL.md")
        if path.parent.name != "adw-core"
    }
    registry_dirs = {registry.skill_dir_for_name(skill) for skill in registry.WORKFLOWS.values()}
    if operational_dirs != registry_dirs:
        raise AssertionError(f"skill directory mismatch: operational={operational_dirs}, registry={registry_dirs}")


def validate_router_behavior() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    router = importlib.import_module("adw_plugin.router")
    prompts = importlib.import_module("adw_plugin.prompts")
    registry = importlib.import_module("adw_plugin.registry")

    route = registry.parse_route("plan invoice CSV export")
    assert route is not None
    prompt = prompts.build_invocation_prompt(route)
    assert not prompt.startswith("/")
    assert_contains(prompt, "Workflow: plan-feature")
    assert_contains(prompt, "Operational skill: adw-plan-feature")
    assert_contains(prompt, "name: adw-core")
    assert_contains(prompt, "name: adw-plan-feature")

    ctx = FakeCtx()
    router.register(ctx)
    assert "adw" in ctx.commands
    assert ctx.commands["adw"]["args_hint"] == "<workflow> <payload>"
    assert "pre_gateway_dispatch" in ctx.hooks

    help_text = ctx.commands["adw"]["handler"]("")
    assert_contains(help_text, "Usage: `/adw <workflow> <payload>`")
    assert_contains(help_text, "plan-feature")
    assert_contains(help_text, "Plan a new feature")
    assert len(ctx.injected) == 0

    result = ctx.commands["adw"]["handler"]("bug login timeout")
    assert_contains(result, "Queued ADW workflow `plan-bugfix`")
    assert len(ctx.injected) == 1
    role, injected_prompt = ctx.injected[0]
    assert role == "user"
    assert_contains(injected_prompt, "Workflow: plan-bugfix")
    assert_contains(injected_prompt, "User payload: login timeout")

    gateway_result = ctx.hooks["pre_gateway_dispatch"][0](FakeEvent("/adw merge main PR #42"))
    assert gateway_result is not None
    assert gateway_result["action"] == "rewrite"
    assert not gateway_result["text"].startswith("/")
    assert_contains(gateway_result["text"], "Workflow: merge-feature")
    assert_contains(gateway_result["text"], "User payload: main PR #42")
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


def ignore_for_plugin_copy(dirpath: str, names: list[str]) -> set[str]:
    ignored = {".git", "__pycache__"}.intersection(names)
    if Path(dirpath).resolve() == REPO_ROOT:
        ignored.update({".hermes"}.intersection(names))
    return ignored


def validate_hermes_discovery() -> None:
    if not HERMES_SRC.exists():
        raise RuntimeError(f"Hermes source not found: {HERMES_SRC}")
    code = """
from hermes_cli.plugins import discover_plugins, get_plugin_command_handler, get_plugin_commands, invoke_hook

discover_plugins(force=True)
commands = get_plugin_commands()
assert 'adw' in commands, commands
handler = get_plugin_command_handler('adw')
assert handler is not None
assert commands['adw']['args_hint'] == '<workflow> <payload>'
help_text = handler('')
assert 'plan-feature' in help_text
assert 'Plan a new feature' in help_text

class Event:
    text = '/adw test PR #99'
    def get_command(self): return 'adw'
    def get_command_args(self): return 'test PR #99'

results = invoke_hook('pre_gateway_dispatch', event=Event(), gateway=None, session_store=None)
rewrites = [r for r in results if isinstance(r, dict) and r.get('action') == 'rewrite']
assert rewrites, results
assert 'Workflow: test-feature' in rewrites[0]['text']
assert 'name: adw-test-feature' in rewrites[0]['text']
print('Hermes discovery OK: root /adw plugin registered and gateway rewrite hook works')
"""
    with tempfile.TemporaryDirectory(prefix="adw-plugin-package-") as tmp:
        home = Path(tmp) / "home"
        installed = home / "plugins" / "agentic-delivery"
        home.mkdir(parents=True)
        (home / "config.yaml").write_text("plugins:\n  enabled:\n    - adw\n", encoding="utf-8")
        shutil.copytree(REPO_ROOT, installed, ignore=ignore_for_plugin_copy)
        env = os.environ.copy()
        env["HERMES_HOME"] = str(home)
        env["PYTHONPATH"] = f"{HERMES_SRC}:{env.get('PYTHONPATH', '')}"
        completed = subprocess.run(
            [hermes_python(), "-c", code],
            cwd=Path(tmp),
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


def main() -> int:
    validate_manifest_and_entrypoint()
    validate_registry_and_skills()
    validate_router_behavior()
    print("Direct root plugin package tests OK")
    validate_hermes_discovery()
    print("ADW root plugin package validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
