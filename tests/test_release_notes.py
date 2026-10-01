from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_tool():
    path = ROOT / "tools" / "release_notes.py"
    spec = importlib.util.spec_from_file_location("release_notes_tool", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseNotesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()
        cls.changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    def test_current_version_has_a_non_empty_changelog_section(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

        notes = self.tool.section(self.changelog, version)

        self.assertIn("### ", notes)
        self.assertNotIn("## [", notes)

    def test_section_stops_at_the_next_release_heading(self) -> None:
        changelog = "# Changelog\n\n## [1.1.0] - 2026-01-02\n\n### Added\n\n- new\n\n## [1.0.0]\n\n### Added\n\n- old\n"

        self.assertEqual("### Added\n\n- new\n", self.tool.section(changelog, "1.1.0"))
        self.assertEqual("### Added\n\n- old\n", self.tool.section(changelog, "1.0.0"))

    def test_missing_or_empty_section_is_an_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "no section for 9.9.9"):
            self.tool.section(self.changelog, "9.9.9")
        with self.assertRaisesRegex(ValueError, "is empty"):
            self.tool.section("## [1.0.0]\n\n## [0.9.0]\n\n- old\n", "1.0.0")

    def test_version_is_matched_literally(self) -> None:
        changelog = "## [2.2.0]\n\n- dotted\n\n## [2x2x0]\n\n- not a version\n"

        self.assertEqual("- dotted\n", self.tool.section(changelog, "2.2.0"))
        with self.assertRaises(ValueError):
            self.tool.section("## [2x2x0]\n\n- x\n", "2.2.0")


if __name__ == "__main__":
    unittest.main()
