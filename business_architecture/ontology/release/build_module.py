"""Build the release package of a module other than core (Step 10; EPM-DEC-001-0018, EPM-DEC-001-0037).

    python3 build_module.py organization            # build, validate, print the figures
    python3 build_module.py organization --write    # write releases/organization/<version>/
    python3 build_module.py organization --verify   # fail unless the written package equals a fresh build

The package holds the module's Turtle and JSON-LD, its shapes, a DCAT record, its changelog and a
manifest with each file's SHA-256, the shape of the core 1.0.0 package (EPM-DEC-001-0029). A release
candidate (a stage such as "rc.1") carries no issued date: a module's first release is a major, and
a major needs the decision owner's approval (module policy, 2026-09-18). An issued release names where their
approval is recorded; the tests check that the words are there.
"""
import argparse
import hashlib
import json
import os
import sys

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
MODULES_NS = "https://w3id.org/lsc/ontology/modules/"
DCAT = Namespace("http://www.w3.org/ns/dcat#")

# One entry per module. Paths are relative to business_architecture/ontology/.
MODULES = {
    "organization": {
        "title": "LSC Organization Module",
        "description": "Roles, RACI responsibility assignments and control between legal entities (Step 5).",
        # 2.0.0 carries the decision owner's role answers: three roles deprecated, their assignments moved
        # (EPM-DEC-001-0045). Each earlier package stays on disk as released; test_build_module.py
        # checks it is untouched.
        # 2.1.0 is a minor Claude approved under the delegation: the RACI levels stated as top concepts both ways;
        # it requires core 2.3.0, the current release (EPM-DEC-001-0098, item 5; EPM-DEC-001-0106).
        # 2.2.0 is a minor Claude approved under the delegation: the decision owner's close-out answers of 2026-10-28,
        # PSM expanded as Process Safety Management, the Crude RFC reading and Business Planning and Analysis's
        # definition confirmed; it still requires core 2.3.0 (EPM-DEC-001-0045, amendment of 2026-10-28).
        "version": "2.2.0", "stage": None, "approver": "Claude, under the decision owner's delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)", "issued": "2026-10-28",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md", "Yes, delegate as described (Recommended)"),
        "parts": ["organization/vocabulary.ttl", "organization/roles.ttl", "organization/assignments.ttl"],
        "shapes": ["organization/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.3.0"},
        "decisions": ["EPM-DEC-001-0030", "EPM-DEC-001-0031", "EPM-DEC-001-0032", "EPM-DEC-001-0045", "EPM-DEC-001-0098",
                      "EPM-DEC-001-0106"],
    },
    "ref-mpc": {
        "title": "LSC Reference Instances: Marathon Petroleum Corporation",
        "description": "Public reference facts about MPC and MPLX, each with a source and an as-of date (Step 5).",
        # 1.1.0 requires organization 2.0.0; its own content is unchanged (EPM-DEC-001-0045).
        # 1.2.0 adds MPC and MPLX as parties in the party module's terms, moved from party/, and requires
        # party 1.0.0; the decision owner approved it on its own (EPM-DEC-001-0075, EPM-DEC-001-0080).
        # 1.3.0 is a minor Claude approved under the delegation and the decision owner's words: MPC's brands Marathon,
        # ARCO and Tesoro as party:Brand individuals; it requires organization 2.1.0 and party 2.0.0, the current
        # releases (EPM-DEC-001-0108, amendment of 2026-10-27).
        "version": "1.3.0", "stage": None,
        "approver": "Claude, under the decision owner's delegation (EPM-DEC-001-0028; the decision owner's answer of 2026-10-27 on the brands)",
        "issued": "2026-10-27",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-27-customer-inputs.md",
                     "yes those can be brand values. Others I cannot answer."),
        "parts": ["ref-mpc/ref-mpc.ttl", "ref-mpc/reference-parties.ttl", "ref-mpc/reference-brands.ttl"],
        # Its own shapes, then the released shapes of the versions it pins, so a later party or organization
        # release cannot change what this released package is checked against (EPM-DEC-001-0094).
        "shapes": ["ref-mpc/shapes.ttl", "releases/organization/2.1.0/shapes.ttl", "releases/party/2.0.0/shapes.ttl"],
        "depends_on": ["organization", "party"],
        "pins": {"organization": "2.1.0", "party": "2.0.0"},
        "decisions": ["EPM-DEC-001-0015", "EPM-DEC-001-0033", "EPM-DEC-001-0071", "EPM-DEC-001-0075", "EPM-DEC-001-0080",
                      "EPM-DEC-001-0108"],
    },
    "kpi": {
        "title": "LSC KPI Module",
        "description": "Measure definitions, classified by kind, with the planning personas who use them and the core processes they inform (Step 7). Definitions only, never values.",
        # 1.0.0 was the module's first release, a major approved by the decision owner (EPM-DEC-001-0043).
        # 1.0.1 is a patch: the planner list's source names VCO DSV (EPM-DEC-001-0040).
        # 1.1.0 is a minor approved with the release plan: the eight measure populations join the package,
        # the measure shape is closed, and it requires core 2.2.0 (EPM-DEC-001-0079).
        # 1.1.1 is a patch approved with the close-out releases: pop:populationEvidence gains rdfs:range xsd:string,
        # closing its projection gap; it requires core 2.3.0, the current release (EPM-DEC-001-0088, 0093).
        # 1.2.0 is a minor of item F's release plan, which the decision owner approved: KPI-0001 on Crack Spreads
        # Pricing, Additional Market Prices narrowed to renewables and NGLs, the duplicate alias dropped, top
        # concepts both ways; it requires core 2.3.0 (EPM-DEC-001-0097, 0098, 0100).
        # 1.3.0 is a minor Claude approved under the delegation: a KPI or OPM identifier on every measure but the
        # trackers, reports and non-measures, the scheme the decision owner chose; it still requires core 2.3.0
        # (EPM-DEC-001-0109).
        "version": "1.3.0", "stage": None, "approver": "Claude, under the decision owner's delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)", "issued": "2026-10-28",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md", "Yes, delegate as described (Recommended)"),
        "parts": ["kpi/vocabulary.ttl", "kpi/measures.ttl", "population/vocabulary.ttl", "population/population.ttl"],
        "shapes": ["kpi/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.3.0"},
        "decisions": ["EPM-DEC-001-0040", "EPM-DEC-001-0042", "EPM-DEC-001-0043", "EPM-DEC-001-0062", "EPM-DEC-001-0079",
                      "EPM-DEC-001-0088", "EPM-DEC-001-0093", "EPM-DEC-001-0097", "EPM-DEC-001-0098", "EPM-DEC-001-0100",
                      "EPM-DEC-001-0109"],
    },
    "party": {
        "title": "LSC Party Module",
        "description": "The Customer domain's concepts: parties, the roles they hold for a period, accounts, agreements and sites; the customer's systems, data flow and attributes; and the customer lifecycle linked to core processes (Steps 5 to 7). Definitions only, never records.",
        # 1.0.0 is the module's first release, a major approved by the decision owner (EPM-DEC-001-0074).
        # The reference parties are reference instances of real companies, which the playbook's module policy
        # puts in their own module, so they are not part of this package. Since 2026-10-22 they are in
        # ref-mpc/reference-parties.ttl (EPM-DEC-001-0075).
        # 1.1.0 is a minor approved with the close-out releases: the products from MPC's FY2025 Form 10-K with their
        # OEO mappings and PIDX families, the onboarding stage's link to CM 1.3.7.1.7, and the eight projection
        # fixes; it requires core 2.3.0 (EPM-DEC-001-0087, 0088, 0092).
        # 1.2.0 is a minor the decision owner approved: 18 customer systems defined, each citing its source;
        # SAP S/4HANA matched to the system module's SAP; every code list's top concepts stated both ways
        # (EPM-DEC-001-0098, 0099).
        # 1.3.0 is a minor Claude approved under the delegation: the 20 internal customer systems' descriptions,
        # drafted from the repository; it requires system 1.3.0 (EPM-DEC-001-0103).
        # 1.4.0 is a minor Claude approved under the delegation: seven more customer systems matched to the system
        # module's, which gains them with MPC-P11, and one shape message reworded without an apostrophe (the ontology
        # skill's SHACL rule 19); it requires core 2.4.0, which its build now reads, and system 1.4.0 (EPM-DEC-001-0104, 0105).
        # 2.0.0 is a major the decision owner approved: the customer inputs of 2026-10-27 correct Dealer Master's role and
        # definition, two data flows, a sourcing note and the prospect system stage, and deprecate the sourcing that says
        # jobbers start in Dealer Master; they add the sub-jobber role, the dealer classes, the classes of trade, eight
        # systems and 13 flows; it requires system 1.5.0 (EPM-DEC-001-0108).
        # 2.1.0 is a minor Claude approved under the delegation: the decision owner's close-out answers of 2026-10-28,
        # Drop Tank, GasBuddy and DTN defined from their vendors' own published words (Drop Tank's from a 2018 press release, its site being gone) and a note on Polaris; it still requires core
        # 2.4.0 and system 1.5.0 (EPM-DEC-001-0099, amendment of 2026-10-28).
        "version": "2.1.0", "stage": None, "approver": "Claude, under the decision owner's delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)", "issued": "2026-10-28",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md", "Yes, delegate as described (Recommended)"),
        "parts": ["party/vocabulary.ttl", "party/code-lists.ttl", "party/systems.ttl", "party/lifecycle.ttl"],
        "shapes": ["party/shapes.ttl"],
        # Since 1.2.0 it also requires system 1.1.0, whose systems its five skos:exactMatch links name
        # (EPM-DEC-001-0099; the earlier packages name four of them without requiring system). 1.4.0 names twelve
        # and requires system 1.4.0 (EPM-DEC-001-0104). 2.0.0 names twenty and requires system 1.5.0 (EPM-DEC-001-0108).
        "depends_on": ["core", "system"],
        "pins": {"core": "2.4.0", "system": "1.5.0"},
        "decisions": ["EPM-DEC-001-0067", "EPM-DEC-001-0068", "EPM-DEC-001-0069", "EPM-DEC-001-0070",
                      "EPM-DEC-001-0071", "EPM-DEC-001-0072", "EPM-DEC-001-0074", "EPM-DEC-001-0087", "EPM-DEC-001-0088",
                      "EPM-DEC-001-0092", "EPM-DEC-001-0098", "EPM-DEC-001-0099", "EPM-DEC-001-0103",
                      "EPM-DEC-001-0104", "EPM-DEC-001-0108"],
    },
    # The Step 7 modules' first releases, majors the decision owner approved with the release plan
    # (EPM-DEC-001-0077). Each requires core 2.2.0, the release that holds every process they link.
    "data-product": {
        "title": "LSC Data Product Module",
        "description": "The data products of the portfolio, the product lines and segments that group them, and the processes that produce them; and the pricing tables and views on the data platform, foundational or derived, with their lineage and the Genie agents that use them (Step 7). Definitions only, never data values; mapped to DCAT, not imported.",
        # 1.1.0 is a minor approved with the close-out releases: the Customer Master data product, produced by
        # CM 1.3.7.1.1 (MPC-P10.3); it requires core 2.3.0 (EPM-DEC-001-0087, 0088, 0091).
        # 1.2.0 is a minor of item F's release plan, which the decision owner approved: the pricing platform tables,
        # the data product kinds, their lineage and the Genie agents; the four line labels and top concepts both ways.
        # It requires core 2.3.0, and kpi 1.2.0 and system 1.2.0, whose measures and systems it links (EPM-DEC-001-0097,
        # 0098, 0100).
        "version": "1.2.0", "stage": None, "issued": "2026-10-25",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md", "Approve the plan (Recommended)"),
        "parts": ["data-product/vocabulary.ttl", "data-product/data-products.ttl", "data-product/pricing.ttl"],
        "shapes": ["data-product/shapes.ttl"],
        "depends_on": ["core", "kpi", "system"],
        "pins": {"core": "2.3.0", "kpi": "1.2.0", "system": "1.2.0"},
        "decisions": ["EPM-DEC-001-0005", "EPM-DEC-001-0048", "EPM-DEC-001-0053", "EPM-DEC-001-0077", "EPM-DEC-001-0087",
                      "EPM-DEC-001-0088", "EPM-DEC-001-0091", "EPM-DEC-001-0097", "EPM-DEC-001-0098", "EPM-DEC-001-0100"],
    },
    "value-stream": {
        "title": "LSC Value Stream Module",
        "description": "The Commercial Hydrocarbon Lifecycle and Order to Cash value streams: their stages, capabilities and value-stream processes, which realize core processes, produce and consume data products and carry cited measure links (Step 7).",
        # 1.1.0 is a minor the decision owner approved with the close-out releases: the Order to Cash credit
        # review realizes CM 1.3.7.4.2 (MPC-P10.2), and vs:produces and vs:consumes gain rdfs:range skos:Concept;
        # it requires the current core, data-product and kpi releases (EPM-DEC-001-0087, 0088, 0090).
        # 1.2.0 is a minor Claude approved under the delegation: the measure relationships stated as top concepts both
        # ways; it requires the current core, data-product and kpi releases (EPM-DEC-001-0098, item 5; EPM-DEC-001-0106).
        "version": "1.2.0", "stage": None, "approver": "Claude, under the decision owner's delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)", "issued": "2026-10-26",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md", "Yes, delegate as described (Recommended)"),
        "parts": ["value-stream/vocabulary.ttl", "value-stream/value-streams.ttl"],
        "shapes": ["value-stream/shapes.ttl"],
        "depends_on": ["core", "data-product", "kpi"],
        # Every dependency pinned: a later kpi or data-product release must not change this package.
        "pins": {"core": "2.3.0", "data-product": "1.2.0", "kpi": "1.2.0"},
        "decisions": ["EPM-DEC-001-0054", "EPM-DEC-001-0077", "EPM-DEC-001-0087", "EPM-DEC-001-0088", "EPM-DEC-001-0090",
                      "EPM-DEC-001-0098", "EPM-DEC-001-0106"],
    },
    "system": {
        "title": "LSC System Module",
        "description": "The systems, office tools and working documents the process map names, with their kind, definitions and the processes that use them, and the systems the pricing assets name (Step 7).",
        # 1.1.0 is a minor the decision owner approved: 15 systems defined from their vendors' own descriptions
        # or the decision owner's, full names as preferred labels, both code lists' members as top concepts both
        # ways; it requires core 2.3.0 (EPM-DEC-001-0098, 0099).
        # 1.2.0 is a minor of item F's release plan, which the decision owner approved: MIPS and Databricks, which the
        # process map does not name, and MPR's definition, from the decision owner's pricing assets (EPM-DEC-001-0100).
        # 1.3.0 is a minor Claude approved under the delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening):
        # the 14 internal systems' descriptions, drafted from the repository (EPM-DEC-001-0103).
        # 1.4.0 is a minor Claude approved under the delegation: the seven systems and 21 links of MPC-P11, which
        # the decision owner accepted; it requires core 2.4.0, the current release (EPM-DEC-001-0104, 0105).
        # 1.5.0 is a minor Claude approved under the delegation, with the decision owner's alignment with the plan: eight
        # systems the customer inputs of 2026-10-27 name and the process map does not, and notes on TMR and Bridger
        # Insight (EPM-DEC-001-0108).
        "version": "1.5.0", "stage": None, "approver": "Claude, under the decision owner's delegation (EPM-DEC-001-0028; the decision owner's alignment with the plan of 2026-10-27)", "issued": "2026-10-27",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-27-customer-inputs.md",
                     "I am aligned with all your recommendation in the input plan."),
        "parts": ["system/vocabulary.ttl", "system/systems.ttl"],
        "shapes": ["system/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.4.0"},
        "decisions": ["EPM-DEC-001-0055", "EPM-DEC-001-0077", "EPM-DEC-001-0098", "EPM-DEC-001-0099", "EPM-DEC-001-0100",
                      "EPM-DEC-001-0103", "EPM-DEC-001-0104", "EPM-DEC-001-0108"],
    },
    "lane": {
        "title": "LSC Lane Module",
        "description": "The four office lanes as a code list, and the processes the process map places in them (Step 7).",
        # 1.1.0 is a minor Claude approved under the delegation: the four lanes stated as top concepts both ways, and a
        # shape message reworded without an apostrophe (ontology skill, SHACL rule 19); it requires core 2.3.0, then
        # the current release, which build_lanes.py then read (EPM-DEC-001-0098, item 5; EPM-DEC-001-0106). Since then
        # build_lanes.py reads core 2.4.0 (2026-10-30); this entry records lane 1.1.0 as issued.
        "version": "1.1.0", "stage": None, "approver": "Claude, under the decision owner's delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)", "issued": "2026-10-26",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md", "Yes, delegate as described (Recommended)"),
        "parts": ["lane/vocabulary.ttl", "lane/lanes.ttl"],
        "shapes": ["lane/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.3.0"},
        "decisions": ["EPM-DEC-001-0056", "EPM-DEC-001-0077", "EPM-DEC-001-0098", "EPM-DEC-001-0106"],
    },
    "market-data": {
        "title": "LSC Market Data Module",
        "description": "The published series of the crack-spreads measure, from MPC Economics' definition first, with their benchmarks, regions, legs and RIN treatment; the prices the decision owner's pricing views report for the other pricing measures; and where each measure's complete list of series is (Step 7). Definitions only, never prices.",
        # 1.1.0 is a minor of item F's release plan, which the decision owner approved: the pricing views' prices for
        # each pricing measure, the columns that list every series, two NYMEX cracks, top concepts both ways; it
        # requires kpi 1.2.0 (EPM-DEC-001-0097, 0098, 0100).
        "version": "1.1.0", "stage": None, "issued": "2026-10-25",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md", "Approve the plan (Recommended)"),
        "parts": ["market-data/vocabulary.ttl", "market-data/market-data.ttl"],
        "shapes": ["market-data/shapes.ttl"],
        "depends_on": ["kpi"],
        "pins": {"kpi": "1.2.0"},
        "decisions": ["EPM-DEC-001-0046", "EPM-DEC-001-0057", "EPM-DEC-001-0066", "EPM-DEC-001-0077", "EPM-DEC-001-0097",
                      "EPM-DEC-001-0098", "EPM-DEC-001-0100"],
    },
    # The integration package's first release, a major the decision owner approved with the release plan
    # (EPM-DEC-001-0078). It packages three small vocabularies, each keeping its own namespace; the package
    # IRI names the release only. The population statements ship in kpi 1.1.0, and the APQC element list
    # stays a reference file (EPM-DEC-001-0078).
    "integration": {
        "title": "LSC Integration Vocabularies",
        "description": "The rules that tie the modules together: which placing properties certify and which give context (placement), the evidence tier of every cited source (authority), and what a consumer may bind, answer and must refuse (consumer). Each vocabulary keeps its own namespace (Steps 7, 9 and 11).",
        # 2.0.0 is a major the decision owner approved: the five projection fixes (ranges for plc:placementKind and
        # con:reliesOn, whose definition narrows from property or class to property, which makes it a major;
        # cardinality for plc:placementKind, auth:rank and auth:evidenceTier, in two new shape files packaged with
        # consumer's), and it requires the current releases (EPM-DEC-001-0088, 0094).
        # 2.1.0 is a minor the decision owner approved: the 27 sources of the systems' definitions in their tiers,
        # the three code lists' members as top concepts both ways; it requires the new system and party releases
        # (EPM-DEC-001-0098, 0099).
        # 2.2.0 is a minor of item F's release plan, which the decision owner approved: the consumer rule for a value
        # quoted through the bound metric view, eight more sources tiered; it requires the new releases (EPM-DEC-001-0097,
        # 0100).
        # 2.3.0 is a minor Claude approved under the delegation: two more sources in tier 1, the sources of the
        # internal systems' descriptions; it requires the new system and party releases (EPM-DEC-001-0103).
        # 2.4.0 is a minor Claude approved under the delegation, with the decision owner's alignment with the plan: the
        # customer inputs of 2026-10-27 in tier 1; it requires the current releases (EPM-DEC-001-0108).
        # 2.5.0 is a minor Claude approved under the delegation: the three public sources (two vendor pages, a press release) that define Drop Tank, GasBuddy
        # and DTN in party 2.1.0, in tier 4; it requires the current releases, organization 2.2.0 and party 2.1.0
        # among them (EPM-DEC-001-0099, amendment of 2026-10-28).
        "version": "2.5.0", "stage": None, "approver": "Claude, under the decision owner's delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)", "issued": "2026-10-28",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md", "Yes, delegate as described (Recommended)"),
        "parts": ["placement/vocabulary.ttl", "authority/vocabulary.ttl", "authority/source-tiers.ttl",
                  "consumer/vocabulary.ttl"],
        "shapes": ["consumer/shapes.ttl", "placement/shapes.ttl", "authority/shapes.ttl"],
        "own_shapes": 3,  # all three shape files are the package's own; the package's shapes.ttl holds them merged
        "depends_on": ["core", "organization", "kpi", "data-product", "value-stream", "system", "lane", "market-data",
                       "party"],
        "pins": {"core": "2.4.0", "organization": "2.2.0", "kpi": "1.2.0", "data-product": "1.2.0", "value-stream": "1.2.0",
                 "system": "1.5.0", "lane": "1.1.0", "market-data": "1.1.0", "party": "2.1.0"},
        "decisions": ["EPM-DEC-001-0058", "EPM-DEC-001-0059", "EPM-DEC-001-0061", "EPM-DEC-001-0078", "EPM-DEC-001-0088",
                      "EPM-DEC-001-0094", "EPM-DEC-001-0098", "EPM-DEC-001-0099", "EPM-DEC-001-0100", "EPM-DEC-001-0103",
                      "EPM-DEC-001-0108"],
    },
}


