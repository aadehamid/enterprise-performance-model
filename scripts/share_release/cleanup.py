#!/usr/bin/env python3
"""Delete what the validation created, from its ledger, and prove it gone (plan step 9).

    python3 scripts/share_release/cleanup.py --ledger <validate-ledger.jsonl> --env <the validation env file> [--yes] [--tree <folder>]

Without --yes it prints what it would remove. It removes only what the ledger names: containers, compose projects
(with their volumes), folders, files, the demo's test catalog (through the demo's own purge), the ontology's test
table. It exits 0 only with positive proof: every deletion command returned 0, no container, project, folder or
file in the ledger still exists, and nothing in the ledger was left to someone else. The stores are then emptied
and reloaded (rebuild_stores.py --empty, in the release) from the release, not from main (the owner's instruction of 2026-11-01), outside this
script: an "aura" entry is printed and counts as not done until the ledger no longer holds it.

A Databricks catalog is purged only when its name starts with the validation's prefix and the ledger line records that
this run created it, and never when it is a shared catalog such as idp_sbx. So give DEMO_CATALOG that prefix in --env.

A folder or file entry is removed only when it is a plain path of the validation: never "/", the home folder, a
path of fewer than three components, or a folder that holds the checkout (--tree) or this tool.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import procs  # noqa: E402
import scrubbing  # noqa: E402
from validate import read_env  # noqa: E402


def run(args, cwd=None, env=None, timeout=3600):
    """One command in its own process group with a deadline; the record is scrubbed of every secret."""
    merged = {**os.environ, **(env or {})}
    try:
        r = procs.run(args, timeout=timeout, cwd=cwd, env=merged)
    except (procs.Expired, OSError) as exc:
        return 1, scrubbing.scrub(f"{type(exc).__name__}: {exc}"[-600:], scrubbing.secrets_in(args, merged))
    return r.returncode, (r.stdout + r.stderr)[-600:]


def unsafe(path, protected):
    """Why a ledgered path must not be removed, or None when it may be."""
    real = os.path.realpath(os.path.expanduser(path))
    if real == "/" or real == os.path.realpath(os.path.expanduser("~")):
        return "it is the root or the home folder"
    if len([p for p in real.split(os.sep) if p]) < 3:
        return "it is too close to the root"
    for name, folder in protected:
        folder = os.path.realpath(folder)
        if real == folder or folder.startswith(real + os.sep):
            return f"it holds {name}"
    return None


# A shared workspace's catalogs: never this tool's to purge, whatever a ledger line says.
# A purge drops a whole catalog. Prior absence alone is weak proof, since someone could create the name between the check
# and the run, so the name must also be one nobody else would choose.
TEST_CATALOG_PREFIX = "epm_release_validate_"
SHARED_CATALOGS = {"idp_sbx", "workspace", "main", "samples", "system", "hive_metastore"}


def catalog_refusal(entry):
    """Why a ledgered catalog must not be purged, or None. A purge drops a whole catalog, so only one this run created
    may go: the ledger line must say so, and stores.py says so only when the catalog was absent before the run."""
    if entry["name"].lower() in SHARED_CATALOGS:
        return "it is a shared catalog"
    if not entry["name"].startswith(TEST_CATALOG_PREFIX):
        return f"its name does not start with {TEST_CATALOG_PREFIX}, the prefix of a catalog made for one validation"
    if entry.get("detail_created_by_run") is not True:
        return "the ledger does not show that this run created it"
    return None


def docker_names(args):
    """The names a docker listing prints, or None when the listing itself failed, timed out or could not start (no
    proof either way)."""
    try:
        r = procs.run(args, timeout=600)
    except (procs.Expired, OSError):
        return None
    return r.stdout if r.returncode == 0 else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger", required=True); ap.add_argument("--env", required=True); ap.add_argument("--yes", action="store_true")
    ap.add_argument("--tree", default="", help="the tree whose demo and skills run the purge (the release or main)")
    a = ap.parse_args(argv)
    env = read_env(a.env)
    protected = [("this tool", os.path.dirname(os.path.dirname(HERE)))] + ([("the tree", a.tree)] if a.tree else [])
    with open(a.ledger) as f:
        entries = [json.loads(line) for line in f if line.strip()]
    seen, done, left, refused = set(), [], [], []
    # Folders and files go last: the demo's compose project is taken down with its override file, which the ledger
    # names before the project.
    for e in sorted(entries, key=lambda e: e["kind"] in ("folder", "file")):
        key = (e["kind"], e["name"])
        if key in seen:
            continue
        seen.add(key)
        kind, name, cwd = e["kind"], e["name"], None
        if kind == "container":
            cmd = ["docker", "rm", "-f", "-v", name]
        elif kind == "compose-project":
            if name.startswith("pricing"):
                cmd = ["docker", "compose", "-p", name, "-f", "docker/docker-compose.yml", "-f", e.get("detail_override") or "docker/compose.validate.yml", "down", "-v"]
                cwd = os.path.join(a.tree, "demos", "downstream-pricing-databricks-free")
            else:
                cmd = ["docker", "compose", "-p", name, "--profile", "neo4j", "--profile", "fuseki", "down", "-v"]
                cwd = os.path.join(os.path.expanduser(env["SKILLS_DIR"]), "ontology-to-lpg", "docker")
        elif kind in ("folder", "file"):
            cmd = None
            why = unsafe(name, protected)
            if why:
                refused.append((kind, name, why))
                continue
        elif kind == "databricks-catalog":
            why = catalog_refusal(e)
            if why:
                refused.append((kind, name, why))
                continue
            # The purge acts on DEMO_CATALOG, set to this name below; --catalog only confirms it.
            # Explicit selection takes precedence over saved setup state and discovery.
            cmd = ["uv", "run", "python", "-m", "pricing_demo.databricks", "purge", "--yes", "--catalog", name]
            cwd = os.path.join(a.tree, "demos", "downstream-pricing-databricks-free")
        elif kind == "databricks-table":
            cmd = ["uv", "run", "--no-project", "--with", "databricks-sql-connector", "python3", "-c",
                   "import os,sys; from databricks import sql; e={l.split('=',1)[0]:l.split('=',1)[1].strip() for l in open(os.path.expanduser(sys.argv[1])) if '=' in l}; "
                   "c=sql.connect(server_hostname=e['DATABRICKS_HOST'].replace('https://',''),http_path=e['DATABRICKS_HTTP_PATH'],access_token=e['DATABRICKS_TOKEN']); "
                   "cur=c.cursor(); cur.execute(f\"DROP TABLE IF EXISTS {e['DATABRICKS_CATALOG']}.{e['DATABRICKS_SCHEMA']}.\"+sys.argv[2]); "
                   "cur.execute(f\"SHOW TABLES IN {e['DATABRICKS_CATALOG']}.{e['DATABRICKS_SCHEMA']} LIKE '\"+sys.argv[2]+\"'\"); rows=cur.fetchall(); print('left:', rows); sys.exit(1 if rows else 0)",
                   env["DATABRICKS_ENV"], name]
        else:
            left.append(e); continue
        if not a.yes:
            print(f"would remove {kind} {name}" + (f": {' '.join(cmd)}" if cmd else ""))
            continue
        if kind == "folder":
            target = os.path.expanduser(name)
            if os.path.islink(target):  # a link, broken or not, is removed as a link, never followed
                os.unlink(target)
            else:
                shutil.rmtree(target, ignore_errors=True)
            done.append((kind, name, 0 if not os.path.lexists(target) else 1, ""))
        elif kind == "file":
            try:
                os.remove(os.path.expanduser(name))
            except FileNotFoundError:
                pass
            done.append((kind, name, 0 if not os.path.lexists(os.path.expanduser(name)) else 1, ""))
        else:
            rc, out = run(cmd, cwd=cwd, env={"DEMO_CATALOG": name} if kind == "databricks-catalog" else None)
            done.append((kind, name, rc, out))
    # Proof: every command returned 0; no container, project, folder or file in the ledger still exists; nothing is left.
    proof = [f"{kind} {name}: the removal returned {rc}" for kind, name, rc, out in done if rc != 0]
    kinds = {e["kind"] for e in entries}
    containers = docker_names(["docker", "ps", "-a", "--format", "{{.Names}}"]) if a.yes and "container" in kinds else ""
    projects = docker_names(["docker", "compose", "ls", "-a", "--format", "json"]) if a.yes and "compose-project" in kinds else ""
    if containers is None:
        proof.append("docker ps failed: no proof that the containers are gone")
    if projects is None:
        proof.append("docker compose ls failed: no proof that the compose projects are gone")
    for e in entries:
        if e["kind"] == "container" and containers and e["name"] in containers.split():
            proof.append(f"container {e['name']} still exists")
        if e["kind"] == "compose-project" and projects and f'"{e["name"]}"' in projects:
            proof.append(f"compose project {e['name']} still exists")
        if e["kind"] in ("folder", "file") and os.path.lexists(os.path.expanduser(e["name"])):
            proof.append(f"{e['kind']} {e['name']} still exists")
    for kind, name, rc, out in done:
        print(f"{'removed' if rc == 0 else 'FAILED'} {kind} {name} {out.strip()[-200:]}")
    for kind, name, why in refused:
        print(f"REFUSED {kind} {name}: {why}")
    for e in left:
        print(f"left (not this script's to remove): {e['kind']} {e['name']}: {e.get('detail', '')}")
    if not a.yes:
        print("dry run")
        return 0
    if proof or refused or left:
        print("\n".join(proof + [f"{k} {n} was refused" for k, n, _ in refused] + [f"{e['kind']} {e['name']} is left" for e in left]))
        return 1
    print("everything in the ledger is gone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
