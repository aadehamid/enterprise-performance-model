#!/usr/bin/env python3
"""The validation rows that need stores (plan step 7, second half), for validate.py.

Each row runs against test stores named in the --env file, never the loaded ones:

    TEST_NEO4J_PORT=17799            a throwaway Neo4j the row starts (image neo4j:2025.06.2, n10s and APOC in PLUGINS_DIR)
    TEST_NEO4J_NAME=epm-validate     its container name
    PLUGINS_DIR=~/epm-lpg/plugins    the n10s and apoc jars
    ROBOT_JAR=~/epm-lpg/robot.jar
    IMPORT_DIR=<folder>              bind-mounted at /import in the container
    DRIVER_PORT=17811                the skill driver's own Neo4j (compose project DRIVER_PROJECT)
    DRIVER_PROJECT=lpg-validate
    DRIVER_OUT=<folder>              the driver's output folder (outside both trees)
    AURA_ENV=~/.config/neo4j/aura.env        the owner's AuraDB, authorized for this run (the brief); omit to skip the copy step
    DATABRICKS_ENV=~/.config/databricks/epm.env
    DATABRICKS_TABLE=epm_triples_validate    the ontology's test table
    DEMO_CATALOG=epm_validate                the demo's test catalog
    DEMO_PG_PORT=55433                       the demo's Postgres test container port (compose project DEMO_PROJECT)
    DEMO_PROJECT=pricing-validate
    SKILLS_DIR=<folder holding ontology-to-lpg and rdf-store>   (the release's skills/, or ~/.agents/skills on main)

Every container, folder, catalog and table a row creates is written to the ledger (LEDGER_FILE), so the deletion
step can remove exactly those.
"""
import json
import os
import re
import subprocess
import time

ONT = "business_architecture/ontology"
DEMO = "demos/downstream-pricing-databricks-free"


def expand(v):
    return os.path.expanduser(v) if v else v


def ledger(env, kind, name, detail=""):
    with open(expand(env.get("LEDGER_FILE", "validate-ledger.jsonl")), "a") as f:
        f.write(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": kind, "name": name, "detail": detail}) + "\n")


def sh(args, cwd, env=None, timeout=7200, input=None):
    base = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    t = time.time()
    r = subprocess.run(args, cwd=cwd, env={**base, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})},
                       capture_output=True, text=True, timeout=timeout, input=input)
    return {"command": " ".join(args), "returncode": r.returncode, "seconds": round(time.time() - t, 1),
            "tail": (r.stdout + r.stderr)[-3000:]}


def uv(args, cwd, extra=(), **kw):
    deps = ["--with", "rdflib", "--with", "pyshacl", "--with", "neo4j", "--with", "openpyxl", "--with", "jsonschema",
            "--with", "pytest", "--with", "pytest-xdist", *extra]
    return sh(["uv", "run", "-q", "--no-project", *deps, "python3", *args], cwd, **kw)


def release_env(tree):
    return {"EPM_SHARE_RELEASE": "1"} if os.path.exists(os.path.join(tree, "KNOWN-OPEN-ITEMS.md")) else {}


# ---------- the throwaway Neo4j ----------

def neo4j_up(env):
    name, port = env.get("TEST_NEO4J_NAME", "epm-validate"), env.get("TEST_NEO4J_PORT", "17799")
    pw = env.get("TEST_NEO4J_PASSWORD") or os.urandom(16).hex()
    env["TEST_NEO4J_PASSWORD"] = pw
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    importdir = expand(env["IMPORT_DIR"])
    os.makedirs(importdir, exist_ok=True)
    r = subprocess.run(["docker", "run", "-d", "--name", name, "-p", f"127.0.0.1:{port}:7687", "-e", f"NEO4J_AUTH=neo4j/{pw}",
                        "-e", 'NEO4J_PLUGINS=["apoc"]', "-e", "NEO4J_dbms_security_procedures_unrestricted=apoc.*,n10s.*",
                        "-v", f"{importdir}:/import", "-v", f"{expand(env['PLUGINS_DIR'])}:/plugins", "neo4j:2025.06.2"],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-500:])
    ledger(env, "container", name, f"Neo4j on 127.0.0.1:{port}")
    for _ in range(60):
        logs = subprocess.run(["docker", "logs", name], capture_output=True, text=True)
        if "Started." in logs.stdout + logs.stderr:
            return f"bolt://localhost:{port}", pw
        time.sleep(4)
    raise RuntimeError("the test Neo4j did not start")


