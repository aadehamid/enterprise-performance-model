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


# Plan 2 (codebase architecture, 2026-10-30): check.sh lists its module verifies and test files by hand, and
# nothing stopped a new module or test file from being left out. These tests make the lists complete.

def _modules():
    """The module names build_module.py's MODULES table declares, read without importing it."""
    import ast
    path = os.path.join(HERE, "..", "business_architecture", "ontology", "release", "build_module.py")
    tree = ast.parse(open(path).read())
    table = next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == "MODULES" for t in n.targets))
    return [k.value for k in table.keys]


def _commands():
    """check.sh's executable text: every comment dropped, whole-line or after a command (a # that starts a word, as
    after a space or a control operator such as ;, &, | or a bracket; no command in check.sh quotes one), and $step4
    written out, so every path reads in full."""
    import re
    code = [re.sub(r"(^|[\s;&|()<>])#.*$", r"\1", line) for line in _lines()]
    return "\n".join(code).replace("$step4", "business_architecture/ontology/step4")


def test_every_module_release_is_verified():
    text = _commands()
    missing = [m for m in _modules() if f"build_module.py {m} --verify" not in text]
    assert _modules() and not missing, missing


def test_every_tracked_test_file_is_run():
    root = os.path.join(HERE, "..")
    if os.path.exists(os.path.join(root, ".git")):  # a folder, or a file in a worktree
        files = subprocess.run(["git", "ls-files", "*test_*.py"], cwd=root, capture_output=True, text=True,
                               check=True).stdout.split()
    else:  # a tree without Git, such as the share release: every test file in it
        files = sorted(os.path.relpath(os.path.join(r, f), root) for r, ds, fs in os.walk(root) for f in fs
                       if f.startswith("test_") and f.endswith(".py") and "__pycache__" not in r and ".venv" not in r)
    # A share release, cloned or not: the skills' tests (skills/<name>/scripts/) run by module name in the script's own
    # section, not by path. No path of main starts with skills/.
    files = [f for f in files if not f.startswith("skills" + os.sep)]
    # data_lineage/ is a separate catalog with its own dependencies and its own tests (data_lineage/README.md);
    # the ontology's check does not run them.
    files = [f for f in files if not f.replace(os.sep, "/").startswith("data_lineage/")]
    text = _commands()
    missing = [f for f in files if f not in text]  # by its full path, in a command, not in a comment
    assert files and not missing, missing
