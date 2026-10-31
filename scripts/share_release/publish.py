#!/usr/bin/env python3
"""The zip, and the orphan branch (plan step 10).

    python3 scripts/share_release/publish.py zip --release <folder> --out <file.zip>
    python3 scripts/share_release/publish.py branch --release <folder> --repo <checkout> --name share/epm-1.0 [--push]

The zip holds the release tree and nothing else (no .git, no caches). The branch is an orphan: one commit whose
tree is the release, no shared history, so nothing in it carries author names, pull-request numbers or peer
mentions from the build. Pushing it is the owner's decision (the plan's step 10 waits for them), so --push is off
by default. Updating the branch after a change on main means running the export again and this command again.
"""
import argparse
import os
import subprocess
import zipfile


def walk(release):
    for root, dirs, files in os.walk(release):
        dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__", ".venv", ".pytest_cache", "out"))
        for f in sorted(files):
            if f.endswith((".pyc",)) or f == ".DS_Store":
                continue
            yield os.path.join(root, f)


def make_zip(release, out):
    release = os.path.abspath(release)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in walk(release):
            z.write(path, os.path.join(os.path.basename(release), os.path.relpath(path, release)))
            n += 1
    return n, os.path.getsize(out)


def make_branch(release, repo, name, push=False):
    """An orphan branch in `repo` whose single commit holds the release tree, through a temporary index and work tree:
    the checkout itself is not touched."""
    release, repo = os.path.abspath(release), os.path.abspath(repo)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_INDEX_FILE": os.path.join(repo, ".git", "share-release-index"), "GIT_WORK_TREE": release})
    git = lambda *a, **k: subprocess.run(["git", "-C", repo, *a], env=env, check=True, capture_output=True, text=True, **k)
    if os.path.exists(env["GIT_INDEX_FILE"]):
        os.remove(env["GIT_INDEX_FILE"])
    git("add", "-A", "--", ".")
    tree = git("write-tree").stdout.strip()
    commit = git("commit-tree", tree, "-m", f"{name}: the share release, generated from main by scripts/share_release",
                 stdin=subprocess.DEVNULL).stdout.strip()
    git("update-ref", f"refs/heads/{name}", commit)
    os.remove(env["GIT_INDEX_FILE"])
    if push:
        subprocess.run(["git", "-C", repo, "push", "-f", "origin", f"refs/heads/{name}:refs/heads/{name}"], check=True)
    return commit


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("zip"); p.add_argument("--release", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("branch"); p.add_argument("--release", required=True); p.add_argument("--repo", required=True)
    p.add_argument("--name", default="share/epm-1.0"); p.add_argument("--push", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "zip":
        n, size = make_zip(a.release, a.out)
        print(f"{a.out}: {n} files, {size / 1e6:.1f} MB")
    else:
        print(f"{a.name} -> {make_branch(a.release, a.repo, a.name, a.push)}")


if __name__ == "__main__":
    main()
