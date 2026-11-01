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
its reason. No line reaches a shell: a command is split into words (shlex), its variables are the block's own
(never this machine's environment), and it runs with a minimal environment that carries no login; a line with
shell syntax (";", "|", redirection, a substitution) is listed as not run, and "a && b" runs a then b. What may
run is a closed policy (POLICY): a named executable with its allowed options, every path-like operand resolved and
required inside the tree, a Python script only from the tree and never "-c", and nothing else. A folder a block names that is not in the tree,
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
import procs  # noqa: E402
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


REFERENCE_DOCS = re.compile(r"^(?:skills/|best-practices/)")


def run_sparql(text, tree, rel=""):
    """A SPARQL block runs over the newest packages. In a skill's reference or a best-practices guide a block that
    does not parse alone is a fragment shown to explain a query (a CONSTRUCT shown in pieces), listed as not run
    with the parser's words; in the tree's own documents a block that does not parse is a failure."""
    from rdflib import Graph
    from rdflib.plugins.sparql import prepareQuery
    query = "\n".join(l for l in text.split("\n") if not l.strip().startswith("#"))
    try:
        prepareQuery(query)
    except Exception as exc:
        if REFERENCE_DOCS.match(rel):
            where = ", ".join(f"{k} {getattr(exc, k)}" for k in ("lineno", "col") if getattr(exc, k, None) is not None) or f"position {getattr(exc, 'loc', '?')}"
            return {"ran": False, "reason": f"not run: the block did not parse ({where}: {str(exc)[:120]}); in a reference a query fragment shown in pieces is listed, not failed, and a malformed one shows here with its position"}
        raise
    if "g" not in _GRAPH:
        g = Graph()
        for m in MODULES:
            g.parse(os.path.join(tree, ONT, "releases", m, manifest.newest_on_disk(tree, m), f"{m}.ttl"))
        _GRAPH["g"] = g
    res = _GRAPH["g"].query(query)
    return {"ran": True, "rows": len(list(res))}


ASSIGN = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(\S*)$")
FROM = re.compile(r"^#\s*from\s+(.+?)\s*$")
ROOT_WORDS = re.compile(r"^(?:the\s+)?(?:repository|release|tree)\s+root$|^\.$|^/$")


SHELL_SYNTAX = re.compile(r"[;|<>`]|\$\(|\$\{[^}]*[^A-Za-z0-9_}][^}]*\}")
KEEP_ENV = ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "TERM", "UV_CACHE_DIR", "XDG_CACHE_HOME", "SSL_CERT_FILE")

# The command policy: for each executable a document may run, the options it may take (a value-taking option is
# listed with "=" or its value is the next word), and whether its path-like operands are checked. An option not
# listed, an executable not listed, or an operand that resolves outside the tree is not run. Options with values
# are listed as (option, takes_value).
FILE_TOOLS = {
    "ls": {"-l", "-a", "-la", "-al", "-1", "-h", "-lh", "-R", "-t", "-r", "-S", "-d"},
    "cat": {"-n"}, "wc": {"-l", "-c", "-w", "-m"},
    "head": {"-n:", "-c:"}, "tail": {"-n:", "-c:"},
    "grep": {"-r", "-R", "-n", "-c", "-l", "-L", "-i", "-E", "-F", "-o", "-h", "-H", "-w", "-q", "-v", "-s", "-e:", "-A:", "-B:", "-C:", "--include=", "--exclude=", "--exclude-dir="},
    "find": {"-name:", "-iname:", "-type:", "-maxdepth:", "-mindepth:", "-path:", "-newer:", "-size:", "-print", "-not", "-o", "-a", "-prune", "(", ")"},
    "diff": {"-u", "-r", "-q", "-w", "-b"}, "shasum": {"-a:", "-c"}, "sha256sum": set(),
}
PYTHON_MODULES = {"pytest", "unittest"}
UV_OPTIONS = {"-q", "--no-project", "--with:", "--group:", "--python:", "--project:", "--frozen", "--offline", "-B"}
PYTHON_OPTIONS = {"-B", "-I", "-q", "-m:"}
# git may only read, with options that read: no --ext-diff, --textconv, -c, --config-env or pager setting (each runs a program).
GIT_OPTIONS = {"log": {"--oneline", "-n:", "--stat", "--name-only", "--format=", "--pretty=", "--", "--no-color"},
               "status": {"-s", "--short", "--porcelain", "--no-color"},
               "show": {"--stat", "--name-only", "-s", "--format=", "--pretty=", "--no-color", "--"},
               "diff": {"--stat", "--name-only", "--cached", "--no-color", "--"}}
