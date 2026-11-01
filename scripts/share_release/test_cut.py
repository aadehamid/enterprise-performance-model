"""cut.sh refuses an output folder that holds anything else before it removes anything."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = os.path.join(HERE, "cut.sh")


def cut(tmp_path, out, env_extra=None):
    epm, skills = tmp_path / "epm", tmp_path / "skills"
    epm.mkdir(exist_ok=True); skills.mkdir(exist_ok=True)
    (tmp_path / "stores.env").write_text("LEDGER_FILE=" + str(tmp_path / "ledger.jsonl") + "\n")
    env = {**os.environ, **(env_extra or {})}
    return subprocess.run(["bash", CUT, "--epm", str(epm), "--skills", str(skills), "--out", str(out), "--env", str(tmp_path / "stores.env"), "--no-cleanroom"],
                          env=env, capture_output=True, text=True, timeout=60)


def test_dangerous_output_folders_are_refused_before_anything_is_removed(tmp_path):
    home = tmp_path / "home"; home.mkdir(); (home / "keep").write_text("x")
    r = cut(tmp_path, home, {"HOME": str(home)})
    assert r.returncode == 2 and "refusing" in r.stderr and "home folder" in r.stderr and (home / "keep").exists()
    r = cut(tmp_path, "/")
    assert r.returncode == 2 and "it is the root" in r.stderr
    (tmp_path / "epm" / "README.md").write_text("checkout\n")
    r = cut(tmp_path, tmp_path / "epm")
    assert r.returncode == 2 and "checkout" in r.stderr and (tmp_path / "epm" / "README.md").exists()
    r = cut(tmp_path, tmp_path)  # a parent of both checkouts
    assert r.returncode == 2 and "parent" in r.stderr and (tmp_path / "epm" / "README.md").exists()
    other = tmp_path / "other"; other.mkdir(); (other / "notes.txt").write_text("mine")
    r = cut(tmp_path, other)
    assert r.returncode == 2 and "holds no release.json" in r.stderr and (other / "notes.txt").exists()
    (tmp_path / "afile").write_text("x")
    r = cut(tmp_path, tmp_path / "afile")
    assert r.returncode == 2 and "it is a file" in r.stderr and (tmp_path / "afile").exists()


def test_a_missing_option_prints_the_usage():
    r = subprocess.run(["bash", CUT, "--epm", "."], capture_output=True, text=True, timeout=60)
    assert r.returncode == 2 and "--store-rows" in r.stdout


def test_the_header_says_what_the_command_leaves_to_later_steps():
    with open(CUT) as f:
        head = f.read().split("set -euo pipefail")[0]
    assert "projection-driver, demo-live, tech-graph, sync" in head and "Step 9" in head and "Step 10" in head and "cleanup.py" in head and "publish.py branch" in head
