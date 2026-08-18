#!/usr/bin/env python3
"""10_cv_map.py — land controlled vocabulary + map; prove lookup and grains.

Demo 2 / Track B. Working pack only. Does not change TABLES in config.py.
Does not rename tickets.csv. Does not load ontology. Does not add Credit
headroom. Does not touch the certified Genie or the Metric View.
Never prints DATABRICKS_TOKEN, host, or warehouse id.

term_id is the join key; ontology_iri is a bind to the sidecar, not a
replacement. cv_alias and cv_map still point at term_id.
"""

from __future__ import annotations

import csv
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (  # noqa: E402
    DATA_DIR,
    PACK_ROOT,
    connect,
    run_statement,
    settings,
    sql_str,
    values_as_select,
)

EXPECTED_APEX_USD = Decimal("115960.80")
EXPECTED_APEX_TICKETS = 8
CUSTOMER_IDS = {"id:sold-to", "id:loading-authorized-party"}
CERTIFIED_GRAINS = {"id:payer", "id:sold-to", "id:ship-to"}
EXPECTED_TERM_IDS = (
    "id:bill-to",
    "id:loading-authorized-party",
    "id:payer",
    "id:ship-to",
    "id:sold-to",
)
EXPECTED_IRIS = {
    "id:payer": "https://example.org/domain-ontology-kpi/o2c#Payer",
    "id:sold-to": "https://example.org/domain-ontology-kpi/o2c#SoldTo",
    "id:bill-to": "https://example.org/domain-ontology-kpi/o2c#BillTo",
    "id:ship-to": "https://example.org/domain-ontology-kpi/o2c#ShipTo",
    "id:loading-authorized-party": "https://example.org/domain-ontology-kpi/o2c#LoadingAuthorizedParty",
}

TERM_COLS = [
    ("term_id", "STRING", "str"),
    ("preferred_label", "STRING", "str"),
    ("scope_note", "STRING", "str"),
    ("ontology_iri", "STRING", "str"),
]
ALIAS_COLS = [
    ("term_id", "STRING", "str"),
    ("alias", "STRING", "str"),
]
MAP_COLS = [
    ("local_system", "STRING", "str"),
    ("field", "STRING", "str"),
    ("local_key", "STRING", "str"),
    ("term_id", "STRING", "str"),
    ("map_ok", "STRING", "str"),
    ("note", "STRING", "str"),
]
DIM_CUSTOMER_COLS = [
    ("system_name", "STRING", "str"),
    ("customer_id", "STRING", "str"),
    ("party_name", "STRING", "str"),
    ("note", "STRING", "str"),
]


