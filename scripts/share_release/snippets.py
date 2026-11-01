#!/usr/bin/env python3
"""Every snippet in every shipped document, run as the document gives it (plan step 7, "Every snippet").

    python3 scripts/share_release/snippets.py --tree <release or checkout> --out <json> [--env <file>]

A snippet is a fenced block in a Markdown file or a <pre> block in a page. It is classified by its first word:
Cypher (MATCH, CALL, RETURN, WITH, UNWIND) runs against the test Neo4j named in --env; SPARQL (PREFIX, SELECT,
ASK, CONSTRUCT) runs with rdflib over the newest released packages; a shell block runs line by line when every
command is read-only (the allowlist below), in the folder the block's own `cd` names; anything else (Turtle shown
as an example, text, SQL for Databricks, a command that writes data or needs a login) is listed as not run, with
its reason. The result names each snippet by file and line, so a failing one is a release defect with an address.
"""
import argparse
import html as html_mod
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import read_env  # noqa: E402

ONT = "business_architecture/ontology"
DOCS = [f"{ONT}/README.md", f"{ONT}/MODULES.md", f"{ONT}/competency-questions.md", f"{ONT}/OPEN-ITEMS.md",
        f"{ONT}/business-closeout.md", f"{ONT}/projection/README.md", f"{ONT}/projection/LOCAL-STORES.md",
        f"{ONT}/projection/STORE-INVENTORY.md", f"{ONT}/projection/skill-run/README.md", f"{ONT}/regression/README.md",
        f"{ONT}/epm-ontology-guide.html", f"{ONT}/epm-walkthrough.html", f"{ONT}/projection/ontology-stores-runbook.html",
        "demos/downstream-pricing-databricks-free/README.md", "demos/downstream-pricing-databricks-free/DATA.md",
        "README.md", "skills/ontology/SKILL.md", "skills/ontology-to-lpg/SKILL.md", "skills/rdf-store/SKILL.md"]
READ_ONLY = re.compile(r"^(?:cd |ls |cat |head |tail |grep |find |wc |echo |printf |python3? [^\n]*(?:--verify|--check| find | modules | coverage |ask\.py|run\.py|--list|--help)|"
                       r"uv run [^\n]*(?:--verify|--check| find | modules | coverage |ask\.py|run\.py|pytest|counts|describe|check |--dry-run|--help|--list|walk)|"
                       r"sha256sum |shasum |git (?:log|status|show|diff) |docker ps|docker compose [^\n]*\bls\b|curl -s[^\n]*localhost)")
MODULES = ["core", "organization", "ref-mpc", "kpi", "party", "data-product", "value-stream", "system", "lane", "market-data", "integration"]


def blocks_of(path, rel):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    out = []
    if rel.endswith(".md"):
        for m in re.finditer(r"^( *)```([a-zA-Z]*)[^\n]*\n(.*?)^\1```", text, re.S | re.M):
            line = text.count("\n", 0, m.start()) + 1
            body = "\n".join(l[len(m.group(1)):] if l.startswith(m.group(1)) else l for l in m.group(3).split("\n"))
            out.append({"file": rel, "line": line, "lang": m.group(2).lower(), "text": body.strip()})
    else:
        for m in re.finditer(r"<pre[^>]*>(.*?)</pre>", text, re.S):
            line = text.count("\n", 0, m.start()) + 1
            body = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
            out.append({"file": rel, "line": line, "lang": "", "text": body.strip()})
    return out


