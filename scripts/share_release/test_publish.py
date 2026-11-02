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
    os.makedirs(os.path.join(root, "scripts"))
    for d in (".venv/bin", "__pycache__", "out", ".git", ".pytest_cache/v/cache"):
        os.makedirs(os.path.join(root, d))
    files = {"README.md": "hello\n", "release.json": "{}\n", "scripts/check.sh": "#!/bin/sh\necho hi\n",
             ".venv/bin/activate": "secret token\n", "__pycache__/x.pyc": "pyc\n", ".DS_Store": "x", "out/report.json": "{}",
             ".git/config": "[user]\n\tname = Ada Lovelace\n", ".pytest_cache/v/cache/nodeids": "[]"}
    for rel, text in files.items():
        with open(os.path.join(root, rel), "w") as f:
            f.write(text)
    os.chmod(os.path.join(root, "scripts/check.sh"), 0o755)
    return root


SHIPPED = {"README.md", "release.json", "scripts/check.sh"}


def test_the_zip_holds_the_shipped_files_and_extract_keeps_the_executable_bit(tmp_path):
    release = make_release(str(tmp_path / "rel"))
    assert {os.path.relpath(p, release) for p in publish.walk(release)} == SHIPPED
    out = str(tmp_path / "rel.zip")
    n, size = publish.make_zip(release, out)
    assert n == 3 and size > 0
    with zipfile.ZipFile(out) as z:
        assert set(z.namelist()) == {"epm-release/" + s for s in SHIPPED}  # the fixed root, never the output folder's name
    room = tmp_path / "room"; room.mkdir()
    with zipfile.ZipFile(out) as z:
        z.extractall(str(room / "plain"))
    assert not os.access(str(room / "plain" / "epm-release" / "scripts/check.sh"), os.X_OK)  # what extractall does (CPython issue 59999), measured here
    publish.extract(out, str(room / "kept"))
    script = str(room / "kept" / "epm-release" / "scripts/check.sh")
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
    zip_path = str(tmp_path / "rel.zip")
    publish.make_zip(release, zip_path)
    with open(os.path.join(release, "README.md"), "a") as f:
        f.write("edited after the zip, never checked\n")  # must not reach the branch
    (tmp_path / "rel" / "extra.md").write_text("added after the zip\n")
    commit = publish.make_branch(zip_path, repo, "share/test")
    assert git("rev-parse", "share/test") == commit
    assert git("show", "share/test:README.md") == "hello"
    assert git("rev-list", "--count", "share/test") == "1"  # an orphan: one commit, no history
    assert set(git("ls-tree", "-r", "--name-only", "share/test").split("\n")) == SHIPPED
    assert "100755" in git("ls-tree", "share/test", "scripts/check.sh")
    assert git("log", "-1", "--format=%an|%ae|%cn|%ce", "share/test") == "EPM release|epm-release@noreply.invalid|EPM release|epm-release@noreply.invalid"
    assert "Ada" not in git("cat-file", "-p", commit)
    assert git("status", "--porcelain") == "" and not os.path.exists(os.path.join(repo, ".git", "share-release-index"))


def test_a_symlink_in_the_release_stops_the_zip(tmp_path):
    import pytest
    release = make_release(str(tmp_path / "rel"))
    (tmp_path / "secret.env").write_text("TOKEN=x\n")
    os.symlink(str(tmp_path / "secret.env"), os.path.join(release, "linked.env"))
    with pytest.raises(SystemExit, match="symlink"):
        publish.make_zip(release, str(tmp_path / "rel.zip"))
    os.remove(os.path.join(release, "linked.env"))
    os.symlink(str(tmp_path), os.path.join(release, "linked-dir"))
    with pytest.raises(SystemExit, match="symlink"):
        list(publish.walk(release))


