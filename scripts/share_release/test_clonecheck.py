"""clonecheck.py runs check.sh from a Git clone, and reports its exit code."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clonecheck  # noqa: E402


def tree(tmp_path, script):
    (tmp_path / "rel" / "scripts").mkdir(parents=True)
    (tmp_path / "rel" / "scripts" / "check.sh").write_text(script)
    return str(tmp_path / "rel")


def test_it_runs_in_a_real_clone(tmp_path):
    rel = tree(tmp_path, 'test -d .git && git log --format=%an -1 && echo "all checks passed"\n')
    log = tmp_path / "log"
    assert clonecheck.run(rel, str(log)) == 0
    text = log.read_text()
    assert "all checks passed" in text and "release" in text
    assert not os.path.exists(os.path.join(rel, ".git"))  # the release folder is not touched


def test_a_failure_is_its_exit_code(tmp_path):
    assert clonecheck.run(tree(tmp_path, "exit 3\n"), str(tmp_path / "log")) == 3
