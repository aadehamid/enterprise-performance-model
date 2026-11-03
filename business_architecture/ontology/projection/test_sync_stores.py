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
    want = {"catalog_datasets": 50, "catalog_digest": "d", "input_fingerprint": "f", "newest": [], "jena_graphs": {"g": 1}}

    def marker(self, **over):
        return {"catalog_datasets": 50, "catalog_digest": "d", "input_fingerprint": "f", "count": [4193, 21767],
                "marked_at": "2026-10-29T00:00:00Z", "commit": "abc"} | over

    def statuses(self, markers, live):
        return {s: status for s, status, _ in ss.drift(markers, live, self.want)}

    def test_each_status(self):
        markers = {"driver": self.marker(catalog_digest="old"), "aura": self.marker(), "databricks": None}
        live = {"driver": [4193, 21767], "aura": [0, 0], "jena": {"g": 1}, "databricks": [40169]}
        self.assertEqual(self.statuses(markers, live),
                         {"driver": "behind", "aura": "changed", "jena": "current", "databricks": "unmarked"})
        self.assertEqual(self.statuses({"driver": self.marker()}, {"driver": [4193, 21767]})["driver"], "current")

    def delta(self, held):
        """Databricks' status when its marker and its total row count match, from its rows per graph."""
        want = self.want | {"jena_graphs": {"a": 3, "a/shapes": 2, "a/catalog": 1, "a/m.erstudio": 5, "a/m.layer": 4}}
        live = {"databricks": [sum(held.values())], "databricks_graphs": held}
        return ss.drift({"databricks": self.marker(count=live["databricks"])}, live, want, ("databricks",))[0][1:]

    held = {"a": 3, "a/shapes": 2, "a/catalog": 1, "a/m.erstudio": 5, "a/m.layer": 4}

    def test_delta_with_every_graph_at_its_release_count_reads_current(self):
        self.assertEqual(self.delta(self.held)[0], "current")

    def test_a_missing_package_graph_in_delta_reads_changed_although_the_total_holds(self):
        status, why = self.delta({k: v for k, v in self.held.items() if k != "a/m.layer"} | {"a": 7})
        self.assertEqual((status, "a/m.layer" in why), ("changed", True))

    def test_two_delta_graphs_moved_by_one_each_way_read_changed_although_the_total_holds(self):
        status, why = self.delta(self.held | {"a/m.erstudio": 6, "a/m.layer": 3})
        self.assertEqual((status, "a/m.erstudio" in why), ("changed", True))

    def test_an_extra_delta_graph_reads_changed_although_the_total_holds(self):
        status, why = self.delta(self.held | {"old": 1, "a": 2})
        self.assertEqual((status, "old" in why), ("changed", True))

    def test_jena_is_judged_from_its_graphs_with_no_marker(self):
        want = {"a": 1, "a/shapes": 2}
        self.assertEqual(ss.judge_jena({"a": 1, "a/shapes": 2}, want)[0], "current")
        self.assertEqual(ss.judge_jena({}, want)[0], "empty")
        self.assertEqual(ss.judge_jena({"a": 1}, want)[0], "behind")
        self.assertEqual(ss.judge_jena({"a": 1, "a/shapes": 2, "old": 9}, want)[0], "behind")
        self.assertEqual(ss.judge_jena({"a": 1, "a/shapes": 3}, want)[0], "changed")
        self.assertEqual(ss.judge_jena({"a": 1, "a/shapes": 2, "(the default graph)": 4}, want)[0], "behind")

    def test_the_technical_graph_stays_out_of_the_release_comparison_and_is_judged_on_its_own(self):
        want, iri = {"a": 1}, ss.TECH_GRAPHS["tech-graph.ttl"]
        self.assertEqual(ss.judge_jena({"a": 1, iri: 5}, want, {iri: 5})[0], "current")
        self.assertEqual(ss.judge_jena({"a": 1}, want, {iri: 5})[0], "changed")
        self.assertEqual(ss.judge_jena({"a": 1, iri: 4}, want, {iri: 5})[0], "changed")
        self.assertEqual(ss.judge_jena({iri: 5}, want, {iri: 5})[0], "behind")

    def test_the_technical_graphs_names_equal_the_demos(self):
        sys.path.insert(0, ss.DEMO)
        import pricing_demo.tech_graph as tg
        self.assertEqual(ss.TECH_GRAPHS, tg.JENA_GRAPHS)

    def test_an_unreachable_store_says_so_even_with_a_marker(self):
        markers = {s: self.marker() for s in ss.STORES}
        live = {s: [4193, 21767] for s in ss.STORES} | {"aura": "unreachable (ServiceUnavailable)", "jena": {"g": 1}}
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

    def test_check_reads_and_judges_only_the_stores_named(self):
        # check --store driver: a validation whose test store is the local Neo4j reads and judges nothing else, so
        # AuraDB, Jena and Databricks, outside that test, stay untouched. The default is every store.
        self.assertEqual([s for s, _, _ in ss.drift({}, {}, self.want, ("driver",))], ["driver"])

        def no_login(store):
            raise FileNotFoundError(store)

        def databricks_read():
            raise AssertionError("Databricks was read for a check that did not name it")
        with mock.patch.object(ss, "neo4j_session", no_login), mock.patch.object(ss, "databricks", databricks_read):
            markers, live = ss.read_markers_and_counts(("driver",))
        self.assertEqual(set(markers), {"driver"})
        self.assertEqual(live, {"driver": "unreachable (FileNotFoundError)"})
        with mock.patch.object(ss, "neo4j_session", no_login), mock.patch.object(ss, "databricks", databricks_read):
            markers, live = ss.read_markers_and_counts()  # the default reads every store, Databricks included
        self.assertEqual(set(markers), set(ss.STORES))
        self.assertEqual(live["databricks"], "unreachable (AssertionError)")  # it was read, and the reader reported it

    def run_check(self, argv):
        """main() with `check` and the given options; the readers are replaced by recorders, and the report captured."""
        import io
        read = []

        def fake_read(stores=ss.STORES):
            read.append(tuple(stores))
            return {}, {}
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["sync_stores.py", "check"] + argv), \
                mock.patch.object(ss, "read_markers_and_counts", fake_read), \
                mock.patch.object(ss, "read_tech_markers", lambda stores=ss.STORES: read.append(("tech", *stores)) or {}), \
                mock.patch.object(ss, "logical_models", lambda: mock.Mock(check=lambda stores: [])), \
                mock.patch.object(ss, "expected_for", lambda ref, stores: self.want), mock.patch("sys.stdout", out):
            with self.assertRaises(SystemExit) as stop:
                ss.main()
        self.assertEqual(stop.exception.code, 1)  # nothing marked: every judged store is unmarked
        return read, [line.split()[0] for line in out.getvalue().splitlines()]

    def test_main_passes_the_named_stores_to_the_reader_and_the_report(self):
        read, reported = self.run_check(["--store", "driver", "--store", "aura"])
        self.assertEqual(read, [("driver", "aura"), ("tech", "driver", "aura")])
        self.assertEqual(reported, ["driver", "aura", "tech:driver", "tech:aura"])
        read, reported = self.run_check([])
        self.assertEqual(read, [tuple(ss.STORES), ("tech", *ss.STORES)])
        self.assertEqual(reported, list(ss.STORES) + [f"tech:{s}" for s in ss.STORES])


