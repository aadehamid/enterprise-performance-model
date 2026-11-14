"""Check a generated LSC catalog: size against the production profile, real-name leaks, and, once
loaded, that the database holds exactly the generated catalog and answers every competency check.

    python src/verify_synthetic_catalog.py                          # files only
    python src/verify_synthetic_catalog.py --database lsc           # files, then the loaded database
    python src/verify_synthetic_catalog.py --database lsc --against-live governancemetadata

--against-live compares generated names with a production database and is only meaningful on the
machine that holds one. Exit code 1 on any failure.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "synthetic_data"
QUESTIONS_PATH = ROOT / "synthetic" / "competency_questions.json"

# Production lineage graph, 2026-11-01 (counts only). Chat history is sized to the plan, not production.
PROFILE = {
    "nodes": {
        "Server": 210, "DataSystem": 404, "FlatFile": 1, "Schema": 280, "Table": 7387, "Column": 31725,
        "Report": 2623, "BusinessArea": 13, "CapabilityDataDomain": 30, "DataProductLine": 4, "ValueStreamStage": 3,
        "BusinessProcess": 12, "Policy": 2, "MasterDataDomain": 11, "DataProduct": 12, "DataPipeline": 7,
        "DataModel": 42, "Person": 291, "RoleAssignment": 2314, "Session": 50, "Message": 200,
    },
    "labels": {"Table:View": 2298, "Table:Fact": 60, "Table:Dimension": 97, "Table:Legacy": 128, "Schema:Legacy": 7},
    "rels": {
        "Table-HAS_COLUMN-Column": 31713, "Report-CONSUMES-Table": 13237, "Column-DERIVED_FROM-Column": 12239,
        "Schema-CONTAINS-Table": 7365, "Table-DERIVED_FROM-Table": 2764, "Person-HAS_ROLE-RoleAssignment": 2426,
        "DataSystem-CONTAINS-Table": 2109, "Table-REPLICATED_TO-Table": 1744, "RoleAssignment-APPLIES_TO-Report": 1515,
        "RoleAssignment-APPLIES_TO-Table": 799, "DataProduct-REALIZED_BY-Table": 351, "Server-HOSTS-DataSystem": 298,
        "DataSystem-HOSTS-Schema": 293, "DataSystem-BELONGS_TO-BusinessArea": 244,
        "Report-BELONGS_TO-CapabilityDataDomain": 197, "Table-BELONGS_TO-CapabilityDataDomain": 176,
        "MasterDataDomain-REALIZED_IN-Table": 160, "DataSystem-MIGRATED_TO-Table": 110, "Table-REFACTORED_TO-Table": 89,
        "CapabilityDataDomain-SUPPORTS-BusinessProcess": 46, "DataModel-MODELS-CapabilityDataDomain": 38,
        "Schema-BELONGS_TO-BusinessArea": 35, "DataPipeline-READS-Table": 26, "DataModel-BELONGS_TO-DataSystem": 20,
        "DataProductLine-OWNS-CapabilityDataDomain": 17, "DataSystem-SUBJECT_TO-Policy": 15,
        "FlatFile-CONTAINS-Table": 13, "BusinessProcess-BELONGS_TO_STAGE-ValueStreamStage": 12,
        "DataProduct-BELONGS_TO-CapabilityDataDomain": 12, "DataSystem-REPLICATED_TO-Schema": 9,
        "Table-MIGRATED_FROM-DataSystem": 9, "DataPipeline-LOADS-Table": 9, "BusinessArea-HAS_PRODUCT_LINE-DataProductLine": 4,
        "BusinessArea-HAS_STAGE-ValueStreamStage": 3, "ValueStreamStage-NEXT_STAGE-ValueStreamStage": 2,
        "ValueStreamStage-LOOPS_BACK_TO-ValueStreamStage": 1, "BusinessProcess-INFORMS-BusinessProcess": 1,
        "Session-HAS_MESSAGE-Message": 200, "Session-LAST_MESSAGE-Message": 50, "Message-NEXT-Message": 150,
    },
}
TOLERANCE = 0.10

# Tokens that identify the source company or its systems, plants and hosts.
DENYLIST = re.compile(
    r"marathon|\bmpc\b|mplx|andeavor|tesoro|mgroupnet|kitty\s?hawk|\bkh_|\beis\b|garyville|catlettsburg|"
    r"galveston bay|findlay|\b(gbr|gvl|cbg|elp|anr|lar|slc|spp|mtz)\b|nvision|kittyhawk|speedway",
    re.IGNORECASE,
)

# Public products and data sources whose names the catalog keeps on purpose.
PUBLIC_NAMES = {
    "RightAngle", "Profisee", "SAP_S4", "Salesforce", "ServiceNow", "Workday", "IBM_Maximo", "AVEVA_PI",
    "Toptech_TMS", "Enverus", "OPIS", "ARGUS", "Kpler", "Bloomberg", "ICE", "Platts", "Genscape", "IIR", "FactSet",
    "LabWare_LIMS", "Wood Mackenzie", "DTN", "Saviynt", "Solarwinds", "Experian", "Esri ArcGIS", "Databricks", "Excel",
    "SharePoint", "Power BI", "Oracle EBS", "EIA", "EPA", "Aspen PIMS", "Allegro", "OPEC", "PHMSA", "Alteryx Sandbox",
    "Commercial Analysis",
}


def within(target: int, actual: int) -> bool:
    return abs(actual - target) <= max(2, round(target * TOLERANCE))


def profile_failures(counts: dict) -> list[str]:
    failures = []
    for kind, targets in PROFILE.items():
        for name, target in targets.items():
            actual = counts[kind].get(name, 0)
            if not within(target, actual):
                failures.append(f"{kind} {name}: {actual} vs production {target}")
    return failures


def leak_failures(data: Path) -> list[str]:
    hits = []
    for path in sorted(data.rglob("*.jsonl")):
        with path.open(encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                found = DENYLIST.search(line)
                if found:
                    hits.append(f"{path.relative_to(data)}:{n} contains '{found.group(0)}'")
    return hits


def _rels(data: Path, name: str) -> list[tuple[str, str]]:
    with (data / "rels" / f"{name}.jsonl").open(encoding="utf-8") as fh:
        return [(r["sourceId"], r["targetId"]) for r in map(json.loads, fh)]


def report_lineage_failures(data: Path) -> list[str]:
    """Reports with no consumed Semantic view whose DERIVED_FROM / REPLICATED_TO path reaches an Operational table."""
    layer = {t["qualifiedName"]: t["layer"] for t in map(json.loads, (data / "nodes/Table.jsonl").open(encoding="utf-8"))}
    with (data / "labels/Table-View.jsonl").open(encoding="utf-8") as fh:
        semantic_views = {qn for qn in (json.loads(line)["qualifiedName"] for line in fh) if layer.get(qn) == "Semantic"}
    upstream: dict[str, set[str]] = {}
    for down, up in _rels(data, "Table-DERIVED_FROM-Table"):
        upstream.setdefault(down, set()).add(up)
    for op, replica in _rels(data, "Table-REPLICATED_TO-Table"):
        upstream.setdefault(replica, set()).add(op)
    sourced: dict[str, bool] = {}

    def reaches_operational(table: str) -> bool:
        if table not in sourced:
            sourced[table] = False
            sourced[table] = layer.get(table) == "Operational" or any(map(reaches_operational, upstream.get(table, ())))
        return sourced[table]

    consumed: dict[str, list[str]] = {}
    for report, table in _rels(data, "Report-CONSUMES-Table"):
        if table in semantic_views:
            consumed.setdefault(report, []).append(table)
    return [f"Report '{key}' has no Semantic view with lineage to an Operational table"
            for key in sorted(_names(data, "Report", "reportKey"))
            if not any(map(reaches_operational, consumed.get(key, ())))]


REPORT_LINEAGE_CHECK = """
MATCH (r:Report)
WHERE NOT EXISTS {
  MATCH (r)-[:CONSUMES]->(:Table:View {layer: 'Semantic'})-[:DERIVED_FROM*1..8]->(src:Table)
  WHERE src.layer = 'Operational' OR (src)<-[:REPLICATED_TO]-(:Table {layer: 'Operational'})
}
RETURN r.name AS name ORDER BY name
"""


def _names(data: Path, label: str, field: str) -> set[str]:
    path = data / "nodes" / f"{label}.jsonl"
    with path.open(encoding="utf-8") as fh:
        return {json.loads(line)[field] for line in fh}


def live_overlap_failures(data: Path, live) -> list[str]:
    """Generated identifiers that equal a production identifier, apart from public products."""
    checks = [("DataSystem", "name"), ("Person", "name"), ("Report", "name"), ("Server", "serverName"),
              ("Table", "qualifiedName"), ("DataModel", "name"), ("DataProduct", "name"), ("DataPipeline", "name")]
    failures = []
    for label, field in checks:
        generated = _names(data, label, field) - PUBLIC_NAMES
        rows = live.run_query(f"MATCH (n:{label}) WHERE n.{field} IN $names RETURN n.{field} AS hit", names=sorted(generated))
        failures += [f"{label}.{field} '{r['hit']}' exists in production" for r in rows]
    return failures


def expected_value(manifest: dict, expect) -> list | int:
    keys = expect if isinstance(expect, list) else [expect]
    values: list = []
    for key in keys:
        value = manifest["expected"][key]
        if isinstance(value, int) and len(keys) == 1:
            return value
        values += value if isinstance(value, list) else list(value.values()) if isinstance(value, dict) else [value]
    return values


def competency_failures(db, manifest: dict) -> list[str]:
    failures = []
    for q in json.loads(QUESTIONS_PATH.read_text(encoding="utf-8")):
        if q.get("small_talk"):
            continue
        answer = db.run_query(q["check"])[0]["answer"]
        expected = expected_value(manifest, q["expect"])
        if isinstance(expected, int):
            ok = answer == expected
        elif q["match"] == "includes":
            ok = set(expected) <= set(answer)
        else:
            ok = sorted(set(answer)) == sorted(set(expected))
        if not ok:
            failures.append(f"{q['id']} {q['question']!r}: got {answer}, expected {expected}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--database", help="Loaded catalog database to check, e.g. lsc")
    parser.add_argument("--against-live", metavar="DATABASE", help="Production database to compare names against")
    args = parser.parse_args()

    manifest = json.loads((args.data / "manifest.json").read_text(encoding="utf-8"))
    sections = [("profile", profile_failures(manifest["counts"])), ("leaks", leak_failures(args.data)),
                ("report lineage", report_lineage_failures(args.data))]
    if args.database or args.against_live:
        from load_synthetic_catalog import INGEST_PATH, count_mismatches, database_counts, parse_steps
        from neo4j_loader import Neo4jLoader
    if args.against_live:
        live = Neo4jLoader(database=args.against_live)
        sections.append(("production overlap", live_overlap_failures(args.data, live)))
        live.close()
    if args.database:
        db = Neo4jLoader(database=args.database)
        steps = parse_steps(INGEST_PATH.read_text(encoding="utf-8"))
        sections.append(("database", count_mismatches(manifest["counts"], database_counts(db, steps))))
        sections.append(("competency", competency_failures(db, manifest)))
        sections.append(("database report lineage",
                         [f"Report '{r['name']}' has no Semantic view with lineage" for r in db.run_query(REPORT_LINEAGE_CHECK)]))
        db.close()

    failed = False
    for name, failures in sections:
        status = "FAIL" if failures else "ok"
        print(f"[{status}] {name}" + (f" ({len(failures)})" if failures else ""))
        for f in failures[:25]:
            print(f"    {f}")
        failed |= bool(failures)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
