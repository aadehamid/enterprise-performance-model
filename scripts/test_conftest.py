"""The scripts' pytest hook (scripts/conftest.py): on main nothing is skipped; in the share release a test marked
with the inputs it reads skips when one of them is not in the tree, with that input in the reason.

Run: uv run --with pytest python -m pytest -q scripts/test_conftest.py
"""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import conftest as hook  # noqa: E402

EVERY_INPUT = tuple(hook.INPUTS)


@pytest.mark.inputs(*EVERY_INPUT)
def test_on_main_every_input_is_present_so_nothing_skips():
    assert hook.missing_inputs(EVERY_INPUT) == []
    assert hook.skip_reason(EVERY_INPUT) is None
    assert hook.skip_reason(EVERY_INPUT, share=True) is None


def test_main_never_skips_even_with_an_input_missing(tmp_path):
    # Release mode off: a missing input is the test's own failure, never a skip.
    assert hook.skip_reason(("records", "gate"), share=False, root=str(tmp_path)) is None


def test_in_release_mode_a_missing_input_skips_and_the_reason_names_it(tmp_path):
    reason = hook.skip_reason(("records", "gate"), share=True, root=str(tmp_path))
    assert reason.startswith("the decision records, the Step 4 gate not in this tree")
    (tmp_path / "business_architecture" / "domain" / "decisions").mkdir(parents=True)
    reason = hook.skip_reason(("records", "gate"), share=True, root=str(tmp_path))
    assert reason.startswith("the Step 4 gate not in this tree")
    (tmp_path / "business_architecture" / "ontology" / "step4").mkdir(parents=True)
    (tmp_path / "business_architecture" / "ontology" / "step4" / "mapping_v2.py").write_text("")
    assert hook.skip_reason(("records", "gate"), share=True, root=str(tmp_path)) is None


def test_an_input_the_table_does_not_know_is_refused():
    with pytest.raises(ValueError, match="unknown inputs"):
        hook.missing_inputs(("records", "moon"))


def test_release_mode_is_read_from_the_marker_file_or_the_variable(tmp_path, monkeypatch):
    monkeypatch.delenv("EPM_SHARE_RELEASE", raising=False)
    assert hook.share_release(str(tmp_path)) is False
    (tmp_path / "release.json").write_text("{}\n")
    assert hook.share_release(str(tmp_path)) is True
    monkeypatch.setenv("EPM_SHARE_RELEASE", "1")
    assert hook.share_release("/nonexistent") is True


def test_every_mark_in_the_scripts_tests_names_a_known_input():
    marks = []
    for name in sorted(os.listdir(HERE)):
        if name.startswith("test_") and name.endswith(".py"):
            with open(os.path.join(HERE, name)) as f:
                marks += re.findall(r"@pytest\.mark\.inputs\(([^)]*)\)", f.read())
    assert marks
    for args in marks:
        names = [a.strip().strip('"') for a in args.split(",") if a.strip() and not a.strip().startswith("*")]
        assert set(names) <= set(hook.INPUTS), args
