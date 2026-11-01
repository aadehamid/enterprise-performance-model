#!/usr/bin/env python3
"""Every snippet in every shipped document, run as the document gives it (plan step 7, "Every snippet").

    python3 scripts/share_release/snippets.py --tree <release or checkout> --out <json> [--env <file>] [--list]

Every Markdown file and page in the tree is read (a page whose Markdown source sits beside it is the same document
rendered, so it is read once; the page templates and caches are not documents). A snippet is a fenced block in a
Markdown file or a <pre> block in a page. It is classified by its first word: Cypher (MATCH, CALL, RETURN, WITH,
UNWIND) runs against the test Neo4j named in --env (its login from TEST_NEO4J_PASSWORD, else from the login file
the store rows wrote in IMPORT_DIR); SPARQL (PREFIX, SELECT, ASK, CONSTRUCT) runs with rdflib over the newest
released packages; a shell block runs line by line when every command is read-only (the allowlist below), in the
folder the block's own `cd` or "# from <folder>" names, which must be inside the tree; anything else (Turtle shown
as an example, text, SQL for Databricks, a command that writes data or needs a login) is listed as not run, with
its reason. No line reaches a shell: a command is split into words (shlex), its variables are the block's own, and
it runs with a minimal environment that carries no login; a line with shell syntax (";", "|", redirection, a
substitution) is listed as not run, and "a && b" runs a then b. A folder a block names that is not in the tree,
or outside it, stops the block there: in the tree's own documents that is a failure (the document points
nowhere), in a skill's reference it is an example folder and the rest of the block is listed as not run.
The result names each snippet by file and line, so a failing one is a release defect with an address. --list
prints every block with its kind and runs nothing.
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

import manifest  # noqa: E402
import shlex  # noqa: E402

ONT = "business_architecture/ontology"
NOT_DOCS = {"docs_template.html", "playbook_template.html"}  # page templates hold placeholders, not snippets
SKIP_DIRS = (".git", "__pycache__", ".venv", ".pytest_cache", "node_modules", "release-cut")


def documents(tree):
    """Every Markdown file and page in the tree, tree-relative and sorted; a page whose Markdown source sits beside it
    (README.html beside README.md) is the same document rendered, so the Markdown alone is read."""
    out = []
    for root, dirs, files in os.walk(tree):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            if f in NOT_DOCS or not f.endswith((".md", ".html")):
                continue
            if f.endswith(".html") and os.path.exists(os.path.join(root, f[:-5] + ".md")):
                continue
            out.append(os.path.relpath(os.path.join(root, f), tree))
    return sorted(out)


def neo4j_login(env):
    """The test Neo4j's password: TEST_NEO4J_PASSWORD in --env, else the login file the store rows wrote in IMPORT_DIR
    (stores.read_login, the one reader of that file); "" when there is no test Neo4j to run against."""
    from stores import read_login
    return env.get("TEST_NEO4J_PASSWORD") or read_login(env) or ""
READ_ONLY = re.compile(r"^(?:cd |ls |cat |head |tail |grep |find |wc |echo |printf |python3? [^\n]*(?:--verify|--check| find | modules | coverage |ask\.py|run\.py|--list|--help)|"
                       r"uv run [^\n]*(?:--verify|--check| find | modules | coverage |ask\.py|run\.py|pytest|counts|describe|check |--dry-run|--help|--list|walk)|"
                       r"sha256sum |shasum |git (?:log|status|show|diff) |docker ps|docker compose [^\n]*\bls\b|curl -s[^\n]*localhost)")
MODULES = list(manifest.MODULES)


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
            g.parse(os.path.join(tree, ONT, "releases", m, manifest.newest_on_disk(tree, m), f"{m}.ttl"))
        _GRAPH["g"] = g
    query = "\n".join(l for l in text.split("\n") if not l.strip().startswith("#"))
    res = _GRAPH["g"].query(query)
    return {"ran": True, "rows": len(list(res))}


ASSIGN = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(\S*)$")
FROM = re.compile(r"^#\s*from\s+(.+?)\s*$")
ROOT_WORDS = re.compile(r"^(?:the\s+)?(?:repository|release|tree)\s+root$|^\.$|^/$")


SHELL_SYNTAX = re.compile(r"[;|<>`]|\$\(|\$\{[^}]*[^A-Za-z0-9_}][^}]*\}")
KEEP_ENV = ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "TERM", "UV_CACHE_DIR", "XDG_CACHE_HOME", "SSL_CERT_FILE")


def reader_variables(tree):
    """The variables the documents tell a reader to set to their own paths; here they are the tree's."""
    return {"EPM": tree, "SKILLS": os.path.join(tree, "skills"), "DEMO": os.path.join(tree, "demos", "downstream-pricing-databricks-free")}


