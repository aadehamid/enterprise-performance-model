"""Build the `party` module's code lists (Steps 5 to 7; EPM-DEC-001-0067, EPM-DEC-001-0068).

    python3 build_party.py            # check the table and print the figures
    python3 build_party.py --write    # also write code-lists.ttl
    python3 build_party.py --verify   # fail unless code-lists.ttl and systems.ttl equal a fresh build

code-lists.csv holds every code list of the module, one row per value. The build fails unless
every row names a known scheme, has a definition, is unique in its scheme, and points its
broader value at a value of the same scheme; and unless the customer classes carry each of
MPC's classes C1 to C8 exactly once.

systems.csv, data-flows.csv, customer-sources.csv and attributes.csv hold the systems the
customer passes through, the flows between them, the systems each kind of customer starts in or
comes from, and each system's Create and Enrich attributes (EPM-DEC-001-0069). The build fails
unless every system is listed once, has a role that is not blank and implements only entities
of the conceptual model, a system the system module already has keeps its label there, every flow and source names listed systems and code-list values, and every attribute
names a listed system, a category, an entity of the module and, if any, a shared attribute.
Each flow must carry something; each source must have a note (blank text counts as none) and name a party role, customer
class, line of business or party type; and every cited input must be one of the seven.
"""
import argparse
import csv
import os
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "code-lists.csv")
OUTPUT = os.path.join(HERE, "code-lists.ttl")
SYSTEMS_OUTPUT = os.path.join(HERE, "systems.ttl")
SYSTEM_MODULE = os.path.join(HERE, "..", "system", "systems.csv")
SYSTEM = Namespace("https://w3id.org/lsc/ontology/modules/system/system/")
ENTITIES = ("Party", "ExternalIdentifier", "Address", "ContactPoint", "PartyRole", "PartyRelationship",
            "CustomerAccount", "CustomerClass", "LineOfBusiness", "Brand", "Agreement", "SiteBrandAssignment",
            "PartyTransactionAssociation", "Product", "Site", "SystemRecord")
MODEL_ENTITIES = tuple(e for e in ENTITIES if e != "SystemRecord")  # what a system can implement: the conceptual model only
CUST = Namespace("https://w3id.org/lsc/ontology/modules/party/")
MPC_CLASSES = {f"C{n}" for n in range(1, 9)}

