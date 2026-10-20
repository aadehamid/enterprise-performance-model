"""Step 11 regression: run the competency-question queries against a release (EPM-DEC-001-0019).

expected.csv gives each of the 44 questions in competency-questions.md a status:
answerable (its queries must run), partial (the graph part's queries must run;
waits_for names the rest), or waits:<step or decision> (no query yet). A query
whose first comment line says "(must be none)" must return zero rows; every other
query must return at least one row. Prints a coverage summary; exits 1 on a failure.

Run: python3 run.py [path/to/core.ttl]   (default: the current core release; the module graphs in
MODULES are always loaded with it)
"""
import csv
import os
import sys
from collections import Counter

from rdflib import Graph

HERE = os.path.dirname(os.path.abspath(__file__))
RELEASE = os.path.join(HERE, "..", "releases", "core", "2.1.0", "core.ttl")
# The module graphs loaded with the release (Step 5: roles and RACI assignments; Step 7: the kpi, data-product, value-stream, system, lane and market-data modules).
MODULES = [os.path.join(HERE, "..", "organization", n) for n in ("vocabulary.ttl", "roles.ttl", "assignments.ttl")] \
    + [os.path.join(HERE, "..", "kpi", n) for n in ("vocabulary.ttl", "measures.ttl")] \
    + [os.path.join(HERE, "..", "data-product", n) for n in ("vocabulary.ttl", "data-products.ttl")] \
    + [os.path.join(HERE, "..", "value-stream", n) for n in ("vocabulary.ttl", "value-streams.ttl")] \
    + [os.path.join(HERE, "..", "system", n) for n in ("vocabulary.ttl", "systems.ttl")] \
    + [os.path.join(HERE, "..", "lane", n) for n in ("vocabulary.ttl", "lanes.ttl")] \
    + [os.path.join(HERE, "..", "market-data", n) for n in ("vocabulary.ttl", "market-data.ttl")] \
    + [os.path.join(HERE, "..", "placement", "vocabulary.ttl")] \
    + [os.path.join(HERE, "..", "authority", n) for n in ("vocabulary.ttl", "source-tiers.ttl")]  # Step 7 overlays, placement kinds, source tiers
QUESTIONS = os.path.join(HERE, "..", "competency-questions.md")


def load_expected():
    with open(os.path.join(HERE, "expected.csv"), newline="") as f:
        return list(csv.DictReader(f))


def check(graph, rows):
    """Return (failures, status counts). A failure is a string naming the query."""
    failures, statuses = [], Counter()
    for row in rows:
        status = row["status"]
        statuses[status.split(":")[0]] += 1
        queries = [q for q in row["queries"].split(";") if q]
        if status in ("answerable", "partial") and not queries:
            failures.append(f"Q{row['question']}: {status} with no query")
        if status.startswith("waits:") and queries:
            failures.append(f"Q{row['question']}: waits but lists queries")
        for name in queries:
            with open(os.path.join(HERE, "queries", name)) as f:
                text = f.read()
            n = len(list(graph.query(text)))
            must_be_none = "(must be none)" in text.splitlines()[0]
            if must_be_none and n:
                failures.append(f"Q{row['question']} {name}: {n} rows, expected none")
            if not must_be_none and not n:
                failures.append(f"Q{row['question']} {name}: no rows")
    return failures, statuses


def load(path):
    """The release at path, plus the module graphs."""
    graph = Graph()
    for part in [path] + MODULES:
        graph.parse(part)
    return graph


def main(path):
    rows = load_expected()
    graph = load(path)
    failures, statuses = check(graph, rows)
    print(f"competency coverage on {os.path.relpath(path, HERE)}: {len(rows)} questions; "
          f"answerable {statuses['answerable']}, partial {statuses['partial']}, waiting {statuses['waits']}")
    for line in failures:
        print("FAIL", line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else RELEASE))
