"""Loads a release's logical models into the four ontology stores, when its newest releases hold the logical-model
module (EPM-DEC-001-0113, amendment "the stores"). main holds no such package, so in main every command here finds
nothing to load and changes nothing; the share release's cut builds the package (scripts/share_release/augment.py).

    python3 logical_models.py load --store driver --store jena ... [--skills <folder>]   # what the newest releases hold
    python3 logical_models.py rows                                                    # the subgraph's nodes and edges, as JSON

What each store gets, beside the module's vocabulary, which the projection loads like every package's:
- Jena and Delta: every package graph of the newest releases, each as a named graph, <version IRI>/<file name without
  .ttl>. A package graph is a Turtle file the package's manifest.json lists beside its content and its release graphs
  (build_module.py's "graphs"): for logical-model, each model's ER Studio export (<slug>.erstudio.ttl) and annotation
  layer (<slug>.layer.ttl). Jena takes them in one SPARQL Update request, Delta as rows of the triple table in the
  rdf-store skill's columns, from that skill's own rdfstore.py (under --skills), so the rows read back as its rows do.
  sync_stores.py's drift check counts them with the release graphs (jena_graphs).
- The local Neo4j and AuraDB: each model in full as its own subgraph, apart from the ontology's Resource nodes, as the
  technical graph's Tech nodes are (graph_rows has the nodes and edges). The load replaces it in one transaction with
  its marker, a digest of the model graph files, and commits only when every edge found its target and the ontology's
  counts did not move (the demo's tech_graph.replace_subgraph, which the technical graph loads through too). The
  projection's counts, hash and round trip read Resource nodes only, so they never read the subgraph; sync_stores.py
  check compares it with the package's graphs on an lm:<store> line, by marker and content fingerprint.

The labels, node shapes and loader are Claude's build choice, delegated under EPM-DEC-001-0028. Logins come from the
files sync_stores.py reads (EPM_STORES_JSON names another environment's); none is printed.
Needs rdflib; load also needs neo4j for the Neo4j stores, pyoxigraph for Jena and Delta, and databricks-sql-connector
for Delta (uv run --with ...).
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys

import sync_stores as ss

MODULE = "logical-model"
LABEL = "LogicalModel"  # every node of the subgraph; never Resource
MARKER_LABEL = "LogicalModelMarker"
KIND = "model"  # an edge between two nodes of the subgraph, as tech_graph's "tech"
NEO4J_NODES = f"MATCH (n:{LABEL}) RETURN labels(n) AS labels, properties(n) AS p"
NEO4J_EDGES = (f"MATCH (a:{LABEL})-[r]->(b) RETURN a.uri AS s, type(r) AS t, b.uri AS o, b:Resource AS ontology, "
               "properties(r) AS p")
RELEASES = os.path.join(ss.REPO, "business_architecture", "ontology", "releases")
BUILDER = os.path.join(ss.REPO, "business_architecture", "ontology", "logical-model")


# ---------- what the newest releases hold ----------

def held(releases=None):
    """True when the newest version folder of some module holds package graphs, read from its manifest.json with the
    standard library only, so rebuild_stores.py can plan the load without rdflib. load reads the catalog itself."""
    releases = releases or RELEASES
    if not os.path.isdir(releases):
        return False
    for module in sorted(os.listdir(releases)):
        folder = os.path.join(releases, module)
        versions = [v for v in os.listdir(folder) if all(p.isdigit() for p in v.split("."))] if os.path.isdir(folder) else []
        if not versions:
            continue
        manifest = os.path.join(folder, max(versions, key=lambda v: tuple(int(p) for p in v.split("."))), "manifest.json")
        if os.path.isfile(manifest) and ss.extra_graph_files(module, json.load(open(manifest, encoding="utf-8"))):
            return True
    return False


def newest():
    return ss.newest_releases(ss.catalog_datasets(ss.repo_file(ss.CATALOG)))


def package_graphs(releases=None):
    """{graph IRI: path under the repository} of every package graph of the newest releases (sync_stores.package_graphs)."""
    found = {}
    for iri in releases if releases is not None else newest():
        found.update(ss.package_graphs(iri))
    return found


def models(releases=None):
    """[(slug, export path, layer path)] of the newest logical-model package, from its manifest; [] when the newest
    releases hold no logical-model module, as in main. A model whose export or layer is missing stops the load."""
    iri = next((i for i in (releases if releases is not None else newest()) if i.rsplit("/", 2)[-2] == MODULE), None)
    if iri is None:
        return []
    graphs = sorted(ss.package_graphs(iri).values())
    slugs = sorted({os.path.basename(p).split(".")[0] for p in graphs if p.endswith((".erstudio.ttl", ".layer.ttl"))})
    found = []
    for slug in slugs:
        export, layer = (next((p for p in graphs if os.path.basename(p) == f"{slug}.{k}.ttl"), None) for k in ("erstudio", "layer"))
        if not export or not layer:
            raise SystemExit(f"{MODULE}: model {slug} lacks its {'export' if not export else 'layer'} in the package's manifest")
        found.append((slug, export, layer))
    return found


# ---------- the subgraph ----------

def builder():
    """The module's builder, whose namespaces and entity rule (an owl:Class of the export with a dcterms:identifier) the
    subgraph shares, so the share release's IRI rewrite reaches both."""
    if BUILDER not in sys.path:
        sys.path.insert(0, BUILDER)
    import build_logical_model as blm
    return blm


