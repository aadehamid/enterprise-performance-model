"""Build a logical model's two graphs: ER Studio's export as it is, and the annotation layer (EPM-DEC-001-0113).

    python3 build_logical_model.py --export <ttl> --links <csv> --model <slug> --title <text> [--out <folder>]
    ... --write     # also write <out>/<slug>.erstudio.ttl and <out>/<slug>.layer.ttl
    ... --verify    # fail unless both files equal a fresh build

--export, --links, --model and --title may be repeated, once per model, to build several models together. --out
defaults to the first export's folder, so the customer model's graphs stay in the gitignored augment folder beside
its export. The example's build (scripts/check.sh) runs the same builder on the made-up export in example/.

What it does, and when it fails:
- The export is read as it is: ER Studio's namespace kept, nothing re-minted, and <slug>.erstudio.ttl is a byte copy.
- An entity is an owl:Class of the export with a dcterms:identifier. Entities and attributes share one identifier
  space, so the layer is keyed on (model, the identifier of an owl:Class), never on the identifier alone. The builder
  finds each entity's current IRI from its identifier, so an entity renamed in ER Studio keeps its annotations.
- It fails when a row of the links file names an identifier no entity of the export has (an annotated entity has
  gone), when a link target is not in the newest release of its module, or when two entities share an identifier.
- Only `asserted` rows become triples. `doubtful` rows are printed for the decision owner and produce none.
- Every entity of the export gets lm:inModel, and the layer holds the model's lm:LogicalModel individual,
  lm:model/<slug>.
- It fails on an IRI that two models of the build both define (as a subject), except ER Studio's shared vocabulary
  terms (SHARED) and its glossary nodes when both models describe them identically. ER Studio's ontology header
  (:Ontology) is in every export: it is checked per model, never compared across models, and no query
  reads it. Each model's export stays in its own file, so the headers are never merged by the builder; the header's
  creation time is copied onto the model's individual, where it belongs to one model only.
- It checks the export's own key shapes point at the export's entities and their attributes, which question 53
  reads. It does not run them as SHACL, and they are not the module's shapes nor part of the whole-graph gate
  (README, "ER Studio's own shapes").
"""
import argparse
import csv
import glob
import os
import re
import sys

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ONTOLOGY, "release"))
import newest  # noqa: E402

ER = Namespace("https://www.erstudio.com/semanticmodel/")
LM = Namespace("https://w3id.org/lsc/ontology/modules/logical-model/")
SYS = Namespace("https://w3id.org/lsc/ontology/modules/system/")
PARTY = Namespace("https://w3id.org/lsc/ontology/modules/party/")
DP = Namespace("https://w3id.org/lsc/ontology/modules/data-product/")
COLUMNS = ["model", "erstudio_id", "source_system", "describes", "implemented_by", "status", "evidence"]
STATUSES = ("asserted", "doubtful")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# ER Studio's vocabulary, which every export declares the same way: shared by all models, never a collision.
SHARED = {ER[n] for n in ("Attribute", "PrimaryKey", "AlternateKey", "hasPhysicalName", "hasRoleName", "hasNotes",
                          "sourceAttribute", "hasDiscriminator", "businessTerm", "externalTermLinkMissing", "keyType")}
HEADER = ER.Ontology


class BuildError(SystemExit):
    pass


def releases(ontology=ONTOLOGY):
    """The newest release of each module the layer links to."""
    g = Graph()
    for module in ("party", "system", "data-product"):
        g.parse(os.path.join(ontology, "releases", module, newest.newest_version(module, ontology), f"{module}.ttl"))
    return g


def entities(export, errors):
    """{identifier: IRI} for every owl:Class of the export with a dcterms:identifier."""
    found = {}
    for cls in sorted(export.subjects(RDF.type, OWL.Class)):
        for ident in export.objects(cls, DCTERMS.identifier):
            key = str(ident)
            if key in found and found[key] != cls:
                errors.append(f"two entities share identifier {key}: {found[key]} and {cls}")
            found[key] = cls
    return found


def read_links(path, slug, errors):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            errors.append(f"{path}: columns must be {','.join(COLUMNS)}, not {','.join(reader.fieldnames or [])}")
            return []
        rows = [r for r in reader if r["model"] == slug]
    seen = set()
    for r in rows:
        if r["erstudio_id"] in seen:
            errors.append(f"{path}: identifier {r['erstudio_id']} has two rows for model {slug}")
        seen.add(r["erstudio_id"])
        if r["status"] not in STATUSES:
            errors.append(f"{path}: identifier {r['erstudio_id']}: status must be asserted or doubtful, not {r['status']!r}")
    return rows