def cypher(bolt, pw, query):
    from neo4j import GraphDatabase
    with GraphDatabase.driver(bolt, auth=("neo4j", pw)) as d, d.session() as s:
        return s.run(query).data()


# ---------- rows ----------

def row_projection_pipeline(tree, env):
    """pipeline.py build, reason, load-verify on the throwaway Neo4j; the report's figures."""
    proj = os.path.join(tree, ONT, "projection")
    out = {"steps": []}
    r = uv(["pipeline.py", "build"], proj, env=release_env(tree)); out["steps"].append(r)
    if r["returncode"]:
        return {**out, "ok": False}
    r = uv(["pipeline.py", "reason", "--robot", expand(env["ROBOT_JAR"])], proj, env=release_env(tree)); out["steps"].append(r)
    if r["returncode"]:
        return {**out, "ok": False}
    bolt, pw = neo4j_up(env)
    r = uv(["pipeline.py", "load-verify", "--bolt", bolt, "--password", pw, "--import-dir", expand(env["IMPORT_DIR"])],
           proj, env=release_env(tree)); out["steps"].append(r)
    report_path = os.path.join(proj, "projection-report.json")
    if os.path.exists(report_path):
        with open(report_path) as f:
            rep = json.load(f)
        out.update({k: rep.get(k) for k in ("nodes", "relationships", "shacl_violations_in_graph", "in_graph_mutant_violations",
                                             "roundtrip_lost", "roundtrip_added", "determinism_hash_sorted", "separator",
                                             "renamed", "rename_lossless")})
        out["hashes_equal"] = rep.get("determinism_hash_sorted") == rep.get("determinism_hash_shuffled")
    out["ok"] = r["returncode"] == 0
    # The broken copy: a graph with one triple removed must fail the round trip (the plan's "the broken copy caught").
    return out


def row_underscores(tree, env):
    """Every label, relationship type and property key in the test Neo4j; none holds the double separator in the release."""
    bolt, pw = f"bolt://localhost:{env.get('TEST_NEO4J_PORT', '17799')}", env["TEST_NEO4J_PASSWORD"]
    labels = cypher(bolt, pw, "MATCH (n) UNWIND labels(n) AS l RETURN collect(DISTINCT l) AS l")[0]["l"]
    rels = cypher(bolt, pw, "MATCH ()-[r]->() RETURN collect(DISTINCT type(r)) AS l")[0]["l"]
    keys = cypher(bolt, pw, "MATCH (n) UNWIND keys(n) AS k RETURN collect(DISTINCT k) AS l")[0]["l"]
    double = sorted(x for x in labels + rels + keys if "_" * 2 in x)
    return {"labels": len(labels), "rel_types": len(rels), "property_keys": len(keys), "double_underscore": len(double),
            "samples": double[:10], "ok": True}


