"""Offline tests of sync_stores.py and the release-tag workflow (brief item 7c): no store is contacted."""
import inspect
import json
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sync_stores as ss  # noqa: E402

WORKFLOW = os.path.join(ss.REPO, ".github", "workflows", "sync-stores.yml")


class Expected(unittest.TestCase):
    def test_the_working_tree_gives_every_catalog_dataset_and_the_manifest_fingerprint(self):
        want = ss.expected()
        datasets = ss.catalog_datasets(ss.repo_file(ss.CATALOG))
        self.assertEqual(want["catalog_datasets"], len(datasets))
        self.assertEqual(want["catalog_datasets"], len(set(datasets)))
        manifest = json.load(open(os.path.join(ss.REPO, ss.MANIFEST)))
        self.assertEqual(want["input_fingerprint"], manifest["input_fingerprint"])

    def test_newest_takes_each_modules_highest_version_numerically(self):
        base = "https://w3id.org/lsc/ontology/modules/"
        iris = [base + "kpi/1.2.0", base + "kpi/1.10.0", base + "core/2.4.0", base + "core/2.3.0"]
        self.assertEqual(ss.newest_releases(iris), [base + "core/2.4.0", base + "kpi/1.10.0"])

    def test_one_newest_release_per_module_in_the_catalog(self):
        want = ss.expected()
        modules = [iri.rsplit("/", 2)[-2] for iri in want["newest"]]
        self.assertEqual(len(modules), len(set(modules)))
        self.assertIn("https://w3id.org/lsc/ontology/modules/kpi/1.3.0", want["newest"])


class Drift(unittest.TestCase):
    want = {"catalog_datasets": 50, "catalog_digest": "d", "input_fingerprint": "f", "newest": []}

    def marker(self, **over):
        return {"catalog_datasets": 50, "catalog_digest": "d", "input_fingerprint": "f", "count": [4193, 21767],
                "marked_at": "2026-10-29T00:00:00Z", "commit": "abc"} | over

    def statuses(self, markers, live):
        return {s: status for s, status, _ in ss.drift(markers, live, self.want)}

    def test_each_status(self):
        markers = {"pipeline": self.marker(), "driver": self.marker(catalog_digest="old"),
                   "aura": self.marker(), "databricks": None}
        live = {"pipeline": [4193, 21767], "driver": [4193, 21767], "aura": [0, 0], "databricks": [40169]}
        self.assertEqual(self.statuses(markers, live),
                         {"pipeline": "current", "driver": "behind", "aura": "changed", "databricks": "unmarked"})

    def test_an_unreachable_store_says_so_even_with_a_marker(self):
        markers = {s: self.marker() for s in ss.STORES}
        live = {s: [4193, 21767] for s in ss.STORES} | {"aura": "unreachable (ServiceUnavailable)"}
        self.assertEqual(self.statuses(markers, live)["aura"], "unreachable")

    def test_every_store_is_reported(self):
        self.assertEqual([s for s, _, _ in ss.drift({}, {}, self.want)], list(ss.STORES))


class Plan(unittest.TestCase):
    def cmds(self, behind, cloud):
        steps, reloaded = ss.plan(behind, cloud, "~/skills")
        return [" ".join(c) for _, c in steps], reloaded

    def test_local_stores_reload_without_touching_the_cloud(self):
        cmds, reloaded = self.cmds(["pipeline", "driver", "aura", "databricks"], cloud=False)
        self.assertEqual(reloaded, ["pipeline", "driver"])
        self.assertEqual(cmds[0], "./run_local.sh --keep")
        self.assertTrue(cmds[1].endswith("--skip copy,databricks,rebuild"))
        self.assertTrue(cmds[2].endswith("tech_graph load --store pipeline --store driver"))

    def test_cloud_runs_the_full_driver_once_and_reloads_the_technical_graph_in_aura(self):
        cmds, reloaded = self.cmds(["aura"], cloud=True)
        self.assertEqual(reloaded, ["driver", "aura", "databricks"])
        self.assertNotIn("--skip", cmds[0])
        self.assertTrue(cmds[1].endswith("tech_graph load --store driver --store aura"))

    def test_nothing_behind_runs_nothing(self):
        self.assertEqual(self.cmds([], cloud=True), ([], []))


class Markers(unittest.TestCase):
    def test_the_neo4j_marker_is_never_a_resource(self):
        source = inspect.getsource(ss)
        self.assertIn("MERGE (m:EpmStoreMarker {store: $s})", source)
        self.assertNotIn(":EpmStoreMarker:Resource", source)
        self.assertNotRegex(source, r"\(m:Resource")

    def test_mark_refuses_a_store_that_does_not_match_the_repository(self):
        self.assertIn("raise SystemExit", inspect.getsource(ss.neo4j_checked))
        self.assertIn("raise SystemExit", inspect.getsource(ss.databricks_checked))


class Workflow(unittest.TestCase):
    text = open(WORKFLOW).read()

    def test_it_runs_on_every_release_tag(self):
        self.assertIn("tags: ['*-v*']", self.text)
        tags = subprocess.run(["git", "-C", ss.REPO, "tag"], capture_output=True, text=True).stdout.split()
        pattern = re.compile(r"^[^/]*-v[^/]*$")  # GitHub's * matches any character but a slash
        self.assertTrue(all(pattern.match(t) for t in tags), [t for t in tags if not pattern.match(t)])

    def test_every_secret_is_checked_and_every_later_step_waits_for_the_check(self):
        secrets = sorted(set(re.findall(r"secrets\.(\w+)", self.text)))
        guard = self.text.split("- name: Check the logins")[1].split("- if:")[0]
        for name in secrets:
            self.assertIn(name, guard)
        later = self.text.split("- name: Check the logins")[1].split("\n      - ")[1:]
        self.assertTrue(later)
        for step in later:
            self.assertTrue(step.startswith("if: steps.logins.outputs.ready == 'true'"), step[:60])


if __name__ == "__main__":
    unittest.main()
