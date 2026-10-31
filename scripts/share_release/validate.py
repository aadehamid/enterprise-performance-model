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
DEPS = ["--with", "rdflib", "--with", "pyshacl", "--with", "openpyxl", "--with", "jsonschema", "--with", "pytest",
        "--with", "pytest-xdist", "--with", "markdown-it-py>=4,<5", "--with", "neo4j"]
ONT = "business_architecture/ontology"
MODULES = ["core", "organization", "ref-mpc", "kpi", "party", "data-product", "value-stream", "system", "lane",
           "market-data", "integration"]


def sh(args, cwd, env=None, timeout=3600):
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})}
    t = time.time()
    r = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    text = r.stdout + r.stderr
    m = re.search(r"\d+ passed[^\n]*", text)
    return {"command": " ".join(args), "cwd": cwd, "returncode": r.returncode, "seconds": round(time.time() - t, 1),
            "tail": text[-3000:], "pytest_summary": m.group(0) if m else None}


def uv(args, cwd, **kw):
    return sh(["uv", "run", "-q", "--no-project", *DEPS, "python3", *args], cwd, **kw)


def is_release(tree):
    return os.path.exists(os.path.join(tree, "KNOWN-OPEN-ITEMS.md"))


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
    """The four shipped skills' own tests, each with the dependencies its own check names: in the release under
    skills/<name>/, on main in the skills repository's skills/<group>/<name>/."""
    if is_release(tree):
        base = {"ontology": os.path.join(tree, "skills", "ontology"), "ontology-to-lpg": os.path.join(tree, "skills", "ontology-to-lpg"),
                "rdf-store": os.path.join(tree, "skills", "rdf-store")}
    else:
        repo = env.get("SKILLS_REPO", "")
        if not repo:
            return {"ok": None, "reason": "give SKILLS_REPO in --env for main"}
        base = {"ontology": os.path.join(repo, "skills", "data", "ontology"), "ontology-to-lpg": os.path.join(repo, "skills", "data", "ontology-to-lpg"),
                "rdf-store": os.path.join(repo, "skills", "data", "rdf-store")}
    runs = [
        ("ontology", ["uv", "run", "-q", "--no-project", "--with", "rdflib", "--with", "pyyaml", "--with", "pyshacl", "python3", "-m", "unittest", "discover", "-q", "-p", "test_*.py"], os.path.join(base["ontology"], "scripts")),
        ("ontology-to-lpg", ["uv", "run", "-q", "--no-project", "--with", "rdflib", "--with", "pyshacl", "--with", "mcp-neo4j-data-modeling==0.8.2", "python3", "-m", "unittest", "-q", "test_projection", "test_engine_gate", "test_modeling", "test_explore", "test_run_projection"], os.path.join(base["ontology-to-lpg"], "scripts")),
        ("rdf-store", ["uv", "run", "-q", "--no-project", "--with", "pyoxigraph", "python3", "-m", "unittest", "-q", "test_rdf_store"], os.path.join(base["rdf-store"], "scripts")),
    ]
    out = {"runs": {}}
    for name, cmd, cwd in runs:
        r = sh(cmd, cwd)
        m = re.search(r"Ran (\d+) tests", r["tail"])
        out["runs"][name] = {"returncode": r["returncode"], "tests": int(m.group(1)) if m else None, "tail": r["tail"][-400:]}
    out["passed"] = sum(x["tests"] or 0 for x in out["runs"].values())
    out["ok"] = all(x["returncode"] == 0 for x in out["runs"].values())
    return out