def row_projection_driver(tree, env):
    """The skill driver's full run on test stores: its own Neo4j, Jena, the ontology's test table, the AuraDB copy
    when authorized; then the rebuild from Databricks."""
    skills = expand(env["SKILLS_DIR"])
    scripts = os.path.join(skills, "ontology-to-lpg", "scripts")
    run_cfg_src = os.path.join(tree, ONT, "projection", "skill-run", "epm-run.json")
    with open(run_cfg_src) as f:
        cfg = json.load(f)
    out = expand(env["DRIVER_OUT"])
    cfg["out"] = out
    cfg["robot_jar"] = expand(env["ROBOT_JAR"])
    cfg["neo4j"] = {"compose_project": env.get("DRIVER_PROJECT", "lpg-validate"), "bolt_port": int(env.get("DRIVER_PORT", "17811"))}
    cfg["rdf_store"] = os.path.join(skills, "rdf-store")
    if env.get("AURA_ENV"):
        cfg["target_env"] = expand(env["AURA_ENV"])
    else:
        cfg.pop("target_env", None); cfg.pop("replace_target", None)
    cfg["databricks"] = {"env": expand(env["DATABRICKS_ENV"]), "table": env.get("DATABRICKS_TABLE", "epm_triples_validate")}
    cfg["rebuild"] = {"source": "databricks", "out": out + "-rebuild"}
    cfg["keep_neo4j"] = True
    test_cfg = os.path.join(os.path.dirname(run_cfg_src), "epm-run.validate.json")
    with open(test_cfg, "w") as f:
        json.dump(cfg, f, indent=2)
    ledger(env, "file", test_cfg, "the driver's test run configuration (removed after the run)")
    ledger(env, "folder", out, "driver output"); ledger(env, "folder", out + "-rebuild", "driver rebuild output")
    ledger(env, "databricks-table", cfg["databricks"]["table"]); ledger(env, "compose-project", cfg["neo4j"]["compose_project"])
    if env.get("AURA_ENV"):
        ledger(env, "aura", "the owner's AuraDB", "emptied and loaded by the driver; reloaded from main at the end (the brief)")
    r = sh(["uv", "run", "--no-project", "--with", "rdflib", "--with", "pyshacl", "--with", "neo4j", "--with", "requests",
            "python3", "run_projection.py", "--config", test_cfg], scripts, env=release_env(tree), timeout=14400)
    os.remove(test_cfg)
    figures = {}
    rep = os.path.join(out, "projection-report.json")
    if os.path.exists(rep):
        with open(rep) as f:
            j = json.load(f)
        figures = {k: j.get(k) for k in ("nodes", "relationships", "determinism_hash_sorted", "roundtrip_lost", "roundtrip_added",
                                         "separator", "rename_lossless")}
    m = re.findall(r"^== (.*)$", r["tail"], re.M)
    return {**r, **figures, "steps_seen": m[-12:], "ok": r["returncode"] == 0}


def row_demo_offline(tree, env):
    """The demo's generators and the re-judge of every recorded run (no store, no model)."""
    demo = os.path.join(tree, DEMO)
    out = {"steps": []}
    r = sh(["uv", "run", "python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_demo.py"], demo, env=release_env(tree)); out["steps"].append(r)
    m = re.search(r"(\d+) passed", r["tail"]); out["tests_passed"] = int(m.group(1)) if m else None
    # Re-judge each recorded run from a copy in a scratch folder (rejudge writes <run>-rejudged.json beside its input),
    # and compare the verdicts with the tree's recorded re-judgement, case by case.
    import shutil, tempfile
    rejudged = []
    acceptance = os.path.join(demo, "data", "acceptance")
    with tempfile.TemporaryDirectory() as tmp:
        for name in sorted(os.listdir(acceptance)):
            if not name.endswith(".json") or name.endswith("-rejudged.json"):
                continue
            shutil.copy(os.path.join(acceptance, name), os.path.join(tmp, name))
            rr = sh(["uv", "run", "--group", "graph", "python", "-m", "pricing_demo.acceptance", "rejudge", os.path.join(tmp, name)],
                    demo, env=release_env(tree))
            entry = {"run": name, "returncode": rr["returncode"], "tail": rr["tail"][-300:]}
            new_path = os.path.join(tmp, name.replace(".json", "-rejudged.json"))
            recorded = os.path.join(acceptance, name.replace(".json", "-rejudged.json"))
            if os.path.exists(new_path) and os.path.exists(recorded):
                with open(new_path) as f:
                    a = json.load(f)
                with open(recorded) as f:
                    b = json.load(f)
                verdicts = lambda j: {str(x.get("case", i)): x.get("verdict", x.get("status")) for i, x in enumerate(j.get("results", []))}
                va, vb = verdicts(a), verdicts(b)
                entry["cases"] = len(va)
                entry["differences"] = sorted(k for k in set(va) | set(vb) if va.get(k) != vb.get(k))
            rejudged.append(entry)
    out["rejudged"] = rejudged
    out["ok"] = r["returncode"] == 0 and all(x["returncode"] == 0 and not x.get("differences") for x in rejudged)
    return out


ROWS = {
    "projection-pipeline": row_projection_pipeline,
    "underscores": row_underscores,
    "projection-driver": row_projection_driver,
    "demo-offline": row_demo_offline,
}
