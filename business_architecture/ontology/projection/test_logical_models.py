"""Offline tests of logical_models.py (EPM-DEC-001-0113, amendment "the stores"): no store is contacted. The package is
built in a temporary folder from the module's made-up example, the way the share release's cut lays it out, because
main holds no logical-model package."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import logical_models as lm  # noqa: E402
import pipeline as pl  # noqa: E402
import rebuild_stores as rb  # noqa: E402
import sync_stores as ss  # noqa: E402

EXAMPLE = os.path.join(ss.REPO, "business_architecture", "ontology", "logical-model", "example")
SLUG = "example-logical-model"
VERSION_IRI = "https://w3id.org/lsc/ontology/modules/logical-model/1.0.0"
ER = "https://www.erstudio.com/semanticmodel/"


class Package(unittest.TestCase):
    """A repository root in a temporary folder whose releases hold logical-model 1.0.0 with the example model."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        self.folder = os.path.join(self.root, "business_architecture", "ontology", "releases", lm.MODULE, "1.0.0")
        os.makedirs(self.folder)
        names = {"logical-model.ttl": os.path.join(EXAMPLE, "..", "vocabulary.ttl"),
                 "shapes.ttl": os.path.join(EXAMPLE, "..", "shapes.ttl"),
                 f"{SLUG}.erstudio.ttl": os.path.join(EXAMPLE, f"{SLUG}.erstudio.ttl"),
                 f"{SLUG}.layer.ttl": os.path.join(EXAMPLE, f"{SLUG}.layer.ttl")}
        for name, source in names.items():
            shutil.copy(source, os.path.join(self.folder, name))
        with open(os.path.join(self.folder, "catalog.ttl"), "w") as f:
            f.write(f"<{VERSION_IRI}/catalog> <http://www.w3.org/ns/dcat#dataset> <{VERSION_IRI}> .\n")
        self.write_manifest([*names, "catalog.ttl", "logical-model.jsonld", "CHANGELOG.md"])
        for patch in (mock.patch.object(ss, "REPO", self.root), mock.patch.object(lm, "RELEASES", os.path.dirname(os.path.dirname(self.folder)))):
            patch.start()
            self.addCleanup(patch.stop)

    def write_manifest(self, files):
        with open(os.path.join(self.folder, "manifest.json"), "w") as f:
            json.dump({"module": lm.MODULE, "version": "1.0.0", "files": {n: "0" * 64 for n in files}}, f)

    def rows(self):
        return lm.graph_rows(lm.models([VERSION_IRI]))


class InMain(unittest.TestCase):
    @unittest.skipIf(pl.SHARE_RELEASE, "the share release holds the logical-model package")
    def test_main_holds_no_package_graph_so_nothing_loads_and_check_reports_nothing(self):
        self.assertFalse(lm.held())
        self.assertEqual((lm.package_graphs(), lm.models(), lm.check(ss.STORES)), ({}, [], []))

        def touched(*a, **k):
            raise AssertionError("a store was contacted")
        out = io.StringIO()
        with mock.patch.object(ss, "neo4j_session", touched), mock.patch.object(ss, "databricks", touched), \
                mock.patch.object(lm, "rdfstore", touched), mock.patch("sys.stdout", out):
            lm.load(ss.STORES, "~/skills")
        self.assertIn("nothing to load", out.getvalue())

    def test_held_and_the_catalog_agree(self):
        self.assertEqual(lm.held(), bool(lm.package_graphs()))


class PackageGraphs(Package):
    def test_the_manifest_names_the_package_graphs_and_nothing_else(self):
        want = {f"{VERSION_IRI}/{SLUG}.erstudio": f"business_architecture/ontology/releases/{lm.MODULE}/1.0.0/{SLUG}.erstudio.ttl",
                f"{VERSION_IRI}/{SLUG}.layer": f"business_architecture/ontology/releases/{lm.MODULE}/1.0.0/{SLUG}.layer.ttl"}
        self.assertEqual(ss.package_graphs(VERSION_IRI, "worktree"), want)
        self.assertTrue(lm.held())
        self.assertEqual(lm.models([VERSION_IRI]), [(SLUG, want[f"{VERSION_IRI}/{SLUG}.erstudio"], want[f"{VERSION_IRI}/{SLUG}.layer"])])

    def test_a_current_jena_and_delta_hold_each_package_graph_with_the_files_triple_count(self):
        from rdflib import Graph
        want = ss.jena_graphs([VERSION_IRI], "worktree")
        self.assertEqual(set(want), {VERSION_IRI, f"{VERSION_IRI}/shapes", f"{VERSION_IRI}/catalog",
                                     f"{VERSION_IRI}/{SLUG}.erstudio", f"{VERSION_IRI}/{SLUG}.layer"})
        self.assertEqual(want[f"{VERSION_IRI}/{SLUG}.erstudio"], len(Graph().parse(os.path.join(EXAMPLE, f"{SLUG}.erstudio.ttl"))))
        held = dict(want)
        del held[f"{VERSION_IRI}/{SLUG}.layer"]
        self.assertEqual(ss.judge_jena(held, want)[0], "behind")  # a reload without the model graphs

    def test_a_model_without_its_layer_stops_the_load(self):
        self.write_manifest(["logical-model.ttl", "shapes.ttl", "catalog.ttl", f"{SLUG}.erstudio.ttl"])
        with self.assertRaisesRegex(SystemExit, "lacks its layer"):
            lm.models([VERSION_IRI])

    def test_a_release_set_without_the_module_has_no_model(self):
        self.assertEqual(lm.models(["https://w3id.org/lsc/ontology/modules/kpi/1.3.0"]), [])