# Each scheme's label and definition, in the order the module lists them.
SCHEMES = {
    "party-type": ("party types", "Person or organization: the two kinds of party.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "party-role": ("party roles", "The governed list of role types a party can hold. A new role type needs a governance decision.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "relationship-type": ("party relationship types", "The kinds of link from one party role to another.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "agreement-type": ("agreement types", "The types of agreement. They overlap: one agreement can have several.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "line-of-business": ("lines of business", "The governed categories of the company's business that a customer sits under.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "customer-class": ("customer classes", "The kinds of customer, grouped by value-chain role and brand attachment. Each class is assigned to a customer account with dates. Together with MPC's classification C1 to C8 they form the channel dimension of MPC-P06.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "site-type": ("site types", "The kinds of physical operating location.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "operating-model": ("site operating models", "Who owns and who operates a site.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "identifier-type": ("identifier types", "The kinds of external identifier of a party.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "address-usage": ("address usages", "How an address is used.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "contact-type": ("contact types", "The kinds of contact point.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "transaction-kind": ("transaction kinds", "The kinds of transaction a party or an account is associated with.", "EPM-DEC-001-0067; EPM-DEC-001-0068"),
    "system-tier": ("customer system tiers", "Where a system sits in the customer's data flow: core, integration, enrichment, downstream or landscape source.", "EPM-DEC-001-0069"),
    "attribute-category": ("attribute categories", "The decision owner's two categories of a system's customer attributes: those that define the customer there, and those that enrich it.", "EPM-DEC-001-0067; EPM-DEC-001-0069"),
    "shared-attribute": ("shared attributes", "Attributes that several systems carry under different names for one thing.", "EPM-DEC-001-0069"),
    "sourcing-kind": ("customer sourcing kinds", "How a system relates to a kind of customer: where it starts, where it is set up, or a source of it.", "EPM-DEC-001-0069"),
}


def scheme_iri(scheme):
    return CUST[scheme]


def value_iri(scheme, notation):
    return CUST[f"{scheme}/{notation}"]


def load():
    with open(TABLE, newline="") as f:
        rows = list(csv.DictReader(f))
    problems = [f"{r['scheme']}/{r['notation']}: unknown scheme" for r in rows if r["scheme"] not in SCHEMES]
    problems += [f"{r['scheme']}/{r['notation']}: no definition" for r in rows if not r["definition"]]
    keys = Counter((r["scheme"], r["notation"]) for r in rows)
    problems += [f"{s}/{n} is listed {c} times" for (s, n), c in keys.items() if c > 1]
    problems += [f"{r['scheme']}/{r['notation']}: broader {r['broader']} is not in its scheme"
                 for r in rows if r["broader"] and (r["scheme"], r["broader"]) not in keys]
    mpc = Counter(r["mpc_class"] for r in rows if r["mpc_class"])
    problems += [f"MPC class {c} is used {n} times" for c, n in mpc.items() if n > 1]
    problems += [f"MPC class {c} is not one of C1 to C8" for c in mpc if c not in MPC_CLASSES]
    problems += [f"MPC class {c} has no customer class" for c in sorted(MPC_CLASSES - set(mpc))]
    problems += [f"{r['scheme']}/{r['notation']}: only customer classes carry an MPC class"
                 for r in rows if r["mpc_class"] and r["scheme"] != "customer-class"]
    problems += [f"{s}: no values" for s in SCHEMES if not any(r["scheme"] == s for r in rows)]
    if problems:
        sys.exit("code-lists.csv does not reconcile:\n  " + "\n  ".join(problems))
    return rows


def build(rows):
    g = Graph()
    g.bind("party", CUST)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    for scheme, (label, definition, citation) in SCHEMES.items():
        s = scheme_iri(scheme)
        g.add((s, RDF.type, SKOS.ConceptScheme))
        g.add((s, RDFS.label, Literal(label, lang="en")))
        g.add((s, SKOS.definition, Literal(definition, lang="en")))
        g.add((s, DCTERMS.bibliographicCitation, Literal(citation, lang="en")))
    for r in rows:
        v = value_iri(r["scheme"], r["notation"])
        g.add((v, RDF.type, SKOS.Concept))
        if r["scheme"] == "line-of-business":
            g.add((v, RDF.type, CUST.LineOfBusiness))
        g.add((v, SKOS.inScheme, scheme_iri(r["scheme"])))
        g.add((v, SKOS.notation, Literal(r["notation"])))
        g.add((v, SKOS.prefLabel, Literal(r["label"], lang="en")))
        g.add((v, SKOS.definition, Literal(r["definition"], lang="en")))
        if r["broader"]:
            g.add((v, SKOS.broader, value_iri(r["scheme"], r["broader"])))
        else:
            g.add((v, SKOS.topConceptOf, scheme_iri(r["scheme"])))
        if r["mpc_class"]:
            g.add((v, CUST.mpcClassification, Literal(r["mpc_class"])))
    return g


def read(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


def slugify(text):
    out = "".join(c.lower() if c.isalnum() else "-" for c in text)
    return "-".join(p for p in out.split("-") if p)


def split(text):
    return [t for t in text.split(";") if t]


# What a customer sourcing may name (party:sourcedConcept), and the decision owner's seven inputs (EPM-DEC-001-0067).
SOURCED_SCHEMES = {"party-role", "customer-class", "line-of-business", "party-type"}
INPUTS = {str(i) for i in range(1, 8)}


def load_systems(codes):
    systems, flows, sources, attrs = (read(n) for n in ("systems.csv", "data-flows.csv", "customer-sources.csv", "attributes.csv"))
    existing = {r["slug"]: r["label"] for r in read(SYSTEM_MODULE)}
    values = {(r["scheme"], r["notation"]) for r in codes}
    slugs = {r["slug"] for r in systems}
    problems = [f"systems.csv lists {s} {n} times" for s, n in Counter(r["slug"] for r in systems).items() if n > 1]
    problems += [f"{r['slug']}: the system module calls it {existing[r['slug']]!r}, not {r['label']!r}"
                 for r in systems if r["slug"] in existing and existing[r["slug"]].lower() != r["label"].lower()]
    problems += [f"{r['slug']}: tier {r['tier']!r} is not a system tier" for r in systems if ("system-tier", r["tier"]) not in values]
    problems += [f"{r['slug']}: implements {e!r}, not an entity of the conceptual model"
                 for r in systems for e in split(r["implements"]) if e not in MODEL_ENTITIES]
    problems += [f"{r['slug']}: no role" for r in systems if not r["role"].strip()]
    problems += [f"flow {r['from']} -> {r['to']}: {e} is not a listed system" for r in flows for e in (r["from"], r["to"]) if e not in slugs]
    problems += [f"flow {f} -> {t} is listed {n} times" for (f, t), n in Counter((r["from"], r["to"]) for r in flows).items() if n > 1]
    problems += [f"flow {r['from']} -> {r['to']}: no input" for r in flows if not split(r["inputs"])]
    problems += [f"source {r['system']}: not a listed system" for r in sources if r["system"] not in slugs]
    problems += [f"source {r['system']}: kind {r['kind']!r} is not a sourcing kind" for r in sources if ("sourcing-kind", r["kind"]) not in values]
    problems += [f"source {r['system']}: {r['concept']} is not a code-list value" for r in sources if tuple(r["concept"].split("/", 1)) not in values]
    problems += [f"source {r['system']}: {r['concept']} is not a party role, customer class, line of business or party type"
                 for r in sources if r["concept"].split("/", 1)[0] not in SOURCED_SCHEMES]
    problems += [f"flow {r['from']} -> {r['to']}: carries nothing" for r in flows if not r["carries"].strip()]
    problems += [f"source {r['system']}: no note" for r in sources if not r["note"].strip()]
    problems += [f"source {r['system']}: no input" for r in sources if not split(r["inputs"])]
    problems += [f"{what}: input {i!r} is not one of the seven inputs" for what, r in
                 [(f"flow {r['from']} -> {r['to']}", r) for r in flows] + [(f"source {r['system']}", r) for r in sources]
                 for i in split(r["inputs"]) if i not in INPUTS]
    problems += [f"attribute {r['label']!r}: {r['system']} is not a listed system" for r in attrs if r["system"] not in slugs]
    problems += [f"attribute {r['label']!r}: category {r['category']!r}" for r in attrs if ("attribute-category", r["category"]) not in values]
    problems += [f"attribute {r['label']!r}: describes {r['describes']!r}, not an entity" for r in attrs if r["describes"] not in ENTITIES]
    problems += [f"attribute {r['label']!r}: shared {r['shared']!r} is not a shared attribute"
                 for r in attrs if r["shared"] and ("shared-attribute", r["shared"]) not in values]
    keys = Counter((r["system"], r["category"], slugify(r["label"])) for r in attrs)
    sourcing = Counter((r["system"], r["kind"], r["concept"]) for r in sources)
    problems += [f"source {k} is listed {n} times" for k, n in sourcing.items() if n > 1]
    problems += [f"attribute {k} is listed {n} times" for k, n in keys.items() if n > 1]
    if problems:
        sys.exit("the customer systems tables do not reconcile:\n  " + "\n  ".join(problems))
    return systems, flows, sources, attrs, existing


def node(slug):
    return CUST[f"system/{slug}"]


def build_systems(systems, flows, sources, attrs, existing):
    g = Graph()
    for prefix, ns in (("party", CUST), ("system", SYSTEM), ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    scheme = CUST["customer-systems"]
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, RDFS.label, Literal("customer systems", lang="en")))
    g.add((scheme, SKOS.definition, Literal("The systems the customer passes through, from the decision owner's customer inputs (EPM-DEC-001-0069).", lang="en")))
    for r in systems:
        s = node(r["slug"])
        g.add((s, RDF.type, CUST.CustomerSystem))
        g.add((s, RDF.type, SKOS.Concept))
        g.add((s, SKOS.prefLabel, Literal(r["label"], lang="en")))
        g.add((s, SKOS.notation, Literal(r["slug"])))
        g.add((s, SKOS.inScheme, scheme))
        if r["slug"] in existing:  # the same system as the system module's, which the process map names
            g.add((s, SKOS.exactMatch, SYSTEM[r["slug"]]))
        for alt in split(r["alt_labels"]):
            g.add((s, SKOS.altLabel, Literal(alt, lang="en")))
        g.add((s, CUST.systemTier, CUST[f"system-tier/{r['tier']}"]))
        g.add((s, CUST.customerRole, Literal(r["role"], lang="en")))
        for e in split(r["implements"]):
            g.add((s, CUST.implements, CUST[e]))
    for r in flows:
        f = CUST[f"flow/{r['from']}--{r['to']}"]
        g.add((f, RDF.type, CUST.DataFlow))
        g.add((f, CUST.fromSystem, node(r["from"])))
        g.add((f, CUST.toSystem, node(r["to"])))
        g.add((f, CUST.carries, Literal(r["carries"], lang="en")))
        g.add((f, CUST.evidenceInput, Literal(", ".join(split(r["inputs"])))))
        g.add((node(r["from"]), CUST.feeds, node(r["to"])))
    for r in sources:
        n = CUST[f"sourcing/{r['system']}--{r['kind']}--{r['concept'].replace('/', '--')}"]
        g.add((n, RDF.type, CUST.CustomerSourcing))
        g.add((n, CUST.sourcingSystem, node(r["system"])))
        g.add((n, CUST.sourcingKind, CUST[f"sourcing-kind/{r['kind']}"]))
        g.add((n, CUST.sourcedConcept, CUST[r["concept"]]))
        g.add((n, RDFS.comment, Literal(r["note"], lang="en")))
        g.add((n, CUST.evidenceInput, Literal(", ".join(split(r["inputs"])))))
    for r in attrs:
        a = CUST[f"attribute/{r['system']}/{r['category']}/{slugify(r['label'])}"]
        g.add((a, RDF.type, CUST.SystemAttribute))
        g.add((a, SKOS.prefLabel, Literal(r["label"], lang="en")))
        g.add((a, CUST.inSystem, node(r["system"])))
        g.add((a, CUST.attributeCategory, CUST[f"attribute-category/{r['category']}"]))
        g.add((a, CUST.describes, CUST[r["describes"]]))
        if r["shared"]:
            g.add((a, CUST.sharedAttribute, CUST[f"shared-attribute/{r['shared']}"]))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    rows = load()
    systems, flows, sources, attrs, existing = load_systems(rows)
    stext = ("# The customer systems, data flows and attributes (EPM-DEC-001-0069). Built by build_party.py\n"
             "# from systems.csv, data-flows.csv, customer-sources.csv and attributes.csv. Do not edit by hand.\n"
             + build_systems(systems, flows, sources, attrs, existing).serialize(format="turtle"))
    text = ("# The `party` module's code lists (Steps 5 to 7; EPM-DEC-001-0067, 0068, 0069).\n"
            "# Built by build_party.py from code-lists.csv. Do not edit by hand.\n"
            + build(rows).serialize(format="turtle"))
    counts = Counter(r["scheme"] for r in rows)
    print("code lists " + ", ".join(f"{s} {counts[s]}" for s in SCHEMES))
    cat = Counter(r["category"] for r in attrs)
    print(f"systems {len(systems)} ({sum(1 for r in systems if r['slug'] in existing)} already in the system module); "
          f"flows {len(flows)}; sourcings {len(sources)}; attributes {len(attrs)} (create {cat['create']}, enrich {cat['enrich']})")
    if args.verify:
        if not (os.path.exists(OUTPUT) and open(OUTPUT).read() == text):
            sys.exit("code-lists.ttl is not current: run build_party.py --write")
        if not (os.path.exists(SYSTEMS_OUTPUT) and open(SYSTEMS_OUTPUT).read() == stext):
            sys.exit("systems.ttl is not current: run build_party.py --write")
        print("code-lists.ttl and systems.ttl are current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        with open(SYSTEMS_OUTPUT, "w") as f:
            f.write(stext)
        print(f"wrote {OUTPUT} and {SYSTEMS_OUTPUT}")


if __name__ == "__main__":
    main()
