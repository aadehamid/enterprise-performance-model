"""Tests for scripts/entire-local.sh: it moves Entire's git hooks out of scripts/hooks into the clone's
git dir, puts the tracked hooks back, and its pre-push runs the repo's checks before Entire, giving both
git's ref list. Without `entire` on PATH, the hooks run the repo's checks and nothing else."""
import os
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SETUP = os.path.join(HERE, "entire-local.sh")
PRE_PUSH = os.path.join(HERE, "hooks", "pre-push")
ZERO = "0" * 40
SHA = "1" * 40
MARKER = "#!/bin/sh\n# Entire CLI hooks\n"


def _git(repo, *args, env):
    return subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True).stdout.strip()


def _path_without_entire(fake_bin):
    """PATH with every real `entire` left out; `fake_bin` (if given) comes first."""
    dirs = [d for d in os.environ["PATH"].split(os.pathsep)
            if d and not os.access(os.path.join(d, "entire"), os.X_OK)]
    git_dir = os.path.dirname(shutil.which("git"))
    if git_dir not in dirs:
        dirs.append(git_dir)
    return os.pathsep.join(([fake_bin] if fake_bin else []) + dirs)


class Clone:
    """A temporary repo with this repo's pre-push hook, a stub check.sh, and a fake `entire` that logs
    each call and the ref list it was given."""

    def __init__(self, tmp, check_status=0, with_entire=True):
        self.repo = os.path.join(tmp, "a repo")
        self.log = os.path.join(tmp, "calls.log")
        fake_bin = os.path.join(tmp, "bin")
        os.makedirs(fake_bin)
        if with_entire:
            entire = os.path.join(fake_bin, "entire")
            with open(entire, "w") as f:
                f.write(f'#!/bin/sh\necho "ENTIRE $* env=$ENTIRE_PRE_PUSH_STDIN_REFS refs=$(cat | tr "\\n" "|")"'
                        f' >> "{self.log}"\nexit ${{FAKE_ENTIRE_STATUS:-0}}\n')
            os.chmod(entire, 0o755)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env["PATH"] = _path_without_entire(fake_bin)
        self.env["CHECK_LOG"] = self.log
        _git(tmp, "init", "-q", self.repo, env=self.env)
        hooks = os.path.join(self.repo, "scripts", "hooks")
        os.makedirs(hooks)
        shutil.copy(PRE_PUSH, os.path.join(hooks, "pre-push"))
        shutil.copy(SETUP, os.path.join(self.repo, "scripts", "entire-local.sh"))
        check = os.path.join(self.repo, "scripts", "check.sh")
        with open(check, "w") as f:
            f.write(f'#!/usr/bin/env bash\necho CHECKS RAN >> "$CHECK_LOG"\nexit {check_status}\n')
        os.chmod(check, 0o755)
        _git(self.repo, "add", ".", env=self.env)
        _git(self.repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init", env=self.env)
        _git(self.repo, "config", "core.hooksPath", "scripts/hooks", env=self.env)

    def setup(self, *args):
        return subprocess.run(["bash", "scripts/entire-local.sh", *args], cwd=self.repo, env=self.env,
                              check=True, capture_output=True, text=True)

    def push(self, stdin):
        hook = os.path.join(_git(self.repo, "config", "core.hooksPath", env=self.env), "pre-push")
        proc = subprocess.run(["sh", hook, "origin", "git@example:repo.git"], input=stdin, cwd=self.repo,
                              env=self.env, capture_output=True, text=True)
        return proc.returncode, self.calls()

    def calls(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log) as f:
            return f.read().splitlines()


def test_setup_moves_the_hooks_out_of_scripts_hooks():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        hooks = os.path.join(c.repo, "scripts", "hooks")
        os.rename(os.path.join(hooks, "pre-push"), os.path.join(hooks, "pre-push.pre-entire"))
        for name in ("pre-push", "commit-msg"):
            with open(os.path.join(hooks, name), "w") as f:
                f.write(MARKER + "entire hooks git " + name + "\n")
        c.setup()
        assert _git(c.repo, "status", "--porcelain", env=c.env) == ""
        assert sorted(os.listdir(hooks)) == ["pre-push"]
        hooks_path = _git(c.repo, "config", "core.hooksPath", env=c.env)
        assert hooks_path == os.path.join(os.path.realpath(_git(c.repo, "rev-parse", "--absolute-git-dir", env=c.env)),
                                          "entire-hooks")
        assert sorted(os.listdir(hooks_path)) == ["commit-msg", "post-commit", "post-rewrite", "pre-push",
                                                  "prepare-commit-msg"]
        for name in os.listdir(hooks_path):
            with open(os.path.join(hooks_path, name)) as f:
                assert "Entire CLI hooks" in f.read()


def test_setup_keeps_your_own_edit_to_a_tracked_hook():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        with open(os.path.join(c.repo, "scripts", "hooks", "pre-push"), "a") as f:
            f.write("# my edit\n")
        c.setup()
        assert _git(c.repo, "status", "--porcelain", env=c.env) == "M scripts/hooks/pre-push"


def _saved(c):
    """The contents of every file entire-local.sh saved, keyed by hook name."""
    saved = os.path.join(_git(c.repo, "rev-parse", "--absolute-git-dir", env=c.env), "entire-local-saved")
    out = {}
    for name in os.listdir(saved) if os.path.isdir(saved) else []:
        with open(os.path.join(saved, name)) as f:
            out[name.split(".")[0]] = f.read()
    return out


def _entire_rewrote(c, edit_before="", edit_after="", keep_hook=True):
    """Do what `entire enable` does to scripts/hooks/pre-push, with optional edits before and after."""
    hook = os.path.join(c.repo, "scripts", "hooks", "pre-push")
    with open(hook, "a") as f:
        f.write(edit_before)
    os.rename(hook, hook + ".pre-entire")
    if keep_hook:
        with open(hook, "w") as f:
            f.write(MARKER + "entire hooks git pre-push\n" + edit_after)
    return hook


def test_setup_restores_an_edited_hook_that_entire_moved_aside():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        hook = _entire_rewrote(c, edit_before="# my edit\n")
        c.setup()
        with open(hook) as f:
            assert f.read().endswith("# my edit\n")
        assert sorted(os.listdir(os.path.dirname(hook))) == ["pre-push"]


def test_an_edit_to_entires_hook_is_saved_before_the_backup_returns():
    for args in ((), ("--remove",)):
        with tempfile.TemporaryDirectory() as tmp:
            c = Clone(tmp)
            hook = _entire_rewrote(c, edit_after="# edited later\n")
            c.setup(*args)
            assert _git(c.repo, "status", "--porcelain", env=c.env) == ""
            assert _saved(c)["pre-push"].endswith("# edited later\n")


def test_an_entire_hook_with_no_backup_is_saved_and_the_checks_still_run():
    for args in ((), ("--remove",)):
        with tempfile.TemporaryDirectory() as tmp:
            c = Clone(tmp)
            hook = os.path.join(c.repo, "scripts", "hooks", "pre-push")
            with open(hook, "w") as f:
                f.write(MARKER + "entire hooks git pre-push\n# my edit\n")
            c.setup(*args)
            assert _git(c.repo, "status", "--porcelain", env=c.env) == ""
            assert _saved(c)["pre-push"].endswith("# my edit\n")
            assert c.push(f"refs/heads/a {SHA} refs/heads/a {ZERO}\n")[1][0] == "CHECKS RAN"


def test_a_backup_with_no_hook_is_restored():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        _entire_rewrote(c, keep_hook=False)
        c.setup()
        assert _git(c.repo, "status", "--porcelain", env=c.env) == ""
        assert c.push(f"refs/heads/a {SHA} refs/heads/a {ZERO}\n")[1][0] == "CHECKS RAN"


def test_a_backup_beside_a_hook_that_is_not_entires_is_left():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        backup = os.path.join(c.repo, "scripts", "hooks", "pre-push.pre-entire")
        with open(backup, "w") as f:
            f.write("#!/bin/sh\n# some other tool\n")
        c.setup()
        assert os.path.exists(backup)
        assert _saved(c) == {}


def test_the_cursor_installer_keeps_an_entire_hook_folder():
    with open(os.path.join(HERE, "..", ".cursor", "install.sh")) as f:
        text = f.read()
    block = text[text.index('case "$(git -C "$REPO_ROOT" config core.hooksPath'):]
    block = block[:block.index("esac") + len("esac")]
    for before, after in (("", "scripts/hooks"), ("/x/.git/entire-hooks", "/x/.git/entire-hooks"),
                          ("other", "scripts/hooks")):
        with tempfile.TemporaryDirectory() as tmp:
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            _git(tmp, "init", "-q", tmp, env=env)
            if before:
                _git(tmp, "config", "core.hooksPath", before, env=env)
            subprocess.run(["bash", "-euo", "pipefail", "-c", block], env={**env, "REPO_ROOT": tmp}, check=True)
            assert _git(tmp, "config", "core.hooksPath", env=env) == after


def test_setup_excludes_entires_config_files():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        for path in (".entire/settings.json", ".claude/settings.json", ".codex/hooks.json", ".cursor/hooks.json",
                     ".pi/extensions/entire/index.ts"):
            os.makedirs(os.path.join(c.repo, os.path.dirname(path)), exist_ok=True)
            open(os.path.join(c.repo, path), "w").close()
        c.setup()
        c.setup()
        assert _git(c.repo, "status", "--porcelain", env=c.env) == ""
        with open(os.path.join(c.repo, ".git", "info", "exclude")) as f:
            assert f.read().count(".entire/") == 1


def test_a_push_runs_the_checks_then_entire_with_the_ref_list():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        c.setup()
        status, calls = c.push(f"refs/heads/a {SHA} refs/heads/a {ZERO}\n")
        assert status == 0
        assert calls == ["CHECKS RAN", f"ENTIRE hooks git pre-push origin env=1 refs=refs/heads/a {SHA} refs/heads/a {ZERO}|"]


def test_a_failing_check_stops_the_push_before_entire():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp, check_status=1)
        c.setup()
        status, calls = c.push(f"refs/heads/a {SHA} refs/heads/a {ZERO}\n")
        assert status == 1
        assert calls == ["CHECKS RAN"]


