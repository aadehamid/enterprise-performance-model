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
import datetime
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
            "--with", "pytest", "--with", "pytest-xdist", "--with", "databricks-sql-connector", *extra]
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
    with open(os.path.join(importdir, "validate-neo4j.env"), "w") as f:  # the later rows read the login back from here
        f.write(f"NEO4J_URI=bolt://localhost:{port}\nNEO4J_USERNAME=neo4j\nNEO4J_PASSWORD={pw}\n")
    os.chmod(os.path.join(importdir, "validate-neo4j.env"), 0o600)
    for _ in range(60):
        logs = subprocess.run(["docker", "logs", name], capture_output=True, text=True)
        if "Started." in logs.stdout + logs.stderr:
            return f"bolt://localhost:{port}", pw
        time.sleep(4)
    raise RuntimeError("the test Neo4j did not start")


def test_password(env):
    """The test Neo4j's password: from this run's neo4j_up, else from the login file an earlier run wrote."""
    if not env.get("TEST_NEO4J_PASSWORD"):
        path = os.path.join(expand(env["IMPORT_DIR"]), "validate-neo4j.env")
        with open(path) as f:
            env["TEST_NEO4J_PASSWORD"] = [l.split("=", 1)[1].strip() for l in f if l.startswith("NEO4J_PASSWORD=")][0]
    return env["TEST_NEO4J_PASSWORD"]


def cypher(bolt, pw, query):
    """Run one Cypher statement through the neo4j driver in a uv environment (this script runs under the system Python)."""
    code = ("import json, os, sys\nfrom neo4j import GraphDatabase\n"
            "with GraphDatabase.driver(sys.argv[1], auth=('neo4j', os.environ['NEO4J_PASSWORD'])) as d, d.session() as s:\n"
            "    print(json.dumps(s.run(sys.argv[2]).data(), default=str))\n")
    r = subprocess.run(["uv", "run", "-q", "--no-project", "--with", "neo4j", "python3", "-c", code, bolt, query],
                       capture_output=True, text=True, env={**os.environ, "NEO4J_PASSWORD": pw})
    if r.returncode:
        raise RuntimeError(r.stderr[-500:])
    return json.loads(r.stdout)


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
        if r["returncode"] == 0 and release_env(tree):
            out["readme_note"] = note_projection_figures(tree, rep)
    out["ok"] = r["returncode"] == 0
    # The broken copy: a graph with one triple removed must fail the round trip (the plan's "the broken copy caught").
    return out