def kind_of(b):
    first = (b["text"].split() or [""])[0]
    words = re.sub(r"^(?:#|//|--)[^\n]*\n", "", b["text"]).split()  # skip a leading comment line
    first2 = words[0] if words else first
    if b["lang"] in ("cypher",) or first2.upper() in ("MATCH", "CALL", "RETURN", "WITH", "UNWIND", "PROFILE", "EXPLAIN"):
        return "cypher"
    body = "\n".join(l for l in b["text"].split("\n") if not l.strip().startswith("--"))
    if first2.upper() == "SELECT" and (re.search(r"\bFROM\s+[a-z_]+\.[a-z_]+", body) or "MEASURE(" in body or "GROUP BY ALL" in body.upper()):
        return "sql"  # Databricks SQL over a catalog table or a metric view
    if b["lang"] in ("sparql",) or first2.upper() in ("PREFIX", "SELECT", "ASK", "CONSTRUCT", "DESCRIBE"):
        return "sparql"
    if b["lang"] in ("bash", "sh", "shell", "console") or first2 in ("cd", "uv", "python3", "python", "docker", "./run_local.sh", "scripts/check.sh", "export", "set", "curl", "ls"):
        return "shell"
    if b["lang"] in ("turtle", "ttl") or first2.startswith("@prefix"):
        return "turtle"
    if b["lang"] in ("sql",) or first2.upper() in ("CREATE", "SHOW", "DESCRIBE") and "sparql" != b["lang"]:
        return "sql"
    return "text"


def run_cypher(text, env):
    from stores import cypher
    bolt, pw = f"bolt://localhost:{env.get('TEST_NEO4J_PORT', '17799')}", env.get("TEST_NEO4J_PASSWORD", "")
    stmts = [s.strip() for s in re.split(r";\s*\n", text) if s.strip() and not s.strip().startswith("//")]
    rows = 0
    for st in stmts:
        st = re.sub(r"\$[a-zA-Z_]+", "''", st) if "$" in st and "SET" not in st.upper() else st
        if re.search(r"\b(DELETE|DETACH|SET|CREATE|MERGE|DROP|REMOVE)\b", st.upper()):
            return {"ran": False, "reason": "writes data; run in the test store by the store rows"}
        rows += len(cypher(bolt, pw, st))
    return {"ran": True, "rows": rows}


_GRAPH = {}


def run_sparql(text, tree):
    from rdflib import Graph
    if "g" not in _GRAPH:
        g = Graph()
        for m in MODULES:
            folders = sorted(p for p in os.listdir(os.path.join(tree, ONT, "releases", m)) if p[0].isdigit())
            g.parse(os.path.join(tree, ONT, "releases", m, folders[-1], f"{m}.ttl"))
        _GRAPH["g"] = g
    query = "\n".join(l for l in text.split("\n") if not l.strip().startswith("#"))
    res = _GRAPH["g"].query(query)
    return {"ran": True, "rows": len(list(res))}


ASSIGN = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(\S*)$")
FROM = re.compile(r"^#\s*from\s+(\S+)")


