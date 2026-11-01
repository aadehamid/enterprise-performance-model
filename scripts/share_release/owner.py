"""The owner's names and handle, which the rules rewrite and the gate flags: never from a tracked file (the
repository's rule that no tracked file names the decision owner, EPM-DEC-001-0049).

They come from EPM_RELEASE_OWNER_NAMES (comma-separated) or, when it is not set, from ~/.config/epm/owner-names.txt
(one per line). Without them the export and the gate refuse to run, since a release cut without them would leak.
"""
import os

CONFIG = os.path.expanduser("~/.config/epm/owner-names.txt")


def owner_names():
    raw = os.environ.get("EPM_RELEASE_OWNER_NAMES", "")
    names = [n.strip() for n in raw.split(",") if n.strip()]
    if not names and os.path.exists(CONFIG):
        with open(CONFIG, encoding="utf-8") as f:
            names = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    if not names:
        raise SystemExit("the owner's names are not configured: set EPM_RELEASE_OWNER_NAMES (comma-separated) or write "
                         + CONFIG + " (one per line); the cut refuses to run without them")
    return sorted(set(names), key=len, reverse=True)  # the longest first, so a full name goes before a first name