def check_targets(row, linked, errors):
    """A link target must be in the newest release of its module, as the right kind of thing."""
    where = f"identifier {row['erstudio_id']}"
    system = row["source_system"]
    if system and not ((URIRef(system), RDF.type, SYS.System) in linked or (URIRef(system), RDF.type, PARTY.CustomerSystem) in linked):
        errors.append(f"{where}: source system {system} is not a system of the newest system or party release")
    concept = row["describes"]
    if concept and not (concept.startswith(str(PARTY)) and ((URIRef(concept), RDF.type, OWL.Class) in linked
                                                            or (URIRef(concept), RDF.type, SKOS.Concept) in linked)):
        errors.append(f"{where}: {concept} is not a concept or class of the newest party release")
    impl = row["implemented_by"]
    if impl and not ((URIRef(impl), RDF.type, DP.PlatformTable) in linked or (URIRef(impl), RDF.type, DP.DataProduct) in linked):
        errors.append(f"{where}: {impl} is not a platform table or data product of the newest data-product release")


def check_header(slug, export, errors):
    headers = set(export.subjects(RDF.type, OWL.Ontology))
    if headers - {HEADER}:
        errors.append(f"{slug}: the export declares an ontology other than ER Studio's {HEADER}: "
                      + ", ".join(sorted(str(h) for h in headers - {HEADER})))


def check_key_shapes(slug, export, found, errors):
    """ER Studio's key shapes, which question 53 reads, must point at the export's own entities and attributes: each
    names a key type, targets an entity and constrains that entity's datatype properties. They are not run as SHACL:
    their SPARQL uses ER Studio's prefix without declaring it (no sh:prefixes) and a nested SELECT that does not
    project $this, which pySHACL refuses once a record is there (README, "ER Studio's own shapes")."""
    sh = Namespace("http://www.w3.org/ns/shacl#")
    entity_set = set(found.values())
    for shape in sorted(export.subjects(ER.keyType, None)):
        kinds = set(export.objects(shape, ER.keyType))
        if not kinds <= {ER.PrimaryKey, ER.AlternateKey}:
            errors.append(f"{slug}: key shape {shape} has a key type other than a primary or alternate key")
        targets = set(export.objects(shape, sh.targetClass))
        if len(targets) != 1 or not targets <= entity_set:
            errors.append(f"{slug}: key shape {shape} does not target exactly one entity of the export")
            continue
        target = next(iter(targets))
        for prop in export.objects(shape, sh.property):
            for path in export.objects(prop, sh.path):
                if (path, RDFS.domain, target) not in export:
                    errors.append(f"{slug}: key shape {shape} constrains {path}, which is not an attribute of {target}")


def layer(slug, title, export, rows, found):
    g = Graph()
    g.bind("lm", LM)
    g.bind("dcterms", DCTERMS)
    model = LM["model/" + slug]
    g.add((model, RDF.type, LM.LogicalModel))
    g.add((model, RDFS.label, Literal(title, lang="en")))
    g.add((model, DCTERMS.identifier, Literal(slug)))
    for created in export.objects(HEADER, DCTERMS.created):
        g.add((model, DCTERMS.created, created))
    for entity in found.values():
        g.add((entity, LM.inModel, model))
    for r in rows:
        if r["status"] != "asserted":
            continue
        entity = found[r["erstudio_id"]]
        if r["source_system"]:  # empty when neither the system nor the party module holds the entity's system
            g.add((entity, LM.sourceSystem, URIRef(r["source_system"])))
        if r["describes"]:
            g.add((entity, LM.describes, URIRef(r["describes"])))
        if r["implemented_by"]:
            g.add((entity, LM.implementedBy, URIRef(r["implemented_by"])))
    return g


def defined(export):
    """The IRIs an export defines: its subjects, less the shared vocabulary and the per-model header."""
    return {s for s in export.subjects() if isinstance(s, URIRef)} - SHARED - {HEADER}


def glossary_node(export, iri):
    return (iri, RDF.type, SKOS.ConceptScheme) in export or (iri, RDF.type, SKOS.Concept) in export