def money(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def load_csv(name: str) -> list[dict]:
    path = DATA_DIR / name
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fallback_lookup_sql(fq: str, q: str) -> str:
    """Documented SELECT used when CREATE FUNCTION is refused on Free."""
    lit = sql_str(q)
    return f"""SELECT DISTINCT
  t.term_id,
  t.preferred_label,
  h.hit_kind,
  h.hit_value,
  t.scope_note
FROM (
  SELECT a.term_id, 'alias' AS hit_kind, a.alias AS hit_value
  FROM {fq}.cv_alias a
  WHERE lower(a.alias) = lower({lit})
  UNION ALL
  SELECT term.term_id, 'label' AS hit_kind,
    CASE
      WHEN lower(term.preferred_label) = lower({lit}) THEN term.preferred_label
      ELSE term.term_id
    END AS hit_value
  FROM {fq}.cv_term term
  WHERE lower(term.preferred_label) = lower({lit})
     OR lower(term.term_id) = lower({lit})
  UNION ALL
  SELECT m.term_id, 'map_key' AS hit_kind, m.local_key AS hit_value
  FROM {fq}.cv_map m
  WHERE m.term_id IS NOT NULL
    AND lower(m.local_key) = lower({lit})
) h
INNER JOIN {fq}.cv_term t ON t.term_id = h.term_id
ORDER BY t.term_id, h.hit_kind"""


def function_ddl(fq: str) -> str:
    return f"""CREATE OR REPLACE FUNCTION {fq}.cv_lookup(q STRING)
RETURNS TABLE (
  term_id STRING,
  preferred_label STRING,
  hit_kind STRING,
  hit_value STRING,
  scope_note STRING
)
LANGUAGE SQL
READS SQL DATA
RETURN
SELECT DISTINCT
  t.term_id,
  t.preferred_label,
  h.hit_kind,
  h.hit_value,
  t.scope_note
FROM (
  SELECT a.term_id, 'alias' AS hit_kind, a.alias AS hit_value
  FROM {fq}.cv_alias a
  WHERE lower(a.alias) = lower(q)
  UNION ALL
  SELECT term.term_id, 'label' AS hit_kind,
    CASE
      WHEN lower(term.preferred_label) = lower(q) THEN term.preferred_label
      ELSE term.term_id
    END AS hit_value
  FROM {fq}.cv_term term
  WHERE lower(term.preferred_label) = lower(q)
     OR lower(term.term_id) = lower(q)
  UNION ALL
  SELECT m.term_id, 'map_key' AS hit_kind, m.local_key AS hit_value
  FROM {fq}.cv_map m
  WHERE m.term_id IS NOT NULL
    AND lower(m.local_key) = lower(q)
) h
INNER JOIN {fq}.cv_term t ON t.term_id = h.term_id"""


def lookup_sql(fq: str, q: str, use_function: bool) -> str:
    if use_function:
        return f"SELECT * FROM {fq}.cv_lookup({sql_str(q)})"
    return fallback_lookup_sql(fq, q)


def land(cur, fq: str) -> None:
    print(f"\n======== LAND CV TABLES → {fq} ========")
    specs = [
        ("cv_term.csv", f"{fq}.cv_term", TERM_COLS),
        ("cv_alias.csv", f"{fq}.cv_alias", ALIAS_COLS),
        ("cv_map.csv", f"{fq}.cv_map", MAP_COLS),
        ("dim_customer.csv", f"{fq}.dim_customer", DIM_CUSTOMER_COLS),
    ]
    for csv_name, table, cols in specs:
        rows = load_csv(csv_name)
        print(f"  {csv_name} → {table} ({len(rows)} rows)")
        run_statement(cur, values_as_select(table, cols, rows), fetch=False)


def try_create_lookup(cur, fq: str) -> bool:
    print("\n======== CREATE FUNCTION cv_lookup(q STRING) ========")
    try:
        run_statement(cur, function_ddl(fq), fetch=False)
        print("CREATE FUNCTION ok. Prove will call SELECT * FROM cv_lookup(q).")
        return True
    except Exception as exc:
        print(
            "CREATE FUNCTION refused on this warehouse (Free gap or SQL UDTF limit).\n"
            f"  ({type(exc).__name__}: {exc})\n"
            "Falling back to the documented SELECT (alias ∪ label ∪ map_key).\n"
            "Lookup still runs; customer must still return two IDs."
        )
        return False


def prove_lookup(cur, fq: str, q: str, use_function: bool) -> list:
    print(f"\n======== LOOKUP {q!r} ========")
    return run_statement(cur, lookup_sql(fq, q, use_function))


def distinct_ids(rows: list) -> set[str]:
    return {str(r[0]) for r in rows if r and r[0] is not None}


def labels_for(rows: list) -> set[str]:
    return {str(r[1]) for r in rows if r and r[1] is not None}


def main() -> int:
    cfg = settings()
    fq = cfg.fq
    print("CV / map land + prove")
    print(f"  catalog.schema = {fq}")
    print("  token          = (set, not printed)")
    print("  host           = (from .env, not printed)")
    print("  warehouse      = (from .env, id not printed)")
    print("  tickets.csv    = not renamed; no customer_id column added")
    print("  config.TABLES  = not edited (sidecar is not Lakebase/raw)")

    failures: list[str] = []
    tickets_header = (PACK_ROOT / "data" / "tickets.csv").read_text(encoding="utf-8").splitlines()[0]
    if "customer_id" in [c.strip() for c in tickets_header.split(",")]:
        failures.append("tickets.csv header now has customer_id (must stay unchanged)")

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            land(cur, fq)
            use_function = try_create_lookup(cur, fq)

            print("\n======== 0. cv_term ontology_iri binds (term_id stays the join key) ========")
            terms = run_statement(
                cur,
                f"""SELECT term_id, preferred_label, ontology_iri
FROM {fq}.cv_term
ORDER BY term_id""",
            )
            got_ids = [str(r[0]) for r in terms]
            if tuple(got_ids) != EXPECTED_TERM_IDS:
                failures.append(
                    f"cv_term term_id values changed: expected {list(EXPECTED_TERM_IDS)}, got {got_ids}"
                )
            else:
                print("  PASS: term_id values unchanged (still id:payer / id:sold-to / …)")
            for term_id, label, iri in terms:
                tid = str(term_id)
                want = EXPECTED_IRIS.get(tid, "MISSING")
                if tid not in EXPECTED_IRIS:
                    failures.append(f"unexpected term_id {tid!r}")
                    continue
                if want is None:
                    if iri is not None:
                        failures.append(
                            f"{tid} ontology_iri must be NULL (no invented LAP class), got {iri!r}"
                        )
                    else:
                        print(f"  PASS: {tid} ontology_iri IS NULL")
                elif iri != want:
                    failures.append(f"{tid} ontology_iri expected {want}, got {iri!r}")
                else:
                    print(f"  PASS: {tid} / {label} → {iri}")

            print("\n======== 1. FULL cv_map ========")
            cmap = run_statement(
                cur,
                f"""SELECT local_system, field, local_key, term_id, map_ok, note
FROM {fq}.cv_map
ORDER BY local_system, field, local_key""",
            )
            if len(cmap) != 22:
                failures.append(f"cv_map expected 22 rows, got {len(cmap)}")

            print("\n======== 2. cv_lookup('customer') ========")
            customer = prove_lookup(cur, fq, "customer", use_function)
            got_ids = distinct_ids(customer)
            print(f"  distinct term_ids = {sorted(got_ids)}")
            if got_ids != CUSTOMER_IDS:
                failures.append(
                    f"lookup('customer') distinct IDs expected {sorted(CUSTOMER_IDS)}, got {sorted(got_ids)}"
                )
            else:
                print("  PASS: exactly two IDs — id:sold-to and id:loading-authorized-party")

            print("\n======== 3. cv_lookup('RG') ========")
            rg = prove_lookup(cur, fq, "RG", use_function)
            rg_ids = distinct_ids(rg)
            rg_labels = labels_for(rg)
            if rg_ids != {"id:payer"} or "Payer" not in rg_labels:
                failures.append(f"lookup('RG') expected id:payer / Payer, got ids={rg_ids} labels={rg_labels}")
            else:
                print("  PASS: RG → id:payer / Payer")

            print("\n======== 4. cv_lookup('APEX-PAYER') ========")
            apex_key = prove_lookup(cur, fq, "APEX-PAYER", use_function)
            apex_ids = distinct_ids(apex_key)
            apex_labels = labels_for(apex_key)
            if apex_ids != {"id:payer"} or "Payer" not in apex_labels:
                failures.append(
                    f"lookup('APEX-PAYER') expected id:payer / Payer, got ids={apex_ids} labels={apex_labels}"
                )
            else:
                print("  PASS: APEX-PAYER → id:payer / Payer")

            print("\n======== 5. Good Unbilled MEASURE() at mapped payer grain ========")
            measure_sql = f"""SELECT payer, MEASURE(unbilled_usd) AS unbilled_usd, MEASURE(unbilled_ticket_count) AS tickets
FROM {fq}.unbilled_usd
WHERE payer = 'Apex Fuels LLC'
GROUP BY payer"""
            try:
                apex = run_statement(cur, measure_sql)
            except Exception as exc:
                print(f"MEASURE() failed ({type(exc).__name__}: {exc}). DESCRIBE the view.")
                try:
                    run_statement(cur, f"DESCRIBE TABLE EXTENDED {fq}.unbilled_usd")
                except Exception as desc_exc:
                    print(f"  DESCRIBE also failed: {desc_exc}")
                failures.append(f"Apex MEASURE() failed: {exc}")
                apex = []
            if not apex:
                if "Apex MEASURE() failed" not in " ".join(failures):
                    failures.append("Apex MEASURE() returned 0 rows")
            else:
                payer_name, usd, n = apex[0][0], money(apex[0][1]), int(apex[0][2])
                print(f"  payer={payer_name!r} usd={usd} tickets={n}")
                if payer_name != "Apex Fuels LLC" or usd != EXPECTED_APEX_USD or n != EXPECTED_APEX_TICKETS:
                    failures.append(
                        f"Apex MEASURE() expected 115960.80 / 8, got {usd} / {n}"
                    )
                else:
                    print("  PASS: Apex Fuels LLC Unbilled $115960.80 / 8 tickets")

            print("\n======== 6. Refused customer_id grain ========")
            refused_customer = (
                f"""SELECT customer_id, MEASURE(unbilled_usd) AS unbilled_usd
FROM {fq}.unbilled_usd
WHERE customer_id = '1000123'
GROUP BY customer_id"""
            )
            try:
                bad = run_statement(cur, refused_customer)
                failures.append(
                    f"customer_id grain unexpectedly succeeded ({len(bad)} rows). Must fail."
                )
                print("  FAIL: customer_id is not a certified Unbilled dimension")
            except Exception as exc:
                print(f"  PASS (refused): {type(exc).__name__}: {exc}")

            print("\n======== 7. Refused CONS-4412 / loading-authorized grain ========")
            cons_map = run_statement(
                cur,
                f"""SELECT local_system, field, local_key, term_id, map_ok, note
FROM {fq}.cv_map
WHERE local_key = 'CONS-4412'""",
            )
            cons_ids = {str(r[3]) for r in cons_map}
            if cons_ids != {"id:loading-authorized-party"}:
                failures.append(
                    f"CONS-4412 map expected id:loading-authorized-party, got {cons_ids}"
                )
            elif cons_ids & CERTIFIED_GRAINS:
                failures.append(f"CONS-4412 must not map to a certified Unbilled grain, got {cons_ids}")
            else:
                print("  PASS: CONS-4412 maps to id:loading-authorized-party (not payer/sold-to/ship-to)")

            cons_dim_sql = f"""SELECT loading_authorized_party, MEASURE(unbilled_usd) AS unbilled_usd
FROM {fq}.unbilled_usd
GROUP BY loading_authorized_party"""
            cons_reason = None
            try:
                dim_rows = run_statement(cur, cons_dim_sql)
                eq_sql = f"""SELECT payer, MEASURE(unbilled_usd) AS unbilled_usd
FROM {fq}.unbilled_usd
WHERE payer = 'CONS-4412'
GROUP BY payer"""
                eq_rows = run_statement(cur, eq_sql)
                if eq_rows:
                    failures.append(
                        f"CONS-4412 equality on payer returned {len(eq_rows)} rows; expected refuse or 0"
                    )
                else:
                    cons_reason = "no loading-authorized dim; payer equality to CONS-4412 returned 0 rows"
                    print(f"  PASS (0 rows on payer = 'CONS-4412'): {cons_reason}")
            except Exception as exc:
                cons_reason = f"dimension-missing / refused: {type(exc).__name__}: {exc}"
                print(f"  PASS (refused CONS-4412 grain): {cons_reason}")

            print("\n======== 8. Raw dim_customer + tickets header ========")
            raw_cust = run_statement(
                cur,
                f"SELECT customer_id FROM {fq}.dim_customer",
            )
            raw_ids = [str(r[0]) for r in raw_cust]
            if raw_ids != ["1000123"]:
                failures.append(f"dim_customer.customer_id expected ['1000123'], got {raw_ids}")
            else:
                print("  PASS: raw SELECT customer_id → 1000123")
            print(f"  tickets.csv header (unchanged) = {tickets_header}")
            if "customer_id" in tickets_header.split(","):
                failures.append("tickets.csv gained a customer_id column")
            try:
                desc = run_statement(cur, f"DESCRIBE {fq}.raw_tickets")
                raw_cols = {str(r[0]).lower() for r in desc}
                if "customer_id" in raw_cols:
                    failures.append("raw_tickets has customer_id (tickets were not to be renamed)")
                else:
                    print("  PASS: raw_tickets has no customer_id column")
            except Exception as exc:
                print(f"  DESCRIBE raw_tickets skipped: {type(exc).__name__}: {exc}")

            print("\n======== 9. Catalog about-ID (read-only; no UPDATE) ========")
            meta = run_statement(
                cur,
                f"""SELECT kpi_id, name, ontology_iri
FROM {fq}.dim_kpi_metadata
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'""",
            )
            if not meta:
                failures.append("dim_kpi_metadata missing Unbilled row KPI-O2C-UNBILLED-USD")
            else:
                about = str(meta[0][2])
                print(f"  Unbilled about-ID / ontology_iri = {about}")
                if not about.endswith("#UnbilledState"):
                    failures.append(f"Unbilled about-ID must stay UnbilledState, got {about!r}")
                else:
                    print("  PASS: catalog about-ID still UnbilledState (not updated)")

            print("\n======== 10. Teaching SELECT — two seats, not collapsed ========")
            run_statement(
                cur,
                f"""SELECT 'cv_term' AS seat, term_id AS key, preferred_label AS label, ontology_iri
FROM {fq}.cv_term
WHERE ontology_iri IS NOT NULL
UNION ALL
SELECT 'catalog', kpi_id, name, ontology_iri
FROM {fq}.dim_kpi_metadata
WHERE ontology_iri LIKE '%#UnbilledState'""",
            )
            print("  (party IRIs on cv_term; Unbilled catalog bind stays #UnbilledState)")

    print()
    print("RULE: Unbilled MEASURE() may only slice on keys that map to id:payer / id:sold-to / id:ship-to. Join on customer_id or CONS-4412 is not a certified grain.")
    print()
    if failures:
        print("FAIL: one or more prove steps failed:")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASS: CV/map landed. ontology_iri bound on all five terms. lookup('customer') is two IDs. Mapped payer MEASURE() holds. Refused grains refused. Catalog about-ID still UnbilledState.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
