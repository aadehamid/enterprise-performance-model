"""Frozen sources: the builders read a frozen copy of the process map when one exists, else Git."""
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
    def test_pins_are_dropped_and_core_is_its_newest_package(self):
        import importlib
        os.environ["EPM_SHARE_RELEASE"] = "1"
        try:
            import build_module as bm
            bm = importlib.reload(bm)
            self.assertTrue(bm.SHARE_RELEASE)
            deps = bm.dependencies("kpi")
            self.assertEqual(deps["core"], bm.newest_on_disk("core"))
            self.assertEqual(bm.newest_on_disk("core"), "2.4.0")
            for name in bm.MODULES:
                for dep, version in bm.dependencies(name).items():
                    expected = bm.newest_on_disk("core") if dep == "core" else bm.label(bm.MODULES[dep])
                    self.assertEqual(version, expected, (name, dep))
        finally:
            del os.environ["EPM_SHARE_RELEASE"]
            importlib.reload(bm)

    def test_on_main_the_pins_stand(self):
        import build_module as bm
        self.assertFalse(bm.SHARE_RELEASE)
        self.assertEqual(bm.dependencies("kpi")["core"], "2.3.0")


if __name__ == "__main__":
    unittest.main()
