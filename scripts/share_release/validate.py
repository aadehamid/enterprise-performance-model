#!/usr/bin/env python3
"""Validation after the cut (plan step 7): the same rows on main and on the release, so the two can be compared.

    python3 scripts/share_release/validate.py run --tree <checkout or release> --out <json> [--rows checks,regression,...]
    python3 scripts/share_release/validate.py compare --main <checkout> --release <release> --out <json>
    python3 scripts/share_release/validate.py report <baseline json> <release json> [<compare json>]

`run` records each row's result for one tree: its exit code, the figures it prints, the time it took. The
baseline is `run` on a checkout of main; the release gets the same `run`. `compare` reads both trees at once
for the rows that are a comparison by nature: the business-process JSON after the rewrite rules, each newest
module's Turtle after the rules (graph isomorphism and triple counts), the newest packages' pins, the IRI base
in every file, and the leak gate. `report` writes the table the plan asks for: every row with main's result,
the release's result, and whether a rewrite rule explains any difference.

The rows that need stores (the projection pipeline and driver, the technical graph, the store sync, the live
demo, the underscore and store-map checks) take their logins and ports from `--env <file>`; without it they
are recorded as not run, with that reason.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifest  # noqa: E402
import procs  # noqa: E402
import scrubbing  # noqa: E402
import skill_checks  # noqa: E402

DEPS = ["--with", "rdflib", "--with", "pyshacl", "--with", "openpyxl", "--with", "jsonschema", "--with", "pytest",
        "--with", "pytest-xdist", "--with", "markdown-it-py>=4,<5", "--with", "neo4j"]
ONT = "business_architecture/ontology"
MODULES = list(manifest.MODULES)  # the one inventory of modules (manifest.py)
MODULES_NS = "https://w3id.org/mpc/ontology/modules/"

SKILL_CHECKS = skill_checks.SKILL_CHECKS  # the one table of the skills' checks (skill_checks.py); rebuild.py renders it too


def skill_folder(tree, skill, env):
    """Where a skill lives: in the release under skills/<name>/, on main in the skills repository's skills/<group>/<name>/."""
    if is_release(tree):
        return os.path.join(tree, "skills", skill) if skill else os.path.join(tree, "skills")
    repo = env.get("SKILLS_REPO", "")
    if not repo:
        return None
    return os.path.join(repo, "skills", "data", skill) if skill else repo


def sh(args, cwd, env=None, timeout=3600):
    """One command in its own process group with a deadline; its record is scrubbed of every secret (scrubbing.py)."""
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})}
    secrets = scrubbing.secrets_in(args, env)
    t = time.time()
    try:
        r = procs.run(args, timeout=timeout, cwd=cwd, env=env)
        rc, text = r.returncode, r.stdout + r.stderr
    except procs.Expired as exc:
        rc, text = -1, f"timed out after {timeout} s: " + exc.partial
    m = re.search(r"\d+ passed[^\n]*", text)
    return {"command": scrubbing.scrub(" ".join(args), secrets), "cwd": cwd, "returncode": rc, "seconds": round(time.time() - t, 1),
            "tail": scrubbing.scrub(text[-3000:], secrets), "pytest_summary": m.group(0) if m else None}


def uv(args, cwd, **kw):
    return sh(["uv", "run", "-q", "--no-project", *DEPS, "python3", *args], cwd, **kw)


def is_release(tree):
    return manifest.is_release(tree)  # release.json at the root, the one marker every reader asks


# ---------- rows for one tree ----------

def row_checks(tree, env):
    r = sh(["bash", "scripts/check.sh"], tree, env={"EPM_SHARE_RELEASE": "1"} if is_release(tree) else {})
    m = re.search(r"(\d+) passed(?:, (\d+) skipped)?", r.get("pytest_summary") or "")
    r["passed"] = int(m.group(1)) if m else None
    r["skipped"] = int(m.group(2)) if m and m.group(2) else 0
    r["ok"] = r["returncode"] == 0
    return r