class Plan(unittest.TestCase):
    def cmds(self, behind, cloud):
        steps, reloaded = ss.plan(behind, cloud, "~/skills")
        return [" ".join(c) for _, c in steps], reloaded

    def test_local_stores_reload_without_touching_the_cloud(self):
        cmds, reloaded = self.cmds(["driver", "jena", "aura", "databricks"], cloud=False)
        self.assertEqual(reloaded, ["driver", "jena"])
        self.assertTrue(cmds[0].endswith("--skip copy,databricks,rebuild"))
        self.assertTrue(cmds[1].endswith(f"pipeline.py record --run {ss.DRIVER_OUT}"))
        self.assertTrue(cmds[2].endswith("tech_graph load --store driver --store jena"))
        self.assertEqual(len(cmds), 3)

    def test_cloud_runs_the_full_driver_once_and_reloads_the_technical_graph_in_aura(self):
        cmds, reloaded = self.cmds(["aura"], cloud=True)
        self.assertEqual(reloaded, ["driver", "jena", "aura", "databricks"])
        self.assertNotIn("--skip", cmds[0])
        self.assertTrue(cmds[2].endswith("tech_graph load --store driver --store jena --store aura"))
        self.assertTrue(cmds[3].endswith("tech_graph sync"))

    def test_jena_alone_runs_only_the_jena_step_and_touches_no_neo4j(self):
        cmds, reloaded = self.cmds(["jena"], cloud=False)
        self.assertEqual(reloaded, ["jena"])
        self.assertTrue(cmds[0].endswith("--only jena"))
        self.assertTrue(cmds[1].endswith("tech_graph load --store jena"))
        self.assertEqual(len(cmds), 2)

    def test_nothing_behind_runs_nothing(self):
        self.assertEqual(self.cmds([], cloud=True), ([], []))

    def tech_cmds(self, behind, tech_behind, cloud):
        steps, reloaded = ss.plan(behind, cloud, "~/skills", tech_behind)
        return [" ".join(c) for _, c in steps], reloaded

    def test_a_stale_technical_graph_alone_reloads_only_the_technical_graph(self):
        cmds, reloaded = self.tech_cmds([], ["driver", "jena"], cloud=False)
        self.assertEqual(reloaded, [])
        self.assertEqual(len(cmds), 1)
        self.assertTrue(cmds[0].endswith("tech_graph load --store driver --store jena"))

    def test_the_delta_copy_follows_with_sync_and_the_cloud_stores_need_cloud(self):
        cmds, _ = self.tech_cmds([], ["aura", "databricks"], cloud=False)
        self.assertEqual(cmds, [])
        cmds, _ = self.tech_cmds([], ["aura", "databricks"], cloud=True)
        self.assertTrue(cmds[0].endswith("tech_graph load --store aura"))
        self.assertTrue(cmds[1].endswith("tech_graph sync"))
        self.assertEqual(len(cmds), 2)
        cmds, _ = self.tech_cmds(["driver"], ["databricks"], cloud=True)
        self.assertTrue(cmds[2].endswith("tech_graph load --store driver --store jena"))
        self.assertTrue(cmds[3].endswith("tech_graph sync"))