RELEASED = {"core": "1.0.0"}  # released modules this builder does not build
# The share release rebuilds every newest package so that it names only the newest versions (EPM-DEC-001-0110,
# "All links go through the latest release"). With EPM_SHARE_RELEASE set, a module's pins are ignored and core is
# its newest package on disk; on main nothing changes.
SHARE_RELEASE = bool(os.environ.get("EPM_SHARE_RELEASE"))


def newest_on_disk(module):
    folder = os.path.join(ONTOLOGY, "releases", module)
    versions = [v for v in os.listdir(folder) if v[0].isdigit() and os.path.isfile(os.path.join(folder, v, "manifest.json"))]
    return max(versions, key=lambda v: tuple(int(x) for x in v.split(".")))


def label(m):
    return m["version"] if m["stage"] is None else f"{m['version']}-{m['stage']}"


def dependencies(name):
    """Each dependency with the version this package is built against: a released version, or the
    dependency's own current candidate, so a candidate never names a release that does not exist."""
    pins = {} if SHARE_RELEASE else MODULES[name].get("pins", {})
    released = {"core": newest_on_disk("core")} if SHARE_RELEASE else RELEASED
    return {d: pins.get(d) or released.get(d) or label(MODULES[d]) for d in MODULES[name]["depends_on"]}