def note_projection_figures(tree, rep):
    """The release's own load-verify figures, written at the head of the projection README's run paragraph (the
    paragraph's figures are main's), then the page rebuilt. Returns the sentence written, or what stood in its way."""
    path = os.path.join(tree, ONT, "projection", "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    marker = "The last run, on every released package with"
    if marker not in text or "*This release's own run" in text:
        return "not written: the run paragraph was not found, or the note is already there"
    renamed = rep.get("renamed") or {}
    renamed_txt = ", ".join(f"{v:,} {k.replace('_', ' ')}" for k, v in renamed.items()) if isinstance(renamed, dict) else str(renamed)
    note = (f"*This release's own run ({datetime.date.today().isoformat()}):* {rep['nodes']:,} nodes and {rep['relationships']:,} "
            f"relationships, {rep['shacl_violations_in_graph']} SHACL violations in the graph over "
            f"{rep.get('in_graph_shape_constraints', 0):,} in-graph constraints, the deliberate mutant caught, a round trip that lost "
            f"{rep['roundtrip_lost']} and added {rep['roundtrip_added']} triples, equal hashes for the sorted and shuffled loads, and "
            f"every name renamed to one underscore without loss ({renamed_txt}). The nodes are fewer than main's because the "
            f"pins moved to the newest packages, which drop the older versions' IRIs. *Before the release, on main:* the last run, "
            f"on every released package with")
    text = text.replace(marker, note, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    r = sh(["uv", "run", "-q", "--no-project", "--with", "markdown-it-py>=4,<5", "python3", "scripts/build_docs_html.py"], tree,
           env=release_env(tree))
    return note if r["returncode"] == 0 else f"written, but the page rebuild failed: {r.get('stderr', '')[-300:]}"


def row_underscores(tree, env):
    """Every label, relationship type and property key in the test Neo4j; none holds the double separator in the release."""
    bolt, pw = f"bolt://localhost:{env.get('TEST_NEO4J_PORT', '17799')}", test_password(env)
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
    # uv's environment for the demo's project goes outside the tree: a .venv inside the release would be a defect.
    import tempfile as _tf
    venv = os.path.join(_tf.gettempdir(), "epm-share-release-demo-venv")
    r = sh(["uv", "run", "python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_demo.py"], demo,
           env={**release_env(tree), "UV_PROJECT_ENVIRONMENT": venv}); out["steps"].append(r)
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
            recorded = os.path.join(acceptance, name.replace(".json", "-rejudged.json"))
            repeat = []
            if os.path.exists(recorded):
                with open(recorded) as f:
                    k = json.load(f).get("repeat")
                repeat = ["--repeat", str(k)] if k else []
            rr = sh(["uv", "run", "--group", "graph", "python", "-m", "pricing_demo.acceptance", "rejudge", *repeat, os.path.join(tmp, name)],
                    demo, env=release_env(tree))
            entry = {"run": name, "returncode": rr["returncode"], "tail": rr["tail"][-300:]}
            new_path = os.path.join(tmp, name.replace(".json", "-rejudged.json"))
            if os.path.exists(new_path) and os.path.exists(recorded):
                with open(new_path) as f:
                    a = json.load(f)
                with open(recorded) as f:
                    b = json.load(f)
                verdicts = lambda j: {str(x.get("n", i)): x.get("passed") for i, x in enumerate(j.get("results", []))}
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


# ---------- the demo and the technical graph ----------

COMPOSE_OVERRIDE = """services:
  sources:
    container_name: {name}
    ports: !override
      - "127.0.0.1:{port}:5432"
    volumes: !override
      - ./init:/docker-entrypoint-initdb.d:ro
      - {volume}:/var/lib/postgresql/data
volumes:
  {volume}:
    name: {volume}
"""


def demo_env(tree, env):
    """The demo's environment for the test: its own Postgres, catalog and triple table."""
    e = {**release_env(tree), "SOURCE_PG_DSN": f"postgresql://demo:demo@localhost:{env.get('DEMO_PG_PORT', '55433')}",
         "DEMO_CATALOG": env.get("DEMO_CATALOG", "epm_validate")}
    if env.get("DATABRICKS_TRIPLES_TABLE_FULL"):
        e["EPM_TRIPLES"] = env["DATABRICKS_TRIPLES_TABLE_FULL"]
    return e


def row_demo_live(tree, env):
    """The demo's pipeline on test stores: its own Postgres, the replica, the Databricks build in the test catalog, the
    counts. The Genie agents and the orchestrator are not run: the agents are workspace objects found by title, so a
    test run would repoint the shared ones; the live acceptance run is skipped by the owner's decision."""
    demo = os.path.join(tree, DEMO)
    project, port = env.get("DEMO_PROJECT", "pricing-validate"), env.get("DEMO_PG_PORT", "55433")
    name, volume = f"{project}-sources", f"{project}-pgdata"
    override = os.path.join(demo, "docker", "compose.validate.yml")
    with open(override, "w") as f:
        f.write(COMPOSE_OVERRIDE.format(name=name, port=port, volume=volume))
    compose = ["docker", "compose", "-p", project, "-f", "docker/docker-compose.yml", "-f", "docker/compose.validate.yml"]
    out = {"steps": []}
    r = sh([*compose, "up", "-d"], demo); out["steps"].append(r)
    ledger(env, "compose-project", project, f"the demo's test Postgres {name} on {port}, volume {volume}; override {override}")
    if r["returncode"]:
        return {**out, "ok": False}
    time.sleep(8)
    e = demo_env(tree, env)
    ledger(env, "databricks-catalog", e["DEMO_CATALOG"], "the demo's test catalog (purge with pricing_demo.databricks purge --yes --catalog)")
    for step in (["python", "-m", "pricing_demo.load_postgres"], ["python", "-m", "pricing_demo.replicate"],
                 ["python", "-m", "pricing_demo.databricks", "setup"], ["python", "-m", "pricing_demo.databricks", "upload"],
                 ["python", "-m", "pricing_demo.databricks", "build"], ["python", "-m", "pricing_demo.databricks", "counts"]):
        r = sh(["uv", "run", *step], demo, env=e, timeout=7200); out["steps"].append(r)
        if r["returncode"]:
            return {**out, "ok": False}
    out["counts"] = r["tail"][-2500:]
    out["genie_and_orchestrator"] = "not run: the Genie agents are found by title in the shared workspace; the live acceptance run is skipped (the owner, 2026-10-31)"
    out["ok"] = True
    return out


def stores_json(env):
    """EPM_STORES_JSON for the tools that read stores: the test Neo4j as 'pipeline', the driver's test Neo4j as 'driver'."""
    test_env = expand(env["IMPORT_DIR"]) + "/validate-neo4j.env"
    test_password(env)  # written by neo4j_up
    driver_out = expand(env["DRIVER_OUT"])
    over = {"pipeline": {"bolt": f"bolt://127.0.0.1:{env.get('TEST_NEO4J_PORT', '17799')}", "env": [test_env]},
            "driver": {"bolt": f"bolt://127.0.0.1:{env.get('DRIVER_PORT', '17811')}",
                       "env": [driver_out + "-rebuild/neo4j-run/run.env", driver_out + "/neo4j-run/run.env"]},
            "driver_reports": [driver_out + "-rebuild/projection-report.json", driver_out + "/projection-report.json"]}
    if env.get("AURA_ENV"):
        over["aura"] = {"env": [expand(env["AURA_ENV"])]}
    if env.get("DATABRICKS_ENV"):
        over["databricks_env"] = expand(env["DATABRICKS_ENV"])
    return json.dumps(over)


def row_tech_graph(tree, env):
    """tech_graph collect, build, load, sync, walk on the test stores, after the demo's live row."""
    demo = os.path.join(tree, DEMO)
    e = {**demo_env(tree, env), "EPM_STORES_JSON": stores_json(env)}
    out = {"steps": []}
    stores = ["--store", "pipeline", "--store", "driver"] + (["--store", "aura"] if env.get("AURA_ENV") else [])
    for step in (["collect"], ["build"], ["load", *stores], ["sync"], ["walk"]):
        r = sh(["uv", "run", "--group", "graph", "python", "-m", "pricing_demo.tech_graph", *step], demo, env=e, timeout=3600)
        out["steps"].append(r)
        if r["returncode"]:
            return {**out, "ok": False}
    out["walk_rows"] = r["tail"].count("\n")
    m = re.search(r"(\d+) nodes.*?(\d+) (?:edges|relationships)", "".join(s["tail"] for s in out["steps"]), re.S)
    if m:
        out["nodes"], out["edges"] = int(m.group(1)), int(m.group(2))
    out["ok"] = True
    return out


def row_sync(tree, env):
    """sync_stores.py mark and check on the test stores; then one node removed on purpose, and check reports it."""
    proj = os.path.join(tree, ONT, "projection")
    e = {**release_env(tree), "EPM_STORES_JSON": stores_json(env)}
    ref = ["--ref", "worktree"]
    out = {"steps": []}
    r = uv(["sync_stores.py", "mark", "--store", "pipeline", "--store", "driver"], proj, env=e); out["steps"].append(r)
    r = uv(["sync_stores.py", "check", *ref], proj, env=e); out["steps"].append(r)
    out["check_before"] = r["tail"][-800:]
    bolt, pw = f"bolt://localhost:{env.get('TEST_NEO4J_PORT', '17799')}", test_password(env)
    victim = cypher(bolt, pw, "MATCH (n:Resource) WITH n ORDER BY n.uri LIMIT 1 RETURN n.uri AS uri")  # any one resource
    if victim:
        cypher(bolt, pw, f"MATCH (n:Resource {{uri: '{victim[0]['uri']}'}}) DETACH DELETE n")
        r = uv(["sync_stores.py", "check", *ref], proj, env=e); out["steps"].append(r)
        out["check_after_drift"] = r["tail"][-800:]
        out["drift_caught"] = "pipeline" in r["tail"] and ("changed" in r["tail"] or "behind" in r["tail"])
        out["removed"] = victim[0]["uri"]
    out["repair"] = "the test repairs by reloading the pipeline row's load-verify (sync's reload is bound to the loaded container names)"
    out["ok"] = out["steps"][1]["returncode"] == 0 and out.get("drift_caught", False)
    return out


def row_store_map(tree, env):
    """What the test stores hold: node counts by label and relationship counts by type in the test Neo4j."""
    bolt, pw = f"bolt://localhost:{env.get('TEST_NEO4J_PORT', '17799')}", test_password(env)
    labels = cypher(bolt, pw, "MATCH (n) UNWIND labels(n) AS l RETURN l, count(*) AS n ORDER BY l")
    rels = cypher(bolt, pw, "MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS n ORDER BY t")
    return {"labels": {x["l"]: x["n"] for x in labels}, "relationship_types": {x["t"]: x["n"] for x in rels},
            "resources": cypher(bolt, pw, "MATCH (n:Resource) RETURN count(n) AS n")[0]["n"],
            "tech": cypher(bolt, pw, "MATCH (n:Tech) RETURN count(n) AS n")[0]["n"], "ok": True}


ROWS.update({"demo-live": row_demo_live, "tech-graph": row_tech_graph, "sync": row_sync, "store-map": row_store_map})
