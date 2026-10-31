"""Pytest hooks for the scripts' tests.

The share release (EPM-DEC-001-0110) carries no decision records, no saved answers and no Step 4 evidence,
so the tests of the checks that read them are skipped there, each with its reason. On main every file is
present and nothing is skipped.
"""
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECISIONS = os.path.join(ROOT, "business_architecture", "domain", "decisions")
STEP4_LEDGER = os.path.join(ROOT, "business_architecture", "ontology", "step4", "ledger-v2.md")
STEP4_GATE = os.path.join(ROOT, "business_architecture", "ontology", "step4", "mapping_v2.py")
ANSWERS = os.path.join(ROOT, "business_architecture", "ontology", "step4", "review-evidence", "decision-owner-answers")

# Tests of test_epm_facts.py and test_published_figures.py that read the records, the answers or the Step 4 ledger.
RECORD_TESTS = re.compile(r"quotes|decision|citations|recorded_words|saved_answer|names_the_decision_owner|status|"
                          r"raw_html|review_holds|held_provenance|parser_ignores|wrapped_lists|look_alike|"
                          r"invisible_format|images_are_refused|home_section|sentences_starting")
LEDGER_TESTS = re.compile(r"ledger|backlog|counts_break|phase1|readme_guard|step4_readme|row_reports|sweep")
# Tests of test_docs_html.py that read the decision records or their index page.
PAGE_RECORD_TESTS = re.compile(r"index_row|decision_record|decision_id")


def pytest_collection_modifyitems(config, items):
    no_records = not os.path.isdir(DECISIONS) or not os.path.isdir(ANSWERS)
    no_ledger = not os.path.isfile(STEP4_LEDGER)
    no_gate = not os.path.isfile(STEP4_GATE)
    for item in items:
        if item.fspath.basename == "test_docs_html.py":
            if no_records and PAGE_RECORD_TESTS.search(item.name):
                item.add_marker(pytest.mark.skip(reason="no decision records here (the share release carries none)"))
            continue
        if not item.fspath.basename in ("test_epm_facts.py", "test_published_figures.py"):
            continue
        if no_gate and "facts" in getattr(item, "fixturenames", ()):
            item.add_marker(pytest.mark.skip(reason="no Step 4 gate here, so `epm_facts.py counts` cannot run (the share release leaves it out)"))
        elif no_records and RECORD_TESTS.search(item.name):
            item.add_marker(pytest.mark.skip(reason="no decision records or saved answers here (the share release carries none)"))
        elif no_ledger and LEDGER_TESTS.search(item.name):
            item.add_marker(pytest.mark.skip(reason="no Step 4 ledger here (the share release leaves the Step 4 gate out)"))
