"""Pytest hooks for the scripts' tests.

The share release (EPM-DEC-001-0110) carries no decision records, no saved answers, no Step 4 gate, ledger, backlog
or review evidence, and no Git history. A test that reads one of them says so with the mark `inputs`, naming what it
reads (`@pytest.mark.inputs("records", "answers")`); a test that builds its own inputs in a temporary tree carries no
mark and runs everywhere. In release mode (EPM_SHARE_RELEASE, or release.json at the tree's root) the hook skips a
marked test whose input is not in the tree, with the input in the reason. On main the hook does nothing: release mode
is off, so a missing input fails its test as it always did, and no test is skipped (scripts/test_conftest.py).
"""
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEP4 = os.path.join("business_architecture", "ontology", "step4")
# Each input a test may name: its path from the tree's root, and how a skip reason names it.
INPUTS = {
    "records": (os.path.join("business_architecture", "domain", "decisions"), "the decision records"),
    "answers": (os.path.join(STEP4, "review-evidence", "decision-owner-answers"), "the saved answers"),
    "reviews": (os.path.join(STEP4, "review-evidence"), "the Step 4 review evidence"),
    "backlog": (os.path.join(STEP4, "source-workbook-backlog.md"), "the Step 4 backlog"),
    "ledger": (os.path.join(STEP4, "ledger-v2.md"), "the Step 4 ledger"),
    "gate": (os.path.join(STEP4, "mapping_v2.py"), "the Step 4 gate"),
    "step4-readme": (os.path.join(STEP4, "README.md"), "the Step 4 README"),
    "history": (".git", "the Git history"),
}


def share_release(root=ROOT):
    """Whether this tree is a share release: EPM_SHARE_RELEASE is set, or release.json sits at the tree's root."""
    return bool(os.environ.get("EPM_SHARE_RELEASE")) or os.path.isfile(os.path.join(root, "release.json"))


SHARE_RELEASE = share_release()


def missing_inputs(names, root=ROOT):
    """Of the named inputs, those not in the tree under root, as (name, how the reason names it)."""
    unknown = sorted(set(names) - set(INPUTS))
    if unknown:
        raise ValueError(f"unknown inputs {unknown}; the known ones are {sorted(INPUTS)}")
    return [(n, INPUTS[n][1]) for n in names if not os.path.exists(os.path.join(root, INPUTS[n][0]))]


def skip_reason(names, share=None, root=ROOT):
    """Why a test marked with these inputs skips: None on main (never a skip there), and None in release mode when
    every input it names is in the tree."""
    if not (SHARE_RELEASE if share is None else share):
        return None
    missing = missing_inputs(names, root)
    if not missing:
        return None
    return (", ".join(what for _, what in missing)
            + " not in this tree (the share release leaves them out, EPM-DEC-001-0110)")


def pytest_configure(config):
    config.addinivalue_line("markers", "inputs(name, ...): the live repository inputs the test reads ("
                            + ", ".join(INPUTS) + "); in the share release the test skips when one is not in the tree")


def pytest_collection_modifyitems(config, items):
    for item in items:
        mark = item.get_closest_marker("inputs")
        if mark is None:
            continue
        reason = skip_reason(mark.args)  # raises on an input name the table does not know
        if reason:
            item.add_marker(pytest.mark.skip(reason=reason))
