"""Offline tests of rebuild_stores.py and empty_stores.py: no store is contacted."""
import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import empty_stores as es  # noqa: E402
import rebuild_stores as rb  # noqa: E402

AURA = "NEO4J_URI=neo4j+s://x\nNEO4J_USERNAME=neo4j\nNEO4J_PASSWORD=secret-aura\n"
DBX = ("DATABRICKS_HOST=https://x\nDATABRICKS_TOKEN=secret-token\nDATABRICKS_HTTP_PATH=/p\nDATABRICKS_CATALOG=c\nDATABRICKS_SCHEMA=s\n")
ALL = ("driver", "jena", "aura", "databricks")


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name

    def env_file(self, text, mode=0o600):
        path = os.path.join(self.tmp, "qa.env")
        with open(path, "w") as f:
            f.write(text)
        os.chmod(path, mode)
        return path

    def skills(self):
        for script in ("ontology-to-lpg/scripts/run_projection.py", "rdf-store/scripts/rdfstore.py"):
            path = os.path.join(self.tmp, "skills", script)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w").close()
        return os.path.join(self.tmp, "skills")


class Settings(Base):
    def test_a_file_others_can_read_is_refused(self):
        with self.assertRaisesRegex(rb.Refused, "chmod 600"):
            rb.settings(self.env_file("", 0o644))

    def test_an_unknown_key_is_refused_and_named(self):
        with self.assertRaisesRegex(rb.Refused, "EPM_NEO4J_PROT"):
            rb.settings(self.env_file("EPM_NEO4J_PROT=1\n"))

    def test_a_missing_file_is_refused(self):
        with self.assertRaisesRegex(rb.Refused, "no environment file"):
            rb.settings(os.path.join(self.tmp, "none"))

    def test_the_file_overrides_every_default_and_home_paths_are_defaults_only(self):
        s = rb.settings(self.env_file("EPM_OUT=/q/out\nEPM_NEO4J_PORT=1\nEPM_ROBOT_JAR=/q/r.jar\n"))
        self.assertEqual((s["EPM_OUT"], s["EPM_NEO4J_PORT"], s["EPM_ROBOT_JAR"]), ("/q/out", "1", "/q/r.jar"))
        self.assertEqual(s["EPM_AURA_ENV"], os.path.join(self.tmp, "qa.env"))  # the logins may sit in this one file

    def test_every_key_in_the_example_is_known_and_every_known_key_is_listed(self):
        with open(os.path.join(HERE, "skill-run", "environment.example")) as f:
            text = f.read()
        listed = {line[2:].split("=")[0] for line in text.splitlines() if line.startswith("# ") and "=" in line.split()[1]}
        self.assertEqual(listed - rb.KNOWN, set())
        self.assertEqual(rb.KNOWN - listed - {"AURA_INSTANCEID", "AURA_INSTANCENAME"}, set())


class Preflight(Base):
    def test_each_missing_thing_is_named_and_no_value_is_printed(self):
        s = rb.settings(self.env_file("NEO4J_URI=neo4j+s://x\nNEO4J_PASSWORD=secret-aura\nDATABRICKS_HOST=h\n" + f"EPM_SKILLS={self.tmp}/none\nEPM_ROBOT_JAR={self.tmp}/none.jar\n"))
        problems = rb.preflight(s, ALL, which=lambda tool: None)
        text = "\n".join(problems)
        for needed in ("docker is not on the PATH", "uv is not", "java", "EPM_SKILLS", "EPM_ROBOT_JAR", "lacks NEO4J_USERNAME", "lacks DATABRICKS_TOKEN"):
            self.assertIn(needed, text)
        self.assertNotIn("secret-aura", text)

    def test_a_robot_with_another_checksum_is_named(self):
        jar = os.path.join(self.tmp, "r.jar")
        with open(jar, "w") as f:
            f.write("other")
        s = rb.settings(self.env_file(f"EPM_SKILLS={self.skills()}\nEPM_ROBOT_JAR={jar}\n"))
        self.assertEqual(rb.preflight(s, ("driver",), which=lambda tool: tool), [f"EPM_ROBOT_JAR: {jar} is not the pinned ROBOT 1.9.10"])

    def test_the_local_part_needs_no_cloud_value(self):
        s = rb.settings(self.env_file(f"EPM_SKILLS={self.skills()}\n"))
        self.assertEqual(rb.preflight(s, ("jena",), which=lambda tool: tool), [])

    def test_aura_needs_the_local_neo4j(self):
        s = rb.settings(self.env_file(f"EPM_SKILLS={self.skills()}\n" + AURA))
        self.assertIn("aura is a copy of the local Neo4j: name driver too", rb.preflight(s, ("aura",), which=lambda tool: tool))


