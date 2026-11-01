"""Offline tests of sync_stores.py and the release-tag workflow (brief item 7c): no store is contacted."""
import contextlib
import importlib
import inspect
import json
import os
import re
import subprocess
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pipeline as pl  # noqa: E402  (release mode: EPM_SHARE_RELEASE, or release.json at the tree's root)
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

    def test_a_missing_login_file_reads_as_unreachable_not_a_crash(self):
        # Bugbot on #406: newest() used to raise SystemExit, which except Exception does not catch.
        from unittest import mock
        missing = (os.path.join(HERE, "no-such-run.env"),)
        with self.assertRaises(FileNotFoundError):
            ss.newest(missing)
        def no_login(store):
            ss.newest(missing)
        def no_databricks():
            raise ConnectionError("down")
        with mock.patch.object(ss, "neo4j_session", no_login), mock.patch.object(ss, "databricks", no_databricks):
            markers, live = ss.read_markers_and_counts()
        self.assertEqual({s: live[s] for s in ss.NEO4J_STORES}, {s: "unreachable (FileNotFoundError)" for s in ss.NEO4J_STORES})
        self.assertEqual(live["databricks"], "unreachable (ConnectionError)")

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


@unittest.skipIf(pl.SHARE_RELEASE and not os.path.exists(WORKFLOW), "no workflow file here (the share release ships no GitHub workflow)")
class Workflow(unittest.TestCase):
    text = open(WORKFLOW).read() if os.path.exists(WORKFLOW) else ""  # on main a missing file fails the tests below

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


class StoreTablesAgree(unittest.TestCase):
    """Plan 2 (codebase architecture, 2026-10-30): the Neo4j stores and their login files are listed twice, here and in
    the demo's tech_graph.py, which sync_stores runs as a separate program. The demo is its own project, so the two
    tables stay apart, and this test keeps them equal."""

    @staticmethod
    def demo_literal():
        """The demo's table as written in tech_graph.py, before any EPM_STORES_JSON override."""
        import ast
        path = os.path.join(ss.DEMO, "pricing_demo", "tech_graph.py")
        tree = ast.parse(open(path).read())
        node = next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "STORES" for t in n.targets))
        return ast.literal_eval(node)

    @staticmethod
    def demo_module():
        import importlib
        sys.path.insert(0, ss.DEMO)
        import pricing_demo.tech_graph as tg
        return importlib.reload(tg)

    def test_the_demo_lists_the_same_neo4j_stores(self):
        if os.environ.get("EPM_STORES_JSON"):
            # Both modules applied the same override at import; the literal in the file no longer says what they hold.
            self.assertEqual(self.demo_module().STORES, ss.NEO4J_STORES)
        else:
            self.assertEqual(self.demo_literal(), ss.NEO4J_STORES)

    def test_the_tables_still_agree_under_an_override(self):
        with stores_env(json.dumps({"driver": {"bolt": "bolt://127.0.0.1:17898"}, "aura": {"env": ["/tmp/a.env"]}})):
            mod = importlib.reload(ss)
            self.assertEqual(mod.NEO4J_STORES["driver"][0], "bolt://127.0.0.1:17898")
            self.assertEqual(self.demo_module().STORES, mod.NEO4J_STORES)
            self.assertNotEqual(self.demo_literal(), mod.NEO4J_STORES)
        self.demo_module()


@contextlib.contextmanager
def stores_env(value):
    """EPM_STORES_JSON set to `value` for the block (None: unset); the caller's value is put back after, and
    sync_stores is reloaded, so a release run that sets it for the whole session keeps its stores."""
    missing = object()
    before = os.environ.get("EPM_STORES_JSON", missing)
    if value is None:
        os.environ.pop("EPM_STORES_JSON", None)
    else:
        os.environ["EPM_STORES_JSON"] = value
    try:
        yield
    finally:
        if before is missing:
            os.environ.pop("EPM_STORES_JSON", None)
        else:
            os.environ["EPM_STORES_JSON"] = before
        importlib.reload(ss)


class StoreOverrides(unittest.TestCase):
    def test_the_env_json_replaces_only_what_it_names(self):
        with stores_env(json.dumps({"pipeline": {"bolt": "bolt://127.0.0.1:17899", "env": ["/tmp/x.env"]},
                                    "driver_reports": ["/tmp/r.json"], "databricks_env": "/tmp/d.env"})):
            mod = importlib.reload(ss)
            self.assertEqual(mod.NEO4J_STORES["pipeline"], ("bolt://127.0.0.1:17899", ("/tmp/x.env",)))
            self.assertEqual(mod.NEO4J_STORES["aura"], (None, ("~/.config/neo4j/aura.env",)))
            self.assertEqual(mod.DRIVER_REPORTS, ("/tmp/r.json",))
            self.assertEqual(mod.DATABRICKS_ENV, "/tmp/d.env")

    def test_the_callers_value_is_put_back(self):
        missing = object()
        before = os.environ.get("EPM_STORES_JSON", missing)
        for preset in ('{"databricks_env": "/tmp/preset.env"}', None):
            if preset is None:
                os.environ.pop("EPM_STORES_JSON", None)
            else:
                os.environ["EPM_STORES_JSON"] = preset
            try:
                with stores_env('{"databricks_env": "/tmp/inner.env"}'):
                    self.assertEqual(importlib.reload(ss).DATABRICKS_ENV, "/tmp/inner.env")
                self.assertEqual(os.environ.get("EPM_STORES_JSON"), preset)
                self.assertEqual(ss.DATABRICKS_ENV, "/tmp/preset.env" if preset else "~/.config/databricks/epm.env")
            finally:
                if before is missing:
                    os.environ.pop("EPM_STORES_JSON", None)
                else:
                    os.environ["EPM_STORES_JSON"] = before
                importlib.reload(ss)


class WithoutGit(unittest.TestCase):
    def test_a_tree_without_git_has_no_commit_and_reads_itself(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(ss, "REPO", tmp):
            self.assertEqual(ss.commit(), "unknown (not a Git checkout)")
            self.assertEqual(ss.default_ref(), "worktree")
            os.mkdir(os.path.join(tmp, ".git"))  # a checkout: the default is main's newest catalog
            self.assertEqual(ss.default_ref(), "origin/main")


if __name__ == "__main__":
    unittest.main()
