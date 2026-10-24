"""Tests for scripts/hooks/pre-push: a push that only deletes remote refs skips the checks; any other
push, and a run with no ref lines (`git hook run pre-push`), runs scripts/check.sh and keeps its exit status."""
import os
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "hooks", "pre-push")
ZERO = "0" * 40
SHA = "1" * 40


def _run(stdin, check_status=0):
    with tempfile.TemporaryDirectory() as repo:
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        subprocess.run(["git", "init", "-q", repo], env=env, check=True)
        os.makedirs(os.path.join(repo, "scripts", "hooks"))
        hook = os.path.join(repo, "scripts", "hooks", "pre-push")
        shutil.copy(HOOK, hook)
        check = os.path.join(repo, "scripts", "check.sh")
        with open(check, "w") as f:
            f.write(f"#!/usr/bin/env bash\necho CHECKS RAN\nexit {check_status}\n")
        os.chmod(check, 0o755)
        proc = subprocess.run(["bash", hook, "origin", "git@example:repo.git"], input=stdin, cwd=repo, env=env,
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout


def test_a_delete_only_push_skips_the_checks():
    status, out = _run(f"(delete) {ZERO} refs/heads/a {SHA}\n(delete) {ZERO} refs/heads/b {SHA}\n")
    assert status == 0
    assert "CHECKS RAN" not in out
    assert "only deletes" in out


def test_a_sha256_delete_skips_the_checks():
    status, out = _run(f"(delete) {'0' * 64} refs/heads/a {'1' * 64}\n")
    assert status == 0
    assert "CHECKS RAN" not in out


def test_a_push_with_commits_runs_the_checks():
    status, out = _run(f"refs/heads/a {SHA} refs/heads/a {ZERO}\n")
    assert status == 0
    assert "CHECKS RAN" in out


def test_a_delete_with_an_update_runs_the_checks():
    status, out = _run(f"(delete) {ZERO} refs/heads/a {SHA}\nrefs/heads/b {SHA} refs/heads/b {SHA}\n")
    assert "CHECKS RAN" in out


def test_no_ref_lines_runs_the_checks():
    status, out = _run("")
    assert status == 0
    assert "CHECKS RAN" in out


def test_a_failing_check_fails_the_push():
    status, out = _run(f"refs/heads/a {SHA} refs/heads/a {ZERO}\n", check_status=1)
    assert status == 1
    assert "CHECKS RAN" in out