class LoginFiles(Base):
    def separate(self, text, mode=0o600):
        path = os.path.join(self.tmp, "aura.env")
        with open(path, "w") as f:
            f.write(text)
        os.chmod(path, mode)
        s = rb.settings(self.env_file(f"EPM_SKILLS={self.skills()}\nEPM_AURA_ENV={path}\n"))
        return rb.read_logins(s, ("aura",))[1], path

    def test_a_separate_login_file_others_can_read_is_refused(self):
        problems, path = self.separate(AURA, 0o644)
        self.assertEqual(problems, [f"aura: {path} is readable by others: run chmod 600 on it"])

    def test_a_separate_login_file_with_an_unknown_key_is_refused(self):
        problems, path = self.separate(AURA + "NEO4J_PASWORD=x\n")
        self.assertEqual(problems, [f"aura: {path}: the key NEO4J_PASWORD is not one this tool reads"])

    def test_a_correct_separate_login_file_passes(self):
        self.assertEqual(self.separate(AURA + "AURA_INSTANCEID=x\n")[0], [])


class Plan(Base):
    def names(self, stores, empty=True, extra=""):
        s = rb.settings(self.env_file(f"EPM_SKILLS={self.skills()}\n" + AURA + DBX + extra))
        return s, [n for n, _, _ in rb.plan(s, stores, "/c.json", empty)], rb.plan(s, stores, "/c.json", empty)

    def test_the_final_order_runs_the_build_right_before_the_lineage_check(self):
        _, names, _ = self.names(ALL)
        self.assertEqual(names, ["empty", "load", "record", "demo-postgres", "demo-sources", "demo-replicate", "demo-setup", "demo-upload",
                                 "demo-build", "demo-genie", "collect", "tech-build", "tech-compare", "lineage", "tech-load", "tech-sync",
                                 "mark", "check"])

    def test_the_local_part_runs_no_cloud_step(self):
        _, names, steps = self.names(("driver", "jena"), empty=False)
        self.assertEqual(names, ["load", "record", "tech-load", "mark", "check"])
        self.assertIn("copy,databricks,rebuild", dict((n, c) for n, _, c in steps)["load"])
        text = " ".join(" ".join(c) for _, _, c in steps)
        self.assertNotIn("aura", text)
        self.assertNotIn("databricks-sql-connector", text)

    def test_a_named_postgres_starts_no_container(self):
        _, names, _ = self.names(ALL, extra="SOURCE_PG_DSN=postgresql://u:p@h:1\n")
        self.assertNotIn("demo-postgres", names)

    def test_collect_waits_for_the_lineage_the_file_says(self):
        _, _, steps = self.names(ALL, extra="EPM_LINEAGE_WAIT_SECONDS=30\n")
        self.assertIn("30", dict((n, c) for n, _, c in steps)["collect"])

    def test_no_command_carries_a_secret(self):
        _, _, steps = self.names(ALL)
        text = " ".join(" ".join(c) for _, _, c in steps)
        self.assertNotIn("secret", text)

    def test_the_driver_runs_only_what_the_stores_need(self):
        self.assertEqual(rb.driver_arguments(ALL), [])
        self.assertEqual(rb.driver_arguments(("driver",)), ["--skip", "copy,jena,databricks,rebuild"])
        self.assertEqual(rb.driver_arguments(("jena",)), ["--only", "jena"])
        self.assertEqual(rb.driver_arguments(("databricks",)), ["--only", "databricks"])

    def test_the_run_configuration_names_this_environment_and_keeps_no_relative_path(self):
        s = rb.settings(self.env_file(f"EPM_SKILLS={self.skills()}\nEPM_OUT=/q/out\nEPM_NEO4J_PROJECT=qa\nEPM_NEO4J_PORT=5\nEPM_TRIPLES_TABLE=t\n"))
        cfg = rb.run_config(s, ALL, False)
        self.assertEqual((cfg["out"], cfg["neo4j"], cfg["databricks"]["table"], cfg["replace_target"]), ("/q/out", {"compose_project": "qa", "bolt_port": 5}, "t", False))
        for key in ("projection_config", "inputs_script", "releases", "queries", "robot_jar", "rdf_store"):
            self.assertTrue(os.path.isabs(cfg[key]), key)

    def test_the_stores_variable_holds_no_secret_and_the_demo_gets_the_logins_in_its_environment(self):
        s = rb.settings(self.env_file(f"EPM_SKILLS={self.skills()}\n" + AURA + DBX))
        env = rb.child_env(s, ALL, "/c.json")
        self.assertNotIn("secret", env["EPM_STORES_JSON"])
        self.assertEqual(json.loads(env["EPM_STORES_JSON"])["run_config"], "/c.json")
        self.assertEqual((env["DATABRICKS_TOKEN"], env["EPM_TRIPLES"]), ("secret-token", "c.s.epm_triples"))