def literals(g, *subjects, names=None):
    """A node's properties from its literals: rdfs:label is name, dcterms:identifier erstudio_id, dcterms:description
    description, and any other literal its predicate's local name. A key with two values holds a sorted list."""
    from rdflib import Literal
    from rdflib.namespace import DCTERMS, RDFS
    tg = ss.demo_graph()
    names = {RDFS.label: "name", DCTERMS.identifier: "erstudio_id", DCTERMS.description: "description", **(names or {})}
    found = {}
    for s in subjects:
        for p, o in g.predicate_objects(s):
            if isinstance(o, Literal):
                found.setdefault(names.get(p, tg.local_name(p)), set()).add(tg.neo4j_value(o.toPython()))
    return {k: next(iter(v)) if len(v) == 1 else sorted(map(str, v)) for k, v in found.items()}


def graph_rows(model_files):
    """Nodes ({"labels", "props"}) and edges ({"s", "t", "o", "ontology", "p"}) of the subgraph, from each model's export
    and layer. Every node is labelled LogicalModel and one of:
      Model      the model's lm:LogicalModel individual: uri, slug, name (its title), created
      Entity     an owl:Class of the export with a dcterms:identifier: uri, models, name, erstudio_id, description and
                 its other literals
      Attribute  a datatype property of the export whose domain is an entity, with the literals of its ER Studio
                 attribute (:sourceAttribute) and its own: uri, models, name, datatype (its range's local name),
                 description, erstudio_id, business_term (the IRI of its glossary term, when it has one)
      Key        a key shape of the export (:keyType): uri, models, name (the shape's local name), key_type, message
    and the edges are
      (Entity)-[:IN_MODEL]->(Model), (Entity)-[:HAS_ATTRIBUTE]->(Attribute), (Entity)-[:HAS_KEY]->(Key),
      (Key)-[:ON_ATTRIBUTE]->(Attribute), (Entity)-[:RELATES_TO {uri, name}]->(Entity) for each object property between
      two entities (the inverse twin that ER Studio adds, an owl:inverseOf of another such property, is left out), and
      (Entity)-[:SOURCE_SYSTEM|DESCRIBES|IMPLEMENTED_BY]->(:Resource) for each link of its layer.
    A node two models share (a reused attribute, which the builder allows only when both describe it the same way) is
    one node, with both slugs in models."""
    from rdflib import Graph, URIRef
    from rdflib.namespace import DCTERMS, OWL, RDF, RDFS
    blm, tg = builder(), ss.demo_graph()
    sh = "http://www.w3.org/ns/shacl#"
    nodes, edges = {}, set()

    def node(uri, kind, props, slug=None):
        n = nodes.setdefault(str(uri), {"labels": [LABEL, kind], "props": {"uri": str(uri)}})
        n["props"].update(props)
        if slug:
            n["props"]["models"] = sorted({*n["props"].get("models", []), slug})

    for slug, export_path, layer_path in model_files:
        export = Graph().parse(os.path.join(ss.REPO, export_path), format="turtle")
        layer = Graph().parse(os.path.join(ss.REPO, layer_path), format="turtle")
        entities = set(blm.entities(export, []).values())
        for m in layer.subjects(RDF.type, blm.LM.LogicalModel):
            node(m, "Model", {"slug": slug, **literals(layer, m, names={DCTERMS.identifier: "slug"})})
        for e in entities:
            node(e, "Entity", literals(export, e), slug)
        attributes = set()
        for prop in sorted(export.subjects(RDF.type, OWL.DatatypeProperty)):
            owners = [d for d in export.objects(prop, RDFS.domain) if d in entities]
            if not owners:
                continue
            sources = list(export.objects(prop, blm.ER.sourceAttribute))
            props = literals(export, *sources, prop)
            ranges = sorted(tg.local_name(r) for r in export.objects(prop, RDFS.range))
            if ranges:
                props["datatype"] = ranges[0] if len(ranges) == 1 else ranges
            terms = sorted(str(t) for s in sources for t in export.objects(s, blm.ER.businessTerm))
            if terms:
                props["business_term"] = terms[0] if len(terms) == 1 else terms
            node(prop, "Attribute", props, slug)
            attributes.add(prop)
            for d in owners:
                edges.add((str(d), "HAS_ATTRIBUTE", str(prop), False, ()))
        for key in sorted(export.subjects(blm.ER.keyType, None)):
            props = {"name": tg.local_name(key), **{k: v for k, v in literals(export, key).items() if k != "name"}}
            types = sorted(tg.local_name(t) for t in export.objects(key, blm.ER.keyType))
            props["key_type"] = types[0] if len(types) == 1 else types
            node(key, "Key", props, slug)
            for target in export.objects(key, URIRef(sh + "targetClass")):
                if target in entities:
                    edges.add((str(target), "HAS_KEY", str(key), False, ()))
            for shape in export.objects(key, URIRef(sh + "property")):
                for path in export.objects(shape, URIRef(sh + "path")):
                    if path in attributes:
                        edges.add((str(key), "ON_ATTRIBUTE", str(path), False, ()))
        between = {r for r in export.subjects(RDF.type, OWL.ObjectProperty)
                   if set(export.objects(r, RDFS.domain)) & entities and set(export.objects(r, RDFS.range)) & entities}
        for r in sorted(between):
            if set(export.objects(r, OWL.inverseOf)) & between:
                continue  # ER Studio's inverse twin of a relationship already drawn
            label = sorted(str(n) for n in export.objects(r, RDFS.label))
            p = (("uri", str(r)),) + ((("name", label[0]),) if label else ())
            for d in export.objects(r, RDFS.domain):
                for e in export.objects(r, RDFS.range):
                    if d in entities and e in entities:
                        edges.add((str(d), "RELATES_TO", str(e), False, p))
        for e, m in layer.subject_objects(blm.LM.inModel):
            edges.add((str(e), tg.edge_type(blm.LM.inModel), str(m), False, ()))
        for link in (blm.LM.sourceSystem, blm.LM.describes, blm.LM.implementedBy):
            for e, target in layer.subject_objects(link):
                edges.add((str(e), tg.edge_type(link), str(target), True, ()))
    return ([nodes[u] for u in sorted(nodes)],
            [{"s": s, "t": t, "o": o, "ontology": ont, "p": dict(p)} for s, t, o, ont, p in sorted(edges)])


