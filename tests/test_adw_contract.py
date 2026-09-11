from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "adw" / "adw-core" / "assets" / "mise" / "v1" / "adw_contract.py"


def load_contract_module():
    spec = importlib.util.spec_from_file_location("adw_contract", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_manifest() -> dict:
    generic_source = {
        "layer": "generic",
        "ref": "1111111111111111111111111111111111111111",
        "checksum": "sha256:" + "a" * 64,
        "path": "mise-helper/vendor/agentic-delivery/tasks.toml",
    }
    contract = load_contract_module()
    unsupported = {
        task: {
            "status": "unsupported",
            "side_effect": contract.TASK_SIDE_EFFECTS[task],
            "environments": [],
            "source": generic_source,
        }
        for task in load_contract_module().CANONICAL_TASKS
    }
    unsupported.update({
        "adw:describe": {
            "status": "supported",
            "side_effect": "read-only",
            "environments": [],
            "source": generic_source,
        },
        "adw:check": {
            "status": "supported",
            "side_effect": "read-only",
            "environments": [],
            "source": generic_source,
        },
        "adw:build": {
            "status": "supported",
            "side_effect": "local-write",
            "environments": [],
            "source": {"layer": "project", "ref": "HEAD", "checksum": "sha256:" + "b" * 64, "path": "mise-helper/tasks.toml"},
        },
        "adw:verify:minimal": {
            "status": "supported",
            "side_effect": "local-write",
            "environments": [],
            "source": {"layer": "project", "ref": "HEAD", "checksum": "sha256:" + "b" * 64, "path": "mise-helper/tasks.toml"},
        },
        "adw:verify:full": {
            "status": "supported",
            "side_effect": "local-write",
            "environments": [],
            "source": {"layer": "project", "ref": "HEAD", "checksum": "sha256:" + "b" * 64, "path": "mise-helper/tasks.toml"},
        },
        "adw:hotfix:apply": {
            "status": "supported",
            "side_effect": "remote-write",
            "environments": ["preview"],
            "source": {"layer": "project", "ref": "HEAD", "checksum": "sha256:" + "b" * 64, "path": "mise-helper/tasks.toml"},
        },
    })
    return {
        "schema_version": "1.0.0",
        "contract": {
            "name": "adw-mise-task-contract",
            "version": "1.0.0",
            "compatible": ">=1.0.0,<2.0.0",
        },
        "project": {"id": "example/service"},
        "evidence": {"root": ".hermes/evidence"},
        "environments": ["preview"],
        "sources": [
            generic_source,
            {
                "layer": "project",
                "ref": "HEAD",
                "checksum": "sha256:" + "b" * 64,
                "path": "mise-helper/tasks.toml",
            },
        ],
        "capabilities": unsupported,
        "verification": {
            "minimal": ["adw:build"],
            "full": ["adw:build"],
        },
        "required_secret_env": ["EXAMPLE_API_TOKEN"],
    }


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract_module()
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        (self.root / ".hermes").mkdir()

    def write_manifest(self, manifest: dict | None = None) -> Path:
        path = self.root / ".hermes" / "adw-task-manifest.json"
        path.write_text(json.dumps(manifest or valid_manifest()), encoding="utf-8")
        return path

    def read_only_evidence_files(self) -> list[Path]:
        return list((self.root / ".hermes" / "evidence").glob("*/*.json"))

    def test_describe_emits_manifest_summary_and_atomic_evidence(self) -> None:
        self.write_manifest()

        result = self.contract.describe(self.root, run_id="run-describe")

        self.assertEqual(0, result.exit_code)
        self.assertEqual("passed", result.evidence["status"])
        self.assertEqual("example/service", result.payload["project"])
        self.assertEqual(["preview"], result.payload["environments"])
        self.assertEqual("project", result.payload["capabilities"]["adw:build"]["source"]["layer"])
        files = self.read_only_evidence_files()
        self.assertEqual(1, len(files))
        self.assertFalse(any(path.suffix == ".tmp" for path in files[0].parent.iterdir()))

    def test_check_missing_manifest_is_blocked(self) -> None:
        result = self.contract.check(self.root, task_names={"adw:describe", "adw:check"}, run_id="run-missing")

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertEqual("blocked", result.evidence["status"])
        self.assertIn("manifest", result.evidence["findings"][0]["message"].lower())

    def test_check_validates_declared_tasks_and_aggregate_requirements(self) -> None:
        self.write_manifest()
        task_names = set(valid_manifest()["capabilities"])

        result = self.contract.check(self.root, task_names=task_names, run_id="run-check")

        self.assertEqual(0, result.exit_code)
        self.assertEqual("passed", result.evidence["status"])

    def test_check_rejects_missing_declared_task(self) -> None:
        self.write_manifest()
        task_names = set(valid_manifest()["capabilities"]) - {"adw:build"}

        result = self.contract.check(self.root, task_names=task_names, run_id="run-task-missing")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertEqual("contract-error", result.evidence["status"])
        self.assertTrue(any("adw:build" in finding["message"] for finding in result.evidence["findings"]))

    def test_check_rejects_omitted_canonical_capability(self) -> None:
        manifest = valid_manifest()
        del manifest["capabilities"]["adw:e2e"]
        self.write_manifest(manifest)

        result = self.contract.check(self.root, task_names=set(self.contract.CANONICAL_TASKS), run_id="run-capability-missing")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertTrue(any("adw:e2e" in finding["message"] for finding in result.evidence["findings"]))

    def test_check_rejects_source_checksum_drift(self) -> None:
        manifest = valid_manifest()
        generic_path = self.root / "mise-helper" / "vendor" / "agentic-delivery" / "tasks.toml"
        project_path = self.root / "mise-helper" / "tasks.toml"
        generic_path.parent.mkdir(parents=True)
        generic_path.write_text("generic", encoding="utf-8")
        project_path.write_text("project", encoding="utf-8")
        import hashlib
        checksums = {
            "generic": "sha256:" + hashlib.sha256(b"generic").hexdigest(),
            "project": "sha256:" + hashlib.sha256(b"project").hexdigest(),
        }
        for source in manifest["sources"]:
            source["checksum"] = checksums[source["layer"]]
        for capability in manifest["capabilities"].values():
            capability["source"]["checksum"] = checksums[capability["source"]["layer"]]
        self.write_manifest(manifest)
        task_sources = {
            task: manifest["capabilities"][task]["source"]["path"]
            for task in self.contract.CANONICAL_TASKS
        }

        passed = self.contract.check(
            self.root,
            task_names=self.contract.CANONICAL_TASKS,
            task_sources=task_sources,
            run_id="run-checksum-pass",
        )
        project_path.write_text("drifted", encoding="utf-8")
        failed = self.contract.check(
            self.root,
            task_names=self.contract.CANONICAL_TASKS,
            task_sources=task_sources,
            run_id="run-checksum-fail",
        )

        self.assertEqual(0, passed.exit_code)
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, failed.exit_code)
        self.assertTrue(any("checksum" in finding["message"] for finding in failed.evidence["findings"]))

    def test_verification_graph_enforces_full_coverage_and_minimal_smoke(self) -> None:
        incomplete_full = valid_manifest()
        incomplete_full["capabilities"]["adw:lint"] = {
            "status": "supported",
            "side_effect": "local-write",
            "environments": [],
            "source": incomplete_full["sources"][1],
        }
        self.write_manifest(incomplete_full)
        full_result = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, full_result.exit_code)
        self.assertTrue(any(item["code"] == "verification.full" for item in full_result.evidence["findings"]))

        invalid_minimal = valid_manifest()
        invalid_minimal["capabilities"]["adw:lint"] = {
            "status": "supported",
            "side_effect": "local-write",
            "environments": [],
            "source": invalid_minimal["sources"][1],
        }
        invalid_minimal["verification"]["minimal"] = ["adw:lint"]
        invalid_minimal["verification"]["full"].append("adw:lint")
        self.write_manifest(invalid_minimal)
        minimal_result = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, minimal_result.exit_code)
        self.assertTrue(any(item["code"] == "verification.minimal" for item in minimal_result.evidence["findings"]))

    def test_manifest_rejects_incompatible_or_non_exact_contract_version(self) -> None:
        incompatible = valid_manifest()
        incompatible["contract"]["compatible"] = ">=2.0.0,<3.0.0"
        self.write_manifest(incompatible)
        range_result = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, range_result.exit_code)
        self.assertTrue(any(item["code"] == "contract.compatible" for item in range_result.evidence["findings"]))

        non_exact = valid_manifest()
        non_exact["contract"]["version"] = "1.1.0"
        self.write_manifest(non_exact)
        version_result = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, version_result.exit_code)
        self.assertTrue(any(item["code"] == "contract.version" for item in version_result.evidence["findings"]))

    def test_context_source_exact_pin_and_provenance_are_validated(self) -> None:
        manifest = valid_manifest()
        context_source = {
            "layer": "context",
            "ref": "2222222222222222222222222222222222222222",
            "checksum": "sha256:" + "c" * 64,
            "path": "mise-helper/vendor/example-context/tasks.toml",
        }
        manifest["sources"].insert(1, context_source)
        manifest["capabilities"]["adw:context:check"] = {
            "status": "supported",
            "side_effect": "read-only",
            "environments": [],
            "source": context_source,
        }
        self.write_manifest(manifest)

        passed = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )
        self.assertEqual(0, passed.exit_code)

        manifest["sources"][1]["ref"] = "mutable-context-tag"
        self.write_manifest(manifest)
        failed = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, failed.exit_code)
        self.assertTrue(any(item["code"] == "source.ref" for item in failed.evidence["findings"]))

    def test_manifest_rejects_incorrect_canonical_side_effect(self) -> None:
        manifest = valid_manifest()
        manifest["capabilities"]["adw:deploy:apply"]["side_effect"] = "read-only"
        self.write_manifest(manifest)

        result = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertTrue(any(item["code"] == "capability.side_effect" for item in result.evidence["findings"]))

    def test_manifest_rejects_mutable_shared_source_ref(self) -> None:
        manifest = valid_manifest()
        generic = next(source for source in manifest["sources"] if source["layer"] == "generic")
        generic["ref"] = "v1.0.0"
        self.write_manifest(manifest)

        result = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertTrue(any(item["code"] == "source.ref" for item in result.evidence["findings"]))

    def test_check_rejects_missing_environment_input_signature(self) -> None:
        manifest = valid_manifest()
        self.write_manifest(manifest)
        task_usages = {task: "" for task in self.contract.CANONICAL_TASKS}

        result = self.contract.check(
            self.root,
            task_names=self.contract.CANONICAL_TASKS,
            task_usages=task_usages,
            run_id="run-signature",
        )

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertTrue(any("<environment>" in finding["message"] for finding in result.evidence["findings"]))

    def test_check_rejects_implementation_source_mismatch(self) -> None:
        manifest = valid_manifest()
        for capability in manifest["capabilities"].values():
            capability["source"]["path"] = "mise-helper/vendor/agentic-delivery/tasks.toml"
        manifest["capabilities"]["adw:build"]["source"] = {
            "layer": "project",
            "ref": "local",
            "checksum": "sha256:" + "b" * 64,
            "path": "mise-helper/tasks.toml",
        }
        self.write_manifest(manifest)
        task_sources = {
            task: "mise-helper/vendor/agentic-delivery/tasks.toml"
            for task in self.contract.CANONICAL_TASKS
        }

        result = self.contract.check(
            self.root,
            task_names=self.contract.CANONICAL_TASKS,
            task_sources=task_sources,
            run_id="run-source-mismatch",
        )

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertTrue(any("adw:build" in finding["message"] for finding in result.evidence["findings"]))
        self.assertTrue(any("source" in finding["message"] for finding in result.evidence["findings"]))

    def test_manifest_rejects_supported_environment_task_without_scope(self) -> None:
        manifest = valid_manifest()
        manifest["capabilities"]["adw:hotfix:apply"]["environments"] = []

        findings = self.contract.validate_manifest(manifest)

        self.assertTrue(any("environment" in finding["message"] for finding in findings))
        self.assertTrue(any("adw:hotfix:apply" in finding["message"] for finding in findings))

    def test_require_blocks_missing_environment_for_environment_task(self) -> None:
        self.write_manifest()

        result = self.contract.require(self.root, "adw:hotfix:apply", run_id="run-environment-missing")

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertTrue(any("environment" in finding["message"] for finding in result.evidence["findings"]))

    def test_manifest_rejects_capability_source_missing_from_registry(self) -> None:
        manifest = valid_manifest()
        manifest["sources"] = [source for source in manifest["sources"] if source["layer"] == "generic"]

        findings = self.contract.validate_manifest(manifest)

        self.assertTrue(any("registry" in finding["message"] for finding in findings))
        self.assertTrue(any("adw:build" in finding["message"] for finding in findings))

    def test_check_rejects_unknown_environment_and_secret_value_fields(self) -> None:
        manifest = valid_manifest()
        manifest["capabilities"]["adw:hotfix:apply"]["environments"] = ["production"]
        manifest["api_token"] = "plain-text-secret"
        self.write_manifest(manifest)

        result = self.contract.check(self.root, task_names=set(manifest["capabilities"]), run_id="run-invalid")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        messages = "\n".join(item["message"] for item in result.evidence["findings"])
        self.assertIn("production", messages)
        self.assertIn("secret-bearing", messages)
        self.assertNotIn("plain-text-secret", json.dumps(result.evidence))

    def test_check_rejects_escaping_evidence_root_and_writes_safe_evidence(self) -> None:
        manifest = valid_manifest()
        manifest["evidence"]["root"] = "../../outside"
        self.write_manifest(manifest)

        result = self.contract.check(self.root, task_names=set(manifest["capabilities"]), run_id="run-path-escape")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertTrue(any("evidence.root" in finding["message"] for finding in result.evidence["findings"]))
        self.assertTrue((self.root / ".hermes" / "evidence" / "run-path-escape" / "adw_check.json").exists())
        self.assertFalse((self.root.parent / "outside").exists())

    def test_run_command_records_pass_and_failure_without_arguments(self) -> None:
        self.write_manifest()

        passed = self.contract.run_command(
            self.root,
            "adw:verify:minimal",
            ["python3", "-c", "print('ok')"],
            run_id="run-command-pass",
            children=["adw:build"],
        )
        failed = self.contract.run_command(
            self.root,
            "adw:build",
            ["python3", "-c", "raise SystemExit(7)", "sensitive-argument"],
            run_id="run-command-fail",
        )

        self.assertEqual(0, passed.exit_code)
        self.assertEqual("passed", passed.evidence["status"])
        self.assertEqual(["adw:build"], passed.evidence["children"])
        self.assertEqual(7, failed.exit_code)
        self.assertEqual("failed", failed.evidence["status"])
        serialized = json.dumps(failed.evidence)
        self.assertNotIn("sensitive-argument", serialized)
        self.assertNotIn("raise SystemExit", serialized)

    def test_run_command_does_not_execute_unsupported_capability(self) -> None:
        self.write_manifest()
        marker = self.root / "must-not-exist"

        result = self.contract.run_command(
            self.root,
            "adw:lint",
            ["python3", "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"],
            run_id="run-command-blocked",
        )

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertEqual("blocked", result.evidence["status"])
        self.assertFalse(marker.exists())

    def test_unsupported_stub_returns_zero_and_unsupported_evidence(self) -> None:
        self.write_manifest()

        result = self.contract.unsupported(
            self.root,
            "adw:lint",
            run_id="run-unsupported",
            environment="preview",
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual("unsupported", result.evidence["status"])
        self.assertEqual("adw:lint", result.evidence["task"])

    def test_require_turns_unsupported_into_blocked(self) -> None:
        self.write_manifest()

        result = self.contract.require(self.root, "adw:lint", run_id="run-required")

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertEqual("blocked", result.evidence["status"])

    def test_environment_is_validated_before_hotfix_capability_use(self) -> None:
        self.write_manifest()

        result = self.contract.require(
            self.root,
            "adw:hotfix:apply",
            environment="production",
            run_id="run-environment",
        )

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertEqual("blocked", result.evidence["status"])
        self.assertIn("production", result.evidence["findings"][0]["message"])

    def test_run_id_can_be_inherited_from_environment(self) -> None:
        self.write_manifest()
        previous = os.environ.get("ADW_RUN_ID")
        os.environ["ADW_RUN_ID"] = "inherited-run"
        self.addCleanup(self._restore_env, "ADW_RUN_ID", previous)

        result = self.contract.describe(self.root)

        self.assertEqual("inherited-run", result.evidence["run_id"])

    @staticmethod
    def _restore_env(name: str, value: str | None) -> None:
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value


if __name__ == "__main__":
    unittest.main()
