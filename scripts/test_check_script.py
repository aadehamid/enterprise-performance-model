"""Tests for scripts/check.sh itself: it clears inherited GIT_* variables before any check runs, so a test
that builds a temporary repository cannot reach this one from the pre-push hook (the #337 incident)."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check.sh")


def _lines():
    with open(CHECK) as f:
        return f.read().split("\n")


def _guard():
    return next(line for line in _lines() if "compgen -e" in line and "GIT_" in line)


def test_the_guard_clears_every_git_variable():
    env = dict(os.environ, GIT_DIR="/nonexistent", GIT_WORK_TREE="/nonexistent", GIT_INDEX_FILE="/nonexistent/i",
               GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.bare", GIT_CONFIG_VALUE_0="true")
    script = "set -euo pipefail\n" + _guard() + "\nenv | grep -c '^GIT_' || true\n"
    out = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True, check=True).stdout
    assert out.strip() == "0"


def test_the_guard_runs_before_the_first_check():
    lines = _lines()
    guard = lines.index(_guard())
    first = next(i for i, line in enumerate(lines) if line.startswith('before="$(snapshot)"'))
    assert guard < first
