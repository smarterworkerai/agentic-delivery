from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "build_skills.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_skills_under_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BuildSkillsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()

    def copy_repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        target = Path(temporary.name) / "repo"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        return target

    def test_check_detects_each_generated_surface_when_stale(self) -> None:
        mutations = {
            "guardrails": lambda root: self.replace(
                root / "skills/adw/adw-plan/SKILL.md", "Inference is never approval.", "Inference may be approval."
            ),
            "version": lambda root: self.replace(
                root / "skills/adw/adw-plan/SKILL.md", 'version: "2.2.0"', 'version: "9.9.9"'
            ),
            "registry": lambda root: (root / "integrations/hermes/adw_plugin/registry.py").write_text("stale\n"),
            "readme": lambda root: self.replace(
                root / "README.md", "| Skill | Use it to | Human gate |", "| stale | table | here |"
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                root = self.copy_repo()
                mutate(root)
                errors = self.builder.build(root, check=True)
                self.assertTrue(any("generated content is stale" in error for error in errors), errors)

    @staticmethod
    def replace(path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"missing fixture token {old!r}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def write_skill(self, *, folder: str = "valid-skill", name: str = "valid-skill", description: str = "Does useful work. Use when testing.", compatibility: str = "Requires git.", metadata: str = '  suite: agentic-delivery\n  version: "2.2.0"\n  author: tester\n  requires: none', extra_top: str = "", body: str = "# Valid\n\n## Guardrails\n\n<!-- adw:guardrails:start -->\n- Safe.\n<!-- adw:guardrails:end -->\n") -> tuple[Path, object]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        skill_dir = root / "skills" / "adw" / folder
        skill_dir.mkdir(parents=True)
        text = f'''---
name: {name}
description: >-
  {description}
license: MIT
compatibility: {compatibility}
{extra_top}metadata:
{metadata}
---
{body}'''
        path = skill_dir / "SKILL.md"
        path.write_text(text, encoding="utf-8")
        return root, path

    def test_spec_rule_fixtures_are_rejected(self) -> None:
        cases = {
            "folder-name": dict(folder="folder-name", name="different-name"),
            "name-charset": dict(name="invalid--name", folder="invalid--name"),
            "name-length": dict(name="a" * 65, folder="a" * 65),
            "description-empty": dict(description=""),
            "description-length": dict(description="x" * 1025),
            "compatibility-length": dict(compatibility="x" * 501),
            "metadata-flat": dict(metadata="    nested: value"),
            "metadata-string": dict(metadata="  tags: [one, two]"),
            "top-version": dict(extra_top="version: 2.2.0\n"),
            "top-author": dict(extra_top="author: someone\n"),
            "line-limit": dict(body="# Valid\n" + "line\n" * 501 + "<!-- adw:guardrails:start -->\n- Safe.\n<!-- adw:guardrails:end -->\n"),
            "relative-reference": dict(body="# Valid\n\n[escape](../outside.md)\n\n<!-- adw:guardrails:start -->\n- Safe.\n<!-- adw:guardrails:end -->\n"),
        }
        for label, options in cases.items():
            with self.subTest(rule=label):
                root, _ = self.write_skill(**options)
                skills, errors = self.builder.discover_skills(root)
                if skills:
                    errors.extend(self.builder.validate_skill(skills[0], "2.2.0", root))
                self.assertTrue(errors, label)

    def test_claude_manifests_and_release_workflow_are_complete(self) -> None:
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        workflow = (ROOT / ".github/workflows/release.yml").read_text()

        self.assertEqual("./skills/adw/", plugin["skills"])
        self.assertEqual("agentic-delivery", marketplace["plugins"][0]["name"])
        self.assertEqual("./", marketplace["plugins"][0]["source"])
        for token in ("agentic-delivery-skills-", "SHA256SUMS", "gh release create", "ADW_ARCHIVE_SHA256"):
            self.assertIn(token, workflow)


if __name__ == "__main__":
    unittest.main()
