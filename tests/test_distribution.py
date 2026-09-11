from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "skills" / "adw" / "adw-core" / "assets" / "mise" / "v1"


def load_contract_module():
    path = CONTRACT_ROOT / "adw_contract.py"
    spec = importlib.util.spec_from_file_location("adw_contract_distribution", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_contract_module()

    def test_manifest_schema_requires_every_canonical_capability(self) -> None:
        schema = json.loads((CONTRACT_ROOT / "schemas" / "adw-task-manifest.schema.json").read_text())

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        capability_schema = schema["properties"]["capabilities"]
        self.assertEqual(set(self.contract.CANONICAL_TASKS), set(schema["properties"]["capabilities"]["required"]))
        capability_schemas = schema["properties"]["capabilities"]["properties"]
        for task, side_effect in self.contract.TASK_SIDE_EFFECTS.items():
            self.assertEqual(side_effect, capability_schemas[task]["properties"]["side_effect"]["const"])
        self.assertFalse(capability_schema["additionalProperties"])
        self.assertIn("path", schema["$defs"]["source"]["required"])

    def test_evidence_schema_has_the_normative_status_vocabulary(self) -> None:
        schema = json.loads((CONTRACT_ROOT / "schemas" / "adw-task-evidence.schema.json").read_text())

        statuses = set(schema["properties"]["status"]["enum"])
        self.assertEqual(self.contract.STATUSES, statuses)
        self.assertIn("effective_source", schema["required"])
        self.assertFalse(schema["additionalProperties"])
        arguments = schema["properties"]["arguments"]
        self.assertFalse(arguments["additionalProperties"])
        self.assertEqual({"environment"}, set(arguments["properties"]))

    def test_generic_task_snapshot_defines_exact_canonical_abi(self) -> None:
        tasks = tomllib.loads((CONTRACT_ROOT / "tasks.toml").read_text())

        self.assertEqual(self.contract.CANONICAL_TASKS, set(tasks))
        self.assertIn("adw_contract.py describe", tasks["adw:describe"]["run"])
        self.assertIn("adw_contract.py check", tasks["adw:check"]["run"])
        for task_name, task in tasks.items():
            self.assertIn("description", task, task_name)
            self.assertNotIn("Dokploy", task["run"])
            self.assertNotIn("docker", task["run"].lower())
            if task_name in self.contract.ENVIRONMENT_TASKS:
                self.assertIn("<environment>", task.get("usage", ""), task_name)
                self.assertIn("$usage_environment", task["run"], task_name)

    def test_fixtures_conform_to_validator_and_have_all_tasks(self) -> None:
        for fixture_name in ("library", "service"):
            fixture = CONTRACT_ROOT / "fixtures" / fixture_name
            manifest = json.loads((fixture / ".hermes" / "adw-task-manifest.json").read_text())
            task_names = set(json.loads((fixture / "task-names.json").read_text()))

            self.assertEqual([], self.contract.validate_manifest(manifest), fixture_name)
            self.assertEqual(self.contract.CANONICAL_TASKS, task_names, fixture_name)

    def test_project_template_sets_hard_minimum_and_layer_order(self) -> None:
        template = tomllib.loads((CONTRACT_ROOT / "templates" / "mise.toml").read_text())

        self.assertEqual("2026.9.5", template["min_version"]["hard"])
        self.assertEqual("2026.9.5", template["vars"]["adw_mise_tested_version"])
        self.assertEqual(
            [
                "mise-helper/vendor/agentic-delivery/tasks.toml",
                "mise-helper/vendor/context/tasks.toml",
                "mise-helper/tasks.toml",
            ],
            template["task_config"]["includes"],
        )
        self.assertNotIn("adw_default_environment", template["vars"])
        self.assertNotIn("token", (CONTRACT_ROOT / "templates" / "mise.toml").read_text().lower())

    def test_variable_templates_separate_project_and_context_ownership(self) -> None:
        project = tomllib.loads((CONTRACT_ROOT / "templates" / "project-vars.example.toml").read_text())["vars"]
        context = tomllib.loads((CONTRACT_ROOT / "templates" / "context-vars.example.toml").read_text())["vars"]

        self.assertIn("adw_project_id", project)
        self.assertIn("adw_component_id", project)
        self.assertIn("adw_context_id", context)
        self.assertIn("adw_remote_host_alias", context)
        self.assertNotIn("adw_remote_host_alias", project)
        self.assertFalse(any("environment" in key and "default" in key for key in project))

    def test_generation_guide_covers_required_generated_layout_and_safety(self) -> None:
        guide = (CONTRACT_ROOT / "generation-guide.md").read_text()

        for token in (
            ".hermes/adw-task-manifest.json",
            "mise-helper/",
            "mise-helper/vendor/agentic-delivery/",
            ".hermes/evidence/",
            "adw:check",
            "unsupported",
            "reviewable diff",
            "must not execute",
        ):
            self.assertIn(token, guide)

    def test_contract_spec_records_ci_adw_and_hotfix_boundaries(self) -> None:
        contract = (CONTRACT_ROOT / "contract.md").read_text()

        for token in (
            "CI calls mise tasks directly",
            "adw:verify:minimal",
            "adw:verify:full",
            "adw:hotfix:apply",
            "clean working tree",
            "remote-tracking",
            "identity",
            "health/readiness",
            "exit code 0",
            "No automatic rollback",
        ):
            self.assertIn(token, contract)

    def test_operational_skills_use_contract_tasks_without_provider_commands(self) -> None:
        skills_root = ROOT / "skills" / "adw"
        core = (skills_root / "adw-core" / "SKILL.md").read_text()
        implementation = (skills_root / "do-impl" / "SKILL.md").read_text()
        delegated = (skills_root / "do-impl-delegate" / "SKILL.md").read_text()
        testing = (skills_root / "test-feature" / "SKILL.md").read_text()
        merging = (skills_root / "merge-feature" / "SKILL.md").read_text()
        regression = (skills_root / "validate-regression" / "SKILL.md").read_text()
        rollback = (skills_root / "rollback-deployment" / "SKILL.md").read_text()
        adapter_template = (skills_root / "adw-core" / "templates" / "project_adw_adapter.md").read_text()

        self.assertIn("assets/mise/v1/generation-guide.md", core)
        self.assertIn("There is no ad-hoc fallback", core)
        self.assertIn("mise run adw:check", implementation)
        self.assertIn("mise run adw:verify:minimal", implementation)
        self.assertIn("mise run adw:check", delegated)
        self.assertIn("mise run adw:verify:minimal", delegated)
        for task in (
            "adw:deploy:config:plan",
            "adw:deploy:config:apply",
            "adw:deploy:apply",
            "adw:health",
            "adw:readiness",
            "adw:e2e",
            "adw:validate-deployment",
        ):
            self.assertIn(task, testing)
            self.assertIn(task, merging)
        self.assertIn("adw:verify:full", regression)
        self.assertIn("adw:e2e", regression)
        self.assertIn("adw:deploy:config:plan", rollback)
        self.assertIn("adw:deploy:apply", rollback)
        self.assertIn(".hermes/adw-task-manifest.json", adapter_template)
        self.assertIn("mise run adw:check", adapter_template)
        self.assertNotIn("Dokploy", merging)
        self.assertNotIn("Dokploy", rollback)

    def test_greenfield_necessity_log_accounts_for_every_top_level_artifact(self) -> None:
        log = (ROOT / "plans" / "issue-7-greenfield-necessity.md").read_text()

        for token in ("contracts/mise/v1/", "tests/", "README.md", ".gitignore"):
            self.assertIn(token, log)


if __name__ == "__main__":
    unittest.main()
