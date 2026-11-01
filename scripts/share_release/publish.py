#!/usr/bin/env python3
"""The zip, and the orphan branch (plan step 10).

    python3 scripts/share_release/publish.py zip --release <folder> --out <file.zip>
    python3 scripts/share_release/publish.py branch --release <folder> --repo <checkout> --name share/epm-1.0 [--push]
    python3 scripts/share_release/publish.py extract --zip <file.zip> --into <folder>

The zip holds the release tree and nothing else (no .git, no caches, no virtual environment). The branch is an
orphan: one commit whose tree is exactly the zip's file set, no shared history, with a neutral author and
committer ("EPM release", a no-reply address), so nothing in it carries a person's name, pull-request numbers
or peer mentions from the build. Pushing it is the owner's decision (the plan's step 10 waits for them), so
--push is off by default. Updating the branch after a change on main means running the export again and this
command again. `extract` unpacks a zip keeping each file's mode (Python's extractall drops the executable bit).
"""
import argparse
import os
import subprocess
import zipfile

SKIP_DIRS = (".git", "__pycache__", ".venv", ".pytest_cache", "out")
SKIP_FILES = (".DS_Store",)
# The orphan commit's identity: a role, not a person.
IDENTITY = {"GIT_AUTHOR_NAME": "EPM release", "GIT_AUTHOR_EMAIL": "epm-release@noreply.invalid",
            "GIT_COMMITTER_NAME": "EPM release", "GIT_COMMITTER_EMAIL": "epm-release@noreply.invalid"}
# The extraction that keeps modes, as one snippet so the clean room (a container without this tool) can run the same code.
EXTRACT_CODE = ("import sys, zipfile, os\n"
                "with zipfile.ZipFile(sys.argv[1]) as z:\n"
                "    for info in z.infolist():\n"
                "        path = z.extract(info, sys.argv[2])\n"
                "        mode = (info.external_attr >> 16) & 0o7777\n"
                "        if mode and not info.is_dir():\n"
                "            os.chmod(path, mode)\n")


def walk(release):
    """Every file the release ships, in a fixed order: the zip and the branch hold exactly these."""
    for root, dirs, files in os.walk(release):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            if f.endswith((".pyc",)) or f in SKIP_FILES:
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


def extract(zip_path, into):
    """Unpack a zip, restoring each file's mode from the archive (a recipient's ./run_local.sh must still run)."""
    subprocess.run(["python3", "-c", EXTRACT_CODE, zip_path, into], check=True, timeout=600)


def make_branch(release, repo, name, push=False):
    """An orphan branch in `repo` whose single commit holds the release tree, through a temporary index and work tree:
    the checkout itself is not touched. The index is built from walk()'s file list, never from `git add -A`, so a
    cache or virtual environment left in the release folder cannot reach the branch."""
    release, repo = os.path.abspath(release), os.path.abspath(repo)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_INDEX_FILE": os.path.join(repo, ".git", "share-release-index"), "GIT_WORK_TREE": release, **IDENTITY})
    git = lambda *a, **k: subprocess.run(["git", "-C", repo, *a], env=env, check=True, capture_output=True, text=True, timeout=600, **k)
    if os.path.exists(env["GIT_INDEX_FILE"]):
        os.remove(env["GIT_INDEX_FILE"])
    listing = "".join(os.path.relpath(p, release) + "\0" for p in walk(release))
    git("update-index", "--add", "-z", "--stdin", input=listing)
    tree = git("write-tree").stdout.strip()
    commit = git("commit-tree", tree, "-m", f"{name}: the share release, generated from main by scripts/share_release",
                 input="").stdout.strip()
    git("update-ref", f"refs/heads/{name}", commit)
    os.remove(env["GIT_INDEX_FILE"])
    if push:
        subprocess.run(["git", "-C", repo, "push", "-f", "origin", f"refs/heads/{name}:refs/heads/{name}"], check=True, timeout=1800)
    return commit


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("zip"); p.add_argument("--release", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("branch"); p.add_argument("--release", required=True); p.add_argument("--repo", required=True)
    p.add_argument("--name", default="share/epm-1.0"); p.add_argument("--push", action="store_true")
    p = sub.add_parser("extract"); p.add_argument("--zip", required=True); p.add_argument("--into", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "zip":
        n, size = make_zip(a.release, a.out)
        print(f"{a.out}: {n} files, {size / 1e6:.1f} MB")
    elif a.cmd == "branch":
        print(f"{a.name} -> {make_branch(a.release, a.repo, a.name, a.push)}")
    else:
        extract(a.zip, a.into)
        print(f"extracted {a.zip} into {a.into}")


if __name__ == "__main__":
    main()