class Running(Base):
    def holding(self, lines, code=0, containers="", docker_code=0):
        def fake(cmd, **k):
            if cmd[0] == "docker":
                return types.SimpleNamespace(stdout=containers, returncode=docker_code)
            return types.SimpleNamespace(stdout="\n".join(json.dumps(x) for x in lines), returncode=code)
        s = rb.settings(self.env_file(""))
        return rb.holding(s, ALL, {}, runner=fake)

    def test_holding_data_is_named_and_a_store_with_no_container_is_not_a_problem(self):
        lines = [{"store": "driver", "unreachable": "ServiceUnavailable"}, {"store": "jena", "held": 3},
                 {"store": "aura", "unreachable": "AuthError"}, {"store": "databricks", "held": 0}]
        held, problems = self.holding(lines)
        self.assertEqual(held, [("jena", 3)])
        self.assertEqual(problems, ["aura: could not be reached (AuthError); check its login values"])

    def test_a_stopped_container_counts_as_holding_data(self):
        lines = [{"store": "driver", "unreachable": "ServiceUnavailable"}, {"store": "jena", "held": 0},
                 {"store": "aura", "held": 0}, {"store": "databricks", "held": 0}]
        held, problems = self.holding(lines, containers="abc123\n")
        self.assertEqual(held, [("driver", "a container that did not answer, ServiceUnavailable")])
        self.assertEqual(problems, [])

    def test_docker_failing_to_list_containers_is_a_problem_not_an_empty_store(self):
        lines = [{"store": "driver", "unreachable": "ServiceUnavailable"}, {"store": "jena", "held": 0},
                 {"store": "aura", "held": 0}, {"store": "databricks", "held": 0}]
        held, problems = self.holding(lines, docker_code=1)
        self.assertEqual((held, problems), ([], ["driver: Docker could not list its containers; nothing was changed"]))

    def test_a_failed_count_is_not_an_empty_store(self):
        held, problems = self.holding([], code=1)
        self.assertEqual(held, [])
        self.assertIn("the count of what the stores hold failed", problems[0])

    def test_a_store_with_no_count_result_is_a_problem(self):
        held, problems = self.holding([{"store": "driver", "held": 0}])
        self.assertEqual(problems, [f"{store}: the count gave no result; nothing was changed" for store in ALL[1:]])

    def run_with(self, codes):
        calls = []

        def runner(cmd, **kw):
            calls.append(cmd[0])
            return types.SimpleNamespace(returncode=codes.get(cmd[0], 0))
        report = rb.Report(os.path.join(self.tmp, "r.json"), "e", ("driver",))
        failed = rb.run_steps([("a", self.tmp, ["one"]), ("b", self.tmp, ["two"]), ("c", self.tmp, ["three"])], {}, report, os.path.join(self.tmp, "logs"), runner=runner)
        report.finish(failed)
        return failed, calls, json.load(open(report.path))

    def test_every_step_passing(self):
        failed, calls, report = self.run_with({})
        self.assertIsNone(failed)
        self.assertEqual(calls, ["one", "two", "three"])
        self.assertEqual((report["result"], report["failed_step"]), ("passed", None))

    def test_a_failed_step_stops_the_run_and_the_report_names_it(self):
        failed, calls, report = self.run_with({"two": 3})
        self.assertEqual(failed, "b")
        self.assertEqual(calls, ["one", "two"])
        self.assertEqual((report["result"], report["failed_step"]), ("failed", "b"))
        self.assertEqual([x["status"] for x in report["steps"]], ["passed", "failed"])

    def test_main_refuses_before_anything_changes_and_exits_2(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), mock.patch.object(rb, "holding", side_effect=AssertionError("no store is read")):
            self.assertEqual(rb.main(["--env", self.env_file(f"EPM_SKILLS={self.tmp}/none\n")]), 2)
        self.assertIn("REFUSED EPM_SKILLS", err.getvalue())

    def test_main_refuses_a_store_that_holds_data_without_empty(self):
        env = self.env_file(f"EPM_SKILLS={self.skills()}\nEPM_OUT={self.tmp}/out\n")
        err = io.StringIO()
        with contextlib.redirect_stderr(err), mock.patch.object(rb, "holding", lambda *a: ([("jena", 3)], [])), \
                mock.patch.object(rb, "run_steps", side_effect=AssertionError("no step runs")):
            self.assertEqual(rb.main(["--env", env, "--store", "jena"]), 2)
        self.assertIn("jena holds data (3): pass --empty", err.getvalue())
        self.assertFalse(os.path.exists(f"{self.tmp}/out-run.json"))  # a refusal changes nothing


