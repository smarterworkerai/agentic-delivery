from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "skills" / "adw" / "adw-core" / "assets" / "mise" / "v2"
LEGACY_MAIN_SHA = "8c6e649af2067f80b0fbe2ec12f07c2b3d02e3f0"


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
        self.assertNotIn("adw:e2e", capability_schemas)
        self.assertNotIn("adw:test:integration", capability_schemas)
        for optional in ("adw:test:integration:full", "adw:test:e2e:fast", "adw:test:e2e:full"):
            self.assertIn(optional, capability_schemas)
            self.assertNotIn(optional, schema["properties"]["verification"]["properties"]["full"]["items"]["enum"])
        self.assertIn("path", schema["$defs"]["source"]["required"])
        root_schema = schema["properties"]["evidence"]["properties"]["root"]
        self.assertRegex("custom/evidence", root_schema["pattern"])
        self.assertNotRegex("../outside", root_schema["pattern"])
        expected_verification_tasks = sorted(self.contract.LOCAL_QUALITY_TASKS)
        self.assertEqual(expected_verification_tasks, schema["properties"]["verification"]["properties"]["minimal"]["items"]["enum"])
        self.assertEqual(expected_verification_tasks, schema["properties"]["verification"]["properties"]["full"]["items"]["enum"])

    def test_evidence_schema_has_the_normative_status_vocabulary(self) -> None:
        schema = json.loads((CONTRACT_ROOT / "schemas" / "adw-task-evidence.schema.json").read_text())

        statuses = set(schema["properties"]["status"]["enum"])
        self.assertEqual(self.contract.STATUSES, statuses)
        self.assertIn("effective_source", schema["required"])
        self.assertFalse(schema["additionalProperties"])
        arguments = schema["properties"]["arguments"]
        self.assertFalse(arguments["additionalProperties"])
        self.assertEqual({"environment", "target"}, set(arguments["properties"]))
        self.assertEqual("^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$", schema["properties"]["run_id"]["pattern"])

    def test_v2_release_index_publishes_immutable_checksum_verified_snapshot(self) -> None:
        index = json.loads((ROOT / "releases" / "adw-mise-v2.json").read_text())

        self.assertEqual("1.0.0", index["schema_version"])
        self.assertTrue(index["releases"])
        for release in index["releases"]:
            self.assertEqual({"version", "ref", "checksum", "snapshot_path", "required"}, set(release))
            self.assertRegex(release["version"], r"^\d+\.\d+\.\d+$")
            self.assertRegex(release["ref"], r"^[0-9a-f]{40}$")
            self.assertRegex(release["checksum"], r"^sha256:[0-9a-f]{64}$")
            self.assertFalse(Path(release["snapshot_path"]).is_absolute())
            self.assertNotIn("..", Path(release["snapshot_path"]).parts)
            self.assertIsInstance(release["required"], bool)
            snapshot_tasks = subprocess.check_output(
                ["git", "show", f"{release['ref']}:{release['snapshot_path']}/tasks.toml"],
                cwd=ROOT,
            )
            self.assertEqual(release["checksum"], "sha256:" + hashlib.sha256(snapshot_tasks).hexdigest())
            snapshot_contract = subprocess.check_output(
                ["git", "show", f"{release['ref']}:{release['snapshot_path']}/adw_contract.py"],
                cwd=ROOT,
                text=True,
            )
            self.assertIn("_fetch_release_snapshot", snapshot_contract)

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

    def test_delegation_status_schema_is_closed_and_path_safe(self) -> None:
        schema_path = (
            ROOT
            / "skills"
            / "adw"
            / "adw-core"
            / "templates"
            / "delegation"
            / "status.schema.json"
        )
        schema = json.loads(schema_path.read_text())
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertTrue(schema["$id"].endswith("/skills/adw/adw-core/templates/delegation/status.schema.json"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            schema["properties"]["run_id"]["pattern"],
            "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$",
        )

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
        delegation_brief = (skills_root / "adw-core" / "templates" / "delegation" / "task_brief.md").read_text()

        self.assertIn("assets/mise/v2/generation-guide.md", core)
        self.assertIn("There is no ad-hoc fallback", core)
        self.assertIn("mise run adw:check", implementation)
        self.assertIn("mise run adw:verify:minimal", implementation)
        self.assertIn("mise run adw:check", delegated)
        self.assertIn("mise run adw:verify:minimal", delegated)
        self.assertIn("exact route is explicitly approved", implementation)
        self.assertIn("approved PR/MR source/target/replacement route", delegated)
        self.assertIn("Open a PR/MR only when the exact route above is approved", delegation_brief)
        for task in (
            "adw:deploy:config:plan",
            "adw:deploy:config:apply",
            "adw:deploy:apply",
            "adw:health",
            "adw:readiness",
            "adw:validate-deployment",
        ):
            self.assertIn(task, testing)
            self.assertIn(task, merging)
        self.assertIn("adw:verify:full", regression)
        self.assertIn("adw:test:e2e:fast", regression)
        self.assertIn("adw:deploy:config:plan", rollback)
        self.assertIn("adw:deploy:apply", rollback)
        self.assertIn(".hermes/adw-task-manifest.json", adapter_template)
        self.assertIn("mise run adw:check", adapter_template)
        self.assertNotIn("Dokploy", merging)
        self.assertNotIn("Dokploy", rollback)

    def test_chain_full_rollout_requires_bounded_upfront_authorization_and_every_gate(self) -> None:
        skills_root = ROOT / "skills" / "adw"
        chain = (skills_root / "chain" / "SKILL.md").read_text()
        merging = (skills_root / "merge-feature" / "SKILL.md").read_text()
        gates = (skills_root / "adw-core" / "references" / "playbooks" / "deployment_gates.md").read_text()
        for term in (
            "full-rollout opt-in", "single upfront authorization", "exact release route",
            "demo", "main", "new, explicit proposal and authorization",
            "quality", "review", "preview", "deployment parity",
        ):
            self.assertIn(term, chain)
        self.assertIn("upfront chain authorization", merging)
        self.assertIn("upfront chain authorization", gates)
        self.assertIn("No authorization is inherited from a generic chain request", chain)
        self.assertIn("Stop and ask the human to approve the chain plan before creating branches", chain)
        self.assertIn("The first confirmation remains mandatory", chain)
        self.assertIn("Expected implementation commits within the approved feature scope do not alone invalidate", chain)
        self.assertIn("A change to an already reviewed or validated tree invalidates its old proof", chain)
        self.assertIn("a changed target/route, unapproved scope change", chain)
        self.assertIn("The grant has no time-based expiry", chain)
        self.assertIn("failed, pending, or stale", chain)
        self.assertIn("Never silently waive a gate", chain)
        self.assertNotIn("A generic chain command authorizes full rollout", chain)
        preview = (skills_root / "adw-core" / "references" / "playbooks" / "preview_deployments.md").read_text()
        release = (skills_root / "adw-core" / "references" / "playbooks" / "release_targets.md").read_text()
        diagram = (skills_root / "adw-core" / "assets" / "diagrams" / "adw-complete-workflow.puml").read_text()
        self.assertIn("exact, still-valid upfront chain authorization", preview)
        self.assertIn("preview-only grant never expands", preview)
        self.assertIn("first confirmed proposal", release)
        self.assertIn("no unapproved drift", release)
        self.assertIn("at this first confirmation", diagram)
        self.assertIn("continue without repeat confirmation", diagram)
        decision = diagram.index("if (Exact full-rollout grant still valid?)")
        yes = diagram.index("continue without repeat confirmation", decision)
        no = diagram.index("else (no)", decision)
        exceptional = diagram.index("if (Full rollout requested but exact grant cannot be verified or route changed?)", no)
        renewed = diagram.index("Explicitly authorize the new exact route and deployment consequences", exceptional)
        ordinary = diagram.index("else (ordinary chain)", renewed)
        approval = diagram.index("Explicitly approve exact merge target", ordinary)
        end = diagram.index("endif", ordinary)
        self.assertLess(yes, no)
        self.assertLess(no, exceptional)
        self.assertLess(exceptional, renewed)
        self.assertLess(renewed, ordinary)
        self.assertLess(ordinary, approval)
        self.assertLess(approval, end)
        self.assertNotIn("partition Human {", diagram[decision:no])
        from xml.etree import ElementTree
        import re
        import zlib
        svg = skills_root / "adw-core" / "assets" / "diagrams" / "adw-complete-workflow.svg"
        rendered = svg.read_text()
        labels = [node.text or "" for node in ElementTree.fromstring(rendered).iter() if node.tag.endswith("text")]
        for label in (
            "at this first confirmation", "continue without repeat confirmation",
            "Explicitly authorize the new exact route and deployment consequences",
            "Explicitly approve exact merge target",
            "optional E2E only with explicit run authorization",
        ):
            self.assertTrue(any(label in text for text in labels), label)
        # PlantUML embeds its compressed source in the SVG. Comparing the decoded
        # source catches stale renderings even if all of the expected labels remain.
        encoded = re.search(r"<\?plantuml-src ([^?]+)\?>", rendered)
        if encoded is None:
            self.fail("Rendered SVG has no embedded PlantUML source")
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
        data = bytearray()
        for offset in range(0, len(encoded.group(1)) - 3, 4):
            a, b, c, d = (alphabet.index(char) for char in encoded.group(1)[offset:offset + 4])
            data.extend(((a << 2) | (b >> 4), ((b << 4) & 240) | (c >> 2), ((c << 6) & 192) | d))
        embedded = zlib.decompress(data, -15).decode()
        self.assertEqual(embedded.strip(), diagram.split("\n", 1)[1].rsplit("@enduml", 1)[0].strip())

    def test_workflow_policy_requires_exact_pr_route_and_keeps_deployment_optional(self) -> None:
        skills_root = ROOT / "skills" / "adw"
        diagram = (skills_root / "adw-core" / "assets" / "diagrams" / "adw-complete-workflow.puml").read_text()
        merging = (skills_root / "merge-feature" / "SKILL.md").read_text()
        traceability = (skills_root / "adw-core" / "references" / "playbooks" / "github_traceability.md").read_text()

        approval = "Explicitly approve the exact PR source branch, target branch, and replacement/deletion effect"
        creation = "Create or update the linked PR only for the approved exact route"
        self.assertIn(approval, diagram)
        self.assertIn(creation, diagram)
        self.assertLess(diagram.index(approval), diagram.index(creation))
        self.assertIn("Deployment explicitly requested?", diagram)
        self.assertIn("Record verified merge-only result", diagram)
        self.assertIn("If deployment was not explicitly requested, report the merge result and stop", merging)
        self.assertIn("when deployment is requested", merging)
        self.assertIn("Do not infer completion from branch names or prefixes", traceability)

    def test_greenfield_tree_has_no_obsolete_or_machine_local_text(self) -> None:
        forbidden = (
            "/home/pupz",
            "feature/adw-context-extension",
            "raw-compose platform",
            "branch_environment_releases.md",
            "Default to `main` when safe",
            "`main` -> production",
        )
        audit_exceptions = {
            Path(__file__).resolve(),
            (ROOT / "plans" / "issue-7-greenfield-necessity.md").resolve(),
            (ROOT / "plans" / "issue-7-legacy-file-audit.md").resolve(),
        }
        for path in ROOT.rglob("*"):
            if (
                not path.is_file()
                or path.resolve() in audit_exceptions
                or ".git" in path.parts
                or "__pycache__" in path.parts
            ):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in forbidden:
                self.assertNotIn(token, text, f"obsolete token in {path.relative_to(ROOT)}")

    def test_legacy_file_audit_covers_every_main_path_and_decision(self) -> None:
        audit = (ROOT / "plans" / "issue-7-legacy-file-audit.md").read_text()
        legacy_paths = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", LEGACY_MAIN_SHA],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.splitlines()
        self.assertEqual(len(legacy_paths), 58)
        for path in legacy_paths:
            self.assertIn(f"`{path}`", audit, path)

        decisions = re.findall(r"^- \*\*(retain|rewrite|remove)\*\*", audit, re.MULTILINE)
        self.assertEqual(len(decisions), 58)
        self.assertEqual(decisions.count("retain"), 11)
        self.assertEqual(decisions.count("rewrite"), 42)
        self.assertEqual(decisions.count("remove"), 5)

    def test_greenfield_necessity_log_accounts_for_every_top_level_artifact(self) -> None:
        log = (ROOT / "plans" / "issue-7-greenfield-necessity.md").read_text()

        for token in (
            "skills/adw/",
            "skills/adw/adw-core/assets/mise/v1/",
            "adw_plugin/",
            "scripts/install_adw.sh",
            "tools/",
            "tests/",
            "README.md",
            "SOUL.md",
            "LICENSE",
            ".gitignore",
            "plans/PLAN.md",
            "plans/PLAN_plugin.md",
        ):
            self.assertIn(token, log)
        self.assertFalse((ROOT / "contracts").exists())
        self.assertFalse((ROOT / "plans" / "PLAN.md").exists())
        self.assertFalse((ROOT / "plans" / "PLAN_plugin.md").exists())


if __name__ == "__main__":
    unittest.main()