def parse(paths):
    g = Graph()
    for p in paths:
        g.parse(os.path.join(ONTOLOGY, p))
    return g


def build(name):
    m = MODULES[name]
    iri, lab = URIRef(MODULES_NS + name), label(m)
    g = parse(m["parts"])
    for prefix, ns in (("dcterms", DCTERMS), ("owl", OWL)):
        g.bind(prefix, ns)
    # The ontology header names the version; the module refers to others by IRI and imports none.
    g.remove((iri, None, None))
    g.add((iri, RDF.type, OWL.Ontology))
    g.add((iri, DCTERMS.title, Literal(m["title"], lang="en")))
    g.add((iri, DCTERMS.description, Literal(m["description"], lang="en")))
    g.add((iri, OWL.versionInfo, Literal(lab)))
    g.add((iri, OWL.versionIRI, URIRef(f"{iri}/{lab}")))
    for dep, version in sorted(dependencies(name).items()):
        g.add((iri, DCTERMS.requires, URIRef(f"{MODULES_NS}{dep}/{version}")))
    if m["issued"]:
        # Issued and modified dates on every release, both the issue date at the cut (playbook
        # Step 10; build_core.py does the same for core).
        g.add((iri, DCTERMS.issued, Literal(m["issued"], datatype=XSD.date)))
        g.add((iri, DCTERMS.modified, Literal(m["issued"], datatype=XSD.date)))
    return g


