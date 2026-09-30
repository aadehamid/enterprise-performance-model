#!/usr/bin/env python3
"""Regression test: Step 4 scripts must run from any checkout.

Five scripts hardcoded /home/hatch/workspace/..., so test_context_pass.py
(17/17) could only be reproduced on one machine. This test fails if any
Step 4 script names an absolute home path, if test_context_pass.py
doesn't pass when launched from an unrelated working directory, or if a
writer script would overwrite a governed target-report file.
"""
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
SELF = os.path.abspath(__file__)


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def snapshot(directory):
    """File name -> sha256 for every file directly in directory."""
    return {f: sha256(os.path.join(directory, f)) for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))}


HOME_PATH = re.compile(r"""["'](/home/|/Users/|~/)""")


def main():
    failures = []

    # 1. No absolute home paths in any Step 4 Python script
    for path in sorted(glob.glob(f"{BASE}/**/*.py", recursive=True)):
        if os.path.abspath(path) == SELF:
            continue
        with open(path) as f:
            for n, line in enumerate(f, 1):
                if HOME_PATH.search(line):
                    failures.append(f"{os.path.relpath(path, BASE)}:{n} hardcodes a home path")

    # 2. test_context_pass.py passes when run from an unrelated directory
    with tempfile.TemporaryDirectory() as cwd:
        r = subprocess.run([sys.executable, f"{BASE}/target-report/test_context_pass.py"],
                           cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0 or "17/17 passed" not in r.stdout:
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or ["(no output)"]
        failures.append(f"test_context_pass.py from a foreign cwd: exit {r.returncode}; {tail[0]}")

    # 3. Writer scripts must never overwrite governed target-report files.
    #    Once runnable from any checkout, a rerun could revert reviewed
    #    decisions (e.g. target-dispositions-v2.csv carries Hamid's
    #    2026-09-25 approvals). Run them in a throwaway copy laid out like
    #    the original separate workspace (<ws>/ontology-step4 beside
    #    <ws>/enterprise-performance-model), with no path overrides, so
    #    repository discovery is exercised too.
    expected = ["context-pass.csv", "context-sample.txt",
                "target-dispositions-v1.csv", "target-dispositions-v2.csv"]
    repo_root = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
    with tempfile.TemporaryDirectory() as ws:
        copy = os.path.join(ws, "ontology-step4")
        shutil.copytree(BASE, copy, ignore=shutil.ignore_patterns("proposal", "__pycache__"))
        os.symlink(repo_root, os.path.join(ws, "enterprise-performance-model"))
        governed_dir = os.path.join(copy, "target-report")
        before = snapshot(governed_dir)
        env = {k: v for k, v in os.environ.items() if k not in ("EPM_STEP4_DIR", "EPM_REPO_ROOT")}
        for script in ["context_pass.py", "classify.py", "classify_v2.py"]:
            r = subprocess.run([sys.executable, os.path.join(governed_dir, script)],
                               cwd=ws, env=env, capture_output=True, text=True)
            if r.returncode != 0:
                tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or ["(no output)"]
                failures.append(f"{script} (separate-workspace layout) exited {r.returncode}; {tail[0]}")
        after = snapshot(governed_dir)
        for f in sorted(set(before) | set(after)):
            if before.get(f) != after.get(f):
                failures.append(f"GOVERNED DIR CHANGED: target-report/{f}; writers must use proposal/")
        prop_dir = os.path.join(copy, "proposal", "target-report")
        for f in expected:
            if not os.path.exists(os.path.join(prop_dir, f)):
                failures.append(f"proposal/target-report/{f} not generated")
        prop = os.path.join(prop_dir, "context-pass.csv")
        if os.path.exists(prop) and sha256(prop) != before.get("context-pass.csv"):
            failures.append("proposal context-pass.csv differs from governed context-pass.csv")

    for f in failures:
        print("FAIL", f)
    print("PASS" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


def test_script_portability():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