class StoresAreOneNeo4jPlusJena(unittest.TestCase):
    def test_the_stores_and_the_run_configuration_agree(self):
        self.assertEqual(ss.STORES, ("driver", "aura", "jena", "databricks"))
        with open(os.path.join(HERE, "skill-run", "epm-run.json")) as f:
            cfg = json.load(f)
        self.assertIs(cfg["keep_neo4j"], True)
        self.assertIs(cfg["keep_jena"], True)
        self.assertEqual(cfg["out"], ss.DRIVER_OUT)
        self.assertEqual(tuple(cfg["release_graphs"]), ss.RELEASE_GRAPHS)
        self.assertIn(f":{cfg['jena']['port']}/", ss.JENA_QUERY)

    def test_a_current_jena_holds_every_newest_release_three_times_and_each_package_graph(self):
        newest = ss.newest_releases(ss.catalog_datasets(ss.repo_file(ss.CATALOG)))
        want = ss.jena_graphs(newest)
        extra = {g for iri in newest for g in ss.package_graphs(iri)}  # none in main; the release's logical models
        self.assertEqual(len(want), 3 * len(newest) + len(extra))
        self.assertTrue(all(want.values()))
        self.assertEqual({f"{iri}/{n}" for iri in newest for n in ("shapes", "catalog")} | set(newest) | extra, set(want))


