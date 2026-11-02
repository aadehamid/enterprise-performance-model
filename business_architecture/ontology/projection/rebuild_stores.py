"""One command from an environment file to loaded, validated stores, with no prompt and no hand step.

    python3 rebuild_stores.py --env <environment file> [--store driver --store jena ...] [--empty] [--plan]

The environment file is the only thing that names an environment, so QA and production are two files
(skill-run/environment.example lists every key). --store chooses targets: driver (the local Neo4j), jena, aura and
databricks; the default is all four. A store that holds data is refused unless --empty says to replace it. --plan
prints the steps and runs nothing.

The steps, each stopping the run when it fails: preflight, empty, load, record; with Databricks, demo-build, then
aura-test with AuraDB too (a Databricks job tries to reach AuraDB with the login file EPM_AURA_ENV names; a failed probe
is a result, which collect records as the check databricks-reaches-auradb), then collect, tech-build, tech-compare and
lineage, in that order, because Unity Catalog's lineage keeps only recent builds; then tech-load, tech-sync, mark and
check. Without Databricks the technical graph loads from what the release ships.

Exit 0: every step passed. 1: a step failed, and the last line names it. 2: the input is wrong, and each problem is named
before anything changes. It writes <out>-rebuild-report.json (steps, status, seconds, log file; no value from a login)
after each step, and each step's output to <out>-rebuild-logs/. It is safe to run again: each step replaces what it
wrote. Standard library only; the steps fetch what they need with uv.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DEMO = os.path.join(REPO, "demos", "downstream-pricing-databricks-free")
BASE_CONFIG = os.path.join(HERE, "skill-run", "epm-run.json")
ROBOT_SHA256 = "16a73c074f3df359a7338a84b4e0788785fe06117f931bb9796e9619ea776105"  # the driver checks it too
STORES = ("driver", "jena", "aura", "databricks")
AURA_KEYS = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD")
DATABRICKS_KEYS = ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_HTTP_PATH", "DATABRICKS_CATALOG", "DATABRICKS_SCHEMA")
DEFAULTS = {"EPM_SKILLS": None, "EPM_ROBOT_JAR": "~/epm-lpg/robot.jar", "EPM_OUT": "~/lpg-out/epm",
            "EPM_NEO4J_PROJECT": "lpg-local", "EPM_NEO4J_PORT": "17711", "EPM_JENA_PROJECT": "epm-jena", "EPM_JENA_PORT": "13031",
            "EPM_EXPLORE_PROJECT": "lpg-explore", "EPM_EXPLORE_PORT": "13032",
            "EPM_TRIPLESTORE_PROJECT": "lpg-triplestore", "EPM_TRIPLESTORE_PORT": "13030",
            "EPM_AURA_ENV": None, "EPM_DATABRICKS_ENV": None, "EPM_TRIPLES_TABLE": "epm_triples",
            "EPM_LINEAGE_WAIT_SECONDS": "900", "SOURCE_PG_DSN": None, "DEMO_CATALOG": None, "NEO4J_DATABASE": None,
            "AURA_INSTANCEID": None, "AURA_INSTANCENAME": None}
KNOWN = set(DEFAULTS) | set(AURA_KEYS) | set(DATABRICKS_KEYS)


class Refused(Exception):
    """The input is wrong; args holds one line per problem."""


def read_env_file(path):
    values = {}
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if not sep:
                raise Refused(f"{path}: line {number} is not KEY=VALUE")
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def settings(path):
    """The environment file's values over the defaults. A key it does not know is refused, so a misspelt key cannot
    leave a default in force. The file may hold logins, so it must not be readable by others."""
    if not os.path.isfile(path):
        raise Refused(f"no environment file at {path}")
    if stat.S_IMODE(os.stat(path).st_mode) & 0o077:
        raise Refused(f"{path} is readable by others: run chmod 600 on it")
    values = read_env_file(path)
    unknown = sorted(set(values) - KNOWN)
    if unknown:
        raise Refused(*[f"{path}: the key {k} is not one this tool reads; skill-run/environment.example lists them" for k in unknown])
    s = {**DEFAULTS, **values}
    for key in ("EPM_ROBOT_JAR", "EPM_OUT", "EPM_SKILLS", "EPM_AURA_ENV", "EPM_DATABRICKS_ENV"):
        if s.get(key):
            s[key] = os.path.expanduser(s[key])
    s["EPM_SKILLS"] = s["EPM_SKILLS"] or (os.path.join(REPO, "skills") if os.path.isdir(os.path.join(REPO, "skills")) else os.path.expanduser("~/.agents/skills"))
    s["EPM_AURA_ENV"] = s["EPM_AURA_ENV"] or os.path.abspath(path)
    s["EPM_DATABRICKS_ENV"] = s["EPM_DATABRICKS_ENV"] or os.path.abspath(path)
    return s


def read_logins(s, stores):
    """{key: value} of the logins the chosen stores need, and the problems. Names keys, never values."""
    problems, logins = [], {}
    for store, keys, path in (("aura", AURA_KEYS, s["EPM_AURA_ENV"]), ("databricks", DATABRICKS_KEYS, s["EPM_DATABRICKS_ENV"])):
        if store not in stores:
            continue
        if not os.path.isfile(path):
            problems.append(f"{store}: no login file at {path}")
            continue
        if stat.S_IMODE(os.stat(path).st_mode) & 0o077:
            problems.append(f"{store}: {path} is readable by others: run chmod 600 on it")
            continue
        found = read_env_file(path)
        problems += [f"{store}: {path}: the key {k} is not one this tool reads" for k in sorted(set(found) - KNOWN)]
        problems += [f"{store}: {path} lacks {k}" for k in keys if not found.get(k)]
        logins.update({k: found[k] for k in keys if found.get(k)})
    return logins, problems


def preflight(s, stores, which=shutil.which):
    """Every prerequisite and connection value the chosen stores need, each named when it is missing."""
    problems = [f"{tool} is not on the PATH" for tool in ("docker", "uv") if not which(tool)]
    for script in ("ontology-to-lpg/scripts/run_projection.py", "rdf-store/scripts/rdfstore.py"):
        if not os.path.isfile(os.path.join(s["EPM_SKILLS"], script)):
            problems.append(f"EPM_SKILLS: no {script} under {s['EPM_SKILLS']}")
    if "aura" in stores and "driver" not in stores:
        problems.append("aura is a copy of the local Neo4j: name driver too")
    if "driver" in stores:
        if not which("java"):
            problems.append("java is not on the PATH (11 or later; ROBOT runs on it)")
        jar = s["EPM_ROBOT_JAR"]
        if not os.path.isfile(jar):
            problems.append(f"EPM_ROBOT_JAR: no ROBOT 1.9.10 at {jar}")
        else:
            with open(jar, "rb") as f:
                if hashlib.sha256(f.read()).hexdigest() != ROBOT_SHA256:
                    problems.append(f"EPM_ROBOT_JAR: {jar} is not the pinned ROBOT 1.9.10")
    if "databricks" in stores and not which("java"):
        problems.append("java is not on the PATH (SPARQL Anything runs on it)")
    return problems + read_logins(s, stores)[1]


def run_config(s, stores, replace):
    """The driver's run configuration for this environment: epm-run.json with this environment's names, every path absolute."""
    with open(BASE_CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    folder = os.path.dirname(BASE_CONFIG)
    for key in ("projection_config", "inputs_script", "releases", "queries"):
        cfg[key] = os.path.normpath(os.path.join(folder, cfg[key]))
    out = s["EPM_OUT"]
    cfg.update({"out": out, "robot_jar": s["EPM_ROBOT_JAR"], "target_env": s["EPM_AURA_ENV"], "replace_target": replace,
                "keep_neo4j": True, "keep_jena": True,
                "databricks": {"env": s["EPM_DATABRICKS_ENV"], "table": s["EPM_TRIPLES_TABLE"]},
                "rebuild": {"source": "databricks", "out": out + "-rebuild"},
                "rdf_store": os.path.join(s["EPM_SKILLS"], "rdf-store"),
                "neo4j": {"compose_project": s["EPM_NEO4J_PROJECT"], "bolt_port": int(s["EPM_NEO4J_PORT"])},
                "jena": {"compose_project": s["EPM_JENA_PROJECT"], "port": int(s["EPM_JENA_PORT"])},
                "explore_fuseki": {"compose_project": s["EPM_EXPLORE_PROJECT"], "port": int(s["EPM_EXPLORE_PORT"])},
                "triplestore_fuseki": {"compose_project": s["EPM_TRIPLESTORE_PROJECT"], "port": int(s["EPM_TRIPLESTORE_PORT"])}})
    return cfg


def stores_json(s, config_path):
    """EPM_STORES_JSON for sync_stores.py, empty_stores.py and tech_graph.py: names files and addresses, never a secret."""
    out = s["EPM_OUT"]
    return json.dumps({"driver": {"bolt": f"bolt://127.0.0.1:{s['EPM_NEO4J_PORT']}",
                                  "env": [f"{out}-rebuild/neo4j-run/run.env", f"{out}/neo4j-run/run.env"]},
                       "aura": {"env": [s["EPM_AURA_ENV"]]},
                       "jena": {"query": f"http://127.0.0.1:{s['EPM_JENA_PORT']}/ds/query"},
                       "databricks_env": s["EPM_DATABRICKS_ENV"], "run_config": config_path, "driver_out": out,
                       "triples_table": s["EPM_TRIPLES_TABLE"]})


def driver_arguments(stores):
    """What the driver runs for the chosen stores: everything they need and nothing that touches another."""
    if "driver" not in stores:
        return ["--only", ",".join(n for n, on in (("jena", "jena" in stores), ("databricks", "databricks" in stores)) if on)]
    skip = [n for n, on in (("copy", "aura" in stores), ("jena", "jena" in stores), ("databricks", "databricks" in stores),
                            ("rebuild", "databricks" in stores)) if not on]
    return ["--skip", ",".join(skip)] if skip else []


def child_env(s, stores, config_path):
    """The steps' environment: this environment's stores, and the values the demo reads. Passed down, never printed."""
    env = {**os.environ, "EPM_STORES_JSON": stores_json(s, config_path), "EPM_SKILLS": s["EPM_SKILLS"]}
    logins = read_logins(s, stores)[0]
    if "aura" in stores:
        env["EPM_AURA_ENV"] = s["EPM_AURA_ENV"]  # aura_test's login file
    if "databricks" in stores:
        env.update({k: logins[k] for k in DATABRICKS_KEYS[:3]})
        env["EPM_TRIPLES"] = f"{logins['DATABRICKS_CATALOG']}.{logins['DATABRICKS_SCHEMA']}.{s['EPM_TRIPLES_TABLE']}"
        for key in ("SOURCE_PG_DSN", "DEMO_CATALOG"):
            if s.get(key):
                env[key] = s[key]
    return env


def plan(s, stores, config_path, empty):
    """(step, folder, command) in order. Pure, so the tests read the order without running anything."""
    py = ["uv", "run", "-q", "--no-project", "--with", "rdflib", "--with", "neo4j"]
    if "databricks" in stores:
        py += ["--with", "databricks-sql-connector"]
    named = [a for store in stores for a in ("--store", store)]
    graph = ["uv", "run", "-q", "--group", "graph", "python", "-m", "pricing_demo.tech_graph"]
    demo = ["uv", "run", "-q", "python", "-m"]
    tech = [a for store in stores if store != "databricks" for a in ("--store", store)]
    steps = []
    if empty:
        steps.append(("empty", HERE, [*py, "python", "empty_stores.py", *named, "--yes"]))
    steps.append(("load", os.path.join(s["EPM_SKILLS"], "ontology-to-lpg", "scripts"),
                  ["uv", "run", "-q", "--no-project", "--with", "rdflib", "python3", "run_projection.py", "--config", config_path,
                   *driver_arguments(stores)]))
    if "driver" in stores:
        steps.append(("record", HERE, ["uv", "run", "-q", "--no-project", "--with", "rdflib", "--with", "pyshacl", "python",
                                       "pipeline.py", "record", "--run", s["EPM_OUT"]]))
    if "databricks" in stores:
        if not s.get("SOURCE_PG_DSN"):
            steps.append(("demo-postgres", DEMO, ["docker", "compose", "-f", "docker/docker-compose.yml", "up", "-d", "--wait"]))
        steps += [(f"demo-{name}", DEMO, [*demo, *module]) for name, module in (
            ("sources", ["pricing_demo.load_postgres"]), ("replicate", ["pricing_demo.replicate"]),
            ("setup", ["pricing_demo.databricks", "setup"]), ("upload", ["pricing_demo.databricks", "upload"]),
            ("build", ["pricing_demo.databricks", "build"]), ("genie", ["pricing_demo.genie"]))]
        if "aura" in stores:  # collect records the probe's result; the shipped graph holds that check
            steps.append(("aura-test", DEMO, [*demo, "pricing_demo.aura_test"]))
        steps += [("collect", DEMO, [*graph, "collect", "--lineage-wait", s["EPM_LINEAGE_WAIT_SECONDS"]]),
                  ("tech-build", DEMO, [*graph, "build"]), ("tech-compare", DEMO, [*graph, "compare"]),
                  ("lineage", DEMO, [*graph, "lineage"])]
    if tech:
        steps.append(("tech-load", DEMO, [*graph, "load", *tech]))
    if "databricks" in stores:
        steps.append(("tech-sync", DEMO, [*graph, "sync"]))
    steps += [("mark", HERE, [*py, "python", "sync_stores.py", "mark", *named]),
              ("check", HERE, [*py, "python", "sync_stores.py", "check", "--ref", "worktree", *named])]
    return steps


def containers(project, runner=subprocess.run):
    """The containers of a compose project, running or stopped: what the load would remove. None when Docker cannot say."""
    done = runner(["docker", "ps", "-aq", "--filter", f"label=com.docker.compose.project={project}"],
                  stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return done.stdout.split() if done.returncode == 0 else None


def holding(s, stores, env, runner=subprocess.run):
    """[(store, what it holds)] for the chosen stores that hold anything, and the problems. Every store must answer the
    count, because a failed count is not an empty store. The one exception is a local store with no container at all: it
    has nothing to lose, and the run creates it. A stopped container may hold data, and the load would remove it."""
    py = ["uv", "run", "-q", "--no-project", "--with", "rdflib", "--with", "neo4j"] + (["--with", "databricks-sql-connector"] if "databricks" in stores else [])
    named = [a for store in stores for a in ("--store", store)]
    done = runner([*py, "python", "empty_stores.py", *named], cwd=HERE, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if done.returncode != 0:
        return [], [f"the count of what the stores hold failed (exit {done.returncode}); nothing was changed"]
    rows = {}
    for line in done.stdout.splitlines():
        if line.startswith("{"):
            row = json.loads(line)
            rows[row["store"]] = row
    held, problems = [], []
    projects = {"driver": s["EPM_NEO4J_PROJECT"], "jena": s["EPM_JENA_PROJECT"]}
    for store in stores:
        row = rows.get(store)
        if row is None:
            problems.append(f"{store}: the count gave no result; nothing was changed")
        elif "unreachable" in row:
            if store not in projects:
                problems.append(f"{store}: could not be reached ({row['unreachable']}); check its login values")
            else:
                found = containers(projects[store], runner)
                if found is None:
                    problems.append(f"{store}: Docker could not list its containers; nothing was changed")
                elif found:
                    held.append((store, f"a container that did not answer, {row['unreachable']}"))
        elif row.get("held"):
            held.append((store, row["held"]))
    return held, problems


class Report:
    def __init__(self, path, env_file, stores):
        self.path = path
        self.data = {"started": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "environment_file": env_file,
                     "stores": list(stores), "steps": [], "result": "running", "failed_step": None}
        self.write()

    def write(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
            f.write("\n")
        os.replace(self.path + ".tmp", self.path)

    def step(self, name, status, seconds, log=None):
        self.data["steps"].append({"step": name, "status": status, "seconds": round(seconds, 1), "log": log})
        self.write()

    def finish(self, failed=None):
        self.data.update({"result": "failed" if failed else "passed", "failed_step": failed})
        self.write()


def run_steps(steps, env, report, logs, runner=subprocess.run):
    """Runs the steps in order; the first failure ends the run. Returns the failed step's name, or None."""
    shutil.rmtree(logs, ignore_errors=True)   # this run's logs only: a rerun with other steps leaves none behind
    os.makedirs(logs)
    for number, (name, cwd, cmd) in enumerate(steps, 1):
        log = os.path.join(logs, f"{number:02d}-{name}.log")
        started = time.monotonic()
        print(f"== {name}", flush=True)
        with open(log, "w", encoding="utf-8") as f:
            code = runner(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT).returncode
        report.step(name, "passed" if code == 0 else "failed", time.monotonic() - started, log)
        if code != 0:
            return name
    return None


def parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--env", required=True, help="the environment file")
    ap.add_argument("--store", action="append", choices=STORES, help="a target; repeat it (default: all four)")
    ap.add_argument("--empty", action="store_true", help="replace what the chosen stores hold; without it a store that holds data is refused")
    ap.add_argument("--plan", action="store_true", help="print the steps and run nothing")
    return ap


def main(argv=None):
    args = parser().parse_args(argv)
    stores = tuple(s for s in STORES if s in (args.store or STORES))
    try:
        s = settings(args.env)
        problems = preflight(s, stores)
        if problems:
            raise Refused(*problems)
        config_path = s["EPM_OUT"].rstrip("/") + "-run.json"
        steps = plan(s, stores, config_path, args.empty)
        env = child_env(s, stores, config_path)
        if args.plan:
            print("preflight: passed")
            for name, cwd, cmd in steps:
                print(f"{name}: (in {os.path.relpath(cwd, REPO)}) {' '.join(cmd)}")
            return 0
        held, problems = holding(s, stores, env)
        problems += [] if args.empty else [f"{store} holds data ({n}): pass --empty to replace it" for store, n in held]
        if problems:
            raise Refused(*problems)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(run_config(s, stores, args.empty), f, indent=1)
    except Refused as refused:
        for problem in refused.args:
            print(f"REFUSED {problem}", file=sys.stderr)
        return 2
    report = Report(s["EPM_OUT"] + "-rebuild-report.json", os.path.abspath(args.env), stores)
    report.step("preflight", "passed", 0)
    failed = run_steps(steps, env, report, s["EPM_OUT"] + "-rebuild-logs")
    report.finish(failed)
    if failed:
        print(f"FAILED at the step {failed}; its log is in {s['EPM_OUT']}-rebuild-logs, the report at {report.path}")
        return 1
    print(f"every step passed; report at {report.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
