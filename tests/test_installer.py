from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_adw.sh"
REF = "1" * 40
OWNER_MARKER = ".agentic-delivery-owner"
OWNER_VALUE = "agentic-delivery/v1"
SKILL_COUNT = 14


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.archive = self.base / "source.tar.gz"
        self.fakebin = self.base / "fakebin"
        self.fakebin.mkdir()
        self.log = self.base / "actions.log"
        self.log.write_text("")
        self._write_fakes()
        self._build_archive()
        self.checksum = hashlib.sha256(self.archive.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_fakes(self) -> None:
        curl = self.fakebin / "curl"
        curl.write_text(
            """#!/usr/bin/env bash
set -euo pipefail
out=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -o) out="$2"; shift 2 ;;
    *) shift ;;
  esac
done
[[ -n "$out" ]]
cp "${TEST_ARCHIVE:?}" "$out"
"""
        )
        hermes = self.fakebin / "hermes"
        hermes.write_text(
            """#!/usr/bin/env bash
set -euo pipefail
args=("$@")
if [[ " ${args[*]} " == *" config path "* ]]; then
  printf '%s\n' "${TEST_CONFIG:?}"
  exit 0
fi
if [[ " ${args[*]} " == *" plugins list --enabled --json "* ]]; then
  if [[ "${TEST_WAS_ENABLED:-no}" == "yes" ]]; then
    printf '[{"name":"adw","status":"enabled"}]\n'
  else
    printf '[]\n'
  fi
  exit 0
fi
if [[ " ${args[*]} " == *" plugins doctor "* ]]; then
  if [[ "${TEST_FAIL_POST:-no}" == "yes" && " ${args[*]} " == *" ${TEST_POST_TARGET:?} "* ]]; then
    exit 9
  fi
  exit 0
fi
if [[ " ${args[*]} " == *" plugins enable adw "* ]]; then
  printf 'enable\n' >> "${TEST_LOG:?}"
  exit 0
fi
if [[ " ${args[*]} " == *" plugins disable adw "* ]]; then
  if [[ "${TEST_FAIL_DISABLE:-no}" == "yes" ]]; then
    exit 8
  fi
  printf 'disable\n' >> "${TEST_LOG:?}"
  exit 0
fi
printf 'unexpected hermes args: %s\n' "$*" >&2
exit 2
"""
        )
        curl.chmod(0o755)
        hermes.chmod(0o755)

    def _build_archive(self) -> None:
        prefix = f"agentic-delivery-{REF}"
        with tarfile.open(self.archive, "w:gz") as tar:
            for path in ROOT.rglob("*"):
                if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                    continue
                tar.add(path, arcname=str(Path(prefix) / path.relative_to(ROOT)))

    def _env(self, profile: Path, **updates: str) -> dict[str, str]:
        profile.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{self.fakebin}:{env['PATH']}",
                "TEST_ARCHIVE": str(self.archive),
                "TEST_CONFIG": str(profile / "config.yaml"),
                "TEST_POST_TARGET": str(profile / "plugins" / "adw"),
                "TEST_LOG": str(self.log),
                "HERMES_BIN": str(self.fakebin / "hermes"),
                "ADW_PROFILE": "installer-test",
                "ADW_INSTALL_SOUL": "no",
                "ADW_UNINSTALL_SOUL": "no",
                "ADW_REPLACE_UNMANAGED": "no",
                "ADW_REF": REF,
                "ADW_ARCHIVE_SHA256": self.checksum,
            }
        )
        env.update(updates)
        return env

    def _run(self, profile: Path, *args: str, check: bool = True, **updates: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(INSTALLER), *args],
            cwd=ROOT,
            env=self._env(profile, **updates),
            text=True,
            capture_output=True,
            check=check,
        )

    def test_install_is_runtime_only_owned_and_uninstallable(self) -> None:
        profile = self.base / "profile"
        self._run(profile)

        plugin = profile / "plugins" / "adw"
        self.assertEqual((plugin / OWNER_MARKER).read_text().strip(), OWNER_VALUE)
        self.assertEqual(
            {path.name for path in plugin.iterdir()},
            {OWNER_MARKER, "SOUL.md", "__init__.py", "adw_plugin", "plugin.yaml"},
        )
        skills = list((profile / "skills" / "adw").glob("adw-*"))
        self.assertEqual(len(skills), SKILL_COUNT)
        self.assertTrue(all((skill / OWNER_MARKER).read_text().strip() == OWNER_VALUE for skill in skills))

        self._run(profile, "--uninstall")
        self.assertFalse(plugin.exists())
        self.assertFalse(any((profile / "skills" / "adw").glob("adw-*")))

    def test_filesystem_root_profile_is_refused(self) -> None:
        profile = self.base / "profile"
        result = self._run(profile, check=False, TEST_CONFIG="/config.yaml")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to use filesystem root", result.stderr)

    def test_checksum_mismatch_does_not_mutate_targets(self) -> None:
        profile = self.base / "profile"
        result = self._run(profile, check=False, ADW_ARCHIVE_SHA256="0" * 64)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum mismatch", result.stderr)
        self.assertFalse((profile / "plugins" / "adw").exists())
        self.assertFalse((profile / "skills" / "adw").exists())

    def test_unmanaged_collision_is_refused_without_mutation(self) -> None:
        profile = self.base / "profile"
        collision = profile / "skills" / "adw" / "adw-core"
        collision.mkdir(parents=True)
        (collision / "sentinel").write_text("unmanaged\n")

        result = self._run(profile, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing unmanaged collision", result.stderr)
        self.assertEqual((collision / "sentinel").read_text(), "unmanaged\n")
        self.assertFalse((profile / "plugins" / "adw").exists())

    def test_marker_symlink_does_not_authorize_uninstall(self) -> None:
        profile = self.base / "profile"
        skill = profile / "skills" / "adw" / "adw-core"
        skill.mkdir(parents=True)
        (skill / "sentinel").write_text("user-data\n")
        claimed_owner = self.base / "claimed-owner"
        claimed_owner.write_text(f"{OWNER_VALUE}\n")
        (skill / OWNER_MARKER).symlink_to(claimed_owner)

        self._run(profile, "--uninstall")

        self.assertEqual((skill / "sentinel").read_text(), "user-data\n")
        self.assertTrue((skill / OWNER_MARKER).is_symlink())

    def test_dangling_target_symlink_is_refused_and_preserved(self) -> None:
        profile = self.base / "profile"
        parent = profile / "skills" / "adw"
        parent.mkdir(parents=True)
        target = parent / "adw-core"
        target.symlink_to(profile / "missing-target", target_is_directory=True)

        result = self._run(profile, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing unmanaged collision", result.stderr)
        self.assertTrue(target.is_symlink())

    def test_custom_soul_requires_explicit_unmanaged_replacement(self) -> None:
        profile = self.base / "profile"
        profile.mkdir()
        soul = profile / "SOUL.md"
        soul.write_text("custom soul\n")

        result = self._run(profile, check=False, ADW_INSTALL_SOUL="yes")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to replace existing profile SOUL.md", result.stderr)
        self.assertEqual(soul.read_text(), "custom soul\n")
        self.assertFalse((profile / "plugins" / "adw").exists())

    def test_disable_failure_removes_nothing(self) -> None:
        profile = self.base / "profile"
        self._run(profile)
        plugin = profile / "plugins" / "adw"
        core = profile / "skills" / "adw" / "adw-core"

        result = self._run(profile, "--uninstall", check=False, TEST_FAIL_DISABLE="yes")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no installed paths were removed", result.stderr)
        self.assertTrue((plugin / OWNER_MARKER).is_file())
        self.assertTrue((core / OWNER_MARKER).is_file())

    def test_profile_lock_refuses_concurrent_installer(self) -> None:
        profile = self.base / "profile"
        profile.mkdir()
        (profile / ".adw-install.lock").mkdir()

        result = self._run(profile, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Another ADW install or uninstall is active", result.stderr)

    def test_cross_device_skill_root_is_refused_before_activation(self) -> None:
        shared_memory = Path("/dev/shm")
        if not shared_memory.is_dir() or shared_memory.stat().st_dev == self.base.stat().st_dev:
            self.skipTest("no distinct /dev/shm filesystem")
        profile = self.base / "profile"
        profile.mkdir()
        external = Path(tempfile.mkdtemp(prefix="adw-installer-", dir=shared_memory))
        self.addCleanup(shutil.rmtree, external, True)
        (profile / "skills").symlink_to(external, target_is_directory=True)

        result = self._run(profile, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different filesystems", result.stderr)
        self.assertFalse((profile / "plugins" / "adw").exists())

    def test_first_install_post_failure_removes_targets_and_restores_disabled_state(self) -> None:
        profile = self.base / "profile"
        result = self._run(profile, check=False, TEST_FAIL_POST="yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((profile / "plugins" / "adw").exists())
        self.assertFalse(any((profile / "skills" / "adw").glob("adw-*")))
        self.assertEqual(self.log.read_text().splitlines()[-1], "disable")

    def test_update_post_failure_restores_files_and_enabled_state(self) -> None:
        profile = self.base / "profile"
        self._run(profile)
        plugin = profile / "plugins" / "adw"
        (plugin / "sentinel").write_text("old-state\n")

        result = self._run(profile, check=False, TEST_FAIL_POST="yes", TEST_WAS_ENABLED="yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((plugin / "sentinel").read_text(), "old-state\n")
        self.assertEqual(self.log.read_text().splitlines()[-1], "enable")
        self.assertTrue((profile / "skills" / "adw" / "adw-core" / OWNER_MARKER).is_file())


if __name__ == "__main__":
    unittest.main()