class OntologyLabelsOnly(unittest.TestCase):
    """The technical graph (label Tech), the marker and the release records share the local Neo4j. This pins the exact
    Cypher of the counts, which reads :Resource nodes and the edges between them, so none of those moves them. The
    skill's test_release_record.py pins the hash and the round trip."""

    def test_the_counts_read_resource_nodes_and_the_edges_between_them(self):
        queries = []

        class Session:
            def run(self, query):
                queries.append(query)
                return mock.Mock(single=lambda: {"n": 0})
        self.assertEqual(ss.resource_counts(Session()), (0, 0))
        self.assertEqual(queries, ["MATCH (n:Resource) RETURN count(n) AS n", "MATCH (:Resource)-[r]->(:Resource) RETURN count(r) AS n"])


class Neo4jChecked(unittest.TestCase):
    want = {"newest": ["a", "b"]}

    def session(self, nodes, edges, records):
        class Session:
            def run(self, query):
                if "ModuleRelease" in query:
                    return mock.Mock(value=lambda: records)
                if ":Tech" in query:
                    return mock.Mock(single=lambda: {"n": 7})
                return mock.Mock(single=lambda: {"n": nodes if "(n:Resource)" in query else edges})
        return Session()

    def checked(self, nodes, edges, records):
        report = json.load(open(ss.REPORT))
        return ss.neo4j_checked("driver", self.session(report["nodes"] + nodes, report["relationships"] + edges, records), self.want)

    def test_counts_equal_to_the_committed_report_and_one_record_per_release_pass(self):
        report = json.load(open(ss.REPORT))
        self.assertEqual(self.checked(0, 0, ["b", "a"]), [report["nodes"], report["relationships"], 7])

    def test_other_counts_or_records_are_refused(self):
        with self.assertRaisesRegex(SystemExit, "relationships"):
            self.checked(0, 1, ["a", "b"])
        with self.assertRaisesRegex(SystemExit, "release record"):
            self.checked(0, 0, ["a"])


class Markers(unittest.TestCase):
    def test_the_neo4j_marker_is_never_a_resource(self):
        source = inspect.getsource(ss)
        self.assertIn("MERGE (m:EpmStoreMarker {store: $s})", source)
        self.assertNotIn(":EpmStoreMarker:Resource", source)
        self.assertNotRegex(source, r"\(m:Resource")

    def test_mark_refuses_a_store_that_does_not_match_the_repository(self):
        self.assertIn("raise SystemExit", inspect.getsource(ss.neo4j_checked))
        self.assertIn("raise SystemExit", inspect.getsource(ss.databricks_checked))


