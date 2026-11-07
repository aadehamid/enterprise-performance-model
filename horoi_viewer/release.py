"""Stage and verify an additive documentation release. Never reloads stores."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

from horoi_viewer import build as builder

DOC_FILES = {"index.html", "LICENSE.txt", "NOTICE.txt", "build.json"}


def fingerprint(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "executable": bool(path.stat().st_mode & stat.S_IXUSR),
            "mode": stat.S_IMODE(path.stat().st_mode)}


def tracked_files(source):
    return [Path(os.fsdecode(p)) for p in builder.git(source, "ls-files", "-z").split(b"\0") if p]


def verify(source, release):
    source = builder.verify_source(source)
    release = Path(release).resolve()
    if release == source:
        raise ValueError("The staged release must be separate from its source")
    baseline = {p.as_posix(): fingerprint(source / p) for p in tracked_files(source)}
    current = {}
    for root, dirs, files in os.walk(release):
        if any((Path(root) / d).is_symlink() for d in dirs):
            raise ValueError("Release directories must not be symlinks")
        for name in files:
            path = Path(root) / name
            current[path.relative_to(release).as_posix()] = fingerprint(path)
    if any(current.get(p) != state for p, state in baseline.items()):
        raise ValueError("A pre-existing release file was changed, removed, or had its permissions changed")
    expected = {"horoi_viewer/" + name for name in DOC_FILES}
    if set(current) - set(baseline) != expected:
        raise ValueError("The release must add only the documented Horoi output files")
    report = json.loads((release / "horoi_viewer/build.json").read_text())
    index = release / "horoi_viewer/index.html"
    if report["source_commit"] != builder.CONFIG["source_commit"]:
        raise ValueError("Documentation names a different source release")
    if report["index_sha256"] != fingerprint(index)["sha256"]:
        raise ValueError("Documentation HTML differs from its build record")
    # Check the embedded semantic data independently of the recorded HTML hash.
    marker = '<script id="ontology-data" type="application/json">'
    embedded = json.loads(index.read_text().split(marker, 1)[1].split("</script>", 1)[0])
    expected_data = builder.payload(source)
    if embedded != expected_data or report["inputs"] != expected_data["inputs"]:
        raise ValueError("Documentation data differs from the verified release")
    for name, content in builder.render_files(expected_data).items():
        path = "horoi_viewer/" + name
        if current[path] != {"sha256": hashlib.sha256(content).hexdigest(), "executable": False, "mode": 0o644}:
            raise ValueError(f"The generated documentation differs from the current builder: {path}")
    return {"source_commit": builder.CONFIG["source_commit"],
            "unchanged_files": len(baseline), "added_files": sorted(expected),
            "baseline": baseline, "added": {p: current[p] for p in sorted(expected)}}


def stage(source, docs, output):
    source = builder.verify_source(source)
    docs, output = Path(docs).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Choose a new staging folder; existing folders are never replaced")
    if source == output or source in output.parents or docs == output or docs in output.parents:
        raise ValueError("Stage outside the source and generated documentation")
    if (source / "horoi_viewer").exists():
        raise ValueError("The source already contains horoi_viewer; this operation only adds it")
    if {p.name for p in docs.iterdir()} != DOC_FILES:
        raise ValueError("Unexpected or missing documentation output")
    output.mkdir(parents=True)
    for relative in tracked_files(source):
        fingerprint(source / relative)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
    for name in sorted(DOC_FILES):
        fingerprint(docs / name)
    shutil.copytree(docs, output / "horoi_viewer")
    return verify(source, output)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["stage", "verify"])
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--docs", type=Path)
    ap.add_argument("--report", required=True, type=Path, help="Audit report outside the release folder")
    args = ap.parse_args()
    protected = [args.source.resolve(), args.out.resolve()]
    if args.docs:
        protected.append(args.docs.resolve())
    report_path = args.report.resolve()
    if any(report_path == root or root in report_path.parents for root in protected):
        ap.error("Write the audit report outside the source, documentation and staged release")
    if args.report.exists() or args.report.is_symlink():
        ap.error("Choose a new audit report path; existing files are never replaced")
    if not args.report.parent.is_dir():
        ap.error("Choose an audit report path with an existing parent directory")
    if args.command == "stage" and not args.docs:
        ap.error("stage requires --docs")
    result = stage(args.source, args.docs, args.out) if args.command == "stage" else verify(args.source, args.out)
    with args.report.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(f"Verified {result['unchanged_files']} unchanged files; added only horoi_viewer documentation")


if __name__ == "__main__":
    main()
