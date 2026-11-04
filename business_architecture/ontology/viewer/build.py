"""Build an offline viewer from current Turtle packages and the release catalog."""

import argparse
import base64
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from rdflib import BNode, Graph, Literal, RDF, RDFS, OWL, SKOS
from rdflib.namespace import DCTERMS
from rdflib.compare import to_canonical_graph

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from epm_source_descriptions import neutral_source_description

ONTOLOGY = Path("business_architecture/ontology")
SOURCE_COMMIT = "81f2f63b128820854a25204641b6899d55051ae3"
LABELS = (SKOS.prefLabel, RDFS.label, DCTERMS.title)
PARENTS = (RDFS.subClassOf, RDFS.subPropertyOf, SKOS.broader)
SUPPORTING_KINDS = ("Anonymous node", "Evidence", "Metadata", "Constraint")


def release_files(root):
    """Only current packages; examples and history are outside this population."""
    root = Path(root)
    packages = root / ONTOLOGY / "releases"
    files = []
    for module in sorted(packages.iterdir()):
        if not module.is_dir() or module.name == "previous":
            continue
        versions = [
            p
            for p in module.iterdir()
            if p.is_dir() and re.fullmatch(r"\d+\.\d+\.\d+", p.name)
        ]
        if not versions:
            continue
        manifest_path = max(
            versions, key=lambda p: tuple(map(int, p.name.split(".")))
        ) / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        if (
            manifest["module"] != module.name
            or manifest["version"] != manifest_path.parent.name
        ):
            raise ValueError(f"Manifest identity mismatch: {manifest_path}")
        if manifest.get("release_candidate"):
            raise ValueError(f"Unreleased package: {manifest_path}")
        for name, expected in sorted(manifest["files"].items()):
            if not name.endswith(".ttl"):
                continue
            path = manifest_path.parent / name
            if path.resolve().parent != manifest_path.parent.resolve():
                raise ValueError(f"Invalid manifest path: {name}")
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError(f"Package hash mismatch: {path}")
            files.append((path, module.name, manifest["version"]))
    if not files:
        raise ValueError("No released Turtle packages found")
    catalog = packages / "catalog.ttl"
    if catalog.exists():
        files.append((catalog, None, None))
    return files


def pinned_source(root):
    head = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != SOURCE_COMMIT:
        raise ValueError(f"Expected source release {SOURCE_COMMIT}; got {head}")
    changed = subprocess.check_output(
        [
            "git",
            "-C",
            str(root),
            "status",
            "--porcelain",
            "--",
            str(ONTOLOGY / "releases"),
        ],
        text=True,
    )
    if changed:
        raise ValueError("Source release packages have local changes")


def term_id(value):
    return "_:" + str(value) if isinstance(value, BNode) else str(value)