# A document's own variable is never exported under a name a tool reads for a program or a path to one.
NOT_EXPORTED = re.compile(r"^(?:GIT_|PYTHON|UV_|LD_|DYLD_|PIP_|SSL_|XDG_|PATH$|HOME$|TMPDIR$|SHELL$|ENV$|BASH_ENV$|IFS$|VIRTUAL_ENV$)")
# git reads programs to run from its configuration (diff.external, core.pager, textconv) wherever it finds a config
# file, so it runs with a fixed environment that carries no document variable at all: no system or global config,
# a throwaway HOME and XDG folder, no pager and no hooks, and on diff, log and show git's own --no-ext-diff and
# --no-textconv, which override diff.external and a driver's textconv wherever they are configured.
GIT_ARGV_PREFIX = ("--no-pager", "-c", "core.pager=cat", "-c", "core.hooksPath=/dev/null")
GIT_DIFF_GUARDS = ("--no-ext-diff", "--no-textconv")
PACKAGE_SPEC = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*(?:\[[A-Za-z0-9,._-]+\])?(?:[=<>!~]=?[A-Za-z0-9.*,<>=!~ -]*)?$")


def option_ok(word, allowed):
    """Whether an option word is allowed, and whether it takes the next word as its value: (ok, takes_value)."""
    if word in allowed:
        return True, False
    if word + ":" in allowed:
        return True, True
    for a in allowed:
        if a.endswith("=") and word.startswith(a):
            return True, False
    m = re.match(r"^-(\d+)$", word)  # head -5
    if m and ("-n:" in allowed):
        return True, False
    if re.match(r"^-[a-zA-Z]{2,}$", word) and all(f"-{c}" in allowed for c in word[1:]):  # grep -rn: each letter an allowed flag
        return True, False
    return False, False


def path_like(word):
    return "/" in word or word.startswith((".", "~")) or os.path.exists(word)


def operands_inside(words, cwd, tree):
    """Every path-like operand resolved from cwd must be inside the tree; returns the first one that is not."""
    for w in words:
        if path_like(w):
            real = os.path.realpath(os.path.join(cwd, os.path.expanduser(w)))
            root = os.path.realpath(tree)
            if not (real == root or real.startswith(root + os.sep)):
                return w
    return None


def python_policy(words, cwd, tree):
    """python3 [-B] [-I] <script.py in the tree> [args] | python3 -m pytest|unittest [args]: never -c, never a module outside the list."""
    i, module = 0, None
    while i < len(words) and words[i].startswith("-"):
        ok, takes = option_ok(words[i], PYTHON_OPTIONS)
        if not ok:
            return f"option {words[i]} is not on the policy for python"
        if words[i] == "-m":
            module = words[i + 1] if i + 1 < len(words) else ""
            if module not in PYTHON_MODULES:
                return f"python -m {module} is not on the policy (only {', '.join(sorted(PYTHON_MODULES))})"
            i += 2
            break
        i += 1
    if module is None:
        if i >= len(words) or not words[i].endswith(".py"):
            return "python must run a .py script from the tree or -m pytest/unittest"
        if operands_inside(["./" + words[i] if "/" not in words[i] else words[i]], cwd, tree):  # a bare name resolves from cwd, still inside
            return f"the script {words[i]} is not in the tree"
        i += 1
    bad = operands_inside(words[i:], cwd, tree)
    return f"the operand {bad} is outside the tree" if bad else None


