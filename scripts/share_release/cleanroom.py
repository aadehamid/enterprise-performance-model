#!/usr/bin/env python3
"""The clean room (plan step 7), with a deadline: a fresh container with an empty home folder, no Git and no login
of this machine, holding only the release zip; it unpacks the zip keeping each file's mode and runs the release's
own check script as a recipient would (./scripts/check.sh, so the executable bit is proven too).

    python3 scripts/share_release/cleanroom.py <release.zip> --log <file> [--timeout <seconds>] [--name <container>]

The image is uv's Python 3.12 image (ghcr.io/astral-sh/uv), so the checks' dependencies can be fetched from
PyPI; nothing else of this machine is mounted or passed. Docker is not inside the room, so the store rows run
outside it (validate.py, on test stores); this proves the setup, the builders, the regression and every test.
The container is started with a name and waited for with a deadline (macOS has no `timeout` command): when the
deadline passes, the container is stopped and the room exits nonzero, so a stalled download or check is a
failed step, never a hung cut.

    python3 scripts/share_release/cleanroom.py run --timeout <seconds> -- <command...>

runs any command with the same deadline (cut.sh's longest steps), killing it on expiry.
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
IMAGE = "ghcr.io/astral-sh/uv:python3.12-bookworm"
SCRIPT = ('set -e; mkdir -p /tmp/home /tmp/room; cd /tmp/room\n'
          'python3 -c "$EXTRACT" /release.zip .\n'
          'cd "$(ls -d */ | head -1)"\n'
          'echo "room: $(pwd); python $(python3 --version); uv $(uv --version); git: $(command -v git || echo none)"\n'
          './scripts/check.sh\n')


def run_with_deadline(cmd, timeout, log, on_expiry=None):
    """Run cmd, copying its output to the log and to stdout, for at most timeout seconds. On expiry the process is
    killed, on_expiry() runs, and the return is -1."""
    with open(log, "w") as out:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        deadline = time.time() + timeout
        import selectors
        sel = selectors.DefaultSelector()
        sel.register(p.stdout, selectors.EVENT_READ)
        while True:
            left = deadline - time.time()
            if left <= 0:
                p.kill()
                out.write(f"\nclean room: the deadline of {timeout} s passed; stopped\n")
                print(f"clean room: the deadline of {timeout} s passed; stopped", flush=True)
                if on_expiry:
                    on_expiry()
                p.wait()
                return -1
            if sel.select(timeout=min(left, 1.0)):
                line = p.stdout.readline()
                if not line:
                    break
                out.write(line); out.flush()
                sys.stdout.write(line); sys.stdout.flush()
        return p.wait()


def room(zip_path, log, timeout, name):
    import publish
    zip_path = os.path.abspath(zip_path)
    cmd = ["docker", "run", "--rm", "--name", name, "-v", f"{zip_path}:/release.zip:ro", "-e", "HOME=/tmp/home",
           "-e", "GIT_CONFIG_NOSYSTEM=1", "-e", "CHECK_WORKERS=4", "-e", f"EXTRACT={publish.EXTRACT_CODE}", "-w", "/tmp",
           IMAGE, "bash", "-c", SCRIPT]
    stop = lambda: subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=120)
    return run_with_deadline(cmd, timeout, log, on_expiry=stop)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("zip", nargs="?", help="the release zip (omit with run)")
    ap.add_argument("--log", default="cleanroom.log")
    ap.add_argument("--timeout", type=int, default=7200)
    ap.add_argument("--name", default="epm-cleanroom")
    ap.add_argument("command", nargs="*", help="with 'run': the command to run under the deadline")
    a = ap.parse_args(argv)
    if a.zip == "run":
        return 0 if run_with_deadline(a.command, a.timeout, a.log) == 0 else 1
    if not a.zip:
        ap.error("the release zip is required")
    return 0 if room(a.zip, a.log, a.timeout, a.name) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
