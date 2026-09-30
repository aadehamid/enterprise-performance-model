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
    #    2026-09-25 approvals). Run them in a throwaway copy, as the
    #    mapping_v2.py regression test does for canonical facts.
    governed = ["context-pass.csv", "context-sample.txt", "target-dispositions-v2.csv",
                "target-dispositions-v1.1.csv"]
    repo_root = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "step4")
        shutil.copytree(BASE, copy, ignore=shutil.ignore_patterns("proposal", "__pycache__"))
        before = {f: sha256(os.path.join(copy, "target-report", f)) for f in governed}
        env = dict(os.environ, EPM_STEP4_DIR=copy, EPM_REPO_ROOT=repo_root)
        for script in ["context_pass.py", "classify.py", "classify_v2.py"]:
            r = subprocess.run([sys.executable, os.path.join(copy, "target-report", script)],
                               cwd=tmp, env=env, capture_output=True, text=True)
            if r.returncode != 0:
                failures.append(f"{script} exited {r.returncode}")
        for f in governed:
            if sha256(os.path.join(copy, "target-report", f)) != before[f]:
                failures.append(f"GOVERNED FILE OVERWRITTEN: target-report/{f}; writers must use proposal/")
        prop = os.path.join(copy, "proposal", "target-report", "context-pass.csv")
        if not os.path.exists(prop):
            failures.append("proposal/target-report/context-pass.csv not generated")
        elif sha256(prop) != before["context-pass.csv"]:
            failures.append("proposal context-pass.csv differs from governed context-pass.csv")

    for f in failures:
        print("FAIL", f)
    print("PASS" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


def test_script_portability():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
