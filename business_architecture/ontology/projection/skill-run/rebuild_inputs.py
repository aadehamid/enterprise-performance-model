"""The input list rebuild.sh hands to run.sh and load.sh (INPUT_LIST): the projection's data and shapes
read from a store export (rdf-store's `export --ttl-dir`, one Turtle file per named graph listed in
graphs.tsv) instead of the repository, in inputs.py's order.

Run: python3 rebuild_inputs.py <export ttl dir> > input-list.tsv
     python3 rebuild_inputs.py compare-triples <rebuild out> <baseline out>
     python3 rebuild_inputs.py compare-reports <rebuild report> <baseline report>

A data file maps to the exported graph named by its own owl:versionIRI; a release's shapes file
(releases/<module>/<version>/shapes.ttl) to the graph <version IRI>/shapes. A shapes file that is not
part of a release (the whole-graph shapes) was never loaded into the store, so it is read from the
repository, and each such line ends with a third field, "repository". Exit 1 when an expected graph is
missing from the export.

compare-triples: loadable.nt and inferred.nt of the rebuild hold the baseline's triples, compared as
RDF 1.1 terms (the store's export writes a literal typed xsd:string as a plain literal, which RDF 1.1
says is the same term; rdflib keeps them apart). compare-reports: both reports hold exactly the two
graph hashes REPORT_HASHES (sorted and shuffled loads), non-empty and equal: the proof that Neo4j holds
the same graph. Each exits 1 on a difference.
"""
import csv
import os
import sys

from rdflib import Graph
from rdflib.namespace import OWL, RDF

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inputs  # noqa: E402


def version_iri(path):
    g = Graph().parse(path)
    found = {str(v) for s in g.subjects(RDF.type, OWL.Ontology) for v in g.objects(s, OWL.versionIRI)}
    if len(found) != 1:
        raise ValueError(f"{os.path.basename(path)}: expected one owl:versionIRI")
    return found.pop()


def input_list(export_dir, data, shapes):
    with open(os.path.join(export_dir, "graphs.tsv"), encoding="utf-8") as f:
        by_graph = {row[1]: os.path.join(export_dir, row[0]) for row in csv.reader(f, delimiter="\t") if row}
    rows, versions = [], {}
    for path in data:
        v = version_iri(path)
        versions[os.path.dirname(os.path.abspath(path))] = v
        if v not in by_graph:
            raise KeyError(v)
        rows.append(("data", by_graph[v]))
    for path in shapes:
        v = versions.get(os.path.dirname(os.path.abspath(path)))
        if v is not None and os.path.basename(path) == "shapes.ttl":
            if v + "/shapes" not in by_graph:
                raise KeyError(v + "/shapes")
            rows.append(("shapes", by_graph[v + "/shapes"]))
        else:
            rows.append(("shapes", os.path.abspath(path), "repository"))
    return rows


# The graph hashes of the sorted and shuffled loads (the skill's load_verify.py report); both reports
# must hold exactly these hash fields, so a changed report cannot skip one.
REPORT_HASHES = ("determinism_hash_sorted", "determinism_hash_shuffled")


def literal_terms(path):
    from rdflib import Literal
    from rdflib.namespace import XSD

    def plain(t):
        return Literal(str(t)) if isinstance(t, Literal) and t.datatype == XSD.string else t
    return {tuple(plain(t) for t in triple) for triple in Graph().parse(path, format="nt")}


def compare_triples(rebuild, baseline):
    problems = []
    for name in ("loadable.nt", "inferred.nt"):
        new, old = literal_terms(os.path.join(rebuild, name)), literal_terms(os.path.join(baseline, name))
        if new != old:
            problems.append(f"{name}: {len(new - old)} triple(s) only in the rebuild, {len(old - new)} only in the baseline")
        else:
            print(f"{name}: the same {len(new)} triples as the baseline (RDF 1.1 terms)")
    return problems


def compare_reports(rebuild, baseline):
    import json
    with open(rebuild) as f:
        new = json.load(f)
    with open(baseline) as f:
        old = json.load(f)
    keys = list(REPORT_HASHES)
    for name, report in (("the rebuilt report", new), ("the baseline report", old)):
        found = sorted(k for k in report if "hash" in k)
        if found != sorted(keys):
            return [f"{name} has hash fields {found}, not exactly {sorted(keys)}"]
    diff = [k for k in keys if not new[k] or new[k] != old[k]]
    if diff:
        return [f"the reports differ in {', '.join(diff)}"]
    print(f"the report's graph hashes equal the baseline's: {', '.join(k + '=' + old[k] for k in keys)}")
    return []


def main(argv):
    if argv and argv[0] in ("compare-triples", "compare-reports"):
        if len(argv) != 3:
            print(f"usage: rebuild_inputs.py {argv[0]} <rebuild> <baseline>", file=sys.stderr)
            return 2
        problems = (compare_triples if argv[0] == "compare-triples" else compare_reports)(argv[1], argv[2])
        for p in problems:
            print(p, file=sys.stderr)
        return 1 if problems else 0
    if len(argv) != 1:
        print("usage: rebuild_inputs.py <export ttl dir>", file=sys.stderr)
        return 2
    try:
        rows = input_list(argv[0], inputs.paths("data"), inputs.paths("shapes"))
    except KeyError as missing:
        print(f"the export has no graph {missing}", file=sys.stderr)
        return 1
    for row in rows:
        print("\t".join(row))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