class TechGraphContent(unittest.TestCase):
    """Codex round 1 on #455: a marker that matches says nothing of the content, so a hand edit that kept the counts,
    or a change to Jena or Delta that left the marker, read as current. Each store's content is now compared too."""
    folder = os.path.join(ss.DEMO, "graph")

    @classmethod
    def setUpClass(cls):
        cls.tg = ss.demo_graph()
        cls.want = ss.tech_content(cls.folder)
        cls.digest = ss.tech_digest(cls.folder)

    def rows(self):
        nodes, edges = self.tg.graph_rows(self.tg.read_graph(self.folder))
        return [{"labels": n["labels"], "p": dict(n["props"])} for n in nodes], edges

    def judge(self, store, markers, nodes):
        live = {store: [0, 0, len(nodes)]} if store in ss.NEO4J_STORES else {store: [0]}
        return ss.tech_drift(markers, live, self.digest, (store,), self.want)[0][1]

    def neo4j(self, nodes, edges):
        marker = {"digest": self.digest, "nodes": len(nodes)}

        class Result(list):
            def single(self):
                return self[0] if self else None

        class Session(contextlib.nullcontext):
            def run(_, query, **kw):
                if ss.TECH_MARKER_LABEL in query:
                    return Result([{"p": marker}])
                return Result(nodes if query == self.tg.NEO4J_NODES else edges)

        with mock.patch.object(ss, "neo4j_session", lambda store: (contextlib.nullcontext(), Session())):
            return ss.read_tech_markers(("driver",))

    def test_neo4j_with_its_marker_and_counts_but_edited_content_reads_changed(self):
        nodes, edges = self.rows()
        self.assertEqual(self.judge("driver", self.neo4j(nodes, edges), nodes), "current")
        nodes[0]["p"]["name"] = "edited by hand"
        self.assertEqual(self.judge("driver", self.neo4j(nodes, edges), nodes), "changed")

    def jena(self, edit):
        from rdflib import Graph, Literal
        graphs = {iri: Graph().parse(os.path.join(self.folder, name), format="turtle") for name, iri in ss.TECH_GRAPHS.items()}
        if edit:
            g = graphs[ss.TECH_GRAPHS["tech-graph.ttl"]]
            s, p, o = next(t for t in sorted(g) if isinstance(t[2], Literal))
            g.remove((s, p, o))
            g.add((s, p, Literal("edited by hand")))  # same triple count
        with mock.patch.object(ss, "jena_select", lambda q: [{"d": {"value": self.digest}}]), \
                mock.patch.object(ss, "jena_construct", lambda iri: graphs[iri]):
            return ss.read_tech_markers(("jena",))

    def test_jena_with_its_marker_but_edited_content_reads_changed(self):
        self.assertEqual(self.judge("jena", self.jena(False), []), "current")
        self.assertEqual(self.judge("jena", self.jena(True), []), "changed")

    def databricks(self, nodes, edges, schema="idp_sbx.tech_graph"):
        node_rows, edge_rows = self.tg.delta_rows(nodes, edges)
        marker = {"digest": self.digest, "schema": schema} if schema else {"digest": self.digest}

        class Cursor:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def execute(self, query):
                self.query = query

            def fetchone(self):
                return (json.dumps(marker),)

            def fetchall(self):
                return node_rows if "tech_graph_nodes" in self.query else edge_rows

        class Conn:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def cursor(self):
                return Cursor()
        with mock.patch.object(ss, "databricks", lambda: (Conn(), "workspace.epm_ontology")):
            return ss.read_tech_markers(("databricks",))

    def test_the_delta_copy_with_its_marker_but_edited_content_reads_changed(self):
        nodes, edges = self.rows()
        self.assertEqual(self.judge("databricks", self.databricks(nodes, edges), nodes), "current")
        edges[0] = {**edges[0], "t": "EDITED"}
        self.assertEqual(self.judge("databricks", self.databricks(nodes, edges), nodes), "changed")
        self.assertEqual(self.judge("databricks", self.databricks(*self.rows(), schema=None), nodes), "changed")


class DatabricksChecked(unittest.TestCase):
    """#455: mark read the triple table's graph names and recorded its row count without comparing it, so a load that
    stopped part way, with every graph present, could be marked current."""
    want = {"newest": ["a"], "jena_graphs": {"a": 3, "a/shapes": 2, "a/catalog": 1}}

    def cursor(self, held):
        class Cursor:
            def execute(self, query):
                assert "GROUP BY graph" in query, query
                self.query = query

            def fetchall(self):
                return sorted(held.items())
        return Cursor()

    def test_a_table_with_every_graph_at_its_release_count_passes(self):
        self.assertEqual(ss.databricks_checked(self.cursor({"a": 3, "a/shapes": 2, "a/catalog": 1}), "c.s", self.want), [6])

    def test_a_partial_load_with_every_graph_present_is_refused(self):
        with self.assertRaisesRegex(SystemExit, "another row count"):
            ss.databricks_checked(self.cursor({"a": 2, "a/shapes": 2, "a/catalog": 1}), "c.s", self.want)

    def test_a_missing_or_stray_graph_is_refused(self):
        with self.assertRaisesRegex(SystemExit, "lacks 1 graph"):
            ss.databricks_checked(self.cursor({"a": 3, "a/shapes": 2}), "c.s", self.want)
        with self.assertRaisesRegex(SystemExit, "holds 1 other"):
            ss.databricks_checked(self.cursor({"a": 3, "a/shapes": 2, "a/catalog": 1, "old": 4}), "c.s", self.want)