def row_regression(tree, env):
    r = uv(["run.py"], os.path.join(tree, ONT, "regression"))
    m = re.search(r"(\d+) questions; answerable (\d+), partial (\d+), waiting (\d+), parked (\d+)", r["tail"])
    r.update({"questions": int(m.group(1)), "answerable": int(m.group(2)), "partial": int(m.group(3)),
              "waiting": int(m.group(4)), "parked": int(m.group(5))} if m else {})
    r["ok"] = r["returncode"] == 0
    return r


def row_docs_links(tree, env):
    """Every relative link in a Markdown or HTML file resolves to a file in the tree (anchors ignored)."""
    broken, checked = [], 0
    for root, dirs, files in os.walk(tree):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "node_modules", "release-cut")]
        for f in files:
            if not f.endswith((".md", ".html")) or f == "docs_template.html":
                continue  # the page template holds placeholders, not links
            path = os.path.join(root, f)
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            links = re.findall(r"\]\(([^)\s]+)\)", text) if f.endswith(".md") else re.findall(r'href="([^"#]+)"', text)
            for link in links:
                if re.match(r"^[a-z]+:", link) or link.startswith("#") or link.startswith("mailto"):
                    continue
                target = link.split("#", 1)[0]
                if not target:
                    continue
                checked += 1
                full = os.path.normpath(os.path.join(root, target))
                if not os.path.exists(full):
                    broken.append(f"{os.path.relpath(path, tree)} -> {link}")
    return {"checked": checked, "broken": len(broken), "samples": broken[:20], "ok": not broken}


def row_skills_tests(tree, env):
    """The four shipped skills' own checks (SKILL_CHECKS, the same table the release's check.sh is rendered from): in
    the release under skills/<name>/, on main in the skills repository's skills/<group>/<name>/. A test command
    that ran no test fails the row."""
    if skill_folder(tree, "ontology", env) is None:
        return {"ok": None, "reason": "give SKILLS_REPO in --env for main"}
    out = {"runs": {}}
    for skill, folder, cmd, kind in SKILL_CHECKS:
        name = skill_checks.name_of(skill, cmd, kind)
        r = sh(cmd, os.path.join(skill_folder(tree, skill, env), folder))
        m = re.search(r"Ran (\d+) tests?", r["tail"])
        tests = int(m.group(1)) if m else None
        out["runs"][name] = {"returncode": r["returncode"], "kind": kind, "tests": tests, "tail": r["tail"][-400:],
                             "ok": r["returncode"] == 0 and (kind != "tests" or bool(tests))}
    out["passed"] = sum(x["tests"] or 0 for x in out["runs"].values())
    out["ok"] = all(x["ok"] for x in out["runs"].values())
    return out


def row_iri_base(tree, env):
    """The old IRI base and company name anywhere in the tree (0 expected on the release)."""
    pat = re.compile(r"w3id\\*\.org/lsc|\bLSC\b|Lagos Specialty", re.I)
    hits, unreadable = [], []
    for root, dirs, files in os.walk(tree):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "release-cut")]
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    n = len(pat.findall(fh.read()))
            except OSError as exc:
                unreadable.append(f"{os.path.relpath(path, tree)}: {exc.strerror}")  # a file not read proves nothing
                continue
            if n:
                hits.append((os.path.relpath(path, tree), n))
    # On main the row measures (the old base is everywhere there); on the release the old base may be nowhere.
    return {"files": len(hits), "places": sum(n for _, n in hits), "samples": hits[:10], "unreadable": unreadable,
            "ok": not unreadable and (not hits if is_release(tree) else True)}


def row_gate(tree, env):
    if not is_release(tree):
        return {"ok": None, "reason": "the gate runs on the release only"}
    r = sh([sys.executable, os.path.join(HERE, "gate.py"), tree], tree)
    m = re.search(r"(\d+) leak", r["tail"])
    r["leaks"] = int(m.group(1)) if m else 0
    r["ok"] = r["returncode"] == 0
    return r


def row_not_run(reason):
    return lambda tree, env: {"ok": None, "reason": reason}