def fake_docker(folder, exit_code=0, sleep=0, rm_exit=0):
    """A docker on PATH that records its arguments NUL-separated and the subcommand of every call, sleeps as told
    (in a grandchild, as a real docker client waits on its daemon), then exits as told; rm exits as told too."""
    path = os.path.join(folder, "docker")
    with open(path, "w") as f:
        f.write("#!/bin/sh\necho \"$1 $2\" >> \"$FAKE_DOCKER_CALLS\"\n"
                f"[ \"$1\" = rm ] && exit {rm_exit}\n"
                "[ \"$1\" = run ] && printf '%s\\0' \"$@\" > \"$FAKE_DOCKER_LOG\"\n"
                f"[ \"$1\" = run ] && [ {sleep} -gt 0 ] && sh -c 'exec sleep {sleep}' \n"
                f"exit {exit_code}\n")
    os.chmod(path, 0o755)
    return path


def room_env(tmp_path, bindir):
    return {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}", "FAKE_DOCKER_LOG": str(tmp_path / "log"),
            "FAKE_DOCKER_CALLS": str(tmp_path / "calls"), "DATABRICKS_TOKEN": "t0ken", "NEO4J_PASSWORD": "pw"}


def test_the_clean_room_mounts_only_the_zip_and_reports_a_failed_check(tmp_path):
    bindir = tmp_path / "bin"; bindir.mkdir()
    fake_docker(str(bindir))
    (tmp_path / "rel.zip").write_bytes(b"PK")
    env = room_env(tmp_path, bindir)
    cmd = [sys.executable, os.path.join(HERE, "cleanroom.py"), str(tmp_path / "rel.zip"), "--log", str(tmp_path / "room.log"), "--timeout", "30"]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    args = (tmp_path / "log").read_text().split("\0")[:-1]  # NUL-terminated
    assert args.count("-v") == 1 and f"{tmp_path / 'rel.zip'}:/release.zip:ro" in args and "--name" in args
    envs = [args[i + 1] for i, a in enumerate(args) if a == "-e"]
    assert "HOME=/tmp/home" in envs and not any("TOKEN" in e or "PASSWORD" in e for e in envs)
    script = args[-1]
    assert 'python3 -c "$EXTRACT"' in script and "./scripts/check.sh" in script and "zipfile" in next(e for e in envs if e.startswith("EXTRACT="))
    fake_docker(str(bindir), exit_code=1)
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert r.returncode != 0