class TechGraphMarker(unittest.TestCase):
    """#455: each store that holds the technical graph is marked with a digest of the graph files it was loaded from."""

    def marker(self, **over):
        return {"digest": "d" * 64, "nodes": 142, "marked_at": "2026-11-02T00:00:00Z"} | over

    def test_each_status(self):
        markers = {"driver": self.marker(), "aura": self.marker(digest="e" * 64), "jena": None,
                   "databricks": "unreachable (ConnectionError)"}
        live = {"driver": [4193, 21767, 142], "aura": [4193, 21767, 142]}
        self.assertEqual({s: st for s, st, _ in ss.tech_drift(markers, live, "d" * 64)},
                         {"driver": "current", "aura": "behind", "jena": "unmarked", "databricks": "unreachable"})
        changed = ss.tech_drift({"driver": self.marker()}, {"driver": [4193, 21767, 0]}, "d" * 64, ("driver",))
        self.assertEqual(changed[0][1], "changed")  # the Tech nodes went, the marker stayed
        self.assertEqual(ss.tech_drift({"databricks": self.marker()}, {"databricks": [1]}, "d" * 64, ("databricks",))[0][1], "current")

    def test_the_marker_names_and_digest_equal_the_demos(self):
        sys.path.insert(0, ss.DEMO)
        import pricing_demo.tech_graph as tg
        self.assertEqual((ss.TECH_MARKER_LABEL, ss.TECH_MARKER_GRAPH, ss.TECH_MARKER_DIGEST, ss.TECH_MARKER_ROW),
                         (tg.MARKER_LABEL, tg.MARKER_GRAPH, tg.MARKER_DIGEST, tg.MARKER_ROW))
        self.assertEqual(tuple(ss.TECH_GRAPHS), tg.GRAPH_FILES)
        folder = os.path.join(ss.DEMO, "graph")
        self.assertEqual(ss.tech_digest(folder), tg.graph_digest(folder))

    def test_jena_leaves_the_marker_graph_to_the_technical_graphs_check(self):
        want, iri = {"a": 1}, ss.TECH_GRAPHS["tech-graph.ttl"]
        self.assertEqual(ss.judge_jena({"a": 1, iri: 5, ss.TECH_MARKER_GRAPH: 1}, want, {iri: 5})[0], "current")

    def test_check_fails_when_the_ontology_is_current_and_the_technical_graph_is_not(self):
        import io
        want = {"catalog_datasets": 50, "catalog_digest": "d", "input_fingerprint": "f", "newest": []}
        marker = {"catalog_datasets": 50, "catalog_digest": "d", "input_fingerprint": "f", "count": [1, 2, 3],
                  "marked_at": "t", "commit": "c"}
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["sync_stores.py", "check", "--store", "driver"]), \
                mock.patch.object(ss, "read_markers_and_counts", lambda stores: ({"driver": marker}, {"driver": [1, 2, 3]})), \
                mock.patch.object(ss, "read_tech_markers", lambda stores: {"driver": {"digest": "old", "nodes": 3}}), \
                mock.patch.object(ss, "logical_models", lambda: mock.Mock(check=lambda stores: [])), \
                mock.patch.object(ss, "expected_for", lambda ref, stores: want), mock.patch("sys.stdout", out):
            with self.assertRaises(SystemExit) as stop:
                ss.main()
        self.assertEqual(stop.exception.code, 1)
        lines = {line.split()[0]: line.split()[1] for line in out.getvalue().splitlines()}
        self.assertEqual(lines, {"driver": "current", "tech:driver": "behind"})

    def test_the_marker_readers_report_an_unreachable_store_without_a_crash(self):
        def no_login(store):
            raise FileNotFoundError(store)

        def down(*args):
            raise ConnectionError("down")
        with mock.patch.object(ss, "neo4j_session", no_login), mock.patch.object(ss, "jena_select", down), \
                mock.patch.object(ss, "databricks", down):
            self.assertEqual(ss.read_tech_markers(), {"driver": "unreachable (FileNotFoundError)", "aura": "unreachable (FileNotFoundError)",
                                                       "jena": "unreachable (ConnectionError)", "databricks": "unreachable (ConnectionError)"})


