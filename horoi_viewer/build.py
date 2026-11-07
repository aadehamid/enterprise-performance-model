"""Build offline reference pages without changing the released ontology."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
sys.path.insert(0, str(HERE / "vendor"))
from horoi.page import TEMPLATE, DARK_CSS  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "epm_viewer_reader", HERE.parent / "business_architecture/ontology/viewer/build.py"
)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.check_output(["git", "-C", str(root), *args], env=env)


def verify_source(root):
    """Bind both identity and bytes; untracked inputs must not enter the build."""
    root = Path(root).resolve()
    head = git(root, "rev-parse", "HEAD").decode().strip()
    if head != CONFIG["source_commit"]:
        raise ValueError(f"Expected release {CONFIG['source_commit']}; got {head}")
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("The source release must be a clean checkout")
    for entry in git(root, "ls-tree", "-rz", "HEAD").split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        path = root / os.fsdecode(name)
        if kind != b"blob" or mode not in (b"100644", b"100755") or path.is_symlink():
            raise ValueError("The source release must contain regular files only")
        content = path.read_bytes()
        actual = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest().encode()
        if actual != oid or bool(path.stat().st_mode & 0o100) != (mode == b"100755"):
            raise ValueError(f"Source bytes or executable mode differ from the pinned commit: {name!r}")
    return root


def payload(root):
    """Use the existing reader's file-scoped blank nodes and package hash checks."""
    data = reader.build_data(root)
    data["sourceCommit"] = CONFIG["source_commit"]
    data["pilotModules"] = CONFIG["modules"]
    data["horoiCommit"] = CONFIG["horoi_commit"]
    data["supportingKinds"] = list(data["supportingKinds"])
    # Context nodes let the reference name every relationship endpoint, including
    # supporting nodes. Only the selected modules have term-browser entry points.
    by_id = {n["id"]: n for n in data["nodes"]}
    for module in CONFIG["modules"]:
        if not any(any(m["name"] == module for m in n["modules"]) for n in data["nodes"]):
            raise ValueError(f"Missing pilot module: {module}")
    data["moduleInfo"] = []
    manifests = {module: path.parent / "manifest.json"
                 for path, module, _ in reader.release_files(root) if module}
    tracked = {os.fsdecode(p) for p in git(root, "ls-files", "-z").split(b"\0") if p}
    used = [entry["path"] for entry in data["inputs"]]
    used += [str(path.relative_to(root)) for path in manifests.values()]
    if any(p not in tracked for p in used):
        raise ValueError("Every documentation input must be tracked in the pinned release")
    for module, path in sorted(manifests.items()):
        manifest = json.loads(path.read_text())
        node = by_id[manifest["ontology_iri"]]
        data["moduleInfo"].append({"name": module, "version": manifest["version"],
            "id": node["id"], "label": node["label"],
            "description": next((v["v"] for v in node["values"] if v["p"] == str(reader.DCTERMS.description)), ""),
            "requires": [v["v"] for v in node["values"] if v["p"] == str(reader.DCTERMS.requires)]})
    data["pilotTerms"] = [n["id"] for n in data["nodes"]
        if n["kind"] not in (*reader.SUPPORTING_KINDS, "Metadata")
        and any(m["name"] in CONFIG["modules"] for m in n["modules"])]
    assert all(i in by_id for i in data["pilotTerms"])
    return data


def script_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("&", "\\u0026")


def build(source, out):
    source = verify_source(source)
    out = Path(out).resolve()
    if out == source or source in out.parents:
        raise ValueError("Build output must be outside the source release")
    if out.exists() and any(out.iterdir()):
        raise ValueError("Choose a new or empty output folder; existing files are never replaced")
    data = payload(source)
    css = TEMPLATE.split("<style>", 1)[1].split("</style>", 1)[0]
    css = css.replace("{dark}", DARK_CSS).replace("{svg_light}", "").replace("{svg_dark}", "")
    css = css.replace("{{", "{").replace("}}", "}")
    page = (HERE / "page.html").read_text()
    page = page.replace("<!-- HOROI_CSS -->", css + "\n" + (HERE / "style.css").read_text())
    page = page.replace("<!-- DATA -->", script_json(data))
    page = page.replace("<!-- APP -->", (HERE / "app.js").read_text())
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    (out / "LICENSE.txt").write_bytes((HERE / "vendor/LICENSE").read_bytes())
    (out / "NOTICE.txt").write_bytes((HERE / "NOTICE.txt").read_bytes())
    report = {"source_commit": CONFIG["source_commit"], "horoi_commit": CONFIG["horoi_commit"],
        "modules": CONFIG["modules"], "inputs": data["inputs"],
        "pilot_terms": len(data["pilotTerms"]), "triples_available": data["triples"],
        "index_sha256": hashlib.sha256((out / "index.html").read_bytes()).hexdigest()}
    (out / "build.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    print(json.dumps(build(args.source, args.out), indent=2))


if __name__ == "__main__":
    main()
