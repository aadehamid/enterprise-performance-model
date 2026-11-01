"""The zip, the orphan branch and the clean room ship exactly the gated files, with their modes and no person's name."""
import os
import stat
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import publish  # noqa: E402


def make_release(root):
    os.makedirs(os.path.join(root, "business_architecture", "ontology", "projection"))
    os.makedirs(os.path.join(root, ".venv", "bin")); os.makedirs(os.path.join(root, "__pycache__")); os.makedirs(os.path.join(root, "out"))
    files = {"README.md": "hello\n", "release.json": "{}\n", "business_architecture/ontology/projection/run_local.sh": "#!/bin/sh\necho hi\n",
             ".venv/bin/activate": "secret token\n", "__pycache__/x.pyc": "pyc\n", ".DS_Store": "x", "out/report.json": "{}"}
    for rel, text in files.items():
        with open(os.path.join(root, rel), "w") as f:
            f.write(text)
    os.chmod(os.path.join(root, "business_architecture/ontology/projection/run_local.sh"), 0o755)
    return root


SHIPPED = {"README.md", "release.json", "business_architecture/ontology/projection/run_local.sh"}


def test_the_zip_holds_the_shipped_files_and_extract_keeps_the_executable_bit(tmp_path):
    release = make_release(str(tmp_path / "rel"))
    assert {os.path.relpath(p, release) for p in publish.walk(release)} == SHIPPED
    out = str(tmp_path / "rel.zip")
    n, size = publish.make_zip(release, out)
    assert n == 3 and size > 0
    with zipfile.ZipFile(out) as z:
        assert set(z.namelist()) == {"rel/" + s for s in SHIPPED}
    room = tmp_path / "room"; room.mkdir()
    with zipfile.ZipFile(out) as z:
        z.extractall(str(room / "plain"))
    assert not os.access(str(room / "plain" / "rel" / "business_architecture/ontology/projection/run_local.sh"), os.X_OK)  # what extractall does
    publish.extract(out, str(room / "kept"))
    script = str(room / "kept" / "rel" / "business_architecture/ontology/projection/run_local.sh")
    assert stat.S_IMODE(os.stat(script).st_mode) == 0o755
    assert subprocess.run([script], capture_output=True, text=True).stdout == "hi\n"


def test_the_orphan_branch_holds_the_zips_files_with_a_neutral_identity(tmp_path):
    repo = str(tmp_path / "repo")
    git = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "init", "-q", repo], check=True)
    git("config", "user.name", "Ada Lovelace"); git("config", "user.email", "ada@example.com")
    with open(os.path.join(repo, "main.txt"), "w") as f:
        f.write("main\n")
    git("add", "main.txt"); git("commit", "-q", "-m", "main")
    release = make_release(str(tmp_path / "rel"))
    commit = publish.make_branch(release, repo, "share/test")
    assert git("rev-parse", "share/test") == commit
    assert git("rev-list", "--count", "share/test") == "1"  # an orphan: one commit, no history
    assert set(git("ls-tree", "-r", "--name-only", "share/test").split("\n")) == SHIPPED
    assert "100755" in git("ls-tree", "share/test", "business_architecture/ontology/projection/run_local.sh")
    assert git("log", "-1", "--format=%an|%ae|%cn|%ce", "share/test") == "EPM release|epm-release@noreply.invalid|EPM release|epm-release@noreply.invalid"
    assert "Ada" not in git("cat-file", "-p", commit)
    assert git("status", "--porcelain") == "" and not os.path.exists(os.path.join(repo, ".git", "share-release-index"))


def fake_docker(folder, exit_code=0):
    """A docker on PATH that records its arguments and the script it was given, then exits as told."""
    path = os.path.join(folder, "docker")
    with open(path, "w") as f:
        f.write("#!/bin/sh\nprintf '%s\\0' \"$@\" > \"$FAKE_DOCKER_LOG\"\nexit " + str(exit_code) + "\n")
    os.chmod(path, 0o755)
    return path


def test_the_clean_room_mounts_only_the_zip_and_reports_a_failed_check(tmp_path):
    bindir = tmp_path / "bin"; bindir.mkdir()
    fake_docker(str(bindir))
    (tmp_path / "rel.zip").write_bytes(b"PK")
    env = {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}", "FAKE_DOCKER_LOG": str(tmp_path / "log"),
           "DATABRICKS_TOKEN": "t0ken", "NEO4J_PASSWORD": "pw"}
    r = subprocess.run(["bash", os.path.join(HERE, "cleanroom.sh"), str(tmp_path / "rel.zip"), str(tmp_path / "room.log")], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    args = (tmp_path / "log").read_text().split("\0")[:-1]  # NUL-terminated
    assert args.count("-v") == 1 and f"{tmp_path / 'rel.zip'}:/release.zip:ro" in args
    envs = [args[i + 1] for i, a in enumerate(args) if a == "-e"]
    assert "HOME=/tmp/home" in envs and not any("TOKEN" in e or "PASSWORD" in e for e in envs)
    script = args[-1]
    assert 'python3 -c "$EXTRACT"' in script and "./scripts/check.sh" in script and "zipfile" in next(e for e in envs if e.startswith("EXTRACT="))
    fake_docker(str(bindir), exit_code=1)
    r = subprocess.run(["bash", os.path.join(HERE, "cleanroom.sh"), str(tmp_path / "rel.zip"), str(tmp_path / "room.log")], env=env, capture_output=True, text=True)
    assert r.returncode != 0
