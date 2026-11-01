"""cleanup.py removes only what the ledger names, refuses dangerous paths, and exits 0 only with proof."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLEANUP = os.path.join(HERE, "cleanup.py")


def fake_docker(folder, rm_exit=0, ps_names=""):
    path = os.path.join(folder, "docker")
    with open(path, "w") as f:
        f.write("#!/bin/sh\necho \"$@\" >> \"$FAKE_DOCKER_LOG\"\n"
                f"case \"$1 $2\" in 'rm -f') exit {rm_exit};; 'ps -a') printf '%s\\n' {ps_names!r}; exit 0;; 'compose ls') echo '[]'; exit 0;; esac\nexit 0\n")
    os.chmod(path, 0o755)


def setup(tmp_path, entries, rm_exit=0, ps_names=""):
    bindir = tmp_path / "bin"; bindir.mkdir(exist_ok=True)
    fake_docker(str(bindir), rm_exit, ps_names)
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("".join(json.dumps(e) + "\n" for e in entries))
    envf = tmp_path / "validate.env"; envf.write_text("SKILLS_DIR=/nowhere\n")
    env = {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}", "FAKE_DOCKER_LOG": str(tmp_path / "docker.log"),
           "HOME": str(tmp_path / "home")}
    (tmp_path / "home").mkdir(exist_ok=True)
    return ledger, envf, env


def run(ledger, envf, env, *extra):
    return subprocess.run([sys.executable, CLEANUP, "--ledger", str(ledger), "--env", str(envf), *extra], env=env, capture_output=True, text=True)


def validation_paths(tmp_path):
    folder = tmp_path / "scratch" / "validate" / "driver-out"; folder.mkdir(parents=True)
    (folder / "x").write_text("x")
    login = tmp_path / "scratch" / "validate" / "validate-neo4j.env"; login.write_text("NEO4J_PASSWORD=x\n")
    return folder, login


def test_a_ledger_of_folder_file_and_container_is_removed_with_proof(tmp_path):
    folder, login = validation_paths(tmp_path)
    ledger, envf, env = setup(tmp_path, [{"kind": "folder", "name": str(folder)}, {"kind": "file", "name": str(login)},
                                         {"kind": "container", "name": "epm-validate"}, {"kind": "file", "name": str(login)}])
    r = run(ledger, envf, env)  # a dry run removes nothing
    assert r.returncode == 0 and "dry run" in r.stdout and folder.exists() and login.exists()
    r = run(ledger, envf, env, "--yes")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not folder.exists() and not login.exists() and "everything in the ledger is gone" in r.stdout
    assert (tmp_path / "docker.log").read_text().count("rm -f -v epm-validate") == 1  # the duplicate entry once


def test_a_failed_or_unproven_removal_is_not_success(tmp_path):
    folder, login = validation_paths(tmp_path)
    ledger, envf, env = setup(tmp_path, [{"kind": "container", "name": "epm-validate"}], rm_exit=1)
    r = run(ledger, envf, env, "--yes")
    assert r.returncode == 1 and "FAILED container epm-validate" in r.stdout and "returned 1" in r.stdout
    ledger, envf, env = setup(tmp_path, [{"kind": "container", "name": "epm-validate"}], ps_names="epm-validate")
    r = run(ledger, envf, env, "--yes")
    assert r.returncode == 1 and "container epm-validate still exists" in r.stdout
    ledger, envf, env = setup(tmp_path, [{"kind": "aura", "name": "the owner's AuraDB", "detail": "reloaded by the driver"}])
    r = run(ledger, envf, env, "--yes")
    assert r.returncode == 1 and "left (not this script's to remove): aura" in r.stdout and "is left" in r.stdout


def test_dangerous_paths_are_refused_and_kept(tmp_path):
    home = tmp_path / "home"; home.mkdir(exist_ok=True); (home / "keep.txt").write_text("keep")
    tree = tmp_path / "checkout"; tree.mkdir(); (tree / "README.md").write_text("tree")
    ledger, envf, env = setup(tmp_path, [{"kind": "folder", "name": str(home)}, {"kind": "folder", "name": "/"},
                                         {"kind": "folder", "name": str(tmp_path)}, {"kind": "file", "name": "/etc"},
                                         {"kind": "folder", "name": str(tree)}])
    r = run(ledger, envf, env, "--yes", "--tree", str(tree))
    assert r.returncode == 1, r.stdout + r.stderr
    assert (home / "keep.txt").exists() and (tree / "README.md").exists() and tmp_path.exists()
    assert r.stdout.count("REFUSED") == 5 and "the home folder" in r.stdout and "holds the tree" in r.stdout and "holds this tool" not in r.stdout
    assert not os.path.exists(str(tmp_path / "docker.log"))  # nothing ran


def test_a_missing_docker_is_no_proof_and_a_broken_symlink_is_removed_as_a_link(tmp_path):
    folder, login = validation_paths(tmp_path)
    ledger, envf, env = setup(tmp_path, [{"kind": "container", "name": "epm-validate"}])
    env["PATH"] = str(tmp_path / "nowhere")  # no docker at all
    r = run(ledger, envf, env, "--yes")
    assert r.returncode == 1 and "docker ps failed: no proof" in r.stdout and "Traceback" not in r.stderr
    link = tmp_path / "scratch" / "validate" / "gone-link"
    os.symlink(str(tmp_path / "scratch" / "validate" / "never-existed"), str(link))  # a broken folder symlink
    ledger, envf, env = setup(tmp_path, [{"kind": "folder", "name": str(link)}])
    assert os.path.lexists(str(link))
    r = run(ledger, envf, env, "--yes")
    assert r.returncode == 0 and not os.path.lexists(str(link)) and "everything in the ledger is gone" in r.stdout


def test_a_catalog_the_run_did_not_create_is_refused(tmp_path):
    entries = [{"kind": "databricks-catalog", "name": "epm_release_validate_a"}]
    ledger, envf, env = setup(tmp_path, entries)
    r = run(ledger, envf, env, "--yes", "--tree", str(tmp_path))
    assert r.returncode == 1 and "REFUSED databricks-catalog epm_release_validate_a" in r.stdout


def test_a_shared_catalog_is_refused_whatever_the_line_says(tmp_path):
    entries = [{"kind": "databricks-catalog", "name": "idp_sbx", "detail_created_by_run": True}]
    ledger, envf, env = setup(tmp_path, entries)
    r = run(ledger, envf, env, "--yes", "--tree", str(tmp_path))
    assert r.returncode == 1 and "REFUSED databricks-catalog idp_sbx: it is a shared catalog" in r.stdout


def test_a_catalog_the_run_created_may_be_purged():
    sys.path.insert(0, HERE)
    import cleanup
    assert cleanup.catalog_refusal({"name": "epm_release_validate_a", "detail_created_by_run": True}) is None
    assert cleanup.catalog_refusal({"name": "epm_release_validate_a", "detail_created_by_run": "yes"})  # only the literal true
    assert cleanup.catalog_refusal({"name": "IDP_SBX", "detail_created_by_run": True})
    assert cleanup.catalog_refusal({"name": "team_catalog", "detail_created_by_run": True})  # absence alone is not enough