def policy(argv, cwd, tree):
    """Why argv may not run, or None when it may."""
    exe, rest = argv[0], argv[1:]
    if exe in ("echo", "printf"):
        return None
    if exe in FILE_TOOLS:
        allowed, i = FILE_TOOLS[exe], 0
        operands = []
        while i < len(rest):
            w = rest[i]
            if w.startswith("-") and w != "-":
                ok, takes = option_ok(w, allowed)
                if not ok:
                    return f"option {w} is not on the policy for {exe}"
                i += 2 if takes else 1
                continue
            operands.append(w); i += 1
        bad = operands_inside(operands, cwd, tree)
        return f"the operand {bad} is outside the tree" if bad else None
    if exe in ("python", "python3"):
        return python_policy(rest, cwd, tree)
    if exe == "uv":
        if not rest or rest[0] != "run":
            return "uv may only run"
        i = 1
        while i < len(rest) and rest[i].startswith("-"):
            ok, takes = option_ok(rest[i], UV_OPTIONS)
            if not ok:
                return f"option {rest[i]} is not on the policy for uv run"
            if takes:  # an option's value is checked like any operand: a package name, a version, a folder inside the tree
                value = rest[i + 1] if i + 1 < len(rest) else ""
                if rest[i] == "--with" and (not PACKAGE_SPEC.match(value) or "/" in value or ":" in value):
                    return f"--with {value} is not a package name"
                if rest[i] == "--python" and not re.match(r"^(?:python)?3(?:\.\d+)*$", value):
                    return f"--python {value} is not a version (a path to an interpreter is not allowed)"
                if rest[i] == "--group" and not re.match(r"^[A-Za-z0-9_-]+$", value):
                    return f"--group {value} is not a group name"
                if rest[i] == "--project" and operands_inside([value if path_like(value) else "./" + value], cwd, tree):
                    return f"--project {value} is outside the tree"
            i += 2 if takes else 1
        if i < len(rest) and rest[i] in ("python", "python3"):
            return python_policy(rest[i + 1:], cwd, tree)
        if i < len(rest) and rest[i].endswith(".py"):
            return python_policy(rest[i:], cwd, tree)
        if i < len(rest) and rest[i] in PYTHON_MODULES:
            bad = operands_inside(rest[i + 1:], cwd, tree)
            return f"the operand {bad} is outside the tree" if bad else None
        return "uv run must run python, a .py script from the tree, pytest or unittest"
    if exe == "docker":
        if rest[:1] == ["ps"] and all(w.startswith("--format") or w in ("-a",) for w in rest[1:2]) and len(rest) <= 3:
            return None
        if rest[:1] == ["compose"] and "ls" in rest and all(w in ("compose", "ls", "-p", "-a", "--format") or (i and rest[i - 1] in ("-p", "--format")) for i, w in enumerate(rest)):
            return None
        return "docker may only list (ps, compose ls)"
    if exe == "git":
        if not rest or rest[0] not in GIT_OPTIONS:
            return "git may only read (log, status, show, diff)"
        allowed, i, operands = GIT_OPTIONS[rest[0]], 1, []
        while i < len(rest):
            w = rest[i]
            if w.startswith("-") and w != "--":
                ok, takes = option_ok(w, allowed)
                if not ok:
                    return f"option {w} is not on the policy for git {rest[0]}"
                i += 2 if takes else 1
                continue
            if w != "--":
                operands.append(w)
            i += 1
        bad = operands_inside(operands, cwd, tree)
        return f"the operand {bad} is outside the tree" if bad else None
    if exe == "curl":
        if all(w in ("-s", "-S", "-f", "-sS", "-sf", "-I") or re.match(r"^https?://(?:localhost|127\.0\.0\.1)(?::\d+)?(?:/|$)", w) for w in rest):
            return None
        return "curl may only read localhost"
    return f"{exe} is not on the runner's command policy"