def collisions(exports, errors):
    """An IRI two models both define, other than ER Studio's vocabulary and identically described glossary nodes."""
    slugs = sorted(exports)
    for i, a in enumerate(slugs):
        for b in slugs[i + 1:]:
            for iri in sorted(defined(exports[a]) & defined(exports[b])):
                if glossary_node(exports[a], iri) and glossary_node(exports[b], iri) and \
                        set(exports[a].predicate_objects(iri)) == set(exports[b].predicate_objects(iri)):
                    continue
                errors.append(f"models {a} and {b} both define {iri}")


def layer_text(slug, g):
    return (f"# The annotation layer of logical model {slug} (EPM-DEC-001-0113): links from ER Studio's entities to the\n"
            "# ontology, keyed on ER Studio's identifiers. Built by build_logical_model.py. Do not edit by hand.\n"
            + g.serialize(format="turtle")).encode("utf-8")


def build(models, out, ontology=ONTOLOGY):
    """models: [(export, links, slug, title)]. Returns ({file name: bytes}, report lines); raises BuildError."""
    errors, report, files, exports = [], [], {}, {}
    linked = releases(ontology)
    slugs = [m[2] for m in models]
    for slug in slugs:
        if not SLUG.match(slug):
            errors.append(f"model slug {slug!r} must be lower case words joined by hyphens")
    if len(set(slugs)) != len(slugs):
        errors.append("a model is named twice in one build")
    for export_path, links_path, slug, title in models:
        with open(export_path, "rb") as f:
            raw = f.read()
        export = Graph().parse(data=raw.decode("utf-8"), format="turtle")
        exports[slug] = export
        check_header(slug, export, errors)
        found = entities(export, errors)
        check_key_shapes(slug, export, found, errors)
        rows = read_links(links_path, slug, errors)
        for r in rows:
            if r["erstudio_id"] not in found:
                errors.append(f"{slug}: identifier {r['erstudio_id']} is in the links file but no entity of the export has "
                              "it: the annotated entity has gone from the export")
            elif r["status"] == "asserted":
                check_targets(r, linked, errors)
        if errors:
            continue
        g = layer(slug, title, export, rows, found)
        files[f"{slug}.erstudio.ttl"] = raw
        files[f"{slug}.layer.ttl"] = layer_text(slug, g)
        annotated = {r["erstudio_id"] for r in rows}
        report.append(f"{slug}: {len(found)} entities; {sum(r['status'] == 'asserted' for r in rows)} asserted, "
                      f"{sum(r['status'] == 'doubtful' for r in rows)} doubtful, "
                      f"{len(set(found) - annotated)} with no row; layer {len(g)} triples")
        for r in rows:
            if r["status"] == "doubtful":
                report.append(f"  doubtful, no triples: {slug} {r['erstudio_id']} {found[r['erstudio_id']]}: {r['evidence']}")
    # Models already built into the same folder take part in the collision check.
    for path in sorted(glob.glob(os.path.join(out, "*.erstudio.ttl"))):
        slug = os.path.basename(path)[:-len(".erstudio.ttl")]
        if slug not in exports:
            exports[slug] = Graph().parse(path, format="turtle")
    collisions(exports, errors)
    if errors:
        raise BuildError("the logical model does not build:\n  " + "\n  ".join(errors))
    return files, report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("export", "links", "model", "title"):
        ap.add_argument("--" + name, action="append", required=True)
    ap.add_argument("--out")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args(argv)
    if not len(args.export) == len(args.links) == len(args.model) == len(args.title):
        ap.error("give --export, --links, --model and --title once per model")
    out = args.out or os.path.dirname(os.path.abspath(args.export[0]))
    files, report = build(list(zip(args.export, args.links, args.model, args.title)), out)
    print("\n".join(report))
    if args.verify:
        stale = []
        for name, data in sorted(files.items()):
            path = os.path.join(out, name)
            if not os.path.exists(path) or open(path, "rb").read() != data:
                stale.append(name)
        if stale:
            sys.exit(f"not current: {', '.join(stale)}: run build_logical_model.py with --write")
        print("the logical model's graphs are current")
    if args.write:
        os.makedirs(out, exist_ok=True)
        for name, data in sorted(files.items()):
            with open(os.path.join(out, name), "wb") as f:
                f.write(data)
            print(f"wrote {os.path.join(out, name)}")


if __name__ == "__main__":
    main()