def row_iri_base(tree, env):
    """The old IRI base and company name anywhere in the tree (0 expected on the release)."""
    pat = re.compile(r"w3id\\*\.org/lsc|\bLSC\b|Lagos Specialty", re.I)
    hits = []
    for root, dirs, files in os.walk(tree):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "release-cut")]
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    n = len(pat.findall(fh.read()))
            except OSError:
                continue
            if n:
                hits.append((os.path.relpath(path, tree), n))
    return {"files": len(hits), "places": sum(n for _, n in hits), "samples": hits[:10], "ok": True}


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
    tree = os.path.abspath(tree)
    result = {"tree": tree, "release": is_release(tree), "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rows": {}}
    if os.path.exists(os.path.join(tree, ".git")):
        result["commit"] = subprocess.run(["git", "-C", tree, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    for name in rows:
        print(f"--- {name}", flush=True)
        try:
            result["rows"][name] = ROWS[name](tree, env)
        except Exception as exc:  # a row that crashes is a result too
            result["rows"][name] = {"ok": False, "error": repr(exc)[:500]}
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
    diffs, same = [], 0
    for path in sorted(glob.glob(os.path.join(main, "business_architecture/business_process/*.json"))):
        rel = os.path.relpath(path, main)
        with open(path, encoding="utf-8") as f:
            expected, _ = rules.apply(f.read(), rel, dates)
        with open(os.path.join(release, rel), encoding="utf-8") as f:
            got = f.read()
        (diffs if expected != got else [None]) and (diffs.append(rel) if expected != got else None)
        same += expected == got
    result["rows"]["business-process-json"] = {"equal": same, "different": diffs, "ok": not diffs}

    # 2. Each newest module's Turtle: main's after the rules is isomorphic to the release's, with the same triple count.
    from rdflib import Graph, URIRef
    from rdflib.compare import graph_diff, to_isomorphic
    content = {}
    for m in MODULES:
        folder = sorted(glob.glob(os.path.join(release, ONT, "releases", m, "[0-9]*")))[-1]
        version = os.path.basename(folder)
        src = os.path.join(main, ONT, "releases", m, version, f"{m}.ttl")
        with open(src, encoding="utf-8") as f:
            text, _ = rules.apply(f.read(), f"{ONT}/releases/{m}/{version}/{m}.ttl", dates)
        a = Graph().parse(data=text, format="turtle")
        b = Graph().parse(os.path.join(folder, f"{m}.ttl"))
        both, only_main, only_release = graph_diff(to_isomorphic(a), to_isomorphic(b))
        # A difference that the rules explain: the newest package's pins moved to the newest versions
        # (dcterms:requires on the module's own IRI), nothing else.
        requires = URIRef("http://purl.org/dc/terms/requires")
        module_iri = URIRef(f"https://w3id.org/mpc/ontology/modules/{m}")
        explained = all(t[0] == module_iri and t[1] == requires for t in list(only_main) + list(only_release))
        content[m] = {"version": version, "main_triples": len(a), "release_triples": len(b),
                      "isomorphic": not only_main and not only_release, "only_main": len(only_main),
                      "only_release": len(only_release), "explained_by_pin_move": explained,
                      "samples": [" ".join(x.n3()[:90] for x in t) for t in list(only_main)[:3] + list(only_release)[:3]]}
    result["rows"]["ontology-content"] = {"modules": content,
                                          "ok": all(c["isomorphic"] or c["explained_by_pin_move"] for c in content.values())}

    # 3. The newest packages' pins name only newest versions; the catalog lists the newest set.
    newest = {m: content[m]["version"] for m in MODULES}
    bad = []
    for m in MODULES:
        with open(os.path.join(release, ONT, "releases", m, newest[m], "manifest.json")) as f:
            man = json.load(f)
        for dep, v in (man.get("depends_on") or {}).items():
            if newest.get(dep) != v:
                bad.append(f"{m} {newest[m]} requires {dep} {v}, newest is {newest.get(dep)}")
    result["rows"]["latest-links"] = {"older_pins": bad, "ok": not bad}

    # 4. The gate.
    r = sh([sys.executable, os.path.join(HERE, "gate.py"), release], release)
    result["rows"]["gate"] = {"returncode": r["returncode"], "tail": r["tail"][-1500:], "ok": r["returncode"] == 0}
    with open(out, "w") as f:
        json.dump(result, f, indent=1, default=str)
    return result


def report(baseline, release, comparison, out):
    with open(baseline) as f:
        b = json.load(f)
    with open(release) as f:
        r = json.load(f)
    c = json.load(open(comparison)) if comparison else {"rows": {}}
    lines = ["# Validation after the cut", "", f"Baseline: `{b.get('tree')}` at `{b.get('commit', '?')}`. Release: `{r.get('tree')}`.", "",
             "| Row | Main | Release | Same? |", "|---|---|---|---|"]
    keys = ("passed", "skipped", "answerable", "partial", "waiting", "parked", "broken", "files", "places", "leaks")

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
    for name, row in c["rows"].items():
        lines.append(f"| {name} (comparison) | | {'pass' if row.get('ok') else 'FAIL'} | |")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run"); p.add_argument("--tree", required=True); p.add_argument("--out", required=True)
    p.add_argument("--rows", default=",".join(ROWS)); p.add_argument("--env", default="")
    p = sub.add_parser("compare"); p.add_argument("--main", required=True); p.add_argument("--release", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("report"); p.add_argument("baseline"); p.add_argument("release"); p.add_argument("comparison", nargs="?"); p.add_argument("--out", default="VALIDATION.md")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run(a.tree, a.out, [r for r in a.rows.split(",") if r], read_env(a.env))
    elif a.cmd == "compare":
        compare(a.main, a.release, a.out)
    else:
        report(a.baseline, a.release, a.comparison, a.out)


if __name__ == "__main__":
    main()