def digest(model_files):
    """The SHA-256 of the model graph files, each file's name and bytes in name order: what a Neo4j store's
    LogicalModelMarker records."""
    h = hashlib.sha256()
    for path in sorted(p for _, *paths in model_files for p in paths):
        with open(os.path.join(ss.REPO, path), "rb") as f:
            h.update(os.path.basename(path).encode() + b"\0" + f.read() + b"\0")
    return h.hexdigest()


def content(nodes, edges):
    """The subgraph reduced to one SHA-256 (tech_graph.neo4j_fingerprint), from graph_rows or from a store's rows."""
    return ss.demo_graph().neo4j_fingerprint(nodes, edges)


# ---------- the drift check ----------

def read_markers(stores):
    """Each named Neo4j store's LogicalModelMarker, with the store's live content fingerprint as "content": a dict,
    None when it has none, or "unreachable (<error>)"."""
    markers = {}
    for store in [s for s in stores if s in ss.NEO4J_STORES]:
        try:
            driver, session = ss.neo4j_session(store)
            with driver, session:
                rec = session.run(f"MATCH (m:{MARKER_LABEL}) RETURN properties(m) AS p").single()
                markers[store] = dict(rec["p"]) if rec else None
                if markers[store]:
                    markers[store]["content"] = content(list(session.run(NEO4J_NODES)), list(session.run(NEO4J_EDGES)))
        except Exception as err:  # as sync_stores' readers: a store that can't be read says so, with the reason
            markers[store] = f"unreachable ({type(err).__name__})"
    return markers