def test_a_delete_only_push_skips_the_checks_and_still_runs_entire():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        c.setup()
        status, calls = c.push(f"(delete) {ZERO} refs/heads/a {SHA}\n")
        assert status == 0
        assert calls == [f"ENTIRE hooks git pre-push origin env=1 refs=(delete) {ZERO} refs/heads/a {SHA}|"]


def test_without_entire_the_hooks_run_only_the_checks():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp, check_status=1, with_entire=False)
        c.setup()
        status, calls = c.push(f"refs/heads/a {SHA} refs/heads/a {ZERO}\n")
        assert status == 1
        assert calls == ["CHECKS RAN"]
        _git(c.repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x",
             env=c.env)
        assert c.calls() == ["CHECKS RAN"]


def test_remove_goes_back_to_scripts_hooks():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        c.setup()
        hooks_path = _git(c.repo, "config", "core.hooksPath", env=c.env)
        c.setup("--remove")
        assert _git(c.repo, "config", "core.hooksPath", env=c.env) == "scripts/hooks"
        assert not os.path.exists(hooks_path)


def test_a_failing_entire_stops_the_push():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        c.setup()
        c.env["FAKE_ENTIRE_STATUS"] = "3"
        status, calls = c.push(f"refs/heads/a {SHA} refs/heads/a {ZERO}\n")
        assert status == 3
        assert calls[0] == "CHECKS RAN"


def test_a_real_push_of_two_refs_from_a_linked_worktree():
    with tempfile.TemporaryDirectory() as tmp:
        c = Clone(tmp)
        remote = os.path.join(tmp, "the remote.git")
        _git(tmp, "init", "-q", "--bare", remote, env=c.env)
        _git(c.repo, "remote", "add", "origin", remote, env=c.env)
        worktree = os.path.join(tmp, "a worktree")
        _git(c.repo, "worktree", "add", "-q", "-b", "two", worktree, env=c.env)
        subprocess.run(["bash", "scripts/entire-local.sh"], cwd=worktree, env=c.env, check=True, capture_output=True)
        assert _git(c.repo, "config", "core.hooksPath", env=c.env).endswith(os.path.join(".git", "entire-hooks"))
        _git(worktree, "push", "-q", "origin", "HEAD:refs/heads/one", "HEAD:refs/heads/two", env=c.env)
        head = _git(worktree, "rev-parse", "HEAD", env=c.env)
        assert c.calls() == ["CHECKS RAN", f"ENTIRE hooks git pre-push origin env=1 refs=HEAD {head} refs/heads/one "
                             f"{ZERO}|HEAD {head} refs/heads/two {ZERO}|"]