def test_the_clean_room_stops_its_container_when_the_deadline_passes(tmp_path):
    bindir = tmp_path / "bin"; bindir.mkdir()
    fake_docker(str(bindir), sleep=30)
    (tmp_path / "rel.zip").write_bytes(b"PK")
    env = room_env(tmp_path, bindir)
    cmd = [sys.executable, os.path.join(HERE, "cleanroom.py"), str(tmp_path / "rel.zip"), "--log", str(tmp_path / "room.log"), "--timeout", "2", "--name", "epm-room-test"]
    import time
    t0 = time.time()
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 1 and time.time() - t0 < 20
    assert "deadline of 2 s passed" in (tmp_path / "room.log").read_text()
    calls = (tmp_path / "calls").read_text().split("\n")
    assert "run --rm" in calls and "rm -f" in calls  # the container was stopped by name
    fake_docker(str(bindir), sleep=30, rm_exit=1)
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 1 and "could not remove the container epm-room-test" in (tmp_path / "room.log").read_text()  # a failed removal is said
    r = subprocess.run([sys.executable, os.path.join(HERE, "cleanroom.py"), "run", "--timeout", "1", "--log", str(tmp_path / "step.log"), "--", "sleep", "30"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 1 and "deadline of 1 s passed" in (tmp_path / "step.log").read_text()
    r = subprocess.run([sys.executable, os.path.join(HERE, "cleanroom.py"), "run", "--timeout", "10", "--log", str(tmp_path / "step.log"), "--", "echo", "done"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and (tmp_path / "step.log").read_text() == "done\n"


def test_the_deadline_kills_the_whole_process_group_and_bounds_every_wait(tmp_path):
    import time
    sys.path.insert(0, HERE)
    import procs
    token = f"epm-grandchild-{os.getpid()}"
    log = str(tmp_path / "log")
    t0 = time.time()
    rc = procs.stream(["sh", "-c", f"python3 -c 'import time; time.sleep(60)  # {token}' & sleep 60"], 1, log, echo=False)
    assert rc == -1 and time.time() - t0 < 15
    time.sleep(0.5)
    alive = subprocess.run(["pgrep", "-f", token], capture_output=True, text=True).stdout.strip()
    assert alive == "", f"a grandchild survived the deadline: {alive}"  # the group, not only the child, was killed
    t0 = time.time()
    rc = procs.stream(["sh", "-c", "printf partial; sleep 60"], 1, log, echo=False)  # output without a newline, then silence
    assert rc == -1 and time.time() - t0 < 15 and "partial" in open(log).read()
    t0 = time.time()
    rc = procs.stream(["sh", "-c", "exec >/dev/null 2>&1; sleep 60"], 1, log, echo=False)  # output closed, process lingers
    assert rc == -1 and time.time() - t0 < 15
    assert procs.stream(["sh", "-c", "echo done; exit 3"], 10, log, echo=False) == 3 and open(log).read() == "done\n"
    try:
        procs.run(["sh", "-c", f"python3 -c 'import time; time.sleep(60)  # {token}-run' & sleep 60"], timeout=1)
        assert False, "no Expired"
    except procs.Expired:
        pass
    time.sleep(0.5)
    assert subprocess.run(["pgrep", "-f", token + "-run"], capture_output=True, text=True).stdout.strip() == ""


def test_the_ref_update_is_guarded_and_each_publication_has_its_own_index(tmp_path):
    import threading
    sys.path.insert(0, HERE)
    repo = str(tmp_path / "repo")
    git = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "init", "-q", repo], check=True)
    git("config", "user.name", "x"); git("config", "user.email", "x@example.com")
    with open(os.path.join(repo, "main.txt"), "w") as f:
        f.write("main\n")
    git("add", "main.txt"); git("commit", "-q", "-m", "main")
    zips = []
    for n in ("one", "two"):
        rel = make_release(str(tmp_path / n))
        with open(os.path.join(rel, "which.txt"), "w") as f:
            f.write(n + "\n")
        publish.make_zip(rel, str(tmp_path / f"{n}.zip")); zips.append(str(tmp_path / f"{n}.zip"))
    results, errors = {}, []

    def go(n, z):
        try:
            results[n] = publish.make_branch(z, repo, f"share/{n}")
        except Exception as exc:
            errors.append(exc)
    threads = [threading.Thread(target=go, args=(n, z)) for n, z in zip(("one", "two"), zips)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    assert not errors and git("show", "share/one:which.txt") == "one" and git("show", "share/two:which.txt") == "two"
    assert not [f for f in os.listdir(os.path.join(repo, ".git")) if f.startswith("share-release-index")]
    stale, other = git("rev-parse", "share/one"), git("rev-parse", "share/two")
    run_git = lambda *a, **k: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True)
    git("update-ref", "refs/heads/share/one", other)  # someone moved share/one after its value was read
    try:
        publish.guarded_update_ref(run_git, "share/one", stale, stale)  # expects the value it read, which is gone
        assert False, "the stale update went through"
    except subprocess.CalledProcessError:
        pass
    assert git("rev-parse", "refs/heads/share/one") == other  # untouched by the losing writer
    publish.guarded_update_ref(run_git, "share/one", stale, other)  # expecting the current value, the update goes through
    assert git("rev-parse", "refs/heads/share/one") == stale
    try:
        publish.guarded_update_ref(run_git, "share/new", stale, "")  # "" means the ref must not exist: it does not, so it is created
        assert git("rev-parse", "refs/heads/share/new") == stale
        publish.guarded_update_ref(run_git, "share/new", other, "")  # and a second creation of an existing ref is refused
        assert False, "a second creation went through"
    except subprocess.CalledProcessError:
        pass
