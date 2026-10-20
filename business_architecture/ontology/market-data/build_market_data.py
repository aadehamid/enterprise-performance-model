"""Build the market-data module (Step 7; EPM-DEC-001-0057, EPM-DEC-001-0066).

    python3 build_market_data.py            # check the tables and print the figures
    python3 build_market_data.py --write    # also write market-data.ttl
    python3 build_market_data.py --verify   # fail unless market-data.ttl equals a fresh build

regions.csv gives MPC's refining regions and MPC Economics' product market regions;
benchmarks.csv the crude markers, product benchmarks and the RVO cost; series.csv the
published series of the crack-spreads measure, each with its legs, the series it blends, or a
mark that its source does not list its legs. The build fails unless every region, benchmark
and blended series a row names exists, each leg-built series has one crude leg, at least one
product leg and at most one compliance-cost leg, a blended series has no legs, a series with
neither legs nor a blend is marked legs_unstated, and every source is in the source list.
"""
import argparse
import csv
import os
import sys

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
MEASURES = os.path.join(HERE, "..", "kpi", "measures.ttl")
OUTPUT = os.path.join(HERE, "market-data.ttl")

MKT = Namespace("https://w3id.org/lsc/ontology/modules/market-data/")
BKIND = Namespace("https://w3id.org/lsc/ontology/modules/market-data/benchmark-kind/")
REGION = Namespace("https://w3id.org/lsc/ontology/modules/market-data/region/")
BENCH = Namespace("https://w3id.org/lsc/ontology/modules/market-data/benchmark/")
SERIES = Namespace("https://w3id.org/lsc/ontology/modules/market-data/series/")
LEG = Namespace("https://w3id.org/lsc/ontology/modules/market-data/leg/")
MEASURE = Namespace("https://w3id.org/lsc/ontology/modules/kpi/measure/")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")
MEASURE_ID = "crack-spreads"
SOURCES = {
    # The same title the kpi module gives this shared source node (build_measures.py).
    "MPC-S01": (SRC["mpc-performance-measures-evidence"],
                "MPC performance measures, business_architecture/reference/mpc/mpc-performance-measures-evidence.md"),
    "CME-CRACK": (SRC["cme-trading-crack-spreads-2024"],
                  "CME Group, Trading Crack Spreads (2024), https://www.cmegroup.com/articles/2024/trading-crack-spreads.html, "
                  "retrieved 2026-10-19"),
    "MPC-ECON": (SRC["mpc-economics-crack-spread-kpi-definition"],
                 "MPC Economics, 3-2-1 Crack Spread KPI Definition, provided by the decision owner on 2026-10-20, "
                 "business_architecture/reference/internal/crack-spread-kpi-definition.md"),
    "CME-FRESH": (SRC["cme-fresh-from-the-trading-room-2026-07-14"],
                  "CME Group, Fresh from the Trading Room: Papering over the cracks (2026-07-14), "
                  "https://www.cmegroup.com/newsletters/fresh-from-the-trading-room/2026-07-14.html, retrieved 2026-10-19"),
}
REGION_SOURCE = "MPC-S01"
# The blended series' weights change by period, so they are a note with their source, not a value.
BLEND_NOTE = ("Beginning in the second quarter of 2024, MPC weighted the blended crack spread 42 percent Gulf Coast, "
              "40 percent Mid-Continent and 18 percent West Coast, based on its refining capacity by region in each "
              "period (MPC FY2025 Form 10-K, Item 7). The weights for 2026 are in the Q2 2026 Form 10-Q (MPC-S03; "
              "mpc-performance-measures-evidence.md, row 10).")
NYMEX_NOTE = ("Shares the name 3-2-1 with MPC's regional crack spreads but is a different series: its legs are "
              "exchange futures, and its gasoline leg is RBOB, which MPC's benchmarks do not use. MPC Economics "
              "publishes it as NYMEX 3-2-1 Crack (Price Master 39998) and calls the diesel leg NYMEX Heating Oil "
              "(crack-spread-kpi-definition.md, section 4.3).")
