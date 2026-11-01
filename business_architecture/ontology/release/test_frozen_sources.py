"""Frozen sources: the builders read a frozen copy of the process map when one exists, else Git."""
import contextlib
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frozen_sources as fs  # noqa: E402


class Frozen(unittest.TestCase):
    def test_the_frozen_file_is_read_before_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = fs.FROZEN
            fs.FROZEN = tmp
            try:
                self.assertFalse(fs.is_frozen("abc123def456", "x/map.json"))
                with open(fs.frozen_path("abc123def456", "x/map.json"), "wb") as f:
                    f.write(b'{"frozen": true}')
                self.assertTrue(fs.is_frozen("abc123def456", "x/map.json"))
                self.assertEqual(fs.read("abc123def456", "x/map.json", repo="/nonexistent"), b'{"frozen": true}')
            finally:
                fs.FROZEN = old

    def test_without_a_frozen_file_git_is_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            subprocess.run(["git", "init", "-q", tmp], check=True, env=env)
            with open(os.path.join(tmp, "map.json"), "w") as f:
                f.write('{"v": 1}')
            subprocess.run(["git", "-C", tmp, "add", "map.json"], check=True, env=env)
            subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "m"], check=True, env=env)
            sha = subprocess.run(["git", "-C", tmp, "rev-parse", "HEAD"], capture_output=True, text=True, env=env).stdout.strip()
            old = fs.FROZEN
            fs.FROZEN = os.path.join(tmp, "frozen")
            try:
                self.assertEqual(fs.read(sha, "map.json", repo=tmp), b'{"v": 1}')
            finally:
                fs.FROZEN = old

    def test_the_pinned_commits_are_the_four_the_core_builders_name(self):
        pins = fs.pinned()
        self.assertEqual([c[:8] for c, _ in pins], ["b75fd991", "82593547", "c351ef0e", "4906666a"])
        self.assertTrue(all(p == "business_architecture/business_process/downstream_process_map.json" for _, p in pins))

    def test_freeze_writes_one_file_per_pinned_commit(self):
        if not os.path.exists(os.path.join(fs.REPO, ".git")):
            self.skipTest("not a Git checkout (the share release reads its frozen copies and never freezes)")
        with tempfile.TemporaryDirectory() as tmp:
            old = fs.FROZEN
            fs.FROZEN = tmp
            try:
                written = fs.freeze()
                self.assertEqual(len(written), 4)
                for p in written:
                    with open(p, "rb") as f:
                        self.assertTrue(f.read().lstrip().startswith(b"["))
            finally:
                fs.FROZEN = old


class ReleaseMode(unittest.TestCase):
    """build_module reads release mode from EPM_SHARE_RELEASE or release.json at the tree's root. Each test that sets
    the variable puts the caller's value back (a release run sets it for the whole session) and reloads the module."""

    @contextlib.contextmanager
    def with_env(self, value):
        """Run build_module with EPM_SHARE_RELEASE set to `value` (None: unset); restore the environment after."""
        import importlib
        import build_module as bm
        missing = object()
        before = os.environ.get("EPM_SHARE_RELEASE", missing)
        if value is None:
            os.environ.pop("EPM_SHARE_RELEASE", None)
        else:
            os.environ["EPM_SHARE_RELEASE"] = value
        try:
            yield importlib.reload(bm)
        finally:
            if before is missing:
                os.environ.pop("EPM_SHARE_RELEASE", None)
            else:
                os.environ["EPM_SHARE_RELEASE"] = before
            importlib.reload(bm)

    def test_the_marker_file_or_the_variable_means_release_mode(self):
        import build_module as bm
        with tempfile.TemporaryDirectory() as tmp:
            with self.with_env(None) as bm:
                self.assertFalse(bm.share_release(tmp))
                with open(os.path.join(tmp, "release.json"), "w") as f:
                    f.write("{}\n")
                self.assertTrue(bm.share_release(tmp))
            with self.with_env("1") as bm:
                self.assertTrue(bm.share_release(tempfile.gettempdir()))

    def test_pins_are_dropped_and_core_is_its_newest_package(self):
        with self.with_env("1") as bm:
            self.assertTrue(bm.SHARE_RELEASE)
            deps = bm.dependencies("kpi")
            self.assertEqual(deps["core"], bm.newest_on_disk("core"))
            self.assertEqual(bm.newest_on_disk("core"), "2.4.0")
            for name in bm.MODULES:
                for dep, version in bm.dependencies(name).items():
                    expected = bm.newest_on_disk("core") if dep == "core" else bm.label(bm.MODULES[dep])
                    self.assertEqual(version, expected, (name, dep))

    def test_the_callers_variable_is_put_back(self):
        missing = object()
        before = os.environ.get("EPM_SHARE_RELEASE", missing)
        for preset in ("preset", None):
            if preset is None:
                os.environ.pop("EPM_SHARE_RELEASE", None)
            else:
                os.environ["EPM_SHARE_RELEASE"] = preset
            try:
                with self.with_env("1") as bm:
                    self.assertTrue(bm.SHARE_RELEASE)
                self.assertEqual(os.environ.get("EPM_SHARE_RELEASE", None), preset)
            finally:
                if before is missing:
                    os.environ.pop("EPM_SHARE_RELEASE", None)
                else:
                    os.environ["EPM_SHARE_RELEASE"] = before
        import importlib
        import build_module as bm
        importlib.reload(bm)

    def test_without_the_marker_and_the_variable_the_pins_stand(self):
        # No skip: the mode is read from the two inputs themselves, and each mode has its own assertion.
        import build_module as bm
        marker = os.path.isfile(os.path.join(bm.ROOT, "release.json"))
        variable = bool(os.environ.get("EPM_SHARE_RELEASE"))
        self.assertEqual(bm.SHARE_RELEASE, marker or variable)
        if marker or variable:
            self.assertEqual(bm.dependencies("kpi")["core"], bm.newest_on_disk("core"))
        else:
            self.assertEqual(bm.dependencies("kpi")["core"], "2.3.0")  # the pin on main (EPM-DEC-001-0106)
            self.assertEqual(bm.dependencies("ref-mpc"), {"organization": "2.1.0", "party": "2.0.0"})


if __name__ == "__main__":
    unittest.main()
