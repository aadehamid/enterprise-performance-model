#!/usr/bin/env python3
"""12_cv_hunt.py — demonstrate the hunt that produced cv_map / cv_term.

Demo 2 / Track B. Working pack only. Runs after 10_cv_map.py.
Lands hunt stubs (sap_partner, tas_lift, sf_account, ra_business_associate) + re-lands
dim_customer. Does not land cv_*. If cv_* is missing, calls out and
runs 10, then continues.

Does not change TABLES in config.py. Does not rename tickets.csv.
Does not add a term_id or KPI. Does not touch the certified Genie,
the Metric View, gold, or the Unbilled catalog about-ID. Never prints
DATABRICKS_TOKEN, host, or warehouse id.

Walk (print as you go):
  hunt (table → column → value) → meanings → labels → map
  (system + field + key) → lookup → Unbilled still holds.

TABS is skipped. A TABS stub would invent a meaning or duplicate
sold-to. No TABS table is landed. No kunnr column.
"""

from __future__ import annotations

import csv
import subprocess
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
EXPECTED_CUSTOMER_ID = "1000123"
EXPECTED_CONS = "CONS-4412"
PASTE_FQ = "workspace.o2c_unbilled"

DIM_CUSTOMER_COLS = [
    ("system_name", "STRING", "str"),
    ("customer_id", "STRING", "str"),
    ("party_name", "STRING", "str"),
    ("note", "STRING", "str"),
]
SAP_PARTNER_COLS = [
    ("system_name", "STRING", "str"),
    ("sold_to", "STRING", "str"),
    ("bill_to", "STRING", "str"),
    ("payer", "STRING", "str"),
    ("ship_to", "STRING", "str"),
]
TAS_COLS = [
    ("system_name", "STRING", "str"),
    ("lift_id", "STRING", "str"),
    ("consignee", "STRING", "str"),
]
SF_COLS = [
    ("system_name", "STRING", "str"),
    ("account_id", "STRING", "str"),
]
RA_COLS = [
    ("system_name", "STRING", "str"),
    ("ba_id", "STRING", "str"),
    ("business_associate", "STRING", "str"),
    ("remittance_party", "STRING", "str"),
]
EXPECTED_SYSTEMS = {
    "raw_tickets": "Demo2",
    "sap_partner": "SAP",
    "sf_account": "Salesforce",
    "tas_lift": "TAS",
    "dim_customer": "Warehouse",
    "ra_business_associate": "RightAngle",
}


