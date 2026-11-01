#!/usr/bin/env python3
"""The zip, and the orphan branch (plan step 10).

    python3 scripts/share_release/publish.py zip --release <folder> --out <file.zip>
    python3 scripts/share_release/publish.py branch --zip <file.zip> --repo <checkout> --name share/epm-1.0 [--push]
    python3 scripts/share_release/publish.py extract --zip <file.zip> --into <folder>

The zip holds the release tree and nothing else (no .git, no caches, no virtual environment; a symlink stops it),
under the fixed root folder "epm-release", never the output folder's own name. The branch is an orphan built from
the zip itself (unpacked to a temporary folder), so it holds exactly the files the gate and the clean room
checked: one commit, no shared history, with a neutral author and committer ("EPM release", a no-reply address),
so nothing in it carries a person's name, pull-request numbers or peer mentions from the build. Pushing it is
the owner's decision (the plan's step 10 waits for them), so --push is off by default. Updating the branch after
a change on main means running the export again and this command again.

`extract` unpacks a zip keeping each file's mode: Python's ZipFile.extractall does not restore Unix permissions
(CPython issue 59999, "Zipfile.extractall does not preserve file permissions", open since 2012-08-27, read
2026-10-31; test_publish.py measures it on the Python the clean room uses, 3.12), while the mode is recorded in
ZipInfo.external_attr ("External file attributes", the zipfile documentation for Python 3.12,
https://docs.python.org/3.12/library/zipfile.html#zipfile.ZipInfo.external_attr, read 2026-10-31).
"""
import argparse
import os
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = (".git", "__pycache__", ".venv", ".pytest_cache", "out")
SKIP_FILES = (".DS_Store",)
ROOT = "epm-release"  # the folder every zip entry sits under
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
    """Every file the release ships, in a fixed order: the zip and the branch hold exactly these. A symlink is refused:
    the zip would copy its target's bytes and the branch would record a link, and the target may be any file of
    this machine."""
    for root, dirs, files in os.walk(release):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for d in dirs:
            if os.path.islink(os.path.join(root, d)):
                raise SystemExit(f"{os.path.join(root, d)} is a symlink; the release holds files only")
        for f in sorted(files):
            if f.endswith((".pyc",)) or f in SKIP_FILES:
                continue
            path = os.path.join(root, f)
            if os.path.islink(path):
                raise SystemExit(f"{path} is a symlink; the release holds files only")
            yield path


def make_zip(release, out):
    release = os.path.abspath(release)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in walk(release):
            z.write(path, os.path.join(ROOT, os.path.relpath(path, release)))
            n += 1
    return n, os.path.getsize(out)


def extract(zip_path, into):
    """Unpack a zip, restoring each file's mode from the archive (a recipient's ./run_local.sh must still run)."""
    import procs
    r = procs.run(["python3", "-c", EXTRACT_CODE, zip_path, into], timeout=600)
    if r.returncode:
        raise SystemExit(f"extracting {zip_path} failed: {r.stderr[-300:]}")


def guarded_update_ref(git, name, commit, expected):
    """Point refs/heads/<name> at commit only if it still is what was read (expected; "" when it did not exist): a
    second publisher racing on the same name loses with an error instead of both appearing to win."""
    git("update-ref", f"refs/heads/{name}", commit, expected or "0" * 40)


def make_branch(zip_path, repo, name, push=False):
    """An orphan branch in `repo` whose single commit holds the zip's tree, through a temporary extraction, a per-call
    temporary index and work tree: the checkout itself is not touched, nothing but the checked zip reaches the
    branch, and two publications at once cannot share an index or silently overwrite each other's ref."""
    import procs
    zip_path, repo = os.path.abspath(zip_path), os.path.abspath(repo)
    with tempfile.TemporaryDirectory() as tmp:
        extract(zip_path, tmp)
        roots = os.listdir(tmp)
        if len(roots) != 1:
            raise SystemExit(f"{zip_path} must hold one root folder, not {roots}")
        tree_dir = os.path.join(tmp, roots[0])
        index = tempfile.NamedTemporaryFile(prefix="share-release-index-", dir=os.path.join(repo, ".git"), delete=False)
        index.close(); os.remove(index.name)  # a fresh name of this call's own; git creates it
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update({"GIT_INDEX_FILE": index.name, "GIT_WORK_TREE": tree_dir, **IDENTITY})

        def git(*a, **k):
            r = procs.run(["git", "-C", repo, *a], timeout=600, env=env, **k)
            if r.returncode:
                raise subprocess.CalledProcessError(r.returncode, ["git", *a], r.stdout, r.stderr)
            return r
        try:
            expected = procs.run(["git", "-C", repo, "rev-parse", "-q", "--verify", f"refs/heads/{name}"], timeout=600, env=env).stdout.strip()
            listing = "".join(os.path.relpath(p, tree_dir) + "\0" for p in walk(tree_dir))
            git("update-index", "--add", "-z", "--stdin", input=listing)
            tree = git("write-tree").stdout.strip()
            commit = git("commit-tree", tree, "-m", f"{name}: the share release, generated from main by scripts/share_release",
                         input="").stdout.strip()
            guarded_update_ref(git, name, commit, expected)
        finally:
            if os.path.exists(index.name):
                os.remove(index.name)
    if push:
        r = procs.run(["git", "-C", repo, "push", "-f", "origin", f"refs/heads/{name}:refs/heads/{name}"], timeout=1800)
        if r.returncode:
            raise SystemExit(f"push failed: {r.stderr[-300:]}")
    return commit


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("zip"); p.add_argument("--release", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("branch"); p.add_argument("--zip", required=True, help="the zip the gate and the clean room checked"); p.add_argument("--repo", required=True)
    p.add_argument("--name", default="share/epm-1.0"); p.add_argument("--push", action="store_true")
    p = sub.add_parser("extract"); p.add_argument("--zip", required=True); p.add_argument("--into", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "zip":
        n, size = make_zip(a.release, a.out)
        print(f"{a.out}: {n} files, {size / 1e6:.1f} MB")
    elif a.cmd == "branch":
        print(f"{a.name} -> {make_branch(a.zip, a.repo, a.name, a.push)}")
    else:
        extract(a.zip, a.into)
        print(f"extracted {a.zip} into {a.into}")


if __name__ == "__main__":
    main()