ROWS = {
    "checks": row_checks,
    "regression": row_regression,
    "docs-links": row_docs_links,
    "skills-tests": row_skills_tests,
    "iri-base": row_iri_base,
    "gate": row_gate,
}
try:  # the rows that need stores (stores.py); each reads its logins and ports from --env
    import stores
    ROWS.update(stores.ROWS)
except ImportError:
    pass


def read_env(path):
    values = {}
    if not path:
        return values
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip()
    return values


def run(tree, out, rows, env):
    """Each row in turn, the json rewritten after each. Returns the result; a row with ok False is a failure of the run
    (main() exits 1), a row with ok None was not run and says why."""
    tree = os.path.abspath(tree)
    if not rows:
        raise SystemExit("no row was asked for: a run of no rows is not a validation")
    unknown = [r for r in rows if r not in ROWS]
    if unknown:
        raise SystemExit(f"unknown row(s): {', '.join(unknown)}")
    result = {"tree": tree, "release": is_release(tree), "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rows": {}}
    if os.path.exists(os.path.join(tree, ".git")):
        result["commit"] = procs.run(["git", "-C", tree, "rev-parse", "--short", "HEAD"], timeout=600).stdout.strip()
    for name in rows:
        print(f"--- {name}", flush=True)
        try:
            result["rows"][name] = ROWS[name](tree, env)
        except Exception as exc:  # a row that crashes is a result too; its text is scrubbed like every record
            result["rows"][name] = {"ok": False, "error": scrubbing.scrub(repr(exc))[:500]}
        with open(out, "w") as f:
            json.dump(result, f, indent=1, default=str)
        print(f"    ok={result['rows'][name].get('ok')}", flush=True)
    return result


# ---------- the comparison rows ----------

def compare(main, release, out):
    import rules
    from export import record_dates
    main, release = os.path.abspath(main), os.path.abspath(release)
    dates = record_dates(main)
    result = {"main": main, "release": release, "rows": {}}

    # 1. The business-process JSON: main's files after the rules equal the release's, byte for byte.
    result["rows"]["business-process-json"] = compare_business_process(main, release, dates)

    # 2. Each newest module's Turtle: main's after the rules is isomorphic to the release's, with the same triple count.
    from rdflib import Graph, URIRef
    from rdflib.compare import graph_diff, to_isomorphic
    content = {}
    for m in MODULES:
        version = manifest.newest_on_disk(release, m)
        folder = os.path.join(release, ONT, "releases", m, version)
        src = os.path.join(main, ONT, "releases", m, version, f"{m}.ttl")
        with open(src, encoding="utf-8") as f:
            text, _ = rules.apply(f.read(), f"{ONT}/releases/{m}/{version}/{m}.ttl", dates)
        a = Graph().parse(data=text, format="turtle")
        b = Graph().parse(os.path.join(folder, f"{m}.ttl"))
        both, only_main, only_release = graph_diff(to_isomorphic(a), to_isomorphic(b))
        explained = explained_by_pin_move(only_main, only_release, m, newest_versions(release))
        content[m] = {"version": version, "main_triples": len(a), "release_triples": len(b),
                      "isomorphic": not only_main and not only_release, "only_main": len(only_main),
                      "only_release": len(only_release), "explained_by_pin_move": explained,
                      "samples": [" ".join(x.n3()[:90] for x in t) for t in list(only_main)[:3] + list(only_release)[:3]]}
    result["rows"]["ontology-content"] = {"modules": content,
                                          "ok": all(c["isomorphic"] or c["explained_by_pin_move"] for c in content.values())}

    # 3. The newest packages' pins name only newest versions, of the same dependencies as on main; the catalog lists
    # exactly the newest set.
    newest = {m: content[m]["version"] for m in MODULES}
    bad = latest_links(main, release, newest)
    result["rows"]["latest-links"] = {"problems": bad, "ok": not bad}

    # 4. The gate.
    r = sh([sys.executable, os.path.join(HERE, "gate.py"), release], release)
    result["rows"]["gate"] = {"returncode": r["returncode"], "tail": r["tail"][-1500:], "ok": r["returncode"] == 0}
    with open(out, "w") as f:
        json.dump(result, f, indent=1, default=str)
    return result


