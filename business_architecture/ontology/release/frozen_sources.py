"""The process map at the commits the core builders read, as frozen files, so a tree without Git history
(the share release, a zip of main) rebuilds the same packages byte for byte.

    python3 frozen_sources.py --freeze [--repo <checkout with history>]   # write release/frozen/<commit>-downstream_process_map.json for every pinned commit
    python3 frozen_sources.py --list       # the pinned commits

A builder asks `read(commit, path)`: the frozen file when it exists, else `git show commit:path`. On
main the frozen folder is empty, so the builders read Git as before; the share release's export runs
--freeze before it copies this folder.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FROZEN = os.path.join(HERE, "frozen")


def package_dir(ontology, module, version):
    """A released package's folder: releases/<module>/<version>/, or the share release's history folder
    releases/previous/<module>/<version>/ when the package moved there (EPM-DEC-001-0110)."""
    plain = os.path.join(ontology, "releases", module, version)
    previous = os.path.join(ontology, "releases", "previous", module, version)
    return previous if not os.path.isdir(plain) and os.path.isdir(previous) else plain


def frozen_path(commit, path):
    return os.path.join(FROZEN, f"{commit[:12]}-{os.path.basename(path)}")


def read(commit, path, repo=REPO):
    """The bytes of `path` at `commit`: the frozen copy if there is one, else from Git."""
    frozen = frozen_path(commit, path)
    if os.path.exists(frozen):
        with open(frozen, "rb") as f:
            return f.read()
    return subprocess.run(["git", "-C", repo, "show", f"{commit}:{path}"], check=True, capture_output=True,
                          stdin=subprocess.DEVNULL).stdout


def is_frozen(commit, path):
    return os.path.exists(frozen_path(commit, path))


def pinned():
    """(commit, path) for every commit a core builder names."""
    sys.path.insert(0, HERE)
    import build_core_2_2 as b22
    import build_core_2_3 as b23
    import build_core_2_4 as b24
    import build_core_next as b20
    seen = []
    for mod in (b20, b22, b23, b24):
        for name in ("EARLIER_COMMIT", "SOURCE_COMMIT"):
            commit = getattr(mod, name, None)
            if commit and (commit, mod.SOURCE_PATH) not in seen:
                seen.append((commit, mod.SOURCE_PATH))
    return seen


def freeze(repo=REPO):
    os.makedirs(FROZEN, exist_ok=True)
    written = []
    for commit, path in pinned():
        data = subprocess.run(["git", "-C", repo, "show", f"{commit}:{path}"], check=True, capture_output=True,
                              stdin=subprocess.DEVNULL).stdout
        with open(frozen_path(commit, path), "wb") as f:
            f.write(data)
        written.append(frozen_path(commit, path))
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--repo", default=REPO, help="the checkout whose Git holds the pinned commits (default: this one)")
    a = ap.parse_args()
    if a.list or not a.freeze:
        for commit, path in pinned():
            print(commit, path, "frozen" if is_frozen(commit, path) else "git")
    if a.freeze:
        for p in freeze(a.repo):
            print("wrote", os.path.relpath(p, HERE))


if __name__ == "__main__":
    main()