def short(value):
    return str(value).rstrip("/").rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def build_data(root):
    graph = Graph()
    membership = defaultdict(set)
    inputs = []
    for path, module, version in release_files(root):
        part = to_canonical_graph(Graph().parse(path, format="turtle"))
        # Canonical blank IDs from different files must remain scoped to their file.
        prefix = hashlib.sha256(str(path.relative_to(root)).encode()).hexdigest()[:16]

        def scoped(node):
            return BNode(prefix + str(node)) if isinstance(node, BNode) else node

        for s, p, o in part:
            triple = tuple(scoped(n) for n in (s, p, o))
            graph.add(triple)
            if module:
                membership[triple[0]].add((module, version))
        inputs.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    nodes = []
    subjects = set(graph.subjects())
    for s in sorted(subjects, key=term_id):
        types = set(graph.objects(s, RDF.type))
        labels = [
            o for p in LABELS for o in graph.objects(s, p) if isinstance(o, Literal)
        ]
        labels.sort(key=lambda o: (o.language not in ("en", None), str(o)))
        label = (
            str(labels[0])
            if labels
            else ("Anonymous constraint" if isinstance(s, BNode) else short(s))
        )
        kind = "Individual"
        if isinstance(s, BNode):
            kind = "Anonymous node"
        elif OWL.Class in types or RDFS.Class in types:
            kind = "Class"
        elif any(
            t in types
            for t in (
                RDF.Property,
                OWL.ObjectProperty,
                OWL.DatatypeProperty,
                OWL.AnnotationProperty,
            )
        ):
            kind = "Property"
        elif SKOS.Concept in types:
            kind = "Concept"
        elif SKOS.ConceptScheme in types:
            kind = "Concept scheme"
        elif OWL.Ontology in types or any(
            short(t) in ("Catalog", "Dataset", "Distribution") for t in types
        ):
            kind = "Metadata"
        elif any(
            short(t) in ("CanonicalFact", "EvidenceRow", "BibliographicResource")
            for t in types
        ):
            kind = "Evidence"
        elif any(str(t).startswith("http://www.w3.org/ns/shacl#") for t in types):
            kind = "Constraint"
        values = []
        for p, o in sorted(
            graph.predicate_objects(s),
            key=lambda v: (str(v[0]), term_id(v[1]), v[1].n3()),
        ):
            values.append(
                {
                    "p": str(p),
                    "v": term_id(o),
                    "literal": isinstance(o, Literal),
                    "lang": o.language if isinstance(o, Literal) else None,
                    "datatype": str(o.datatype)
                    if isinstance(o, Literal) and o.datatype
                    else None,
                }
            )
        nodes.append(
            {
                "id": term_id(s),
                "label": label,
                "kind": kind,
                "modules": [
                    {"name": m, "version": v}
                    for m, v in sorted(membership[s] or {("Release metadata", "EPM 1.0")})
                ],
                "parents": sorted(
                    term_id(o)
                    for p in PARENTS
                    for o in graph.objects(s, p)
                    if o in subjects
                ),
                "values": values,
            }
        )
    counts = dict(sorted(Counter(n["kind"] for n in nodes).items()))
    return {
        "release": "EPM 1.0",
        "sourceCommit": SOURCE_COMMIT,
        "nodes": nodes,
        "inputs": inputs,
        "counts": counts,
        "triples": len(graph),
        "supportingKinds": SUPPORTING_KINDS,
        "terms": sum(n["kind"] not in SUPPORTING_KINDS for n in nodes),
    }


def build(root, output, compare=None, require_pin=True):
    root = Path(root).resolve()
    if require_pin:
        pinned_source(root)
    data = build_data(root)
    if compare:
        compare = Path(compare).resolve()
        expected_inputs = [
            {
                "path": str(path.relative_to(root)),
                "sha256": hashlib.sha256(
                    neutral_source_description(path.read_bytes().decode("utf-8")).encode("utf-8")
                ).hexdigest(),
            }
            for path, _, _ in release_files(root)
        ]
        other_inputs = [
            {
                "path": str(path.relative_to(compare)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path, _, _ in release_files(compare)
        ]
        if other_inputs != expected_inputs:
            raise ValueError("Cut packages differ from the pinned viewer release")
        # Emit the verified cut's data, so its source titles and file hashes agree
        # with the files recipients receive. Only the exact source-title substitution
        # above may differ from the pinned release, even in a metadata graph.
        data = build_data(compare)
    payload = (
        json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace("&", "\\u0026")
    )
    font_css = "".join(
        '@font-face{font-family:"IBM Plex Sans";font-style:normal;font-weight:'
        + weight
        + ";src:url(data:font/woff2;base64,"
        + base64.b64encode(
            (HERE / "fonts" / ("plex-" + weight + ".woff2")).read_bytes()
        ).decode()
        + ') format("woff2");}'
        for weight in ("400", "500", "600")
    )
    page = (
        (HERE / "viewer.html")
        .read_text()
        .replace("/* EMBEDDED_FONTS */", font_css)
    )
    import html

    page = page.replace(
        "FONT_LICENSE_TEXT", html.escape((HERE / "fonts/OFL.txt").read_text())
    )
    page = page.replace("/* EMBEDDED_DATA */", payload)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page)
    return {k: data[k] for k in ("sourceCommit", "counts", "terms", "triples")}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--compare")
    args = p.parse_args()
    print(json.dumps(build(args.source, args.out, args.compare), indent=2))


if __name__ == "__main__":
    main()