class Subgraph(Package):
    def test_every_node_is_a_logical_model_node_and_none_is_a_resource(self):
        nodes, _ = self.rows()
        kinds = {}
        for n in nodes:
            self.assertEqual(n["labels"][0], lm.LABEL)
            self.assertNotIn("Resource", n["labels"])
            kinds.setdefault(n["labels"][1], []).append(n["props"])
        self.assertEqual({k: len(v) for k, v in kinds.items()}, {"Model": 1, "Entity": 3, "Attribute": 7, "Key": 3})
        account = next(p for p in kinds["Entity"] if p["erstudio_id"] == "101")
        self.assertEqual((account["name"], account["models"]), ("Example_Account_Dim", [SLUG]))
        self.assertTrue(account["description"].startswith("An invented table of example accounts"))
        name = next(p for p in kinds["Attribute"] if p["name"] == "Account_Name")
        self.assertEqual((name["datatype"], name["business_term"]), ("string", ER + "Term_Example_Account_Name"))
        self.assertEqual(sorted(p["key_type"] for p in kinds["Key"]), ["AlternateKey", "PrimaryKey", "PrimaryKey"])

    def test_the_edges_hold_the_attributes_keys_relationships_and_the_layers_links(self):
        _, edges = self.rows()
        types = {}
        for e in edges:
            types.setdefault(e["t"], []).append(e)
        self.assertEqual({t: len(v) for t, v in types.items()},
                         {"IN_MODEL": 3, "HAS_ATTRIBUTE": 7, "HAS_KEY": 3, "ON_ATTRIBUTE": 3, "RELATES_TO": 1,
                          "SOURCE_SYSTEM": 2, "DESCRIBES": 2, "IMPLEMENTED_BY": 1})
        relates = types["RELATES_TO"][0]  # ER Studio's inverse twin is left out
        self.assertEqual((relates["s"], relates["o"], relates["p"]["name"]),
                         (ER + "example_core_Example_Account_Dim", ER + "example_core_Example_Contact_Dim", "connected by Account_Id"))
        self.assertTrue(all(e["ontology"] for t in ("SOURCE_SYSTEM", "DESCRIBES", "IMPLEMENTED_BY") for e in types[t]))
        self.assertFalse(any(e["ontology"] for t in ("IN_MODEL", "HAS_ATTRIBUTE", "HAS_KEY", "ON_ATTRIBUTE") for e in types[t]))
        self.assertIn("https://w3id.org/lsc/ontology/modules/party/CustomerAccount", {e["o"] for e in types["DESCRIBES"]})

    def test_the_digest_covers_each_model_file_by_name_and_content(self):
        files = lm.models([VERSION_IRI])
        first = lm.digest(files)
        with open(os.path.join(self.folder, f"{SLUG}.layer.ttl"), "a") as f:
            f.write("\n# changed\n")
        self.assertNotEqual(lm.digest(files), first)


class Tx:
    """A Neo4j transaction that records its statements and finds every edge's target."""

    def __init__(self):
        self.queries, self.state = [], "open"

    def run(self, query, **params):
        self.queries.append((query, params))
        n = len(params.get("rows", [])) if "CREATE (a)" in query else 0
        return types.SimpleNamespace(consume=lambda: None, single=lambda: {"n": n}, value=lambda: [])

    def commit(self):
        self.state = "committed"

    def rollback(self):
        self.state = "rolled back"

    def closed(self):
        return self.state != "open"