def json_files(root):
    """Every JSON file under root, relative to it: nested, hidden or upper-case names included, as the export ships
    them. os.walk takes the root literally, so a folder name holding glob characters cannot empty the list. A folder
    that cannot be read, or a linked folder (which os.walk would not enter), stops the row instead of hiding files."""
    def refuse(err):
        raise err
    found = []
    for folder, subfolders, names in os.walk(root, onerror=refuse):
        for sub in subfolders:
            if os.path.islink(os.path.join(folder, sub)):
                raise OSError(f"a linked folder in the process maps: {os.path.join(folder, sub)}")
        found += [os.path.relpath(os.path.join(folder, name), root).replace(os.sep, "/")
                  for name in names if name.lower().endswith(".json")]
    return found


def compare_business_process(main, release, dates):
    """Main's business-process JSON after the rewrite rules must equal the release's copy byte for byte; the two
    folders must hold the same files (the manifest ships the whole folder). Every file that differs, or exists on
    one side only, is recorded and fails the row."""
    import rules
    folder = "business_architecture/business_process"
    names = sorted({name for tree in (main, release) for name in json_files(os.path.join(tree, folder))})
    diffs, same = [], 0
    for name in names:
        rel = f"{folder}/{name}"
        on_main, on_release = os.path.isfile(os.path.join(main, rel)), os.path.isfile(os.path.join(release, rel))
        if not (on_main and on_release):
            diffs.append(f"{rel} (only on {'main' if on_main else 'the release'})")
            continue
        with open(os.path.join(main, rel), encoding="utf-8") as f:
            expected, _ = rules.apply(f.read(), rel, dates)
        with open(os.path.join(release, rel), encoding="utf-8") as f:
            got = f.read()
        if expected != got:
            diffs.append(rel)
        else:
            same += 1
    return {"equal": same, "different": diffs, "ok": not diffs}


def newest_versions(release):
    """Each module's newest version in the release, by number (manifest.newest_on_disk)."""
    return {m: manifest.newest_on_disk(release, m) for m in MODULES}


def explained_by_pin_move(only_main, only_release, module, newest):
    """A difference between main's Turtle (after the rules) and the release's that the rules explain: every differing
    triple is a dcterms:requires on the module's own IRI, the same dependencies moved on both sides, and each new
    target is that dependency's newest version. Nothing else is explained."""
    from rdflib import URIRef
    requires = URIRef("http://purl.org/dc/terms/requires")
    module_iri = URIRef(MODULES_NS + module)
    diff = list(only_main) + list(only_release)
    if not diff:
        return True
    if any(t[0] != module_iri or t[1] != requires for t in diff):
        return False

    def dep_of(obj):
        m = re.match(re.escape(MODULES_NS) + r"([a-z-]+)/(\d+\.\d+\.\d+)$", str(obj))
        return (m.group(1), m.group(2)) if m else (None, None)
    main_deps = {dep_of(t[2])[0] for t in only_main}
    rel = {dep_of(t[2]) for t in only_release}
    return (main_deps == {d for d, _ in rel} and None not in main_deps
            and all(newest.get(d) == v for d, v in rel))


def latest_links(main, release, newest):
    """What is wrong with the newest packages' links: a pin that is not the newest version, a dependency added or
    dropped against main's manifest, or a catalog that does not list exactly the newest set."""
    bad = []
    for m in MODULES:
        with open(os.path.join(release, ONT, "releases", m, newest[m], "manifest.json")) as f:
            deps = json.load(f).get("depends_on") or {}
        main_manifest = os.path.join(main, ONT, "releases", m, newest[m], "manifest.json")
        if not os.path.exists(main_manifest):
            bad.append(f"{m} {newest[m]} has no manifest on main to compare with")  # no baseline, no comparison, no pass
        else:
            with open(main_manifest) as f:
                main_deps = json.load(f).get("depends_on") or {}
            if set(main_deps) != set(deps):
                bad.append(f"{m} {newest[m]} requires {sorted(deps)} in the release and {sorted(main_deps)} on main")
        for dep, v in deps.items():
            if newest.get(dep) != v:
                bad.append(f"{m} {newest[m]} requires {dep} {v}, newest is {newest.get(dep)}")
    catalog = os.path.join(release, ONT, "releases", "catalog.ttl")
    with open(catalog, encoding="utf-8") as f:
        listed = set(re.findall(re.escape(MODULES_NS) + r"([a-z-]+)/(\d+\.\d+\.\d+)> a dcat:Dataset", f.read()))
    expected = set(newest.items())
    if listed != expected:
        bad.append(f"the catalog lists {sorted(listed - expected)} that are not newest and misses {sorted(expected - listed)}")
    return bad