class Empty(unittest.TestCase):
    class Session:
        def __init__(self, nodes):
            self.nodes, self.queries = nodes, []

        def run(self, query):
            self.queries.append(query)
            if "DETACH DELETE" in query:
                n = min(5000, self.nodes)
                self.nodes -= n
                return mock.Mock(single=lambda: {"c": n})
            return mock.Mock(single=lambda: {"n": self.nodes})

    def test_counting_deletes_nothing_and_yes_empties_in_batches(self):
        s = self.Session(12000)
        session_pair = (mock.MagicMock(), mock.MagicMock())
        session_pair[1].__enter__.return_value = s
        session_pair[1].run = s.run
        with mock.patch.object(es.ss, "neo4j_session", lambda store: session_pair):
            self.assertEqual(es.one_store("driver", False), {"store": "driver", "held": 12000})
            self.assertFalse(any("DELETE" in q for q in s.queries))
            self.assertEqual(es.one_store("driver", True), {"store": "driver", "held": 12000, "after": 0})

    def test_databricks_drops_only_this_tools_tables(self):
        class Cur:
            def __init__(self):
                self.sql = []

            def execute(self, sql):
                self.sql.append(sql)

            def fetchall(self):
                return [("s", "epm_triples", False), ("s", "epm_store_markers", False), ("s", "somebody_elses", False)]
        cur = Cur()
        self.assertEqual(es.databricks_tables(cur, "c.s"), ["epm_store_markers", "epm_triples"])

    def test_no_yes_means_no_write_and_an_unreachable_store_is_reported_without_its_message(self):
        out = io.StringIO()

        def down(store):
            raise ConnectionError("bolt://user:secret@host")
        with contextlib.redirect_stdout(out), mock.patch.object(es.ss, "neo4j_session", down):
            self.assertEqual(es.main(["--store", "driver"]), 0)
        self.assertEqual(json.loads(out.getvalue()), {"store": "driver", "unreachable": "ConnectionError"})
        with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(es.ss, "neo4j_session", down):
            self.assertEqual(es.main(["--store", "driver", "--yes"]), 0)  # not running: nothing to delete, and the load creates it
            self.assertEqual(es.main(["--store", "aura", "--yes"]), 1)    # a cloud store must answer before it is replaced


if __name__ == "__main__":
    unittest.main()
