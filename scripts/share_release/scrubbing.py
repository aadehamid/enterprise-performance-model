"""One scrubber for every record this tool writes: the secrets a command was given, the secrets in the environment
it inherited, and every secret registered during the run (the generated Neo4j password, a login read from a file)
are replaced by *** in commands, output tails, timeouts' partial output and exception text, before anything is
recorded. A secret of any length is scrubbed (a one-character password garbles the record; that is the right
side to err on).
"""
import os
import re

SECRET_FLAGS = ("--password", "--token", "--access-token")
SECRET_KEYS = re.compile(r"PASSWORD|TOKEN|SECRET|AUTH", re.I)
SECRETS = set()  # registered during the run


def register(value):
    if value:
        SECRETS.add(str(value))


def secrets_in(args=(), env=None, inherited=None):
    """The secrets a command carries or can see: a value after a secret flag, a --flag=value secret, a value of any
    secret-named variable in the environment it is given or inherits, and everything registered."""
    found = set(SECRETS)
    args = list(args or ())
    for i, a in enumerate(args):
        if i and args[i - 1] in SECRET_FLAGS:
            found.add(a)
        for flag in SECRET_FLAGS:
            if a.startswith(flag + "="):
                found.add(a[len(flag) + 1:])
    for source in (env or {}, os.environ if inherited is None else inherited):
        for k, v in source.items():
            if SECRET_KEYS.search(k) and v:
                found.add(v)
    return {s for s in found if s}


def scrub(text, secrets=None):
    """text with every secret replaced by ***, longest first."""
    if text is None:
        return text
    text = str(text)
    for s in sorted(secrets if secrets is not None else secrets_in(), key=len, reverse=True):
        text = text.replace(s, "***")
    return text