class Loading(Package):
    def session(self, tx):
        class Session(contextlib.nullcontext):
            def begin_transaction(self):
                return tx

            def run(self, *a, **k):
                raise AssertionError("a write outside the transaction")
        return mock.patch.object(ss, "neo4j_session", lambda store: (contextlib.nullcontext(), Session()))

    def test_neo4j_gets_the_subgraph_and_its_marker_in_one_committed_transaction_apart_from_resource(self):
        tx = Tx()
        with self.session(tx), mock.patch("sys.stdout", io.StringIO()):
            lm.load_neo4j("driver", lm.models([VERSION_IRI]))
        self.assertEqual(tx.state, "committed")
        queries = [q for q, _ in tx.queries]
        self.assertIn(f"MATCH (m:{lm.MARKER_LABEL}) DETACH DELETE m", queries)
        self.assertIn(f"MATCH (n:{lm.LABEL}) DETACH DELETE n", queries)
        created = next(p["rows"] for q, p in tx.queries if q.startswith("UNWIND $rows AS row CREATE (n:"))
        self.assertTrue(all(r["labels"][0] == lm.LABEL and "Resource" not in r["labels"] for r in created))
        edge_queries = [q for q in queries if "CREATE (a)" in q]
        self.assertEqual(len(edge_queries), 2)
        self.assertTrue(all("SET r = row.p" in q for q in edge_queries))
        self.assertIn(f"(b:{lm.LABEL} {{uri: row.o}})", edge_queries[0])
        self.assertIn("(b:Resource {uri: row.o})", edge_queries[1])
        marker = tx.queries[-1]
        self.assertEqual(marker[0], f"CREATE (m:{lm.MARKER_LABEL}) SET m = $p")
        self.assertEqual((marker[1]["p"]["digest"], marker[1]["p"]["models"]), (lm.digest(lm.models([VERSION_IRI])), [SLUG]))

    def test_an_edge_with_no_target_rolls_back_and_writes_no_marker(self):
        tx = Tx()
        tx.run = lambda query, **params: (tx.queries.append((query, params)) or
                                          types.SimpleNamespace(consume=lambda: None, single=lambda: {"n": 0}, value=lambda: []))
        with self.session(tx), self.assertRaisesRegex(SystemExit, "edges found no target"):
            lm.load_neo4j("driver", lm.models([VERSION_IRI]))
        self.assertEqual(tx.state, "rolled back")
        self.assertFalse(any(q.startswith(f"CREATE (m:{lm.MARKER_LABEL})") for q, _ in tx.queries))

    def fake_rdfstore(self, published):
        class Fuseki:
            def __init__(self, gsp, query, update):
                published.append(("store", gsp, query, update))

            def publish(self, dataset):
                published.append(("publish", dataset))
        return types.SimpleNamespace(pack=lambda paths, named: sorted(named.values()), FusekiStore=Fuseki,
                                     to_rows=lambda dataset: [("s", "p", "o", "iri", None, None, g) for g in dataset],
                                     insert_sql=lambda table, rows: f"INSERT {table} {len(rows)}",
                                     DatabricksStore=types.SimpleNamespace(BATCH=2000))

    def test_jena_gets_every_package_graph_in_one_update_under_its_graph_iri(self):
        published = []
        graphs = lm.package_graphs([VERSION_IRI])
        with mock.patch("sys.stdout", io.StringIO()):
            lm.load_jena(self.fake_rdfstore(published), graphs)
        base = ss.JENA_QUERY.rsplit("/", 1)[0]
        self.assertEqual(published, [("store", base + "/data", ss.JENA_QUERY, base + "/update"), ("publish", sorted(graphs))])

    def databricks(self, counts):
        executed = []

        class Cursor(contextlib.nullcontext):
            def __enter__(self):
                return self

            def execute(self, query, params=None):
                executed.append((query, params))

            def fetchall(self):
                return list(counts.items())

        class Conn(contextlib.nullcontext):
            def cursor(self):
                return Cursor()
        return executed, mock.patch.object(ss, "databricks", lambda: (Conn(), "c.s"))

    def test_delta_replaces_only_the_package_graphs_rows_and_refuses_a_count_that_differs(self):
        from rdflib import Graph
        graphs = lm.package_graphs([VERSION_IRI])
        counts = {iri: len(Graph().parse(os.path.join(self.root, p))) for iri, p in graphs.items()}
        executed, patch = self.databricks(counts)
        with patch, mock.patch("sys.stdout", io.StringIO()):
            lm.load_databricks(self.fake_rdfstore([]), graphs)
        self.assertTrue(executed[0][0].startswith(f"DELETE FROM c.s.{ss.TRIPLES_TABLE} WHERE graph IN (?, ?)"))
        self.assertEqual(sorted(executed[0][1]), sorted(graphs))
        self.assertTrue(any(q.startswith(f"INSERT c.s.{ss.TRIPLES_TABLE}") for q, _ in executed))
        executed, patch = self.databricks({**counts, next(iter(counts)): 1})
        with patch, self.assertRaisesRegex(SystemExit, "rows of the package graphs"):
            lm.load_databricks(self.fake_rdfstore([]), graphs)

    def test_load_sends_each_store_its_part(self):
        calls = []
        with mock.patch.object(lm, "newest", lambda ref=None: [VERSION_IRI]), mock.patch.object(lm, "rdfstore", lambda skills: "rs"), \
                mock.patch.object(lm, "load_jena", lambda rs, g: calls.append(("jena", rs, sorted(g)))), \
                mock.patch.object(lm, "load_databricks", lambda rs, g: calls.append(("databricks", rs, sorted(g)))), \
                mock.patch.object(lm, "load_neo4j", lambda store, files: calls.append((store, [f[0] for f in files]))):
            lm.load(ss.STORES, "~/skills")
        graphs = sorted(lm.package_graphs([VERSION_IRI]))
        self.assertEqual(calls, [("driver", [SLUG]), ("aura", [SLUG]), ("jena", "rs", graphs), ("databricks", "rs", graphs)])


