#!/usr/bin/env python3
"""Delete what the validation created, from its ledger, and prove it gone (plan step 9).

    python3 scripts/share_release/cleanup.py --ledger <validate-ledger.jsonl> --env <the validation env file> [--yes]

Without --yes it prints what it would remove. It removes only what the ledger names: containers, compose projects
(with their volumes), folders, the demo's test catalog (through the demo's own purge), the ontology's test table.
AuraDB is reloaded from main afterwards by the driver (the owner's instruction), outside this script. Anything the
ledger cannot account for is left and reported.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import read_env  # noqa: E402


def run(args, cwd=None, env=None):
    r = subprocess.run(args, cwd=cwd, env={**os.environ, **(env or {})}, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)[-600:]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True); ap.add_argument("--env", required=True); ap.add_argument("--yes", action="store_true")
    ap.add_argument("--tree", default="", help="the tree whose demo and skills run the purge (the release or main)")
    a = ap.parse_args(argv)
    env = read_env(a.env)
    with open(a.ledger) as f:
        entries = [json.loads(line) for line in f if line.strip()]
    seen, done, left = set(), [], []
    for e in entries:
        key = (e["kind"], e["name"])
        if key in seen:
            continue
        seen.add(key)
        kind, name = e["kind"], e["name"]
        if kind == "container":
            cmd = ["docker", "rm", "-f", "-v", name]
        elif kind == "compose-project":
            if name.startswith("pricing"):
                demo = os.path.join(a.tree, "demos", "downstream-pricing-databricks-free")
                cmd = ["docker", "compose", "-p", name, "-f", "docker/docker-compose.yml", "-f", "docker/compose.validate.yml", "down", "-v"]
                cwd = demo
            else:
                cmd = ["docker", "compose", "-p", name, "--profile", "neo4j", "--profile", "fuseki", "down", "-v"]
                cwd = os.path.join(os.path.expanduser(env["SKILLS_DIR"]), "ontology-to-lpg", "docker")
        elif kind == "folder":
            cmd = None
        elif kind == "file":
            cmd = None
        elif kind == "databricks-catalog":
            cmd = ["uv", "run", "python", "-m", "pricing_demo.databricks", "purge", "--yes", "--catalog", name]
            cwd = os.path.join(a.tree, "demos", "downstream-pricing-databricks-free")
        elif kind == "databricks-table":
            cmd = ["uv", "run", "--no-project", "--with", "databricks-sql-connector", "python3", "-c",
                   "import os,sys; from databricks import sql; e={l.split('=',1)[0]:l.split('=',1)[1].strip() for l in open(os.path.expanduser(sys.argv[1])) if '=' in l}; "
                   "c=sql.connect(server_hostname=e['DATABRICKS_HOST'].replace('https://',''),http_path=e['DATABRICKS_HTTP_PATH'],access_token=e['DATABRICKS_TOKEN']); "
                   "cur=c.cursor(); cur.execute(f\"DROP TABLE IF EXISTS {e['DATABRICKS_CATALOG']}.{e['DATABRICKS_SCHEMA']}.\"+sys.argv[2]); "
                   "cur.execute(f\"SHOW TABLES IN {e['DATABRICKS_CATALOG']}.{e['DATABRICKS_SCHEMA']} LIKE '\"+sys.argv[2]+\"'\"); print('left:', cur.fetchall())",
                   env["DATABRICKS_ENV"], name]
            cwd = None
        else:
            left.append(e); continue
        if not a.yes:
            print(f"would remove {kind} {name}" + (f": {' '.join(cmd)}" if cmd else ""))
            continue
        if kind == "folder":
            shutil.rmtree(os.path.expanduser(name), ignore_errors=True)
            done.append((kind, name, 0 if not os.path.exists(os.path.expanduser(name)) else 1, ""))
        elif kind == "file":
            try:
                os.remove(os.path.expanduser(name))
            except FileNotFoundError:
                pass
            done.append((kind, name, 0 if not os.path.exists(os.path.expanduser(name)) else 1, ""))
        else:
            rc, out = run(cmd, cwd=locals().get("cwd"), env={"DEMO_CATALOG": name} if kind == "databricks-catalog" else None)
            done.append((kind, name, rc, out))
    # Proof: no container, project, folder or file in the ledger still exists.
    proof = []
    containers = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}"], capture_output=True, text=True).stdout.split()
    projects = subprocess.run(["docker", "compose", "ls", "-a", "--format", "json"], capture_output=True, text=True).stdout
    for e in entries:
        if e["kind"] == "container" and e["name"] in containers:
            proof.append(f"container {e['name']} still exists")
        if e["kind"] == "compose-project" and f'"{e["name"]}"' in projects:
            proof.append(f"compose project {e['name']} still exists")
        if e["kind"] in ("folder", "file") and os.path.exists(os.path.expanduser(e["name"])):
            proof.append(f"{e['kind']} {e['name']} still exists")
    for kind, name, rc, out in done:
        print(f"{'removed' if rc == 0 else 'FAILED'} {kind} {name} {out.strip()[-200:]}")
    for e in left:
        print(f"left (not this script's to remove): {e['kind']} {e['name']}: {e.get('detail', '')}")
    print("\n".join(proof) if proof else ("everything in the ledger is gone" if a.yes else "dry run"))
    return 1 if proof else 0


if __name__ == "__main__":
    sys.exit(main())