def report(baseline, release, comparison, out):
    """The table the plan asks for. Returns the failures: a release row that failed, a baseline row the release did
    not run, a comparison row that failed. A figure that differs is listed for the cut's notes to explain (a rewrite
    rule, or the pins' move); it is not by itself a failure, since the release ships fewer tests than main."""
    with open(baseline) as f:
        b = json.load(f)
    with open(release) as f:
        r = json.load(f)
    c = json.load(open(comparison)) if comparison else {"rows": {}}
    lines = ["# Validation after the cut", "", f"Baseline: `{b.get('tree')}` at `{b.get('commit', '?')}`. Release: `{r.get('tree')}`.", "",
             "| Row | Main | Release | Same? |", "|---|---|---|---|"]
    keys = ("passed", "skipped", "answerable", "partial", "waiting", "parked", "broken", "files", "places", "leaks")
    failures, differences = [], []

    def summary(row):
        if row is None:
            return "not run"
        if row.get("ok") is None:
            return f"not run: {row.get('reason', '')}"
        figs = ", ".join(f"{k} {row[k]}" for k in keys if k in row and row[k] is not None)
        return f"{'pass' if row.get('ok') else 'FAIL'}; {figs}".rstrip("; ")
    for name in sorted(set(b["rows"]) | set(r["rows"])):
        mb, mr = b["rows"].get(name), r["rows"].get(name)
        same = "yes" if mb and mr and all(mb.get(k) == mr.get(k) for k in keys if k in mb or k in mr) and mb.get("ok") == mr.get("ok") else "no"
        lines.append(f"| {name} | {summary(mb)} | {summary(mr)} | {same} |")
        if mr is not None and mr.get("ok") is False:
            failures.append(f"{name} failed on the release")
        if mb is not None and mb.get("ok") is not None and (mr is None or mr.get("ok") is None):
            failures.append(f"{name} ran on main and not on the release")
        if same == "no" and mr is not None and mr.get("ok") and mb is not None and mb.get("ok"):
            differences.append(name)
    for name, row in c["rows"].items():
        lines.append(f"| {name} (comparison) | | {'pass' if row.get('ok') else 'FAIL'} | |")
        if not row.get("ok"):
            failures.append(f"{name} (comparison) failed")
    if differences:
        lines += ["", "Figures that differ, to explain in the cut's notes: " + ", ".join(differences) + "."]
    if failures:
        lines += ["", "FAILED: " + "; ".join(failures) + "."]
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run"); p.add_argument("--tree", required=True); p.add_argument("--out", required=True)
    p.add_argument("--rows", default=",".join(ROWS)); p.add_argument("--env", default="")
    p = sub.add_parser("compare"); p.add_argument("--main", required=True); p.add_argument("--release", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("report"); p.add_argument("baseline"); p.add_argument("release"); p.add_argument("comparison", nargs="?"); p.add_argument("--out", default="VALIDATION.md")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        result = run(a.tree, a.out, [r for r in a.rows.split(",") if r], read_env(a.env))
        return 1 if any(v.get("ok") is False for v in result["rows"].values()) else 0
    elif a.cmd == "compare":
        result = compare(a.main, a.release, a.out)
        return 1 if any(not v.get("ok") for v in result["rows"].values()) else 0
    else:
        return 1 if report(a.baseline, a.release, a.comparison, a.out) else 0


if __name__ == "__main__":
    sys.exit(main())