class Drift(Package):
    def neo4j(self, nodes, edges, marker):
        class Result(list):
            def single(self):
                return self[0] if self else None

        class Session(contextlib.nullcontext):
            def run(_, query, **kw):
                if lm.MARKER_LABEL in query:
                    return Result([{"p": marker}] if marker else [])
                return Result(nodes if query == lm.NEO4J_NODES else edges)
        return mock.patch.object(ss, "neo4j_session", lambda store: (contextlib.nullcontext(), Session()))

    def status(self, nodes, edges, marker):
        with self.neo4j(nodes, edges, marker), mock.patch.object(lm, "newest", lambda ref=None: [VERSION_IRI]):
            return lm.check(("driver", "jena"))

    def test_each_status(self):
        nodes, edges = self.rows()
        live = [{"labels": n["labels"], "p": dict(n["props"])} for n in nodes]
        marker = {"digest": lm.digest(lm.models([VERSION_IRI])), "marked_at": "t"}
        self.assertEqual([r[:2] for r in self.status(live, edges, marker)], [("driver", "current")])  # Jena has no lm: line
        live[1]["p"]["description"] = "edited by hand"
        self.assertEqual(self.status(live, edges, marker)[0][1], "changed")
        self.assertEqual(self.status(live, edges, {**marker, "digest": "e" * 64})[0][1], "behind")
        self.assertEqual(self.status(live, edges, None)[0][1], "unmarked")
        edited = [dict(e) for e in edges]
        relates = next(e for e in edited if e["t"] == "RELATES_TO")
        relates["p"] = {**relates["p"], "name": "renamed"}
        self.assertEqual(self.status([{"labels": n["labels"], "p": dict(n["props"])} for n in nodes], edited, marker)[0][1], "changed")

    def git(self, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        subprocess.run(["git", "-C", self.root, *args], check=True, capture_output=True, env=env)

    def commit_catalog(self, with_package):
        """Writes the repository's catalog, with or without the package's dataset, and commits the tree; returns the commit."""
        catalog = os.path.join(self.root, ss.CATALOG)
        with open(catalog, "w") as f:
            f.write(f"<{VERSION_IRI}/../catalog> <http://www.w3.org/ns/dcat#dataset> <{VERSION_IRI}> .\n" if with_package else "")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@example.org", "commit", "-q", "-m", "c")
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        return subprocess.run(["git", "-C", self.root, "rev-parse", "HEAD"], capture_output=True, text=True, env=env).stdout.strip()

    def lines(self, ref):
        with self.neo4j([], [], None):  # a store whose subgraph was wiped: no marker
            return [r[:2] for r in lm.check(("driver",), ref)]

    def test_the_lm_line_follows_the_ref_that_holds_the_package_not_the_working_tree(self):
        self.git("init", "-q")
        ref = self.commit_catalog(with_package=True)
        shutil.rmtree(self.folder)  # the working tree has no package; the ref does
        with open(os.path.join(self.root, ss.CATALOG), "w") as f:
            f.write("")
        self.assertEqual(self.lines(ref), [("driver", "unmarked")])
        self.assertEqual(self.lines("worktree"), [])

    def test_the_lm_line_follows_a_ref_that_holds_no_package_though_the_working_tree_does(self):
        self.git("init", "-q")
        ref = self.commit_catalog(with_package=False)
        with open(os.path.join(self.root, ss.CATALOG), "w") as f:
            f.write(f"<{VERSION_IRI}/../catalog> <http://www.w3.org/ns/dcat#dataset> <{VERSION_IRI}> .\n")
        self.assertEqual(self.lines(ref), [])
        self.assertEqual(self.lines("worktree"), [("driver", "unmarked")])

    def test_an_unreachable_store_says_so(self):
        def no_login(store):
            raise FileNotFoundError(store)
        with mock.patch.object(ss, "neo4j_session", no_login), mock.patch.object(lm, "newest", lambda ref=None: [VERSION_IRI]):
            self.assertEqual(lm.check(("driver", "aura")), [("driver", "unreachable", "unreachable (FileNotFoundError)"),
                                                            ("aura", "unreachable", "unreachable (FileNotFoundError)")])

    def test_check_prints_an_lm_line_and_fails_when_a_logical_model_is_not_current(self):
        want = {"catalog_datasets": 1, "catalog_digest": "d", "input_fingerprint": "f", "newest": []}
        marker = {"catalog_datasets": 1, "catalog_digest": "d", "input_fingerprint": "f", "count": [1, 2, 3], "marked_at": "t", "commit": "c"}
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["sync_stores.py", "check", "--store", "driver"]), \
                mock.patch.object(ss, "read_markers_and_counts", lambda stores: ({"driver": marker}, {"driver": [1, 2, 3]})), \
                mock.patch.object(ss, "read_tech_markers", lambda stores: {}), \
                mock.patch.object(ss, "tech_drift", lambda *a: [("driver", "current", "")]), \
                mock.patch.object(ss, "logical_models", lambda: types.SimpleNamespace(check=lambda stores, ref=None: [("driver", "unmarked", "")])), \
                mock.patch.object(ss, "expected_for", lambda ref, stores: want), mock.patch("sys.stdout", out):
            with self.assertRaises(SystemExit) as stop:
                ss.main()
        self.assertEqual(stop.exception.code, 1)
        self.assertEqual({line.split()[0]: line.split()[1] for line in out.getvalue().splitlines()},
                         {"driver": "current", "tech:driver": "current", "lm:driver": "unmarked"})