def money(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def load_csv(name: str) -> list[dict]:
    path = DATA_DIR / name
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fallback_lookup_sql(fq: str, q: str) -> str:
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


def lookup_sql(fq: str, q: str, use_function: bool) -> str:
    if use_function:
        return f"SELECT * FROM {fq}.cv_lookup({sql_str(q)})"
    return fallback_lookup_sql(fq, q)


def distinct_ids(rows: list) -> set[str]:
    return {str(r[0]) for r in rows if r and r[0] is not None}


def table_names(cur, fq: str) -> set[str]:
    rows = run_statement(cur, f"SHOW TABLES IN {fq}")
    names: set[str] = set()
    for row in rows:
        if not row:
            continue
        # Databricks: database, tableName, isTemporary (tableName often col 1)
        if len(row) >= 2 and row[1] is not None:
            names.add(str(row[1]).lower())
        elif row[0] is not None:
            names.add(str(row[0]).lower())
    return names


def ensure_cv(cur, fq: str) -> int:
    """Require 10 for cv_*. If missing, call out and run 10, then continue."""
    print("\n======== REQUIRE cv_* FROM 10 ========")
    names = table_names(cur, fq)
    needed = {"cv_term", "cv_alias", "cv_map"}
    missing = sorted(needed - names)
    if not missing:
        print("  cv_term / cv_alias / cv_map present (10 already ran).")
        return 0
    print(f"  missing {missing}. 10 must run first for cv_*.")
    print("  Running scripts/10_cv_map.py now, then continuing the hunt.")
    rc = subprocess.call([sys.executable, str(PACK_ROOT / "scripts" / "10_cv_map.py")])
    if rc != 0:
        print("10 failed. Operator: uv run python scripts/10_cv_map.py then re-run 12.")
        return rc
    names_after = table_names(cur, fq)
    still = sorted(needed - names_after)
    if still:
        print(f"  still missing {still} after 10. Stop.")
        return 1
    print("  10 finished. Continuing the hunt.")
    return 0


def land_hunt_stubs(cur, fq: str) -> None:
    print(f"\n======== LAND HUNT STUBS → {fq} ========")
    print("  12 lands sap_partner / tas_lift / sf_account /")
    print("  ra_business_associate + dim_customer.")
    print("  TABS skipped. Rack pricing skipped.")
    print("  CRM / Lift stubs retired (Salesforce + TAS).")
    specs = [
        ("dim_customer.csv", f"{fq}.dim_customer", DIM_CUSTOMER_COLS),
        ("sap_partner.csv", f"{fq}.sap_partner", SAP_PARTNER_COLS),
        ("tas_lift.csv", f"{fq}.tas_lift", TAS_COLS),
        ("sf_account.csv", f"{fq}.sf_account", SF_COLS),
        ("ra_business_associate.csv", f"{fq}.ra_business_associate", RA_COLS),
    ]
    for csv_name, table, cols in specs:
        rows = load_csv(csv_name)
        print(f"  {csv_name} → {table} ({len(rows)} rows)")
        run_statement(cur, values_as_select(table, cols, rows), fetch=False)
    for stale in ("crm_account", "lift_authorization"):
        run_statement(cur, f"DROP TABLE IF EXISTS {fq}.{stale}", fetch=False)
        print(f"  dropped stale {stale}")
    run_statement(
        cur,
        f"""DELETE FROM {fq}.cv_map
WHERE local_system IN ('CRM', 'Lift')
   OR (local_system = 'RightAngle' AND field = 'credit_party')""",
        fetch=False,
    )
    run_statement(
        cur,
        f"""MERGE INTO {fq}.cv_map AS tgt
USING (
  SELECT 'Salesforce' AS local_system, 'account_id' AS field, 'SF-APEX' AS local_key,
         CAST(NULL AS STRING) AS term_id, 'no' AS map_ok,
         'Salesforce account is a relationship, not a role' AS note
  UNION ALL
  SELECT 'TAS', 'consignee', 'CONS-4412',
         'id:loading-authorized-party', 'yes',
         'Wrong sense for Unbilled'
  UNION ALL
  SELECT 'RightAngle', 'business_associate', 'BA-APEX',
         CAST(NULL AS STRING), 'no',
         'Overloaded RightAngle BA — no map'
  UNION ALL
  SELECT 'RightAngle', 'remittance_party', 'APEX-PAYER',
         'id:payer', 'yes',
         'RA remittance is the payer'
) AS src
ON tgt.local_system = src.local_system
   AND tgt.field = src.field
   AND tgt.local_key = src.local_key
WHEN MATCHED THEN UPDATE SET
  term_id = src.term_id, map_ok = src.map_ok, note = src.note
WHEN NOT MATCHED THEN INSERT
  (local_system, field, local_key, term_id, map_ok, note)
VALUES
  (src.local_system, src.field, src.local_key, src.term_id, src.map_ok, src.note)""",
        fetch=False,
    )


def hunt_clues_sql(fq: str) -> str:
    """system_name, table, column, value. Tickets labeled Demo2. SF teaches account_id only."""
    return f"""SELECT DISTINCT system_name, table_name, column_name, value FROM (
  SELECT 'Demo2' AS system_name, 'raw_tickets' AS table_name, 'payer_id' AS column_name, CAST(payer_id AS STRING) AS value
  FROM {fq}.raw_tickets
  UNION ALL
  SELECT 'Demo2', 'raw_tickets', 'sold_to_id', CAST(sold_to_id AS STRING) FROM {fq}.raw_tickets
  UNION ALL
  SELECT 'Demo2', 'raw_tickets', 'bill_to_id', CAST(bill_to_id AS STRING) FROM {fq}.raw_tickets
  UNION ALL
  SELECT 'Demo2', 'raw_tickets', 'terminal_code', CAST(terminal_code AS STRING) FROM {fq}.raw_tickets
  UNION ALL
  SELECT system_name, 'sap_partner', 'sold_to', sold_to FROM {fq}.sap_partner
  UNION ALL
  SELECT system_name, 'sap_partner', 'bill_to', bill_to FROM {fq}.sap_partner
  UNION ALL
  SELECT system_name, 'sap_partner', 'payer', payer FROM {fq}.sap_partner
  UNION ALL
  SELECT system_name, 'sap_partner', 'ship_to', ship_to FROM {fq}.sap_partner
  UNION ALL
  SELECT system_name, 'tas_lift', 'consignee', consignee FROM {fq}.tas_lift
  UNION ALL
  SELECT system_name, 'dim_customer', 'customer_id', customer_id FROM {fq}.dim_customer
  UNION ALL
  SELECT system_name, 'sf_account', 'account_id', account_id FROM {fq}.sf_account
  UNION ALL
  SELECT system_name, 'ra_business_associate', 'business_associate', business_associate FROM {fq}.ra_business_associate
  UNION ALL
  SELECT system_name, 'ra_business_associate', 'remittance_party', remittance_party FROM {fq}.ra_business_associate
) clues"""


def hunt_with_map_sql(fq: str) -> str:
    return f"""SELECT
  h.system_name,
  h.table_name,
  h.column_name,
  h.value,
  m.local_system,
  m.field,
  m.local_key,
  m.term_id,
  m.map_ok,
  m.note
FROM (
  {hunt_clues_sql(fq)}
) h
LEFT JOIN {fq}.cv_map m
  ON m.local_system = h.system_name
 AND m.field = h.column_name
 AND m.local_key = h.value
ORDER BY h.system_name, h.table_name, h.column_name, h.value"""


def detect_lookup_function(cur, fq: str) -> bool:
    print("\n======== LOOKUP FUNCTION ========")
    try:
        run_statement(cur, f"SELECT * FROM {fq}.cv_lookup('customer') LIMIT 1")
        print("  cv_lookup(q) is callable. Prove will use the function.")
        return True
    except Exception as exc:
        print(
            "  cv_lookup function not callable "
            f"({type(exc).__name__}: {exc}).\n"
            "  Falling back to the documented SELECT (alias ∪ label ∪ map_key)."
        )
        return False


def paste_ready_sql() -> str:
    fq = PASTE_FQ
    return f"""+------------------------------------------------------------------------------+
| PASTE-READY SQL Editor hunt walk                                             |
| Qualified catalog.schema = {fq}                                              |
| No token / host / warehouse id. Attach the 2XS warehouse, then paste.        |
+------------------------------------------------------------------------------+

-- 1. Open sources. DESCRIBE shows system_name on every stub.
--    raw_tickets has no system_name column (tickets.csv unchanged).
--    Hunt SELECT labels tickets Demo2.
DESCRIBE {fq}.raw_tickets;
DESCRIBE {fq}.dim_customer;
DESCRIBE {fq}.sap_partner;
DESCRIBE {fq}.tas_lift;
DESCRIBE {fq}.sf_account;
DESCRIBE {fq}.ra_business_associate;

SELECT DISTINCT 'Demo2' AS system_name, 'raw_tickets' AS table_name
FROM {fq}.raw_tickets;
SELECT DISTINCT system_name FROM {fq}.dim_customer;
SELECT DISTINCT system_name FROM {fq}.sap_partner;
SELECT DISTINCT system_name FROM {fq}.tas_lift;
SELECT DISTINCT system_name FROM {fq}.sf_account;
SELECT DISTINCT system_name FROM {fq}.ra_business_associate;

-- 2. Hunt: system_name, table, column, value — then the map row.
--    Six systems: Demo2, SAP, Salesforce, TAS, Warehouse, RightAngle.
--    Salesforce teaches account_id / SF-APEX only. No customer_id column on sf_account.
WITH hunt AS (
  SELECT DISTINCT 'Demo2' AS system_name, 'raw_tickets' AS table_name,
         'payer_id' AS column_name, CAST(payer_id AS STRING) AS value
  FROM {fq}.raw_tickets
  UNION ALL
  SELECT DISTINCT 'Demo2', 'raw_tickets', 'sold_to_id', CAST(sold_to_id AS STRING)
  FROM {fq}.raw_tickets
  UNION ALL
  SELECT DISTINCT 'Demo2', 'raw_tickets', 'bill_to_id', CAST(bill_to_id AS STRING)
  FROM {fq}.raw_tickets
  UNION ALL
  SELECT DISTINCT 'Demo2', 'raw_tickets', 'terminal_code', CAST(terminal_code AS STRING)
  FROM {fq}.raw_tickets
  UNION ALL
  SELECT system_name, 'sap_partner', 'sold_to', sold_to FROM {fq}.sap_partner
  UNION ALL
  SELECT system_name, 'sap_partner', 'bill_to', bill_to FROM {fq}.sap_partner
  UNION ALL
  SELECT system_name, 'sap_partner', 'payer', payer FROM {fq}.sap_partner
  UNION ALL
  SELECT system_name, 'sap_partner', 'ship_to', ship_to FROM {fq}.sap_partner
  UNION ALL
  SELECT system_name, 'tas_lift', 'consignee', consignee FROM {fq}.tas_lift
  UNION ALL
  SELECT system_name, 'dim_customer', 'customer_id', customer_id FROM {fq}.dim_customer
  UNION ALL
  SELECT system_name, 'sf_account', 'account_id', account_id FROM {fq}.sf_account
  UNION ALL
  SELECT system_name, 'ra_business_associate', 'business_associate', business_associate
  FROM {fq}.ra_business_associate
  UNION ALL
  SELECT system_name, 'ra_business_associate', 'remittance_party', remittance_party
  FROM {fq}.ra_business_associate
)
SELECT
  h.system_name, h.table_name, h.column_name, h.value,
  m.local_system, m.field, m.local_key, m.term_id, m.map_ok, m.note
FROM hunt h
LEFT JOIN {fq}.cv_map m
  ON m.local_system = h.system_name
 AND m.field = h.column_name
 AND m.local_key = h.value
ORDER BY h.system_name, h.table_name, h.column_name, h.value;

-- 3. Lookup + Unbilled still holds.
SELECT * FROM {fq}.cv_lookup('customer');
SELECT payer, MEASURE(unbilled_usd) AS unbilled_usd, MEASURE(unbilled_ticket_count) AS tickets
FROM {fq}.unbilled_usd
WHERE payer = 'Apex Fuels LLC'
GROUP BY payer;
"""


def main() -> int:
    cfg = settings()
    fq = cfg.fq
    print("CV hunt — table → column → value → map → lookup → Unbilled holds")
    print(f"  catalog.schema = {fq}")
    print("  token          = (set, not printed)")
    print("  host           = (from .env, not printed)")
    print("  warehouse      = (from .env, id not printed)")
    print("  tickets.csv    = not renamed; no customer_id column added")
    print("  config.TABLES  = not edited (sidecar is not Lakebase/raw)")
    print("  TABS           = skipped (would invent a meaning or duplicate sold-to)")
    print("  new term_id    = none; term_id stays the join key")

    failures: list[str] = []
    tickets_path = PACK_ROOT / "data" / "tickets.csv"
    tickets_header = tickets_path.read_text(encoding="utf-8").splitlines()[0]
    header_cols = [c.strip() for c in tickets_header.split(",")]
    if "customer_id" in header_cols:
        failures.append("tickets.csv header now has customer_id (must stay unchanged)")
    if "kunnr" in header_cols:
        failures.append("tickets.csv header now has kunnr (must stay unchanged)")

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            rc = ensure_cv(cur, fq)
            if rc != 0:
                return rc

            land_hunt_stubs(cur, fq)

            # ----- 1. Open source tables -----
            print("\n======== 1. OPEN SOURCE TABLES (name is a clue) ========")
            print("  raw_tickets             — BOL lifts; party keys live on the ticket")
            print("  dim_customer            — warehouse sidecar; one overloaded customer_id")
            print("  sap_partner             — SAP partner row; four role columns")
            print("  tas_lift                — TAS lift; consignee (not a payer)")
            print("  sf_account              — Salesforce account_id (relationship, not a role)")
            print("  ra_business_associate   — RightAngle BA + remittance (no credit_party)")
            print("  TABS                    — skipped (would invent a meaning or duplicate sold-to)")
            print("  rack pricing            — skipped (no party / customer field)")
            for table in (
                "raw_tickets",
                "dim_customer",
                "sap_partner",
                "tas_lift",
                "sf_account",
                "ra_business_associate",
            ):
                print(f"\n  DESCRIBE {fq}.{table}")
                desc = run_statement(cur, f"DESCRIBE {fq}.{table}")
                cols = {str(r[0]).lower() for r in desc if r and r[0]}
                want = EXPECTED_SYSTEMS[table]
                if table == "raw_tickets":
                    if "system_name" in cols:
                        failures.append("raw_tickets must not gain system_name (tickets.csv unchanged)")
                    else:
                        print("  PASS: raw_tickets has no system_name column; hunt SELECT labels it Demo2")
                else:
                    if "system_name" not in cols:
                        failures.append(f"{table} DESCRIBE missing system_name")
                    else:
                        got = run_statement(
                            cur, f"SELECT DISTINCT system_name FROM {fq}.{table}"
                        )
                        names = {str(r[0]) for r in got if r and r[0]}
                        if names != {want}:
                            failures.append(
                                f"{table} system_name expected {{{want!r}}}, got {names}"
                            )
                        else:
                            print(f"  PASS: {table}.system_name = {want}")

            # ----- 2. Read columns -----
            print("\n======== 2. READ COLUMNS ========")
            print("  tickets: payer_id / sold_to_id / bill_to_id / terminal_code")
            print("  dim:     customer_id")
            print("  sap:     sold_to / bill_to / payer / ship_to")
            print("  tas:     consignee")
            print("  sf:      account_id (no customer_id column)")
            print("  ra:      business_associate / remittance_party")
            run_statement(
                cur,
                f"""SELECT DISTINCT payer_id, sold_to_id, bill_to_id, terminal_code
FROM {fq}.raw_tickets
ORDER BY payer_id, sold_to_id, bill_to_id, terminal_code""",
            )
            run_statement(cur, f"SELECT customer_id FROM {fq}.dim_customer")
            run_statement(
                cur,
                f"SELECT sold_to, bill_to, payer, ship_to FROM {fq}.sap_partner",
            )
            run_statement(
                cur,
                f"SELECT lift_id, consignee FROM {fq}.tas_lift",
            )
            run_statement(
                cur,
                f"SELECT account_id FROM {fq}.sf_account",
            )

            # ----- 3. Read values -----
            print("\n======== 3. READ VALUES ========")
            print("  APEX-PAYER on tickets.payer_id")
            apex_pay = run_statement(
                cur,
                f"""SELECT DISTINCT payer_id
FROM {fq}.raw_tickets
WHERE payer_id = 'APEX-PAYER'""",
            )
            if [str(r[0]) for r in apex_pay] != ["APEX-PAYER"]:
                failures.append(f"APEX-PAYER not on raw_tickets.payer_id, got {apex_pay}")
            else:
                print("  PASS: APEX-PAYER is a live ticket payer_id")

            print("  1000123 in two SAP columns (sold_to and bill_to)")
            sap_vals = run_statement(
                cur,
                f"""SELECT sold_to, bill_to, payer, ship_to
FROM {fq}.sap_partner
WHERE sold_to = '1000123' OR bill_to = '1000123'""",
            )
            if not sap_vals:
                failures.append("sap_partner has no 1000123 row")
            else:
                sold_to, bill_to, payer, ship_to = (str(x) for x in sap_vals[0][:4])
                print(f"  sap_partner sold_to={sold_to} bill_to={bill_to} payer={payer} ship_to={ship_to}")
                if sold_to != EXPECTED_CUSTOMER_ID or bill_to != EXPECTED_CUSTOMER_ID:
                    failures.append(
                        f"sap_partner expected sold_to=bill_to={EXPECTED_CUSTOMER_ID}, "
                        f"got sold_to={sold_to} bill_to={bill_to}"
                    )
                else:
                    print("  PASS: 1000123 appears in two SAP columns (sold_to and bill_to)")
                if payer != "1000450" or ship_to != "2000881":
                    failures.append(
                        f"sap_partner payer/ship_to expected 1000450/2000881, got {payer}/{ship_to}"
                    )

            print("  CONS-4412 on tas_lift.consignee")
            cons_vals = run_statement(
                cur,
                f"""SELECT consignee
FROM {fq}.tas_lift
WHERE consignee = 'CONS-4412'""",
            )
            if [str(r[0]) for r in cons_vals] != [EXPECTED_CONS]:
                failures.append(f"CONS-4412 not on tas_lift.consignee, got {cons_vals}")
            else:
                print("  PASS: CONS-4412 is the live TAS consignee")

            print("  ticket keys (Demo2 payer / sold-to / bill-to / terminal)")
            ticket_keys = run_statement(
                cur,
                f"""SELECT DISTINCT payer_id, sold_to_id, bill_to_id, terminal_code
FROM {fq}.raw_tickets
ORDER BY payer_id, sold_to_id, bill_to_id, terminal_code""",
            )
            if not ticket_keys:
                failures.append("raw_tickets distinct clue-column SELECT returned 0 rows")
            else:
                print(f"  PASS: raw_tickets distinct clue keys = {len(ticket_keys)} rows")

            print("  warehouse 1000123 on dim_customer.customer_id")
            wh = run_statement(
                cur,
                f"""SELECT customer_id
FROM {fq}.dim_customer
WHERE customer_id = '1000123'""",
            )
            if [str(r[0]) for r in wh] != [EXPECTED_CUSTOMER_ID]:
                failures.append(f"warehouse customer_id expected ['{EXPECTED_CUSTOMER_ID}'], got {wh}")
            else:
                print("  PASS: warehouse customer_id is 1000123")

            print("  Salesforce account_id SF-APEX (no customer_id on this stub)")
            sf = run_statement(
                cur,
                f"""SELECT account_id
FROM {fq}.sf_account
WHERE account_id = 'SF-APEX'""",
            )
            if [str(r[0]) for r in sf] != ["SF-APEX"]:
                failures.append(f"sf_account.account_id expected ['SF-APEX'], got {sf}")
            else:
                print("  PASS: Salesforce account_id is SF-APEX")
            sf_desc = run_statement(cur, f"DESCRIBE {fq}.sf_account")
            sf_cols = {str(r[0]).lower() for r in sf_desc if r and r[0]}
            if "customer_id" in sf_cols:
                failures.append("sf_account must not have customer_id (Cut 1)")
            elif "crm_account" in table_names(cur, fq):
                failures.append("crm_account still exists; table name is locked to sf_account")
            else:
                print("  PASS: sf_account has no customer_id; crm_account is gone")

            print("  RightAngle BA-APEX + remittance APEX-PAYER (no credit_party)")
            ra = run_statement(
                cur,
                f"""SELECT ba_id, business_associate, remittance_party
FROM {fq}.ra_business_associate
WHERE business_associate = 'BA-APEX'""",
            )
            if not ra:
                failures.append("ra_business_associate has no BA-APEX row")
            else:
                ba_id, ba, remit = (str(x) for x in ra[0][:3])
                print(f"  ra ba_id={ba_id} ba={ba} remittance={remit}")
                if ba != "BA-APEX" or remit != "APEX-PAYER":
                    failures.append(
                        f"RA expected BA-APEX / APEX-PAYER, got {ba}/{remit}"
                    )
                else:
                    print("  PASS: RightAngle BA-APEX; remittance is APEX-PAYER")
                ra_cols = run_statement(cur, f"DESCRIBE {fq}.ra_business_associate")
                ra_col_names = {str(r[0]).lower() for r in ra_cols if r and r[0]}
                sapish = {"sold_to", "bill_to", "payer", "kunnr"}
                hit = sapish & ra_col_names
                if hit:
                    failures.append(f"RA table must not use SAP columns, found {sorted(hit)}")
                elif "credit_party" in ra_col_names:
                    failures.append("RA credit_party column must be off the stub")
                else:
                    print("  PASS: RA columns are BA language; credit_party is off the stub")

            # ----- meanings -----
            print("\n======== MEANINGS (cv_term — from 10; no new term_id) ========")
            terms = run_statement(
                cur,
                f"""SELECT term_id, preferred_label, scope_note
FROM {fq}.cv_term
ORDER BY term_id""",
            )
            got_ids = {str(r[0]) for r in terms}
            expected_ids = {
                "id:bill-to",
                "id:loading-authorized-party",
                "id:payer",
                "id:ship-to",
                "id:sold-to",
            }
            if got_ids != expected_ids:
                failures.append(f"cv_term ids changed: expected {sorted(expected_ids)}, got {sorted(got_ids)}")
            else:
                print("  PASS: five meanings, no new term_id")

            # ----- labels -----
            print("\n======== LABELS (preferred_label + alias 'customer') ========")
            run_statement(
                cur,
                f"""SELECT term_id, preferred_label
FROM {fq}.cv_term
ORDER BY term_id""",
            )
            cust_alias = run_statement(
                cur,
                f"""SELECT term_id, alias
FROM {fq}.cv_alias
WHERE lower(alias) = 'customer'
ORDER BY term_id""",
            )
            alias_ids = {str(r[0]) for r in cust_alias}
            if alias_ids != CUSTOMER_IDS:
                failures.append(
                    f"alias 'customer' expected {sorted(CUSTOMER_IDS)}, got {sorted(alias_ids)}"
                )
            else:
                print("  PASS: label 'customer' sits on Sold-To and Loading-Authorized Party")

            # ----- hunt grid: system_name, table, column, value → map -----
            print("\n======== HUNT GRID (system_name, table, column, value → map) ========")
            print("  Six systems. Tickets labeled Demo2 (no column on raw_tickets).")
            grid = run_statement(cur, hunt_with_map_sql(fq))
            systems = {str(r[0]) for r in grid if r and r[0]}
            expected_six = {"Demo2", "SAP", "Salesforce", "TAS", "Warehouse", "RightAngle"}
            print(f"  systems on grid = {sorted(systems)}")
            if systems != expected_six:
                failures.append(f"hunt grid systems expected {sorted(expected_six)}, got {sorted(systems)}")
            else:
                print("  PASS: six systems on the hunt grid")
            demo_rows = [r for r in grid if str(r[0]) == "Demo2"]
            if not demo_rows:
                failures.append("hunt grid missing Demo2 / tickets rows")
            else:
                print(f"  PASS: tickets labeled Demo2 ({len(demo_rows)} distinct clue rows)")
            # every grid row's map local_system (when present) matches system_name
            mismatch = [
                r for r in grid
                if r[4] is not None and str(r[4]) != str(r[0])
            ]
            if mismatch:
                failures.append(f"cv_map.local_system does not match system_name: {mismatch[:3]}")
            else:
                print("  PASS: cv_map.local_system matches hunt system_name")

            # ----- 4. map rows from that hunt -----
            print("\n======== 4. MAP ROWS FROM THAT HUNT (system + field + key) ========")
            hunt_map = run_statement(
                cur,
                f"""SELECT local_system, field, local_key, term_id, map_ok, note
FROM {fq}.cv_map
WHERE local_key IN ('APEX-PAYER', '1000123', 'CONS-4412', 'BA-APEX', 'SF-APEX')
ORDER BY local_system, field, local_key""",
            )
            by_key: dict[tuple[str, str, str], tuple[str, str]] = {}
            for row in hunt_map:
                system, field, key = str(row[0]), str(row[1]), str(row[2])
                term = "" if row[3] is None else str(row[3])
                ok = "" if row[4] is None else str(row[4])
                by_key[(system, field, key)] = (term, ok)

            sap_sold = by_key.get(("SAP", "sold_to", EXPECTED_CUSTOMER_ID), ("", ""))
            sap_bill = by_key.get(("SAP", "bill_to", EXPECTED_CUSTOMER_ID), ("", ""))
            sap_1000123 = [
                k for k in by_key if k[0] == "SAP" and k[2] == EXPECTED_CUSTOMER_ID
            ]
            print(f"  SAP 1000123 map rows = {[(k, by_key[k]) for k in sap_1000123]}")
            if sap_sold[0] != "id:sold-to" or sap_bill[0] != "id:bill-to" or len(sap_1000123) != 2:
                failures.append(
                    f"same digits 1000123 must be two map rows "
                    f"(sold_to→id:sold-to, bill_to→id:bill-to), got {sap_1000123} {sap_sold} {sap_bill}"
                )
            else:
                print("  PASS: same digits 1000123 = two map rows (sold-to and bill-to)")

            wh_map = by_key.get(("Warehouse", "customer_id", EXPECTED_CUSTOMER_ID), None)
            if wh_map is None:
                failures.append("Warehouse customer_id 1000123 cv_map row missing")
            else:
                term, ok = wh_map
                print(f"  warehouse map term_id={term!r} map_ok={ok!r}")
                if term.strip() != "" or ok.lower() != "no":
                    failures.append(
                        f"Warehouse 1000123 must be no-map (empty term_id / map_ok=no), "
                        f"got term_id={term!r} map_ok={ok!r}"
                    )
                else:
                    print("  PASS: warehouse 1000123 = no map")


            cons_map = by_key.get(("TAS", "consignee", EXPECTED_CONS), None)
            if cons_map is None or cons_map[0] != "id:loading-authorized-party":
                failures.append(
                    f"TAS.consignee CONS-4412 map expected id:loading-authorized-party, got {cons_map}"
                )
            else:
                print("  PASS: TAS.consignee CONS-4412 → id:loading-authorized-party")

            apex_map = by_key.get(("Demo2", "payer_id", "APEX-PAYER"), None)
            if apex_map is None or apex_map[0] != "id:payer":
                failures.append(f"APEX-PAYER map expected id:payer, got {apex_map}")
            else:
                print("  PASS: APEX-PAYER → id:payer (system+field+key)")

            sf_map = by_key.get(("Salesforce", "account_id", "SF-APEX"), None)
            if sf_map is None:
                failures.append("Salesforce account_id SF-APEX cv_map row missing")
            else:
                term, ok = sf_map
                print(f"  Salesforce map term_id={term!r} map_ok={ok!r}")
                if term.strip() != "" or ok.lower() != "no":
                    failures.append(
                        f"Salesforce SF-APEX must be no-map, got term_id={term!r} map_ok={ok!r}"
                    )
                else:
                    print("  PASS: Salesforce.account_id SF-APEX = no map")
            sf_1000 = [
                k for k in by_key
                if k[0] == "Salesforce" and k[2] == EXPECTED_CUSTOMER_ID
            ]
            if sf_1000:
                failures.append(f"Salesforce must not map 1000123, got {sf_1000}")
            else:
                print("  PASS: no Salesforce 1000123 map")

            ra_ba = by_key.get(("RightAngle", "business_associate", "BA-APEX"), None)
            if ra_ba is None:
                failures.append("RightAngle business_associate BA-APEX cv_map row missing")
            else:
                term, ok = ra_ba
                print(f"  RA BA map term_id={term!r} map_ok={ok!r}")
                if term.strip() != "" or ok.lower() != "no":
                    failures.append(
                        f"RA BA-APEX must be no-map, got term_id={term!r} map_ok={ok!r}"
                    )
                else:
                    print("  PASS: RightAngle BA-APEX = no map")

            ra_remit = by_key.get(("RightAngle", "remittance_party", "APEX-PAYER"), None)
            if ra_remit is None or ra_remit[0] != "id:payer":
                failures.append(f"RA remittance_party APEX-PAYER expected id:payer, got {ra_remit}")
            else:
                print("  PASS: RightAngle remittance_party APEX-PAYER → id:payer")
            stale = run_statement(
                cur,
                f"""SELECT local_system, field, local_key
FROM {fq}.cv_map
WHERE local_system IN ('CRM', 'Lift')
   OR field = 'credit_party'""",
            )
            if stale:
                failures.append(f"stale Lift/CRM/credit map rows still present: {stale}")
            else:
                print("  PASS: no Lift / CRM / credit_party map rows")

            # ----- 5. existing prove -----
            print("\n======== 5. LOOKUP + UNBILLED STILL HOLDS ========")
            use_function = detect_lookup_function(cur, fq)

            print("\n======== LOOKUP 'customer' ========")
            customer = run_statement(cur, lookup_sql(fq, "customer", use_function))
            got_lookup = distinct_ids(customer)
            print(f"  distinct term_ids = {sorted(got_lookup)}")
            if got_lookup != CUSTOMER_IDS:
                failures.append(
                    f"lookup('customer') distinct IDs expected {sorted(CUSTOMER_IDS)}, "
                    f"got {sorted(got_lookup)}"
                )
            else:
                print("  PASS: exactly two IDs — id:sold-to and id:loading-authorized-party")

            print("\n======== Apex Unbilled MEASURE() (view unchanged) ========")
            measure_sql = f"""SELECT payer, MEASURE(unbilled_usd) AS unbilled_usd, MEASURE(unbilled_ticket_count) AS tickets
FROM {fq}.unbilled_usd
WHERE payer = 'Apex Fuels LLC'
GROUP BY payer"""
            try:
                apex = run_statement(cur, measure_sql)
            except Exception as exc:
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

            print("\n======== Refused customer_id grain ========")
            refused_customer = f"""SELECT customer_id, MEASURE(unbilled_usd) AS unbilled_usd
FROM {fq}.unbilled_usd
WHERE customer_id = '1000123'
GROUP BY customer_id"""
            try:
                bad = run_statement(cur, refused_customer)
                failures.append(
                    f"customer_id grain unexpectedly succeeded ({len(bad)} rows). Must fail."
                )
                print("  FAIL: customer_id is not a certified Unbilled dimension")
            except Exception as exc:
                print(f"  PASS (refused): {type(exc).__name__}: {exc}")

            print("\n======== Refused CONS-4412 / loading-authorized grain ========")
            cons_dim_sql = f"""SELECT loading_authorized_party, MEASURE(unbilled_usd) AS unbilled_usd
FROM {fq}.unbilled_usd
GROUP BY loading_authorized_party"""
            try:
                run_statement(cur, cons_dim_sql)
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
                    print("  PASS (0 rows on payer = 'CONS-4412')")
            except Exception as exc:
                print(f"  PASS (refused CONS-4412 grain): {type(exc).__name__}: {exc}")

            print("\n======== dim_customer + tickets header ========")
            raw_cust = run_statement(cur, f"SELECT customer_id FROM {fq}.dim_customer")
            raw_ids = [str(r[0]) for r in raw_cust]
            if raw_ids != [EXPECTED_CUSTOMER_ID]:
                failures.append(f"dim_customer.customer_id expected ['{EXPECTED_CUSTOMER_ID}'], got {raw_ids}")
            else:
                print("  PASS: dim_customer still 1000123")
            print(f"  tickets.csv header (unchanged) = {tickets_header}")
            if "customer_id" in header_cols:
                failures.append("tickets.csv gained a customer_id column")
            else:
                print("  PASS: tickets.csv header has no customer_id")
            try:
                desc = run_statement(cur, f"DESCRIBE {fq}.raw_tickets")
                raw_cols = {str(r[0]).lower() for r in desc}
                if "customer_id" in raw_cols:
                    failures.append("raw_tickets has customer_id (tickets were not to be renamed)")
                else:
                    print("  PASS: raw_tickets has no customer_id column")
                if "kunnr" in raw_cols:
                    failures.append("raw_tickets has kunnr (must not be invented)")
            except Exception as exc:
                failures.append(f"DESCRIBE raw_tickets failed: {exc}")

            print("\n======== CV OBJECTS HAVE NO system_name ========")
            for table in ("cv_term", "cv_alias", "cv_map"):
                desc = run_statement(cur, f"DESCRIBE {fq}.{table}")
                cols = [str(r[0]).lower() for r in desc if r and r[0]]
                print(f"  {table} columns = {cols}")
                if "system_name" in cols:
                    failures.append(f"{table} must not have system_name, got {cols}")
                else:
                    print(f"  PASS: {table} has no system_name")
            map_cols = [
                str(r[0]).lower()
                for r in run_statement(cur, f"DESCRIBE {fq}.cv_map")
                if r and r[0]
            ]
            if "local_system" not in map_cols:
                failures.append("cv_map missing local_system (map contract)")
            else:
                print("  PASS: cv_map.local_system is the map contract (no duplicate system_name)")

            print("\n======== CATALOG Unbilled about-ID (read-only) ========")
            meta = run_statement(
                cur,
                f"""SELECT kpi_id, name, ontology_iri
FROM {fq}.dim_kpi_metadata
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'""",
            )
            if not meta:
                failures.append("dim_kpi_metadata missing Unbilled row")
            else:
                about = str(meta[0][2])
                print(f"  Unbilled about-ID = {about}")
                if not about.endswith("#UnbilledState"):
                    failures.append(f"Unbilled about-ID must stay #UnbilledState, got {about!r}")
                else:
                    print("  PASS: catalog about-ID still #UnbilledState")

    print()
    print(paste_ready_sql())
    print()
    print("RULE: hunt is table → column → value → map (system+field+key). TABS skipped. No new KPI.")
    print()
    if failures:
        print("FAIL: one or more prove steps failed:")
        for item in failures:
            print(f"  - {item}")
        return 1
    print(
        "PASS: hunt walked. 1000123 in two SAP columns and two map rows. "
        "Warehouse no-map. Salesforce.account_id SF-APEX no-map. TAS.consignee CONS-4412 → LAP. RA BA-APEX no-map; "
        "RA remittance → id:payer. No credit map. lookup('customer') is two IDs. "
        "Apex 115960.80/8. Refused grains refused. dim_customer 1000123. "
        "tickets header unchanged. TABS skipped. No new term_id."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
