"""Print the projection's inputs for the ontology-to-lpg skill's scripts, one absolute path per line.

    python3 inputs.py data      the released module files, from ../pipeline.py's INPUTS
    python3 inputs.py shapes    the shape files, from ../pipeline.py's SHAPES
    python3 inputs.py releases  the releases folder (check_projection_rules.py --releases)

The lists come from ../pipeline.py, so the committed CI pipeline and these scripts read one list.
Importing pipeline.py runs nothing: its main() runs only under __main__. It imports rdflib and
pyshacl, so run this with both (uv run --no-project --with rdflib --with pyshacl python3 inputs.py).
"""
import os
import sys

sys.dont_write_bytecode = True  # no __pycache__ beside pipeline.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pipeline  # noqa: E402

ONTOLOGY = os.path.realpath(pipeline.ONTOLOGY)


def paths(kind):
    if kind == "data":
        return [os.path.join(ONTOLOGY, p) for p in pipeline.INPUTS]
    if kind == "shapes":
        return [os.path.join(ONTOLOGY, p) for p in pipeline.SHAPES]
    if kind == "releases":
        return [os.path.join(ONTOLOGY, "releases")]
    raise ValueError(kind)


def main(argv):
    if len(argv) != 1 or argv[0] not in ("data", "shapes", "releases"):
        print("usage: inputs.py data|shapes|releases", file=sys.stderr)
        return 2
    for p in paths(argv[0]):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
