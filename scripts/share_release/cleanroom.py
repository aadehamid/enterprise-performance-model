#!/usr/bin/env python3
"""The clean room (plan step 7), with a deadline: a fresh container with an empty home folder, no Git and no login
of this machine, holding only the release zip; it unpacks the zip keeping each file's mode and runs the release's
own check script as a recipient would (./scripts/check.sh, so the executable bit is proven too).

    python3 scripts/share_release/cleanroom.py <release.zip> --log <file> [--timeout <seconds>] [--name <container>]

The image is uv's Python 3.12 image (ghcr.io/astral-sh/uv), so the checks' dependencies can be fetched from
PyPI; nothing else of this machine is mounted or passed. Docker is not inside the room, so the store rows run
outside it (validate.py, on test stores); this proves the setup, the builders, the regression and every test.
The container is started with a name and waited for with a deadline (procs.stream: reads bounded by the deadline,
the whole process group killed on expiry, the final wait bounded too): when the deadline passes, the container is
removed by name, a removal that fails is logged, and the room exits nonzero, so a stalled download or check is a
failed step, never a hung cut.

    python3 scripts/share_release/cleanroom.py run --timeout <seconds> --log <file> -- <command...>

runs any command under the same deadline (cut.sh's long steps), killing its process group on expiry.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import procs  # noqa: E402

IMAGE = "ghcr.io/astral-sh/uv:python3.12-bookworm"
SCRIPT = ('set -e; mkdir -p /tmp/home /tmp/room; cd /tmp/room\n'
          'python3 -c "$EXTRACT" /release.zip .\n'
          'cd "$(ls -d */ | head -1)"\n'
          'echo "room: $(pwd); python $(python3 --version); uv $(uv --version); git: $(command -v git || echo none)"\n'
          './scripts/check.sh\n')


def remove_container(name):
    """docker rm -f by name; the problem text when it fails, else None."""
    try:
        r = subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True, timeout=120)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return f"could not remove the container {name}: {exc}"
    return None if r.returncode == 0 else f"could not remove the container {name}: docker rm returned {r.returncode}: {r.stderr.strip()[-200:]}"


def room(zip_path, log, timeout, name):
    import publish
    zip_path = os.path.abspath(zip_path)
    cmd = ["docker", "run", "--rm", "--name", name, "-v", f"{zip_path}:/release.zip:ro", "-e", "HOME=/tmp/home",
           "-e", "GIT_CONFIG_NOSYSTEM=1", "-e", "CHECK_WORKERS=4", "-e", f"EXTRACT={publish.EXTRACT_CODE}", "-w", "/tmp",
           IMAGE, "bash", "-c", SCRIPT]
    return procs.stream(cmd, timeout, log, on_expiry=lambda: remove_container(name))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("zip", nargs="?", help="the release zip (omit with run)")
    ap.add_argument("--log", default="cleanroom.log")
    ap.add_argument("--timeout", type=int, default=7200)
    ap.add_argument("--name", default="epm-cleanroom")
    ap.add_argument("command", nargs="*", help="with 'run': the command to run under the deadline")
    a = ap.parse_args(argv)
    if a.zip == "run":
        return 0 if procs.stream(a.command, a.timeout, a.log) == 0 else 1
    if not a.zip:
        ap.error("the release zip is required")
    return 0 if room(a.zip, a.log, a.timeout, a.name) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