def reader_variables(tree):
    """The variables the documents tell a reader to set to their own paths; here they are the tree's."""
    return {"EPM": tree, "SKILLS": os.path.join(tree, "skills"), "DEMO": os.path.join(tree, "demos", "downstream-pricing-databricks-free")}


def expand(text, variables):
    """$VAR and ${VAR} from the block's own variables (unknown ones stay, so the runner can say so). "~" is not
    expanded here: a path operand is expanded where it is then confined to the tree (operands_inside, inside), and an
    operand that is only printed (echo ~) stays a tilde, so the home folder's path never reaches a result."""
    return re.sub(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?", lambda v: variables.get(v.group(1), v.group(0)), text)


def inside(tree, target):
    """The folder a block names, resolved, when it is inside the tree; None when it is not (or not a folder)."""
    real, root = os.path.realpath(target), os.path.realpath(tree)
    return real if os.path.isdir(real) and (real == root or real.startswith(root + os.sep)) else None


def git_env():
    """The environment git runs in: the shell's basics and nothing of the document or of this user's git setup."""
    import tempfile
    empty = tempfile.mkdtemp(prefix="epm-snippet-git-")
    e = {k: os.environ[k] for k in ("PATH", "LANG", "LC_ALL", "TERM") if k in os.environ}
    e.update({"HOME": empty, "XDG_CONFIG_HOME": empty, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
              "GIT_PAGER": "cat", "PAGER": "cat", "GIT_TERMINAL_PROMPT": "0"})
    return e


def minimal_env(variables, release):
    """What a command sees: the shell's basics, the block's variables, release mode; no login of this machine, and
    none of the block's variables under a name a tool reads for a program or a path (GIT_*, PYTHON*, UV_*, PATH,
    LD_*, DYLD_*, and the like), so a document cannot point git or Python at a program of its choosing."""
    e = {k: os.environ[k] for k in KEEP_ENV if k in os.environ}
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    if release:
        e["EPM_SHARE_RELEASE"] = "1"
    e.update({k: v for k, v in variables.items() if not NOT_EXPORTED.match(k)})
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
            target = inside(tree, os.path.join(tree, os.path.expanduser(expand(folder, variables))))
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
            for a in assigned:  # expanded from the block's own variables only, never this machine's environment
                variables[a.group(1)] = expand(a.group(2).strip('"'), variables)
            results.append({"line": line, "ran": True, "set": [a.group(1) for a in assigned]})
            continue
        if any(a for a in assigned):  # assignments beside a mkdir: keep the variables, run nothing
            for a in assigned:
                if a:
                    variables[a.group(1)] = expand(a.group(2).strip('"'), variables)
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
            target = inside(tree, os.path.join(cwd, os.path.expanduser(expand(line[3:].strip().strip('"'), variables))))
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
        why = policy(argv, cwd, tree) if argv else "empty"
        if why:
            results.append({"line": line, "ran": False, "reason": f"not on the runner's command policy: {why}"})
            continue
        try:
            if argv[0] == "git":
                guards = GIT_DIFF_GUARDS if argv[1:2] and argv[1] in ("diff", "log", "show") else ()
                argv = [argv[0], *GIT_ARGV_PREFIX, *argv[1:2], *guards, *argv[2:]]
            env_for = git_env() if argv[0] == "git" else minimal_env(variables, manifest.is_release(tree))
            r = procs.run(argv, timeout=900, cwd=cwd, env=env_for)
            results.append({"line": line, "ran": True, "returncode": r.returncode, "tail": (r.stdout + r.stderr)[-300:]})
        except procs.Expired:
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
                    entry.update(run_sparql(b["text"], tree, b["file"]))
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
