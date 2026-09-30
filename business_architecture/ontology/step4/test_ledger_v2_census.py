#!/usr/bin/env python3
"""Regression test: ledger_v2.py's intake census must match the pinned baseline.

parse_blocks split the Turtle on every blank line, including the one inside
the triple-quoted scopeNote of proc:L2-refinery-asset-reliability-and-
turnaround-coordination. The rest of that concept was read as a block whose
"subject" was the word "Does", and its 5 intake: triples were lost
(5,566 counted vs 5,571). Expected counts below were grounded with an RDF
parser (rdflib) on baseline/step3-taxonomy.ttl at PINNED_SHA 6a155bc.
"""
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
EXPECTED = {
    "intake:apqcDecision": 500, "intake:conceptTypeCheck": 488,
    "intake:keyInputs": 485, "intake:level": 683, "intake:parkedChildren": 5,
    "intake:primaryOutput": 485, "intake:primaryPurpose": 488,
    "intake:processHorizon": 485, "intake:referenceSources": 488,
    "intake:relatedConcepts": 486, "intake:responsibleDomain": 485,
    "intake:status": 2, "intake:terminologyNotes": 491,
}
EXPECTED_TOTAL = 5571


def main():
    failures = []
    with tempfile.TemporaryDirectory() as cwd:
        r = subprocess.run([sys.executable, os.path.join(BASE, "ledger_v2.py")],
                           cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or ["(no output)"]
        failures.append(f"ledger_v2.py exited {r.returncode}; {tail[0]}")
    m = re.search(r"intake triples: (\d+)", r.stdout)
    if not m or int(m.group(1)) != EXPECTED_TOTAL:
        failures.append(f"intake total {m.group(1) if m else 'missing'}, expected {EXPECTED_TOTAL}")
    got = {p: int(n) for p, n in re.findall(r"^\s+(intake:\w+): (\d+)$", r.stdout, re.M)}
    for p, n in EXPECTED.items():
        if got.get(p) != n:
            failures.append(f"{p}: {got.get(p)} counted, expected {n}")
    for f in failures:
        print("FAIL", f)
    print("PASS" if not failures else f"{len(failures)} failure(s)")
    return 1 if failures else 0


def test_ledger_v2_census():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