def drift(markers, want_digest, want_content, stores):
    """Each named Neo4j store's status for the subgraph: current only when its marker names the package's model files
    and its content equals them; behind (other model files), changed (the content differs while the marker matches: a
    hand edit, say), unmarked (no marker: a reload wiped it, or it was never loaded) or unreachable."""
    rows = []
    for store in [s for s in stores if s in ss.NEO4J_STORES]:
        m = markers.get(store)
        if isinstance(m, str):
            rows.append((store, "unreachable", m))
        elif not m:
            rows.append((store, "unmarked", f"no logical-model marker: run logical_models.py load --store {store}, or sync"))
        elif m.get("digest") != want_digest:
            rows.append((store, "behind", f"marked {m.get('marked_at')} from other model files ({str(m.get('digest'))[:12]}, "
                                          f"not {want_digest[:12]})"))
        elif m.get("content") != want_content:
            rows.append((store, "changed", "its logical models differ from the package's graphs although its marker matches; "
                                           f"run logical_models.py load --store {store}, or sync"))
        else:
            rows.append((store, "current", f"marked {m.get('marked_at')} with the model files' digest {want_digest[:12]}"))
    return rows


def check(stores):
    """The lm:<store> rows of sync_stores.py check: none when the newest releases hold no logical-model module."""
    files = models()
    if not files:
        return []
    nodes, edges = graph_rows(files)
    return drift(read_markers(stores), digest(files), content(nodes, edges), stores)


# ---------- loading ----------

def rdfstore(skills):
    """The rdf-store skill's rdfstore.py, whose dataset, row and insert functions the driver's loads use too."""
    path = os.path.join(os.path.expanduser(skills), "rdf-store", "scripts", "rdfstore.py")
    spec = importlib.util.spec_from_file_location("rdfstore", path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(path))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(os.path.dirname(path))
    return module


def dataset(rs, graphs):
    """The package graphs as one rdfstore dataset, each file under its graph IRI."""
    paths = [os.path.join(ss.REPO, p) for p in graphs.values()]
    return rs.pack(paths, {os.path.realpath(os.path.join(ss.REPO, p)): iri for iri, p in graphs.items()})