def expand(text, variables):
    """$VAR and ${VAR} from the block's own variables (unknown ones stay, so the runner can say so), then ~."""
    return os.path.expanduser(re.sub(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?", lambda v: variables.get(v.group(1), v.group(0)), text))


def inside(tree, target):
    """The folder a block names, resolved, when it is inside the tree; None when it is not (or not a folder)."""
    real, root = os.path.realpath(target), os.path.realpath(tree)
    return real if os.path.isdir(real) and (real == root or real.startswith(root + os.sep)) else None


def minimal_env(variables, release):
    """What a command sees: the shell's basics, the block's variables, release mode; no login of this machine."""
    e = {k: os.environ[k] for k in KEEP_ENV if k in os.environ}
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    if release:
        e["EPM_SHARE_RELEASE"] = "1"
    e.update(variables)
    return e


def run_shell(text, tree, env, state=None, strict=True, cwd=None):
    """state carries the shell variables a document's earlier blocks set (PLUGINS=..., ROBOT=...), as a reader's
    shell would; a block that opens with "# from <folder>" runs in that folder of the tree ("# from repository root"
    is the tree). A folder that is not in the tree stops the block: with strict, the block fails; without, its
    remaining lines are listed as not run."""
    state = state if state is not None else {}
    variables = state.setdefault("vars", {})
    for k, v in reader_variables(tree).items():
        variables.setdefault(k, v)
    raw = [l.strip() for l in text.split("\n") if l.strip()]
    cwd, results, stopped = cwd or tree, [], None
    for line in raw:
        if stopped:
            results.append({"line": line, "ran": False, "reason": f"not run: the block stopped at {stopped!r}, a folder not in the tree"})
            continue
        m = FROM.match(line)
        if m:  # "# from <folder>" before a command: the folder it runs in
            folder = m.group(1).strip("`")
            if ROOT_WORDS.match(folder):
                cwd = tree
                continue
            target = inside(tree, os.path.join(tree, expand(folder, variables)))
            if target:
                cwd = target
            else:
                results.append({"line": line, "ran": False, "reason": "folder not in the tree", "failed_folder": True})
                stopped = line
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
        if " && " in line and not SHELL_SYNTAX.search(line) and "||" not in line:
            # "a && b": b runs after a in the same folder (a cd carries); each part is judged on its own.
            chain = run_shell("\n".join(p.strip() for p in line.split(" && ")), tree, env, state, strict=strict, cwd=cwd)
            results.extend(chain["lines"])
            stopped, cwd = chain["stopped_at"] or stopped, chain["cwd"]
            continue
        if SHELL_SYNTAX.search(line) or "||" in line or "&&" in line:
            results.append({"line": line, "ran": False, "reason": "shell syntax (a separator, pipe, redirection or substitution); no line reaches a shell"})
            continue
        if line.startswith("cd "):
            target = inside(tree, os.path.join(cwd, expand(line[3:].strip().strip('"'), variables)))
            if target:
                cwd = target; results.append({"line": line, "ran": True})
            else:
                results.append({"line": line, "ran": False, "reason": "folder not in the tree", "failed_folder": True})
                stopped = line
            continue
        if not READ_ONLY.match(line) or re.search(r"-m pricing_demo\.|sync_stores\.py|--write|--yes|load_postgres|replicate|upload| build\b|tech_graph (?:load|sync|collect)|run_projection|run_local|docker compose [^\n]*up|docker run|--repeat|acceptance run|genie|supervisor", line):
            results.append({"line": line, "ran": False, "reason": "writes data, needs a login or a store, or is not read-only"})
            continue
        unset = [v for v in re.findall(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?", line) if v not in variables]
        if unset:
            results.append({"line": line, "ran": False, "reason": f"uses a variable no earlier block set: {', '.join(unset)}"})
            continue
        try:
            argv = [expand(a, variables) for a in shlex.split(line)]
        except ValueError as exc:
            results.append({"line": line, "ran": False, "reason": f"could not be split into words: {exc}"})
            continue
        try:
            r = subprocess.run(argv, cwd=cwd, env=minimal_env(variables, manifest.is_release(tree)), capture_output=True, text=True, timeout=900)
            results.append({"line": line, "ran": True, "returncode": r.returncode, "tail": (r.stdout + r.stderr)[-300:]})
        except subprocess.TimeoutExpired:
            results.append({"line": line, "ran": True, "returncode": -1, "tail": "timed out"})
        except OSError as exc:
            results.append({"line": line, "ran": True, "returncode": -1, "tail": f"could not start: {exc}"})
    failed = [r for r in results if r.get("ran") and r.get("returncode")]
    if strict:
        failed += [r for r in results if r.get("failed_folder")]
    return {"ran": any(r.get("ran") for r in results), "lines": results, "failed": failed,
            "stopped_at": stopped, "cwd": cwd}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tree", required=True); ap.add_argument("--out", default=""); ap.add_argument("--env", default="")
    ap.add_argument("--list", action="store_true", help="print every block with its kind; run nothing")
    a = ap.parse_args(argv)
    tree, env = os.path.abspath(a.tree), read_env(a.env)
    if a.list:
        for rel in documents(tree):
            for b in blocks_of(os.path.join(tree, rel), rel):
                print(f"{rel}:{b['line']} {kind_of(b)}: {b['text'].split(chr(10))[0][:80]}")
        return 0
    if not a.out:
        ap.error("--out is required unless --list")
    password = neo4j_login(env)
    if password:
        env["TEST_NEO4J_PASSWORD"] = password
    elif env.get("IMPORT_DIR") or env.get("TEST_NEO4J_PORT"):
        print("the --env names a test Neo4j (IMPORT_DIR or TEST_NEO4J_PORT) but no login was found: set TEST_NEO4J_PASSWORD or run the store rows first", file=sys.stderr)
        return 2
    results = []
    for rel in documents(tree):
        path = os.path.join(tree, rel)
        state = {}  # the shell variables this document's blocks set, in order
        strict = not rel.startswith("skills/")  # a skill's reference shows example folders; the tree's own documents name its folders
        for b in blocks_of(path, rel):
            kind = kind_of(b)
            entry = {"file": b["file"], "line": b["line"], "kind": kind, "first": b["text"].split("\n")[0][:100]}
            try:
                if kind == "cypher" and password:
                    entry.update(run_cypher(b["text"], env))
                elif kind == "sparql":
                    entry.update(run_sparql(b["text"], tree))
                elif kind == "shell":
                    entry.update(run_shell(b["text"], tree, env, state, strict=strict))
                else:
                    entry.update({"ran": False, "reason": {"turtle": "an example shown, not a command", "sql": "Databricks SQL; the demo's build runs it in the test catalog",
                                                           "text": "text, not a command", "cypher": "no test Neo4j in --env"}.get(kind, "not a command")})
            except Exception as exc:
                entry.update({"ran": True, "error": repr(exc)[:300]})
            results.append(entry)
    ran = [r for r in results if r.get("ran")]
    failed = [r for r in results if r.get("error") or r.get("failed")]
    summary = {"tree": tree, "documents": len(documents(tree)), "snippets": len(results), "ran": len(ran), "failed": len(failed),
               "not_run": len(results) - len(ran), "stopped_at_missing_folder": sum(1 for r in results if r.get("stopped_at")),
               "by_kind": {k: sum(1 for r in results if r["kind"] == k) for k in ("cypher", "sparql", "shell", "turtle", "sql", "text")},
               "results": results}
    with open(a.out, "w") as f:
        json.dump(summary, f, indent=1, default=str)
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}))
    for r in failed[:20]:
        print(f"FAILED {r['file']}:{r['line']} {r.get('error') or [x['line'] + ' -> ' + x.get('tail', x.get('reason', ''))[-120:] for x in r.get('failed', [])][:2]}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