class Plans(unittest.TestCase):
    def cmds(self, behind, cloud, tech_behind=(), models=None):
        return [" ".join(c) for _, c in ss.plan(behind, cloud, "~/skills", tech_behind, models)[0]]

    def test_sync_loads_the_logical_models_last_where_a_reload_wiped_them_or_they_are_not_current(self):
        self.assertFalse(any("logical_models.py" in c for c in self.cmds(["driver"], False)))  # releases with no package graph
        cmds = self.cmds(["driver"], False, models=[])
        self.assertTrue(cmds[-1].endswith("logical_models.py load --store driver --store jena --skills ~/skills"))
        self.assertEqual(self.cmds([], False, models=[]), [])
        self.assertEqual(self.cmds([], False, models=["aura"]), [])  # AuraDB only with --cloud
        self.assertTrue(self.cmds([], True, models=["aura"])[-1].endswith("logical_models.py load --store aura --skills ~/skills"))
        cmds = self.cmds(["aura"], True, models=[])
        self.assertIn("--with databricks-sql-connector", cmds[-1])
        self.assertTrue(cmds[-1].endswith("load --store driver --store aura --store jena --store databricks --skills ~/skills"))

    def test_the_rebuild_loads_the_logical_models_after_the_technical_graph_and_before_mark(self):
        s = {"EPM_SKILLS": "/skills", "EPM_OUT": "/out", "SOURCE_PG_DSN": "x", "EPM_LINEAGE_WAIT_SECONDS": "0"}
        stores = ("driver", "jena", "aura", "databricks")
        self.assertNotIn("model-load", [n for n, _, _ in rb.plan(s, stores, "/c.json", False)])
        steps = rb.plan(s, stores, "/c.json", False, models=True)
        names = [n for n, _, _ in steps]
        self.assertEqual(names[names.index("tech-sync") + 1:], ["model-load", "mark", "check"])
        cmd = " ".join(dict((n, c) for n, _, c in steps)["model-load"])
        self.assertIn("--with pyoxigraph", cmd)
        self.assertTrue(cmd.endswith("logical_models.py load --store driver --store jena --store aura --store databricks --skills /skills"))


if __name__ == "__main__":
    unittest.main()
