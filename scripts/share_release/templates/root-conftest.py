"""The two groups of this release's tests. scripts/check.sh runs everything that proves the ontology is valid, and leaves
out the tests listed in scripts/pinned-tests.txt, which compare this tree with the release as shipped.
scripts/check-pinned.sh sets EPM_PINNED_ONLY and runs only those.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def pinned():
    with open(os.path.join(HERE, "scripts", "pinned-tests.txt"), encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def pytest_collection_modifyitems(config, items):
    listed, only = pinned(), bool(os.environ.get("EPM_PINNED_ONLY"))
    keep, drop = [], []
    for item in items:
        name = getattr(item, "originalname", None) or item.name
        key = os.path.relpath(str(item.fspath), HERE).replace(os.sep, "/") + "::" + name
        (keep if (key in listed) == only else drop).append(item)
    if drop:
        config.hook.pytest_deselected(items=drop)
        items[:] = keep