def released_requires(dep, version):
    """What a released package requires, read from its own manifest on disk, never from this builder's
    current table: a later release of that module must not change what an earlier package loads."""
    with open(os.path.join(ONTOLOGY, "releases", dep, version, "manifest.json")) as f:
        return json.load(f).get("depends_on") or {}


def released_closure(name):
    """Every released package this module's check loads: its dependencies at the versions it names,
    and theirs (from each selected release's manifest), down to core. Where two paths name different
    versions of one module, the highest is loaded, so a graph never holds two releases of one module."""
    return closure(dependencies(name))


def closure(depends_on):
    """The released packages that the given dependencies load, by the rule of released_closure. A
    written package's closure starts from its own manifest: closure(released_requires(name, version)).
    It settles on the highest release of each module reachable from the given requirements through the
    chosen releases' own requirements, so a release that loses to a higher one adds nothing (the
    fixed point of the ontology skill's check_packages.closure, personal-agent-skills #49)."""
    def key(version):
        return tuple(map(int, version.split(".")))
    chosen = {}
    for _ in range(1000):
        want = {}
        for deps in [dict(depends_on)] + [released_requires(dep, version) for dep, version in chosen.items()]:
            for dep, version in deps.items():
                if dep not in want or key(version) > key(want[dep]):
                    want[dep] = version
        if want == chosen:
            return chosen
        chosen = want
    raise ValueError("the dependency closure does not settle")