def load_jena(rs, graphs):
    """Replaces each package graph in Jena in one SPARQL Update request (rdfstore's FusekiStore.publish)."""
    base = ss.JENA_QUERY.rsplit("/", 1)[0]
    rs.FusekiStore(base + "/data", ss.JENA_QUERY, base + "/update").publish(dataset(rs, graphs))
    print(f"jena: {len(graphs)} package graph(s) loaded")


def load_databricks(rs, graphs):
    """Replaces the package graphs' rows of the triple table, then refuses a table whose count of any of them differs
    from the files' (the marker's check reads the same counts)."""
    from rdflib import Graph
    rows = rs.to_rows(dataset(rs, graphs))
    conn, schema = ss.databricks()
    table = f"{schema}.{ss.TRIPLES_TABLE}"
    with conn, conn.cursor() as cur:
        cur.execute(f"DELETE FROM {table} WHERE graph IN ({', '.join('?' for _ in graphs)})", list(graphs))
        for start in range(0, len(rows), rs.DatabricksStore.BATCH):
            cur.execute(rs.insert_sql(table, rows[start:start + rs.DatabricksStore.BATCH]))
        cur.execute(f"SELECT graph, count(*) FROM {table} WHERE graph IN ({', '.join('?' for _ in graphs)}) GROUP BY graph",
                    list(graphs))
        counts = {r[0]: r[1] for r in cur.fetchall()}
    want = {iri: len(Graph().parse(os.path.join(ss.REPO, p), format="turtle")) for iri, p in graphs.items()}
    if counts != want:
        raise SystemExit(f"databricks: {ss.TRIPLES_TABLE} holds {counts} rows of the package graphs, not the files' {want}")
    print(f"databricks: {len(graphs)} package graph(s), {sum(counts.values())} rows")


def load_neo4j(store, files):
    nodes, edges = graph_rows(files)
    marker = {"store": store, "digest": digest(files), "models": [slug for slug, _, _ in files], "nodes": len(nodes),
              "edges": len(edges), "marked_at": ss.now()}
    driver, session = ss.neo4j_session(store)
    with driver, session:
        tx = session.begin_transaction()
        try:
            made, after = ss.demo_graph().replace_subgraph(tx, store, LABEL, MARKER_LABEL, nodes, edges, marker, KIND,
                                                           edge_props=True)
            tx.commit()
        finally:
            if not tx.closed():
                tx.rollback()
    print(f"{store}: {len(files)} logical model(s), {len(nodes)} {LABEL} nodes, {made[KIND]} edges between them, "
          f"{made['ontology']} to ontology nodes; ontology unchanged at {after[0]} nodes and {after[1]} relationships; "
          f"marked {marker['digest'][:12]}")


def load(stores, skills):
    """Loads what the newest releases hold into each named store; nothing, with a line that says so, when they hold
    no package graph."""
    releases = newest()
    graphs, files = package_graphs(releases), models(releases)
    if not graphs:
        print("the newest releases hold no package graph, so no logical model: nothing to load")
        return
    rs = rdfstore(skills) if {"jena", "databricks"} & set(stores) else None
    for store in stores:
        if store == "jena":
            load_jena(rs, graphs)
        elif store == "databricks":
            load_databricks(rs, graphs)
        elif files:
            load_neo4j(store, files)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=("load", "rows"))
    ap.add_argument("--store", action="append", choices=ss.STORES, help="load: these stores (default: all four)")
    ap.add_argument("--skills", default=os.environ.get("EPM_SKILLS", "~/.agents/skills"),
                    help="load: the folder holding the rdf-store skill (default $EPM_SKILLS or ~/.agents/skills)")
    args = ap.parse_args(argv)
    if args.command == "rows":
        nodes, edges = graph_rows(models())
        print(json.dumps({"nodes": nodes, "edges": edges}, indent=1, default=str))
    else:
        load(tuple(s for s in ss.STORES if s in (args.store or ss.STORES)), args.skills)


if __name__ == "__main__":
    main()
