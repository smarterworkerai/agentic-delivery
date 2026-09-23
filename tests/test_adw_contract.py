from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "adw" / "adw-core" / "assets" / "mise" / "v2" / "adw_contract.py"


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
        "schema_version": "2.0.0",
        "contract": {
            "name": "adw-mise-task-contract",
            "version": "2.0.0",
            "compatible": ">=2.0.0,<3.0.0",
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
        value = manifest or valid_manifest()
        for source in value.get("sources", []):
            source_path = source.get("path") if isinstance(source, dict) else None
            if not isinstance(source_path, str):
                continue
            parsed = Path(source_path)
            if parsed.is_absolute() or ".." in parsed.parts:
                continue
            candidate = self.root / parsed
            candidate.parent.mkdir(parents=True, exist_ok=True)
            if not candidate.exists():
                candidate.write_text(f"# test source: {source_path}\n", encoding="utf-8")
            checksum = "sha256:" + hashlib.sha256(candidate.read_bytes()).hexdigest()
            source["checksum"] = checksum
            for capability in value.get("capabilities", {}).values():
                capability_source = capability.get("source") if isinstance(capability, dict) else None
                if isinstance(capability_source, dict) and capability_source.get("path") == source_path:
                    capability_source["checksum"] = checksum
        path = self.root / ".hermes" / "adw-task-manifest.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def catalog_metadata(self, manifest: dict | None = None) -> tuple[set[str], dict[str, str], dict[str, str]]:
        value = manifest or valid_manifest()
        names = set(value["capabilities"])
        sources = {task: capability["source"]["path"] for task, capability in value["capabilities"].items()}
        usages = {
            task: 'arg "<environment>"' if task in self.contract.ENVIRONMENT_TASKS else ""
            for task in names
        }
        return names, sources, usages

    def read_only_evidence_files(self) -> list[Path]:
        return list((self.root / ".hermes" / "evidence").glob("*/*.json"))

    def test_v2_rejects_v1_capabilities_and_contract(self) -> None:
        manifest = valid_manifest()
        self.assertIn("adw:test:integration:fast", self.contract.CANONICAL_TASKS)
        self.assertIn("adw:test:integration:full", self.contract.CANONICAL_TASKS)
        self.assertIn("adw:test:e2e:fast", self.contract.CANONICAL_TASKS)
        self.assertIn("adw:test:e2e:full", self.contract.CANONICAL_TASKS)
        for retired in ("adw:test:integration", "adw:e2e"):
            self.assertNotIn(retired, self.contract.CANONICAL_TASKS)
            manifest["capabilities"][retired] = manifest["capabilities"]["adw:build"]
        self.assertTrue(any(f["code"] == "capabilities.name" for f in self.contract.validate_manifest(manifest)))
        del manifest["capabilities"]["adw:test:integration"]
        del manifest["capabilities"]["adw:e2e"]
        manifest["contract"]["version"] = "1.0.0"
        self.assertTrue(any(f["code"] == "contract.version" for f in self.contract.validate_manifest(manifest)))

    def test_deployment_aggregate_cannot_hide_optional_e2e(self) -> None:
        manifest = valid_manifest()
        manifest["capabilities"]["adw:validate-deployment"].update(status="supported", environments=["preview"])
        self.write_manifest(manifest)
        marker = self.root / "ran"
        for optional in ("adw:test:e2e:fast", "adw:test:e2e:full", "adw:test:integration:full"):
            with self.subTest(optional=optional):
                result = self.contract.run_command(
                    self.root, "adw:validate-deployment",
                    ["python3", "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"],
                    environment="preview", children=[optional],
                )
                self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
                self.assertFalse(marker.exists())

    def test_v2_catalog_rejects_retired_aliases(self) -> None:
        manifest = valid_manifest()
        self.write_manifest(manifest)
        names, sources, usages = self.catalog_metadata(manifest)
        names.update({"adw:test:integration", "adw:e2e"})
        result = self.contract.check(self.root, names, sources, usages)
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertEqual(2, sum(item["code"] == "task.retired" for item in result.evidence["findings"]))

    def test_optional_suites_cannot_enter_verification_graph(self) -> None:
        manifest = valid_manifest()
        for optional in ("adw:test:integration:full", "adw:test:e2e:fast", "adw:test:e2e:full"):
            for graph in ("minimal", "full"):
                with self.subTest(optional=optional, graph=graph):
                    candidate = json.loads(json.dumps(manifest))
                    candidate["verification"][graph].append(optional)
                    self.assertTrue(any(f["code"] == "verification.child" for f in self.contract.validate_manifest(candidate)))

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
        task_names, task_sources, task_usages = self.catalog_metadata()

        result = self.contract.check(
            self.root,
            task_names=task_names,
            task_sources=task_sources,
            task_usages=task_usages,
            run_id="run-check",
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual("passed", result.evidence["status"])

    def test_check_rejects_incomplete_injected_catalog_metadata(self) -> None:
        self.write_manifest()

        result = self.contract.check(
            self.root,
            task_names=self.contract.CANONICAL_TASKS,
            run_id="run-incomplete-catalog",
        )

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        codes = {finding["code"] for finding in result.evidence["findings"]}
        self.assertIn("task.source", codes)
        self.assertIn("task.signature", codes)

    def test_check_rejects_missing_declared_task(self) -> None:
        self.write_manifest()
        task_names = set(valid_manifest()["capabilities"]) - {"adw:build"}

        result = self.contract.check(self.root, task_names=task_names, run_id="run-task-missing")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertEqual("contract-error", result.evidence["status"])
        self.assertTrue(any("adw:build" in finding["message"] for finding in result.evidence["findings"]))

    def test_check_rejects_omitted_canonical_capability(self) -> None:
        manifest = valid_manifest()
        del manifest["capabilities"]["adw:test:e2e:fast"]
        self.write_manifest(manifest)

        result = self.contract.check(self.root, task_names=set(self.contract.CANONICAL_TASKS), run_id="run-capability-missing")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertTrue(any("adw:test:e2e:fast" in finding["message"] for finding in result.evidence["findings"]))

    def test_check_rejects_source_path_escape_even_with_registered_source(self) -> None:
        manifest = valid_manifest()
        project_source = next(source for source in manifest["sources"] if source["layer"] == "project")
        project_source["path"] = "../outside.toml"
        for capability in manifest["capabilities"].values():
            if capability["source"]["layer"] == "project":
                capability["source"] = dict(project_source)
        self.write_manifest(manifest)
        names, sources, usages = self.catalog_metadata(manifest)

        result = self.contract.check(self.root, names, sources, usages)

        self.assertEqual("contract-error", result.evidence["status"])
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertTrue(any(finding["code"] == "source.path" for finding in result.evidence["findings"]))

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
        task_usages = self.catalog_metadata(manifest)[2]

        passed = self.contract.check(
            self.root,
            task_names=self.contract.CANONICAL_TASKS,
            task_sources=task_sources,
            task_usages=task_usages,
            run_id="run-checksum-pass",
        )
        project_path.write_text("drifted", encoding="utf-8")
        failed = self.contract.check(
            self.root,
            task_names=self.contract.CANONICAL_TASKS,
            task_sources=task_sources,
            task_usages=task_usages,
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

    def test_verification_graph_rejects_mutating_and_recursive_children(self) -> None:
        manifest = valid_manifest()
        manifest["verification"]["minimal"] = ["adw:build", "adw:deploy:apply"]
        manifest["verification"]["full"] = ["adw:build", "adw:verify:full"]

        findings = self.contract.validate_manifest(manifest)

        self.assertTrue(any(item["code"] == "verification.child" and "adw:deploy:apply" in item["message"] for item in findings))
        self.assertTrue(any(item["code"] == "verification.child" and "adw:verify:full" in item["message"] for item in findings))

    def test_dependency_free_validator_matches_closed_schema_constraints(self) -> None:
        cases = []
        empty_root = valid_manifest()
        empty_root["evidence"]["root"] = ""
        cases.append((empty_root, "evidence.root"))
        unknown_top = valid_manifest()
        unknown_top["unexpected"] = True
        cases.append((unknown_top, "schema.additional"))
        unknown_source = valid_manifest()
        unknown_source["sources"][0]["unexpected"] = True
        cases.append((unknown_source, "source.additional"))
        unknown_capability = valid_manifest()
        unknown_capability["capabilities"]["adw:build"]["unexpected"] = True
        cases.append((unknown_capability, "capability.additional"))
        duplicate_graph = valid_manifest()
        duplicate_graph["verification"]["minimal"] = ["adw:build", "adw:build"]
        cases.append((duplicate_graph, "verification.unique"))
        duplicate_secret = valid_manifest()
        duplicate_secret["required_secret_env"].append("EXAMPLE_API_TOKEN")
        cases.append((duplicate_secret, "secret.unique"))

        for manifest, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                findings = self.contract.validate_manifest(manifest)
                self.assertTrue(any(item["code"] == expected_code for item in findings), findings)

    def test_manifest_rejects_incompatible_or_non_exact_contract_version(self) -> None:
        incompatible = valid_manifest()
        incompatible["contract"]["compatible"] = ">=1.0.0,<2.0.0"
        self.write_manifest(incompatible)
        range_result = self.contract.check(
            project_root=self.root,
            task_names=self.contract.CANONICAL_TASKS,
        )
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, range_result.exit_code)
        self.assertTrue(any(item["code"] == "contract.compatible" for item in range_result.evidence["findings"]))

        non_exact = valid_manifest()
        non_exact["contract"]["version"] = "2.1.0"
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

        task_names, task_sources, task_usages = self.catalog_metadata(manifest)
        passed = self.contract.check(
            project_root=self.root,
            task_names=task_names,
            task_sources=task_sources,
            task_usages=task_usages,
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
        task_usages = {
            task: ('notarg "<environment>"' if task in self.contract.ENVIRONMENT_TASKS else "")
            for task in self.contract.CANONICAL_TASKS
        }

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
        manifest["capabilities"]["adw:describe"]["source"]["api_token"] = "nested-secret-value"
        self.write_manifest(manifest)

        result = self.contract.check(self.root, task_names=set(manifest["capabilities"]), run_id="run-invalid")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        messages = "\n".join(item["message"] for item in result.evidence["findings"])
        self.assertIn("production", messages)
        self.assertIn("secret-bearing", messages)
        self.assertNotIn("plain-text-secret", json.dumps(result.evidence))
        self.assertNotIn("nested-secret-value", json.dumps(result.evidence))

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

        child = self.contract.run_command(
            self.root,
            "adw:build",
            ["python3", "-c", "print('child ok')"],
            run_id="run-command-pass",
        )
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

        self.assertEqual(0, child.exit_code)
        self.assertEqual(0, passed.exit_code)
        self.assertEqual("passed", passed.evidence["status"])
        self.assertEqual(["adw:build"], passed.evidence["children"])
        self.assertEqual(self.contract.EXIT_FAILED, failed.exit_code)
        self.assertEqual("failed", failed.evidence["status"])
        serialized = json.dumps(failed.evidence)
        self.assertNotIn("sensitive-argument", serialized)
        self.assertNotIn("raise SystemExit", serialized)

    def test_run_command_launch_error_overwrites_no_passed_preflight(self) -> None:
        self.write_manifest()

        result = self.contract.run_command(
            self.root,
            "adw:build",
            [str(self.root)],
            run_id="run-launch-error",
        )

        self.assertEqual(self.contract.EXIT_FAILED, result.exit_code)
        self.assertEqual("failed", result.evidence["status"])
        evidence = json.loads(
            (self.root / ".hermes" / "evidence" / "run-launch-error" / "adw_build.json").read_text()
        )
        self.assertEqual("failed", evidence["status"])
        self.assertEqual("command.launch", evidence["findings"][0]["code"])

    def test_verification_aggregate_requires_exact_graph_and_child_evidence(self) -> None:
        self.write_manifest()
        marker = self.root / "must-not-run"

        wrong_graph = self.contract.run_command(
            self.root,
            "adw:verify:minimal",
            ["python3", "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"],
            run_id="run-wrong-graph",
            children=["adw:lint"],
        )
        missing_evidence = self.contract.run_command(
            self.root,
            "adw:verify:minimal",
            ["python3", "-c", "pass"],
            run_id="run-missing-child",
            children=["adw:build"],
        )

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, wrong_graph.exit_code)
        self.assertFalse(marker.exists())
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, missing_evidence.exit_code)
        self.assertTrue(
            any(item["code"] == "evidence.child_missing" for item in missing_evidence.evidence["findings"])
        )

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

    def test_unsupported_stub_blocks_when_manifest_is_missing(self) -> None:
        result = self.contract.unsupported(self.root, "adw:lint", run_id="run-unsupported-missing")

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertEqual("blocked", result.evidence["status"])

    def test_unsupported_stub_rejects_invalid_manifest(self) -> None:
        manifest = valid_manifest()
        manifest["schema_version"] = "999.0.0"
        self.write_manifest(manifest)

        result = self.contract.unsupported(self.root, "adw:lint", run_id="run-unsupported-invalid")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertEqual("contract-error", result.evidence["status"])

    def test_require_turns_unsupported_into_blocked(self) -> None:
        self.write_manifest()

        result = self.contract.require(self.root, "adw:lint", run_id="run-required")

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertEqual("blocked", result.evidence["status"])

    def test_require_rejects_invalid_manifest_before_capability_use(self) -> None:
        manifest = valid_manifest()
        manifest["schema_version"] = "999.0.0"
        self.write_manifest(manifest)

        result = self.contract.require(self.root, "adw:build", run_id="run-require-invalid")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertEqual("contract-error", result.evidence["status"])

    def test_run_command_propagates_one_generated_run_id_to_child(self) -> None:
        self.write_manifest()
        marker = self.root / "child-run-id"

        result = self.contract.run_command(
            self.root,
            "adw:build",
            [
                "python3",
                "-c",
                "import os, pathlib; pathlib.Path('child-run-id').write_text(os.environ.get('ADW_RUN_ID', ''))",
            ],
        )

        self.assertEqual(0, result.exit_code)
        self.assertEqual(result.evidence["run_id"], marker.read_text(encoding="utf-8"))
        evidence = list((self.root / ".hermes" / "evidence").glob("*/*"))
        self.assertEqual(1, len(evidence))

    def test_run_command_normalizes_supported_failure_to_exit_one(self) -> None:
        self.write_manifest()

        result = self.contract.run_command(
            self.root,
            "adw:build",
            ["python3", "-c", "raise SystemExit(7)"],
            run_id="run-normalized-failure",
        )

        self.assertEqual(self.contract.EXIT_FAILED, result.exit_code)
        self.assertEqual("failed", result.evidence["status"])
        self.assertIn("code 7", result.evidence["findings"][0]["message"])

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

    def test_invalid_run_id_is_rejected_without_path_escape(self) -> None:
        self.write_manifest()
        outside = self.root.parent / "outside-run-id"

        result = self.contract.describe(self.root, run_id="../../outside-run-id")

        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, result.exit_code)
        self.assertEqual("contract-error", result.evidence["status"])
        self.assertTrue(any(item["code"] == "evidence.run_id" for item in result.evidence["findings"]))
        self.assertFalse(outside.exists())
        self.assertTrue((self.root / ".hermes" / "evidence" / result.evidence["run_id"] / "adw_describe.json").exists())

    def test_target_is_optional_redacted_and_validated_before_child_execution(self) -> None:
        self.write_manifest()
        marker = self.root / "target-child-ran"

        no_target = self.contract.run_command(
            self.root, "adw:hotfix:apply", ["python3", "-c", "pass"], environment="preview", run_id="run-no-target"
        )
        targeted = self.contract.run_command(
            self.root, "adw:hotfix:apply", ["python3", "-c", "pass"], environment="preview", target="shadow-blue", run_id="run-target"
        )
        malformed = self.contract.run_command(
            self.root,
            "adw:hotfix:apply",
            ["python3", "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"],
            environment="preview",
            target="provider/namespace",
            run_id="run-malformed-target",
        )

        self.assertEqual(0, no_target.exit_code)
        self.assertNotIn("target", no_target.evidence["arguments"])
        self.assertEqual("shadow-blue", targeted.evidence["arguments"]["target"])
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, malformed.exit_code)
        self.assertFalse(marker.exists())
        self.assertTrue(any(item["code"] == "target.invalid" for item in malformed.evidence["findings"]))

    def test_context_check_uses_trusted_upstream_main_index(self) -> None:
        manifest = valid_manifest()
        manifest["capabilities"]["adw:context:check"]["status"] = "supported"
        manifest["context_freshness"] = {
            "policy": "require-current-compatible",
            "upstream": {
                "repository": "smarterworkerai/agentic-delivery",
                "branch": "main",
                "index_path": "releases/adw-mise-v2.json",
            },
        }
        self.write_manifest(manifest)
        index = {"schema_version": "1.0.0", "releases": [{
            "version": "2.0.1", "ref": "2" * 40,
            "checksum": manifest["sources"][0]["checksum"], "snapshot_path": "skills/adw/adw-core/assets/mise/v2",
        }]}

        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return json.dumps(index).encode("utf-8")

        from unittest.mock import patch
        with patch("urllib.request.urlopen", return_value=Response()) as fetch:
            result = self.contract.context_check(self.root, run_id="run-upstream-stale")

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertEqual("update-available", result.evidence["freshness"]["verdict"])
        self.assertIn("raw.githubusercontent.com/smarterworkerai/agentic-delivery/main/releases/adw-mise-v2.json", fetch.call_args.args[0].full_url)

    def test_context_check_is_read_only_and_strictly_fails_stale_fixture(self) -> None:
        manifest = valid_manifest()
        generic = manifest["sources"][0]
        manifest["capabilities"]["adw:context:check"]["status"] = "supported"
        manifest["capabilities"]["adw:context:sync"]["status"] = "supported"
        manifest["context_freshness"] = {
            "policy": "require-current-compatible",
            "upstream": {"repository": "smarterworkerai/agentic-delivery", "branch": "main", "index_path": "releases/adw-mise-v2.json"},
        }
        self.write_manifest(manifest)
        index = {
            "schema_version": "1.0.0",
            "releases": [{
                "version": "2.0.1", "ref": "2" * 40, "checksum": generic["checksum"],
                "snapshot_path": "skills/adw/adw-core/assets/mise/v2",
            }],
        }
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return json.dumps(index).encode("utf-8")
        before = self.root / "mise-helper" / "vendor" / "agentic-delivery" / "tasks.toml"
        before_bytes = before.read_bytes()

        from unittest.mock import patch
        with patch("urllib.request.urlopen", return_value=Response()):
            result = self.contract.context_check(self.root, run_id="run-context-stale")

        self.assertEqual(self.contract.EXIT_BLOCKED, result.exit_code)
        self.assertEqual("update-available", result.evidence["freshness"]["verdict"])
        self.assertEqual("2" * 40, result.evidence["freshness"]["latest"]["ref"])
        self.assertEqual(before_bytes, before.read_bytes())

    def test_context_check_rejects_moving_refs_and_sync_updates_only_local_vendor_and_manifest(self) -> None:
        manifest = valid_manifest()
        manifest["capabilities"]["adw:context:check"]["status"] = "supported"
        manifest["capabilities"]["adw:context:sync"]["status"] = "supported"
        manifest["context_freshness"] = {"policy": "advisory", "upstream": {"repository": "smarterworkerai/agentic-delivery", "branch": "main", "index_path": "releases/adw-mise-v2.json"}}
        self.write_manifest(manifest)
        snapshot_path = "skills/adw/adw-core/assets/mise/v2"
        snapshot_files = {"tasks.toml": b"new snapshot\n", "contract.md": b"snapshot contract\n"}
        checksum = "sha256:" + hashlib.sha256(snapshot_files["tasks.toml"]).hexdigest()
        index = {"schema_version": "1.0.0", "releases": [{"version": "2.0.1", "ref": "2" * 40, "checksum": checksum, "snapshot_path": snapshot_path}]}

        archive_buffer = io.BytesIO()
        with tarfile.open(fileobj=archive_buffer, mode="w:gz") as archive:
            for directory in (f"agentic-delivery-{'2' * 40}", f"agentic-delivery-{'2' * 40}/{snapshot_path}"):
                member = tarfile.TarInfo(directory)
                member.type = tarfile.DIRTYPE
                archive.addfile(member)
            for name, contents in snapshot_files.items():
                member = tarfile.TarInfo(f"agentic-delivery-{'2' * 40}/{snapshot_path}/{name}")
                member.size = len(contents)
                archive.addfile(member, io.BytesIO(contents))
        archive_bytes = archive_buffer.getvalue()

        class Response:
            def __init__(self, payload: bytes): self.payload = payload
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return self.payload
        def fetch(request, timeout):
            return Response(json.dumps(index).encode("utf-8") if request.full_url.endswith("releases/adw-mise-v2.json") else archive_bytes)
        from unittest.mock import patch
        with patch("urllib.request.urlopen", side_effect=fetch):
            sync = self.contract.context_sync(self.root, run_id="run-context-sync")
        saved = json.loads((self.root / ".hermes" / "adw-task-manifest.json").read_text(encoding="utf-8"))
        index["releases"][0]["ref"] = "main"
        with patch("urllib.request.urlopen", side_effect=fetch):
            rejected = self.contract.context_check(self.root, run_id="run-moving-ref")

        self.assertEqual(0, sync.exit_code)
        self.assertEqual("2" * 40, saved["sources"][0]["ref"])
        self.assertEqual("new snapshot\n", (self.root / "mise-helper" / "vendor" / "agentic-delivery" / "tasks.toml").read_text())
        self.assertEqual(self.contract.EXIT_CONTRACT_ERROR, rejected.exit_code)
        self.assertTrue(any(item["code"] == "freshness.release.ref" for item in rejected.evidence["findings"]))

    @staticmethod
    def _restore_env(name: str, value: str | None) -> None:
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value


if __name__ == "__main__":
    unittest.main()
