#!/usr/bin/env python3
"""Run the release's check.sh from a real Git clone of it, as a recipient would (the first trial's lesson: a test that
reads Git passed without .git and failed with it). The cut's check step runs the plain folder; this runs the clone.

    python3 scripts/share_release/clonecheck.py --release <folder> --log <file> [--timeout <seconds>]

It copies the tree to a temporary folder, commits it there with a neutral author, clones that, and runs
`bash scripts/check.sh` in the clone. The release folder is not touched, and the temporary folders are removed.
"""
import argparse
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import procs  # noqa: E402

NEUTRAL = {"GIT_AUTHOR_NAME": "release", "GIT_AUTHOR_EMAIL": "release@example.invalid",
           "GIT_COMMITTER_NAME": "release", "GIT_COMMITTER_EMAIL": "release@example.invalid"}
SKIP = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".venv")


def clean_env():
    """The environment without any GIT_ variable a caller set: this works on its own repository only."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git(args, cwd, timeout=600):
    r = procs.run(["git", *args], timeout=timeout, cwd=cwd, env={**clean_env(), **NEUTRAL})
    if r.returncode:
        raise SystemExit(f"git {args[0]} failed: {(r.stdout + r.stderr)[-400:]}")


def run(release, log, timeout=7200):
    """The exit code of check.sh in a clone of the release."""
    with tempfile.TemporaryDirectory(prefix="release-clone-") as tmp:
        source, clone = os.path.join(tmp, "source"), os.path.join(tmp, "clone")
        shutil.copytree(release, source, ignore=SKIP, symlinks=True)
        git(["init", "-q", "-b", "main"], source)
        git(["add", "-A"], source)
        git(["commit", "-q", "-m", "The release"], source)
        git(["clone", "-q", source, clone], tmp)
        env = {k: v for k, v in clean_env().items() if k != "EPM_SHARE_RELEASE"}  # a recipient has no such variable set
        try:
            r = procs.run(["bash", "scripts/check.sh"], timeout=timeout, cwd=clone, env=env)
            code, text = r.returncode, r.stdout + r.stderr
        except procs.Expired as exc:
            code, text = 124, f"timed out after {timeout} s: {exc.partial[-2000:]}"
    with open(log, "w", encoding="utf-8") as f:
        f.write(text)
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--release", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--timeout", type=int, default=7200)
    a = ap.parse_args(argv)
    code = run(os.path.abspath(a.release), a.log, a.timeout)
    print(f"check.sh from a Git clone: exit {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
