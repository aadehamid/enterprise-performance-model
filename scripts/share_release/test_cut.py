"""cut.sh refuses an output folder that holds anything else before it removes anything."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = os.path.join(HERE, "cut.sh")


def cut(tmp_path, out, env_extra=None, *extra):
    epm, skills = tmp_path / "epm", tmp_path / "skills"
    epm.mkdir(exist_ok=True); skills.mkdir(exist_ok=True)
    (tmp_path / "stores.env").write_text("LEDGER_FILE=" + str(tmp_path / "ledger.jsonl") + "\n")
    env = {**os.environ, "EPM_RELEASE_OWNER_NAMES": "Ada Lovelace", **(env_extra or {})}
    return subprocess.run(["bash", CUT, "--epm", str(epm), "--skills", str(skills), "--out", str(out), "--env", str(tmp_path / "stores.env"), "--no-cleanroom", *extra],
                          env=env, capture_output=True, text=True, timeout=120)


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
    assert r.returncode == 2 and "--replace" in r.stderr and (other / "notes.txt").exists()
    (other / "release.json").write_text("")  # a forged, empty marker beside unrelated files
    r = cut(tmp_path, other, None, "--replace")
    assert r.returncode == 2 and "exactly the marker" in r.stderr and (other / "notes.txt").exists()
    (other / "release.json").write_text('{"release": "EPM 1.0", "mode": "share release"}')  # string-valued keys, but not this tool's marker
    r = cut(tmp_path, other, None, "--replace")
    assert r.returncode == 2 and "exactly the marker" in r.stderr and (other / "notes.txt").exists()
    import json, sys
    sys.path.insert(0, HERE); import manifest
    (other / "release.json").write_text(json.dumps({**manifest.marker("2026-11-01"), "from": "x"}))  # one key too many
    r = cut(tmp_path, other, None, "--replace")
    assert r.returncode == 2 and "exactly the marker" in r.stderr and (other / "notes.txt").exists()
    (other / "release.json").write_text(json.dumps(manifest.marker("2026-11-01")))
    r = cut(tmp_path, other, {"EPM_RELEASE_OWNER_NAMES": "", "HOME": str(tmp_path / "nohome")}, "--replace")  # no owner names: nothing removed
    assert r.returncode == 2 and "not configured" in r.stderr and (other / "notes.txt").exists()
    r = cut(tmp_path, other, None, "--replace")  # the exact marker, the names configured: the folder is replaced and the cut starts
    assert "=== export" in r.stdout and not (other / "notes.txt").exists()
    r = cut(tmp_path, tmp_path / "fresh", None, "--store-rows", "")
    assert r.returncode == 2 and "names no row" in r.stderr
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


def test_a_hanging_export_is_stopped_by_the_deadline(tmp_path):
    epm = tmp_path / "epm"; (epm / "business_architecture" / "ontology").mkdir(parents=True)
    os.mkfifo(str(epm / "business_architecture" / "ontology" / "README.md"))  # a reader of this file blocks forever
    (tmp_path / "skills").mkdir()
    (tmp_path / "stores.env").write_text("LEDGER_FILE=" + str(tmp_path / "ledger.jsonl") + "\n")
    env = {**os.environ, "EPM_RELEASE_OWNER_NAMES": "Ada Lovelace", "STEP_TIMEOUT": "2"}
    r = subprocess.run(["bash", CUT, "--epm", str(epm), "--skills", str(tmp_path / "skills"), "--out", str(tmp_path / "out"), "--env", str(tmp_path / "stores.env"), "--no-cleanroom"],
                       env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 1 and "=== export" in r.stdout and "deadline of 2 s passed" in (tmp_path / "out-export.log").read_text()