def validation_graph(name, g):
    """The data the module's shapes run over: the module, with the released packages of its closure."""
    data = Graph()
    data += g
    for dep, version in sorted(released_closure(name).items()):
        data.parse(os.path.join(ONTOLOGY, "releases", dep, version, f"{dep}.ttl"))
    return data


def check(name, g):
    """The module's shapes over the module, with the released packages it depends on loaded: core for
    the concepts a module refers to, the pinned organization release for ref-mpc, and the released
    data-product and kpi packages for value-stream and market-data."""
    # advanced=True: SHACL-AF targets such as sh:SPARQLTarget run, as in every other check (EPM-DEC-001-0094).
    conforms, _, text = validate(validation_graph(name, g), shacl_graph=parse(MODULES[name]["shapes"]), advanced=True)
    return conforms, text


def jsonld(g):
    """JSON-LD with nodes, keys and values in a fixed order, so a rebuild is byte-identical (as for core)."""
    data = json.loads(g.serialize(format="json-ld"))
    nodes = data if isinstance(data, list) else data.get("@graph", [data])
    for node in nodes:
        for key, value in node.items():
            if isinstance(value, list):
                node[key] = sorted(value, key=lambda v: json.dumps(v, sort_keys=True))
    nodes.sort(key=lambda n: n.get("@id", ""))
    return json.dumps(nodes, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def catalog(name):
    m = MODULES[name]
    iri, lab = MODULES_NS + name, label(m)
    base = f"{iri}/releases/{lab}"
    g = Graph()
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    cat, dataset = URIRef("https://w3id.org/lsc/ontology/catalog"), URIRef(f"{iri}/{lab}")
    g.add((cat, RDF.type, DCAT.Catalog))
    g.add((cat, DCAT.dataset, dataset))
    g.add((dataset, RDF.type, DCAT.Dataset))
    g.add((dataset, DCTERMS.title, Literal(f"{m['title']} {lab}", lang="en")))
    g.add((dataset, DCTERMS.isVersionOf, URIRef(iri)))
    g.add((dataset, OWL.versionInfo, Literal(lab)))
    if m["issued"]:
        g.add((dataset, DCTERMS.issued, Literal(m["issued"], datatype=XSD.date)))
    for fname, media in ((f"{name}.ttl", "text/turtle"), (f"{name}.jsonld", "application/ld+json"),
                         ("shapes.ttl", "text/turtle")):
        dist = URIRef(f"{base}/{fname}")
        g.add((dataset, DCAT.distribution, dist))
        g.add((dist, RDF.type, DCAT.Distribution))
        g.add((dist, DCAT.downloadURL, dist))
        g.add((dist, DCAT.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(name, g):
    m = MODULES[name]
    lab = label(m)
    # The package's own shape files lead the list (most modules have one); the rest belong to the modules it requires.
    shapes = parse(m["shapes"][:m.get("own_shapes", 1)])
    files = {f"{name}.ttl": g.serialize(format="turtle"), f"{name}.jsonld": jsonld(g),
             "shapes.ttl": shapes.serialize(format="turtle"), "catalog.ttl": catalog(name)}
    with open(os.path.join(ONTOLOGY, "releases", name, "CHANGELOG.md")) as f:
        files["CHANGELOG.md"] = f.read()
    files["manifest.json"] = json.dumps({
        "module": name, "version": lab, "release_candidate": m["stage"] is not None,
        "ontology_iri": MODULES_NS + name, "version_iri": f"{MODULES_NS}{name}/{lab}",
        "depends_on": dependencies(name), "decisions": m["decisions"], "triples": len(g),
        "approved_by": None if m["stage"] else {"who": m.get("approver", "The decision owner"), "recorded_in": m["approval"][0]},
        "files": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())}}, indent=2) + "\n"
    return files


def release_dir(name):
    return os.path.join(ONTOLOGY, "releases", name, label(MODULES[name]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module", choices=sorted(MODULES))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    g = build(args.module)
    conforms, text = check(args.module, g)
    if not conforms:
        sys.exit(f"{args.module}: the shapes fail:\n{text}")
    files = package(args.module, g)
    out = release_dir(args.module)
    print(f"{args.module} {label(MODULES[args.module])}: {len(g)} triples; shapes conform")
    if args.verify:
        stale = [n for n, t in files.items()
                 if not os.path.exists(os.path.join(out, n)) or open(os.path.join(out, n)).read() != t]
        if stale:
            sys.exit(f"{args.module} release package is not current: {stale}")
        print("release package is current")
    if args.write:
        os.makedirs(out, exist_ok=True)
        for n, t in files.items():
            with open(os.path.join(out, n), "w") as f:
                f.write(t)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