def run_shell(text, tree, env, state=None):
    """state carries the shell variables a document's earlier blocks set (PLUGINS=..., ROBOT=...), as a reader's
    shell would; a block that opens with "# from <folder>" runs in that folder of the tree."""
    state = state if state is not None else {}
    variables = state.setdefault("vars", {})
    raw = [l.strip() for l in text.split("\n") if l.strip()]
    cwd, results = tree, []
    for line in raw:
        m = FROM.match(line)
        if m:  # "# from <folder>" before a command: the folder it runs in
            target = os.path.normpath(os.path.join(tree, m.group(1).strip("`")))
            if os.path.isdir(target):
                cwd = target
            else:
                results.append({"line": line, "ran": False, "reason": "folder not in the tree"})
            continue
        if line.startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", line)
        parts = [p.strip() for p in line.split(";")] if ";" in line and all(ASSIGN.match(p.strip()) or p.strip().startswith("mkdir ") for p in line.split(";")) else [line]
        assigned = [ASSIGN.match(p) for p in parts]
        if all(assigned) and parts:
            for a in assigned:
                variables[a.group(1)] = os.path.expanduser(os.path.expandvars(a.group(2).strip('"')))
            results.append({"line": line, "ran": True, "set": [a.group(1) for a in assigned]})
            continue
        if any(a for a in assigned):  # assignments beside a mkdir: keep the variables, run nothing
            for a in assigned:
                if a:
                    variables[a.group(1)] = os.path.expanduser(os.path.expandvars(a.group(2).strip('"')))
            results.append({"line": line, "ran": False, "reason": "sets the reader's variables and makes folders"})
            continue
        if line.startswith("cd "):
            target = os.path.normpath(os.path.join(cwd, os.path.expanduser(line[3:].strip().strip('"'))))
            if os.path.isdir(target):
                cwd = target; results.append({"line": line, "ran": True})
            else:
                results.append({"line": line, "ran": False, "reason": "folder not in the tree"})
            continue
        if not READ_ONLY.match(line) or re.search(r"-m pricing_demo\.|sync_stores\.py|--write|--yes|load_postgres|replicate|upload| build\b|tech_graph (?:load|sync|collect)|run_projection|run_local|docker compose [^\n]*up|docker run|--repeat|acceptance run|genie|supervisor", line):
            results.append({"line": line, "ran": False, "reason": "writes data, needs a login or a store, or is not read-only"})
            continue
        e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        e.update({"EPM_SHARE_RELEASE": "1"} if os.path.exists(os.path.join(tree, "KNOWN-OPEN-ITEMS.md")) else {})
        e.update(variables)
        unset = [v for v in re.findall(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?", line) if v not in e]
        if unset:
            results.append({"line": line, "ran": False, "reason": f"uses a variable no earlier block set: {', '.join(unset)}"})
            continue
        try:
            r = subprocess.run(["bash", "-lc", line], cwd=cwd, env=e, capture_output=True, text=True, timeout=900)
            results.append({"line": line, "ran": True, "returncode": r.returncode, "tail": (r.stdout + r.stderr)[-300:]})
        except subprocess.TimeoutExpired:
            results.append({"line": line, "ran": True, "returncode": -1, "tail": "timed out"})
    return {"ran": any(r.get("ran") for r in results), "lines": results,
            "failed": [r for r in results if r.get("ran") and r.get("returncode")]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tree", required=True); ap.add_argument("--out", required=True); ap.add_argument("--env", default="")
    a = ap.parse_args(argv)
    tree, env = os.path.abspath(a.tree), read_env(a.env)
    results = []
    for rel in DOCS:
        path = os.path.join(tree, rel)
        if not os.path.exists(path):
            continue
        state = {}  # the shell variables this document's blocks set, in order
        for b in blocks_of(path, rel):
            kind = kind_of(b)
            entry = {"file": b["file"], "line": b["line"], "kind": kind, "first": b["text"].split("\n")[0][:100]}
            try:
                if kind == "cypher" and env.get("TEST_NEO4J_PASSWORD"):
                    entry.update(run_cypher(b["text"], env))
                elif kind == "sparql":
                    entry.update(run_sparql(b["text"], tree))
                elif kind == "shell":
                    entry.update(run_shell(b["text"], tree, env, state))
                else:
                    entry.update({"ran": False, "reason": {"turtle": "an example shown, not a command", "sql": "Databricks SQL; the demo's build runs it in the test catalog",
                                                           "text": "text, not a command", "cypher": "no test Neo4j in --env"}.get(kind, "not a command")})
            except Exception as exc:
                entry.update({"ran": True, "error": repr(exc)[:300]})
            results.append(entry)
    ran = [r for r in results if r.get("ran")]
    failed = [r for r in ran if r.get("error") or r.get("failed")]
    summary = {"tree": tree, "snippets": len(results), "ran": len(ran), "failed": len(failed), "not_run": len(results) - len(ran),
               "by_kind": {k: sum(1 for r in results if r["kind"] == k) for k in ("cypher", "sparql", "shell", "turtle", "sql", "text")},
               "results": results}
    with open(a.out, "w") as f:
        json.dump(summary, f, indent=1, default=str)
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}))
    for r in failed[:20]:
        print(f"FAILED {r['file']}:{r['line']} {r.get('error') or [x['line'] + ' -> ' + x.get('tail', '')[-120:] for x in r.get('failed', [])][:2]}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
