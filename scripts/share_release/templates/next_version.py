#!/usr/bin/env python3
"""The repetitive parts of a new version, so a change that reaches many modules is not many hand edits.

    python3 next_version.py start <module> <new version> <patch|minor|major> --why "<one sentence>" \
        --approver "<who>" --where "<where the approval is recorded>" --words "<the sentence that approved it>" [--date YYYY-MM-DD]
    python3 build_module.py <module> --write
    python3 next_version.py finish <module> <old version>
    python3 next_version.py current <module>

`start` sets the entry in build_module.py's MODULES (version, issued, approver, approval) and adds a section at the top of
the module's CHANGELOG.md, carrying forward its open gaps. `finish` moves the old package to releases/previous/ and
changes the version in projection/pipeline.py and projection/skill-run/epm-config.json. `current` prints the version the entry holds. You may do any of this by hand.
"""
import argparse
import datetime
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)


def set_entry(text, module, version, date, approver, where, words):
    """build_module.py's text with one module's entry changed. It adds `approver` when the entry has none."""
    start = text.find(f'    "{module}": {{\n')
    if start < 0:
        raise SystemExit(f"{module} has no entry in MODULES")
    end = text.index("\n    },\n", start)
    entry = text[start:end]
    entry, n = re.subn(r'"version": "[^"]+"', f'"version": "{version}"', entry, count=1)
    if not n:
        raise SystemExit(f"{module}'s entry has no version")
    fields = re.search(r'^( *)"version": .*$', entry, re.M)
    line = re.sub(r'\s*"(?:issued|approver)": "[^"]*",?', "", fields.group(0)).rstrip(" ,") + ","
    entry = entry.replace(fields.group(0), line, 1)
    entry = re.sub(r'^ *"(?:approver|issued)": "[^"]*",\n', "", entry, flags=re.M)
    entry = re.sub(r'^ *"approval": \((?:[^()]|\([^()]*\))*\),\n', "", entry, flags=re.M)
    pad = fields.group(1)
    added = (f'{line}\n{pad}"approver": {quoted(approver)}, "issued": "{date}",\n'
             f'{pad}"approval": ({quoted(where)}, {quoted(words)}),')
    return text[:start] + entry.replace(line, added, 1) + text[end:]


def quoted(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def open_gaps(changelog):
    """The Known gaps of the newest section, or "None."."""
    m = re.search(r"^### Known gaps\n+(.*?)(?=^## |^### |\Z)", changelog, re.M | re.S)
    return m.group(1).strip() if m else "None."


def add_section(changelog, version, date, kind, why, module):
    """The changelog with a new section under its title line, the open gaps carried forward."""
    title, rest = (changelog.split("\n", 1) + [""])[:2] if changelog.startswith("# ") else (f"# {module} changelog", changelog)
    section = (f"## {version} ({date})\n\nA {kind} release. {why}\n\n- [{kind}] {why}\n\n"
               f"### Known gaps\n\n{open_gaps(changelog)}\n\n")
    return f"{title}\n\n{section}{rest.lstrip()}"


def set_lists(pipeline, config, module, old, new):
    """The two lists of versions with one module's version changed."""
    a, n = re.subn(rf'\("{re.escape(module)}", "{re.escape(old)}"\)', f'("{module}", "{new}")', pipeline)
    b, k = re.subn(rf'"{re.escape(module)}": "{re.escape(old)}"', f'"{module}": "{new}"', config)
    if not n or not k:
        raise SystemExit(f"{module} {old} is not in the projection's lists: pipeline.py {n}, epm-config.json {k}")
    return a, b


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def start(a, ontology=ONTOLOGY):
    path = os.path.join(ontology, "release", "build_module.py")
    write(path, set_entry(read(path), a.module, a.version, a.date, a.approver, a.where, a.words))
    log = os.path.join(ontology, "releases", a.module, "CHANGELOG.md")
    write(log, add_section(read(log) if os.path.exists(log) else "", a.version, a.date, a.kind, a.why, a.module))
    print(f"{a.module} is set to {a.version}. Now run: python3 build_module.py {a.module} --write")


def finish(a, ontology=ONTOLOGY):
    newest = [v for v in os.listdir(os.path.join(ontology, "releases", a.module)) if re.match(r"^\d+\.\d+\.\d+$", v)]
    new = max(newest, key=lambda v: tuple(int(x) for x in v.split(".")))
    if new == a.old:
        raise SystemExit(f"{a.module} {a.old} is still the newest package: write the new one first")
    folder = os.path.join(ontology, "releases", "previous", a.module)
    source, target = os.path.join(ontology, "releases", a.module, a.old), os.path.join(folder, a.old)
    pipeline, config = (os.path.join(ontology, "projection", "pipeline.py"),
                        os.path.join(ontology, "projection", "skill-run", "epm-config.json"))
    # Everything that can stop this is checked before anything changes.
    p, c = set_lists(read(pipeline), read(config), a.module, a.old, new)
    if not os.path.isdir(source) or os.path.exists(target):
        raise SystemExit(f"cannot move {source} to {target}: the source is missing or the target exists")
    # A failed write (a full disk) stops here with nothing changed; the two replaces are renames in one folder.
    write(pipeline + ".new", p)
    write(config + ".new", c)
    os.makedirs(folder, exist_ok=True)
    shutil.move(source, target)
    os.replace(pipeline + ".new", pipeline)
    os.replace(config + ".new", config)
    print(f"{a.module} {a.old} moved to releases/previous/; the projection's lists name {new}")


def current(a, ontology=ONTOLOGY):
    text = read(os.path.join(ontology, "release", "build_module.py"))
    start_at = text.find(f'    "{a.module}": {{\n')
    if start_at < 0:
        raise SystemExit(f"{a.module} has no entry in MODULES")
    found = re.search(r'"version": "([^"]+)"', text[start_at:text.index("\n    },\n", start_at)])
    if not found:
        raise SystemExit(f"{a.module}'s entry has no version")
    print(found.group(1))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("module"); s.add_argument("version"); s.add_argument("kind", choices=("patch", "minor", "major"))
    s.add_argument("--why", required=True); s.add_argument("--approver", required=True)
    s.add_argument("--where", required=True); s.add_argument("--words", required=True)
    s.add_argument("--date", default=datetime.date.today().isoformat())
    f = sub.add_parser("finish")
    f.add_argument("module"); f.add_argument("old")
    c = sub.add_parser("current")
    c.add_argument("module")
    a = ap.parse_args(argv)
    {"start": start, "finish": finish, "current": current}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
