#!/usr/bin/env python3
"""Build the share release from this repository's tree and the skills repository's tree.

    python3 scripts/share_release/export.py --epm <path to main> --skills <path to skills main> --out <folder>

Steps: copy the allowlist (manifest.py), apply the rewrite rules (rules.py) to every text file, write
`<out>-report.json` beside the output with every rule's count per file and every path's source,
so a difference between main and the release is traceable to a rule. The rebuild of packages, pages and
hashes (rebuild.py) and the leak gate (gate.py) run after this. Nothing here reads Git: the trees are
plain folders, so a zip of main would do.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifest  # noqa: E402
import owner  # noqa: E402
import procs  # noqa: E402
import rules  # noqa: E402

TEXT_EXT = {".md", ".html", ".ttl", ".jsonld", ".json", ".csv", ".py", ".rq", ".sql", ".sh", ".yml", ".yaml",
            ".txt", ".nt", ".toml", ".example", ".cypher", ".jsonl", ".css", ".svg", ".gitignore", ".cfg", ".ini"}
TEXT_NAMES = {".python-version", ".gitignore", ".env.example", "pre-push", "VERIFY.txt"}


def tracked(tree):
    """Every file under the tree, repository-relative, as git lists it when the tree is a checkout, else a walk."""
    if os.path.exists(os.path.join(tree, ".git")):  # a folder, or a file in a git worktree: tracked files only
        r = procs.run(["git", "-C", tree, "ls-files", "-z"], timeout=600, text=False)
        if r.returncode:
            raise SystemExit(f"git ls-files failed in {tree}: {r.stderr.decode('utf-8', 'replace')[-300:]}")
        out = r.stdout
        return sorted(p for p in out.decode().split("\0") if p)
    paths = []
    for root, dirs, files in os.walk(tree):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "node_modules")]
        for f in files:
            paths.append(os.path.relpath(os.path.join(root, f), tree))
    return sorted(paths)


OFFICE_EXT = {".xlsx", ".docx", ".pptx"}


def rewrite_office(src, dest, dest_rel, dates):
    """An Office file is a zip of XML parts: each text part takes the same rules, the rest is copied as is."""
    import zipfile
    counts = {}
    if not zipfile.is_zipfile(src):
        shutil.copy2(src, dest)
        return None
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.endswith((".xml", ".rels", ".txt")):
                new, c = rules.apply(data.decode("utf-8", "surrogateescape"), dest_rel + "/" + info.filename, dates)
                data = new.encode("utf-8", "surrogateescape")
                for k, v in c.items():
                    counts[k] = counts.get(k, 0) + v
            zout.writestr(info, data)
    shutil.copymode(src, dest)  # the file's mode travels with it, as for every other kind of file
    return counts


def is_text(path):
    base = os.path.basename(path)
    return os.path.splitext(path)[1].lower() in TEXT_EXT or base in TEXT_NAMES


def record_dates(epm):
    """EPM-DEC-001-NNNN -> its Date row, read from the records on main (which do not ship)."""
    folder = os.path.join(epm, "business_architecture", "domain", "decisions")
    dates = {}
    if not os.path.isdir(folder):
        return dates
    for name in os.listdir(folder):
        m = re.match(r"(EPM-DEC-001-\d{4})", name)
        if not m or not name.endswith(".md"):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            text = f.read()
        d = re.search(r"^\| Date \| (\d{4}-\d{2}-\d{2})", text, re.M)
        dates[m.group(1)] = d.group(1) if d else "an earlier date"
    return dates


def export(epm, skills, out, remove_internal=False):
    if os.path.exists(out):
        raise SystemExit(f"{out} exists; export writes a fresh folder")
    owner.owner_names()  # fail closed before anything is written: a release cut without the names would leak them
    dates = record_dates(epm)
    report = {"epm": os.path.abspath(epm), "skills": os.path.abspath(skills), "files": {}, "rule_totals": {},
              "remove_internal": remove_internal}
    sources = [("epm", epm, manifest.EPM_RULES)]
    if skills:
        sources.append(("skills", skills, manifest.SKILLS_RULES))
    for source, tree, rulz in sources:
        for path in manifest.shipped(tracked(tree), rulz):
            if remove_internal and "reference/internal/" in path:
                report["files"][path] = {"source": source, "out": "removed: internal"}
                continue
            dest_rel = manifest.release_path(path, source)
            dest = os.path.join(out, dest_rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            src = os.path.join(tree, path)
            # A link would put whatever it points at into the release as an ordinary file, and neither repository has one.
            if os.path.realpath(src) != os.path.join(os.path.realpath(tree), path):
                raise SystemExit(f"{path} is a link or sits behind one; the release ships no links")
            entry = {"source": source, "release_path": dest_rel}
            if is_text(path):
                with open(src, encoding="utf-8", errors="surrogateescape") as f:
                    text = f.read()
                new, counts = rules.apply(text, dest_rel, dates)
                with open(dest, "w", encoding="utf-8", errors="surrogateescape") as f:
                    f.write(new)
                shutil.copymode(src, dest)
                entry["rules"] = counts
                for k, v in counts.items():
                    report["rule_totals"][k] = report["rule_totals"].get(k, 0) + v
            elif os.path.splitext(path)[1].lower() in OFFICE_EXT:
                counts = rewrite_office(src, dest, dest_rel, dates)
                if counts is None:
                    entry["binary"] = True
                else:
                    entry["rules"] = counts
                    for k, v in counts.items():
                        report["rule_totals"][k] = report["rule_totals"].get(k, 0) + v
            else:
                shutil.copy2(src, dest)
                entry["binary"] = True
            with open(dest, "rb") as f:
                entry["sha256"] = hashlib.sha256(f.read()).hexdigest()
            report["files"][path] = entry
    # The report sits beside the release, never inside it: it names the source trees and the original paths.
    report["epm"] = os.path.basename(os.path.abspath(epm)); report["skills"] = os.path.basename(os.path.abspath(skills)) if skills else ""
    with open(os.path.abspath(out).rstrip("/") + "-report.json", "w") as f:
        json.dump(report, f, indent=1, sort_keys=True)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--epm", required=True)
    ap.add_argument("--skills", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--remove-internal", action="store_true",
                    help="leave out reference/internal/ (off by default; the review report comes first)")
    a = ap.parse_args(argv)
    r = export(a.epm, a.skills, a.out, a.remove_internal)
    n = len(r["files"])
    print(f"exported {n} files to {a.out}; rules applied: {json.dumps(r['rule_totals'], sort_keys=True)}")


if __name__ == "__main__":
    main()