@unittest.skipIf(pl.SHARE_RELEASE and not os.path.exists(WORKFLOW), "no workflow file here (the share release ships no GitHub workflow)")
class Workflow(unittest.TestCase):
    text = open(WORKFLOW).read() if os.path.exists(WORKFLOW) else ""  # on main a missing file fails the tests below

    def test_it_runs_on_every_release_tag(self):
        self.assertIn("tags: ['*-v*']", self.text)
        tags = subprocess.run(["git", "-C", ss.REPO, "tag"], capture_output=True, text=True).stdout.split()
        pattern = re.compile(r"^[^/]*-v[^/]*$")  # GitHub's * matches any character but a slash
        self.assertTrue(all(pattern.match(t) for t in tags), [t for t in tags if not pattern.match(t)])

    def test_it_never_runs_on_a_schedule(self):
        # EPM-DEC-001-0112, amendment of 2026-11-02 (later), item 3: the drift check stays a written step of each release.
        self.assertNotIn("schedule:", self.text)
        self.assertEqual(self.text.split("\non:\n")[1].split("\njobs:")[0].split(),
                         ["push:", "tags:", "['*-v*']", "workflow_dispatch:"])

    def test_it_loads_the_technical_graph_into_auradb_and_delta_after_the_driver_then_marks_and_checks(self):
        steps = self.text.split("\n      - ")
        order = [next((i for i, st in enumerate(steps) if needle in st), None) for needle in (
            "run_projection.py", "tech_graph load --store aura", "tech_graph sync --store aura",
            "logical_models.py load --store aura --store databricks", "sync_stores.py mark --store aura --store databricks", "sync_stores.py check --ref worktree --store aura --store databricks")]
        self.assertNotIn(None, order)
        self.assertEqual(order, sorted(order))

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
        with stores_env(json.dumps({"driver": {"bolt": "bolt://127.0.0.1:17899", "env": ["/tmp/x.env"]},
                                    "jena": {"query": "http://127.0.0.1:13999/ds/query"}, "databricks_env": "/tmp/d.env"})):
            mod = importlib.reload(ss)
            self.assertEqual(mod.NEO4J_STORES["driver"], ("bolt://127.0.0.1:17899", ("/tmp/x.env",)))
            self.assertEqual(mod.NEO4J_STORES["aura"], (None, ("~/.config/neo4j/aura.env",)))
            self.assertEqual(mod.JENA_QUERY, "http://127.0.0.1:13999/ds/query")
            self.assertEqual(mod.DATABRICKS_ENV, "/tmp/d.env")

    def test_another_environment_names_its_run_configuration_output_and_table(self):
        with stores_env(json.dumps({"run_config": "/qa/run.json", "driver_out": "~/qa", "triples_table": "qa_triples"})):
            mod = importlib.reload(ss)
            cmds = [" ".join(c) for _, c in mod.plan(["driver"], False, "~/skills")[0]]
            self.assertIn("--config /qa/run.json", cmds[0])
            self.assertTrue(cmds[1].endswith("record --run ~/qa"))
            self.assertEqual(mod.TRIPLES_TABLE, "qa_triples")

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
