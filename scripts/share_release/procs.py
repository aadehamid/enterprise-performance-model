"""One way to run a command with a deadline: in its own process group, so that when the deadline passes the whole
group is killed (a stalled download's helper, a builder's child), never only the direct child; with reads that are
bounded by the deadline, so a child that stops writing or closes its output and lingers cannot hold the cut past
it; and with every record scrubbed of secrets (scrubbing.py).

    r = procs.run(args, timeout=..., cwd=..., env=..., input=...)   # a CompletedProcess; raises Expired when the deadline passes
    rc = procs.stream(args, timeout, log, on_expiry=None)           # output copied to the log as it comes; -1 on expiry
"""
import os
import selectors
import signal
import subprocess
import time

import scrubbing


class Expired(Exception):
    """The deadline passed; the group was killed. The message holds no secret."""
    def __init__(self, args, timeout, partial=""):
        self.args, self.timeout, self.partial = args, timeout, partial
        super().__init__(scrubbing.scrub(f"timed out after {timeout} s: {' '.join(args)}", scrubbing.secrets_in(args)))


def kill_group(p):
    """Kill the whole process group the child leads; the child itself when the group is already gone."""
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        p.kill()


def run(args, timeout, cwd=None, env=None, input=None, text=True):
    """subprocess.run with a deadline that kills the process group, output scrubbed of every secret."""
    secrets = scrubbing.secrets_in(args, env)
    p = subprocess.Popen(args, cwd=cwd, env=env, stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text, start_new_session=True)
    try:
        out, err = p.communicate(input=input, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        kill_group(p)
        try:
            out, err = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            out, err = "", ""
        partial = ((exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else str(exc.stdout or "")) + (out or "")
        raise Expired(args, timeout, scrubbing.scrub(partial[-3000:], secrets)) from None
    return subprocess.CompletedProcess(args, p.returncode, scrubbing.scrub(out, secrets) if text else out,
                                       scrubbing.scrub(err, secrets) if text else err)


def stream(args, timeout, log, on_expiry=None, echo=True):
    """Run args, copying its output to the log (and stdout) as it comes, for at most timeout seconds. Reads are bounded
    by the deadline (a partial line or a silent child cannot block past it); the final wait is bounded too (a child
    that closed its output and lingers is killed at the deadline). On expiry the process group is killed, on_expiry()
    runs and its failure is logged, and the return is -1."""
    import sys
    secrets = scrubbing.secrets_in(args)
    deadline = time.time() + timeout
    with open(log, "w") as out:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        fd = p.stdout.fileno()
        os.set_blocking(fd, False)
        sel = selectors.DefaultSelector()
        sel.register(fd, selectors.EVENT_READ)
        pending = b""

        def emit(chunk):
            text = scrubbing.scrub(chunk.decode("utf-8", "replace"), secrets)
            out.write(text); out.flush()
            if echo:
                sys.stdout.write(text); sys.stdout.flush()

        def expire():
            kill_group(p)
            emit((pending + f"\nthe deadline of {timeout} s passed; the step was stopped\n".encode()))
            if on_expiry:
                try:
                    problem = on_expiry()
                except Exception as exc:
                    problem = scrubbing.scrub(repr(exc), secrets)
                if problem:
                    emit(f"after the deadline: {problem}\n".encode())
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                emit(b"the stopped process did not exit within 10 s\n")
            return -1

        while True:
            left = deadline - time.time()
            if left <= 0:
                return expire()
            if not sel.select(timeout=min(left, 1.0)):
                continue
            try:
                chunk = os.read(fd, 65536)
            except BlockingIOError:
                continue
            if not chunk:
                break
            pending += chunk
            if b"\n" in pending:
                lines, pending = pending.rsplit(b"\n", 1)
                emit(lines + b"\n")
        if pending:
            emit(pending)
        left = deadline - time.time()
        try:
            return p.wait(timeout=max(left, 0.01))
        except subprocess.TimeoutExpired:
            return expire()