ECON_BLEND_NOTE = ("MPC Economics weights the three ex-RIN cracks USGC 0.40, Chicago 0.40 and LA 0.20 before 5 May 2024, "
                   "and USGC 0.42, Chicago 0.40 and LA 0.18 after (crack-spread-kpi-definition.md, section 4.4).")
EX_RVO_NOTE = ("Computed daily by MPC Economics' Ex-RVO formula, ((CBOB x 42 x 2) + (ULSD x 42 x 1)) / 3 - Crude - (RVO x 42), "
               "with product prices in dollars per gallon and crude in dollars per barrel; the monthly series is the mean of "
               "the daily published values (crack-spread-kpi-definition.md, sections 3.2 and 5.3). MPC's price data labels "
               "this treatment ex-RIN.")
SCHEMES = {"refining": MKT.RefiningRegions, "market": MKT.MarketRegions}
KINDS = ("crude-marker", "product-benchmark", "compliance-cost")


def read_csv(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


def legs(text):
    return [(b, int(n)) for b, n in (part.split(":") for part in text.split(";") if part)]


def load():
    regions, benchmarks, series = read_csv("regions.csv"), read_csv("benchmarks.csv"), read_csv("series.csv")
    region_ids = {r["slug"] for r in regions}
    bench = {b["slug"]: b for b in benchmarks}
    series_ids = {s["slug"] for s in series}
    measures = {str(n) for n in Graph().parse(MEASURES).objects(None, SKOS.notation)}
    problems = [] if MEASURE_ID in measures else [f"{MEASURE_ID} is not a measure of the kpi module"]
    problems += [f"region {r['slug']}: unknown scheme {r['scheme']!r}" for r in regions if r["scheme"] not in SCHEMES]
    for b in benchmarks:
        if b["region"] and b["region"] not in region_ids:
            problems.append(f"benchmark {b['slug']}: unknown region {b['region']!r}")
        if b["kind"] not in KINDS:
            problems.append(f"benchmark {b['slug']}: unknown kind {b['kind']!r}")
        if b["source"] not in SOURCES:
            problems.append(f"benchmark {b['slug']}: unknown source {b['source']!r}")
    for s in series:
        if s["region"] and s["region"] not in region_ids:
            problems.append(f"series {s['slug']}: unknown region {s['region']!r}")
        if s["source"] not in SOURCES:
            problems.append(f"series {s['slug']}: unknown source {s['source']!r}")
        blend = [x for x in s["blend_of"].split(";") if x]
        problems += [f"series {s['slug']}: blends unknown series {x!r}" for x in blend if x not in series_ids]
        if blend and s["legs"]:
            problems.append(f"series {s['slug']}: a blended series has no legs of its own")
        if s["legs_unstated"] and (blend or s["legs"]):
            problems.append(f"series {s['slug']}: legs_unstated is only for a series with neither legs nor a blend")
        if not blend and not s["legs"] and not s["legs_unstated"]:
            problems.append(f"series {s['slug']}: has neither legs nor a blend, and is not marked legs_unstated")
        if not blend and s["legs"]:
            kinds = [bench[b]["kind"] for b, _ in legs(s["legs"]) if b in bench]
            problems += [f"series {s['slug']}: unknown benchmark {b!r}" for b, _ in legs(s["legs"]) if b not in bench]
            if kinds.count("crude-marker") != 1 or "product-benchmark" not in kinds or kinds.count("compliance-cost") > 1:
                problems.append(f"series {s['slug']}: needs one crude leg, at least one product leg and at most one compliance-cost leg")
            if ("compliance-cost" in kinds) != (s["excludes_rin_cost"] == "false"):
                problems.append(f"series {s['slug']}: a series deducts the RVO cost (an RVO leg) exactly when excludes_rin_cost is false")
    if problems:
        sys.exit("market-data tables do not reconcile:\n  " + "\n  ".join(problems))
    return regions, benchmarks, series


def build(regions, benchmarks, series):
    g = Graph()
    for prefix, ns in (("mkt", MKT), ("bkind", BKIND), ("region", REGION), ("benchmark", BENCH), ("series", SERIES),
                       ("leg", LEG), ("measure", MEASURE), ("src", SRC), ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    for iri, title in SOURCES.values():
        g.add((iri, RDF.type, DCTERMS.BibliographicResource))
        g.add((iri, DCTERMS.title, Literal(title, lang="en")))

    def concept(iri, scheme, row, source):
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.inScheme, scheme))
        g.add((iri, SKOS.prefLabel, Literal(row["label"], lang="en")))
        g.add((iri, SKOS.notation, Literal(row["slug"], datatype=XSD.string)))
        g.add((iri, SKOS.definition, Literal(row["definition"], lang="en")))
        g.add((iri, DCTERMS.source, SOURCES[source][0]))

    for r in regions:
        concept(REGION[r["slug"]], SCHEMES[r["scheme"]], r, REGION_SOURCE if r["scheme"] == "refining" else "MPC-ECON")
    for b in benchmarks:
        iri = BENCH[b["slug"]]
        concept(iri, MKT.Series, b, b["source"])
        g.add((iri, RDF.type, MKT.Benchmark))
        g.add((iri, MKT.benchmarkKind, BKIND[b["kind"]]))
        if b["region"]:
            g.add((iri, MKT.region, REGION[b["region"]]))
        if b["mpr"]:
            g.add((iri, MKT.priceMasterId, Literal(b["mpr"], datatype=XSD.string)))
    for s in series:
        iri = SERIES[s["slug"]]
        concept(iri, MKT.Series, s, s["source"])
        g.add((iri, RDF.type, MKT.BenchmarkSeries))
        g.add((iri, MKT.seriesOf, MEASURE[MEASURE_ID]))
        for alias in (a for a in s["aliases"].split(";") if a):
            g.add((iri, SKOS.altLabel, Literal(alias, lang="en")))
        if s["region"]:
            g.add((iri, MKT.region, REGION[s["region"]]))
        if s["excludes_rin_cost"]:
            g.add((iri, MKT.excludesRINCost, Literal(s["excludes_rin_cost"] == "true")))
        for b, n in legs(s["legs"]):
            leg = LEG[f"{s['slug']}--{b}"]
            g.add((iri, MKT.leg, leg))
            g.add((leg, RDF.type, MKT.Leg))
            g.add((leg, MKT.benchmark, BENCH[b]))
            g.add((leg, MKT.barrels, Literal(n)))
        for x in (x for x in s["blend_of"].split(";") if x):
            g.add((iri, MKT.blendOf, SERIES[x]))
        if s["mpr"]:
            g.add((iri, MKT.priceMasterId, Literal(s["mpr"], datatype=XSD.string)))
        if s["legs_unstated"]:
            g.add((iri, MKT.legsUnstated, Literal(True)))
        note = (NYMEX_NOTE if s["slug"] == "crack-nymex-3-2-1"
                else (ECON_BLEND_NOTE if s["source"] == "MPC-ECON" else BLEND_NOTE) if s["blend_of"]
                else EX_RVO_NOTE if s["excludes_rin_cost"] == "false" else None)
        if note:
            g.add((iri, SKOS.scopeNote, Literal(note, lang="en")))
    return g


def figures(regions, benchmarks, series):
    return {
        "regions": len(regions),
        "market regions": sum(r["scheme"] == "market" for r in regions),
        "benchmarks": len(benchmarks),
        "crude markers": sum(b["kind"] == "crude-marker" for b in benchmarks),
        "price master ids": sum(bool(b["mpr"]) for b in benchmarks) + sum(bool(s["mpr"]) for s in series),
        "series": len(series),
        "legs": sum(len(legs(s["legs"])) for s in series),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    regions, benchmarks, series = load()
    text = ("# Benchmark series of the market-data module (Step 7; EPM-DEC-001-0057, EPM-DEC-001-0066).\n"
            "# Built by build_market_data.py from regions.csv, benchmarks.csv and series.csv. Do not edit by hand.\n"
            + build(regions, benchmarks, series).serialize(format="turtle"))
    print("; ".join(f"{k} {v}" for k, v in figures(regions, benchmarks, series).items()))
    if args.verify:
        if not (os.path.exists(OUTPUT) and open(OUTPUT).read() == text):
            sys.exit("market-data.ttl is not current: run build_market_data.py --write")
        print("market-data.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
