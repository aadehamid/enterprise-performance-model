#!/usr/bin/env python3
"""06_store.py — Silver dim_kpi_metadata + Gold gold_kpi_value.

Honest path: CREATE TABLE IF NOT EXISTS gold_kpi_value, DELETE Unbilled
rows, INSERT … MEASURE() UNION ALL four Unbilled grains.
Fallback: Python runs those MEASURE() queries, then INSERT VALUES
of the results. Still sourced from MEASURE(), never SUM(fct_unbilled).
Never CREATE OR REPLACE the whole gold table (that would wipe KPI 2/3).
Gold publish is not re-approve: refresh Gold only when Unbilled is already
approved. drifted|proposed|archived keep the last approved snapshot.
approve_kpi / 14_reapprove.py is the only path that sets approved and
refreshes definition_hash.

Honest seats:
  fct_unbilled holds the ticket gate + gallons_net * contract_price
    (population / compiler source).
  The Metric View compiles SUM/GROUP BY (MEASURE()).
  Gold and Genie consume MEASURE() and must not re-encode.
  RC-1 per KPI (one compile path each, no second SUM).
C-10: metadata does not author the formula.
Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_status import (  # noqa: E402
    LOCKED_STATUSES,
    STATUS_APPROVED,
    STATUS_ARCHIVED,
    STATUS_DRIFTED,
    STATUS_PROPOSED,
    ensure_definition_hash_column,
    fetch_kpi_row,
    live_definition_hash,
    maybe_reset_approval,
    migrate_certified_to_approved,
)
from config import (  # noqa: E402
    PACK_ROOT,
    connect,
    run_statement,
    settings,
    split_sql,
    sql_str,
    substitute,
)

UNBILLED_ID = "KPI-O2C-UNBILLED-USD"

EXPECTED_USD = Decimal("179934.00")
EXPECTED_TICKETS = 12
EXPECTED_GRAIN_ROWS = {
    "enterprise": 1,
    "payer": 3,
    "sold_to": 4,
    "site": 3,
}
EXPECTED_SOLD_TO = {
    "Apex Fuels Houston Rack": (Decimal("79362.40"), 5),
    "Metro Lubes Beaumont": (Decimal("37454.40"), 2),
    "Apex Fuels Dallas Dealer": (Decimal("36598.40"), 3),
    "Gulf Coast Aviation Inc": (Decimal("26518.80"), 2),
}
EXPECTED_PAYER = {
    "Apex Fuels LLC": (Decimal("115960.80"), 8),
    "Metro Lubricants": (Decimal("37454.40"), 2),
    "Gulf Coast Aviation Inc": (Decimal("26518.80"), 2),
}
EXPECTED_SITE = {
    "HSC": (Decimal("97145.20"), 6),
    "DAL": (Decimal("45334.40"), 4),
    "BMT": (Decimal("37454.40"), 2),
}


def money(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def tickets(value: object) -> int:
    return int(value)


def sql_head(stmt: str) -> str:
    """Uppercased statement with line comments stripped (split_sql keeps headers)."""
    lines: list[str] = []
    for line in stmt.splitlines():
        cut = line.split("--", 1)[0].strip()
        if cut:
            lines.append(cut)
    return " ".join(lines).upper()


def is_gold_measure_insert(stmt: str) -> bool:
    compact = sql_head(stmt)
    return (
        compact.startswith("INSERT")
        and "GOLD_KPI_VALUE" in compact
        and "MEASURE(" in compact
    )


def gold_values_sql(fq: str, rows: list[tuple]) -> str:
    """INSERT Unbilled gold from MEASURE() results (not SUM of the fact)."""
    lines = []
    for kpi_id, grain, grain_key, grain_label, as_of, usd, n, pointer in rows:
        lines.append(
            "  ("
            f"{sql_str(kpi_id)}, {sql_str(grain)}, {sql_str(grain_key)}, "
            f"{sql_str(grain_label)}, DATE {sql_str(str(as_of))}, "
            f"{usd}, {n}, {sql_str(pointer)}"
            ")"
        )
    values = ",\n".join(lines)
    return f"""INSERT INTO {fq}.gold_kpi_value (
  kpi_id, grain, grain_key, grain_label, as_of_date,
  value_usd, ticket_count, formula_pointer, published_ts
)
SELECT
  CAST(kpi_id AS STRING)              AS kpi_id,
  CAST(grain AS STRING)               AS grain,
  CAST(grain_key AS STRING)           AS grain_key,
  CAST(grain_label AS STRING)         AS grain_label,
  CAST(as_of_date AS DATE)            AS as_of_date,
  CAST(value_usd AS DECIMAL(18, 2))   AS value_usd,
  CAST(ticket_count AS BIGINT)        AS ticket_count,
  CAST(formula_pointer AS STRING)     AS formula_pointer,
  current_timestamp()                 AS published_ts
FROM VALUES
{values}
AS v(kpi_id, grain, grain_key, grain_label, as_of_date, value_usd, ticket_count, formula_pointer)"""


def gold_from_measure_values(cur, fq: str, mv: str) -> None:
    """Run the four MEASURE() queries, then CREATE TABLE from those results."""
    print("\n======== GOLD FALLBACK — VALUES from MEASURE() (not SUM of the fact) ========")
    enterprise = run_statement(
        cur,
        f"""SELECT
  MEASURE(unbilled_usd)          AS value_usd,
  MEASURE(unbilled_ticket_count) AS ticket_count
FROM {mv}""",
    )
    sold = run_statement(
        cur,
        f"""SELECT
  sold_to,
  MEASURE(unbilled_usd)          AS value_usd,
  MEASURE(unbilled_ticket_count) AS ticket_count
FROM {mv}
GROUP BY sold_to
ORDER BY value_usd DESC""",
    )
    payer = run_statement(
        cur,
        f"""SELECT
  payer,
  MEASURE(unbilled_usd)          AS value_usd,
  MEASURE(unbilled_ticket_count) AS ticket_count
FROM {mv}
GROUP BY payer
ORDER BY value_usd DESC""",
    )
    site = run_statement(
        cur,
        f"""SELECT
  site,
  site_name,
  MEASURE(unbilled_usd)          AS value_usd,
  MEASURE(unbilled_ticket_count) AS ticket_count
FROM {mv}
GROUP BY site, site_name
ORDER BY value_usd DESC""",
    )

    as_of = "2026-08-01"
    kpi = "KPI-O2C-UNBILLED-USD"
    pointer = "unbilled_usd"
    rows: list[tuple] = []
    if not enterprise:
        raise SystemExit("MEASURE() enterprise returned 0 rows")
    e_usd, e_n = enterprise[0]
    rows.append((kpi, "enterprise", "*", "Enterprise", as_of, money(e_usd), tickets(e_n), pointer))
    for sold_to, usd, n in sold:
        rows.append((kpi, "sold_to", str(sold_to), str(sold_to), as_of, money(usd), tickets(n), pointer))
    for payer_name, usd, n in payer:
        rows.append((kpi, "payer", str(payer_name), str(payer_name), as_of, money(usd), tickets(n), pointer))
    for site_code, site_name, usd, n in site:
        rows.append(
            (kpi, "site", str(site_code), str(site_name), as_of, money(usd), tickets(n), pointer)
        )
    meta = fetch_kpi_row(cur, fq, UNBILLED_ID)
    if str((meta or {}).get("status") or "") != STATUS_APPROVED:
        print("Gold fallback skipped (kpi_id not approved). Last snapshot kept.")
        return
    run_statement(
        cur,
        f"DELETE FROM {fq}.gold_kpi_value WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'",
        fetch=False,
    )
    run_statement(cur, gold_values_sql(fq, rows), fetch=False)


def assert_store(cur, fq: str) -> None:
    meta = run_statement(
        cur,
        f"""SELECT
  kpi_id,
  name,
  owner,
  uom,
  allowed_grain,
  default_grain_rule,
  status,
  formula_pointer,
  formula_object,
  formula_version,
  ontology_iri,
  as_of_date,
  definition_hash
FROM {fq}.dim_kpi_metadata""",
    )
    unbilled = [r for r in meta if str(r[0]) == "KPI-O2C-UNBILLED-USD"]
    if len(unbilled) != 1:
        raise SystemExit(
            f"dim_kpi_metadata: expected Unbilled row KPI-O2C-UNBILLED-USD, "
            f"got {len(unbilled)} matching of {len(meta)} total"
        )
    row = unbilled[0]
    if str(row[7]) != "unbilled_usd":
        raise SystemExit(f"dim_kpi_metadata.formula_pointer must be the measure name, got {row[7]!r}")
    if "unbilled_usd" not in str(row[8]):
        raise SystemExit(f"dim_kpi_metadata.formula_object must point at the Metric View, got {row[8]!r}")
    status = str(row[6])
    if status == STATUS_APPROVED:
        if not str(row[12] or "").strip():
            raise SystemExit("dim_kpi_metadata.definition_hash must be set for approved Unbilled")
    elif status in (STATUS_DRIFTED, STATUS_PROPOSED, STATUS_ARCHIVED):
        print(
            f"Unbilled status={status} (gold publish is not re-approve; "
            "last approved gold snapshot must still hold)."
        )
    else:
        raise SystemExit(f"dim_kpi_metadata.status unexpected for Unbilled, got {status!r}")
    if not str(row[10]).endswith("#UnbilledState"):
        raise SystemExit(
            f"dim_kpi_metadata.ontology_iri must end with #UnbilledState, got {row[10]!r}"
        )
    print("Unbilled metadata row ok (catalog may have more after 08/09).")

    by_grain = run_statement(
        cur,
        f"""SELECT
  grain,
  COUNT(*)          AS gold_rows,
  SUM(value_usd)    AS value_usd,
  SUM(ticket_count) AS tickets
FROM {fq}.gold_kpi_value
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
GROUP BY grain
ORDER BY grain""",
    )
    got_rows = {str(g): int(n) for g, n, _usd, _t in by_grain}
    if got_rows != EXPECTED_GRAIN_ROWS:
        raise SystemExit(f"gold rows by grain: expected {EXPECTED_GRAIN_ROWS}, got {got_rows}")
    for grain, _n, usd, n_tickets in by_grain:
        if money(usd) != EXPECTED_USD:
            raise SystemExit(f"gold grain={grain!r} SUM(value_usd)={usd} != {EXPECTED_USD}")
        if tickets(n_tickets) != EXPECTED_TICKETS:
            raise SystemExit(f"gold grain={grain!r} tickets={n_tickets} != {EXPECTED_TICKETS}")

    detail = run_statement(
        cur,
        f"""SELECT
  grain,
  grain_key,
  grain_label,
  value_usd,
  ticket_count,
  formula_pointer
FROM {fq}.gold_kpi_value
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
ORDER BY grain, value_usd DESC""",
    )
    sold = {str(k): (money(v), tickets(n)) for g, k, _lab, v, n, _p in detail if str(g) == "sold_to"}
    payer = {str(k): (money(v), tickets(n)) for g, k, _lab, v, n, _p in detail if str(g) == "payer"}
    site = {str(k): (money(v), tickets(n)) for g, k, _lab, v, n, _p in detail if str(g) == "site"}
    if sold != EXPECTED_SOLD_TO:
        raise SystemExit(f"sold_to gold mismatch:\n  expected {EXPECTED_SOLD_TO}\n  got      {sold}")
    if payer != EXPECTED_PAYER:
        raise SystemExit(f"payer gold mismatch:\n  expected {EXPECTED_PAYER}\n  got      {payer}")
    if site != EXPECTED_SITE:
        raise SystemExit(f"site gold mismatch:\n  expected {EXPECTED_SITE}\n  got      {site}")
    for _g, _k, _lab, _v, _n, pointer in detail:
        if str(pointer) != "unbilled_usd":
            raise SystemExit(f"gold formula_pointer must be unbilled_usd, got {pointer!r}")

    joined = run_statement(
        cur,
        f"""SELECT
  g.grain,
  g.grain_key,
  g.value_usd,
  g.ticket_count,
  m.name,
  m.status,
  m.formula_pointer,
  m.formula_object
FROM {fq}.gold_kpi_value g
INNER JOIN {fq}.dim_kpi_metadata m
  ON g.kpi_id = m.kpi_id
WHERE g.kpi_id = 'KPI-O2C-UNBILLED-USD'
ORDER BY g.grain, g.value_usd DESC""",
    )
    if len(joined) != 11:
        raise SystemExit(f"Unbilled gold ⋈ metadata: expected 11 rows, got {len(joined)}")

    ent = run_statement(
        cur,
        f"""SELECT SUM(value_usd) AS enterprise_usd
FROM {fq}.gold_kpi_value
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
  AND grain = 'enterprise'""",
    )
    if money(ent[0][0]) != EXPECTED_USD:
        raise SystemExit(f"enterprise published value {ent[0][0]} != {EXPECTED_USD}")


def main() -> None:
    cfg = settings()
    path = PACK_ROOT / "sql" / "05_store.sql"
    sql_text = substitute(path.read_text(encoding="utf-8"), cfg)
    print(f"Running {path} against {cfg.fq}")
    print("Store: dim_kpi_metadata (Silver) + gold_kpi_value (Gold FROM MEASURE()).")
    print("Population is on fct_unbilled. Gold consumes MEASURE(); no second SUM.")

    gold_path = None
    prev_unbilled = None
    with connect(cfg) as conn:
        with conn.cursor() as cur:
            ensure_definition_hash_column(cur, cfg.fq)
            prev_unbilled = fetch_kpi_row(cur, cfg.fq, UNBILLED_ID)
            prev_status = str((prev_unbilled or {}).get("status") or "")
            print(f"Unbilled start status={prev_unbilled.get('status') if prev_unbilled else None}")
            for stmt in split_sql(sql_text):
                compact_pre = sql_head(stmt)
                if compact_pre.startswith("DELETE") and "DIM_KPI_METADATA" in compact_pre:
                    prev_unbilled = fetch_kpi_row(cur, cfg.fq, UNBILLED_ID) or prev_unbilled
                    prev_status = str((prev_unbilled or {}).get("status") or "")
                if (
                    compact_pre.startswith("INSERT")
                    and "DIM_KPI_METADATA" in compact_pre
                    and prev_status in LOCKED_STATUSES
                ):
                    print(
                        f"Skip metadata INSERT: Unbilled status={prev_status} "
                        "(will not write approved over locked row)."
                    )
                    continue
                gold_stmt = (
                    compact_pre.startswith("DELETE") and "GOLD_KPI_VALUE" in compact_pre
                ) or is_gold_measure_insert(stmt)
                if gold_stmt:
                    live = fetch_kpi_row(cur, cfg.fq, UNBILLED_ID)
                    live_status = str((live or {}).get("status") or "")
                    if live_status != STATUS_APPROVED:
                        print(
                            f"\n======== GOLD skipped (status={live_status or 'missing'}; "
                            "not approved - last snapshot kept) ========"
                        )
                        gold_path = "SKIPPED_NOT_APPROVED"
                        continue
                if is_gold_measure_insert(stmt):
                    print("\n======== GOLD — try INSERT FROM MEASURE() (Unbilled rows only) ========")
                    try:
                        run_statement(cur, stmt, fetch=False)
                        gold_path = "INSERT_MEASURE"
                    except Exception as exc:
                        print(
                            "INSERT from MEASURE() refused by the warehouse.\n"
                            f"  ({type(exc).__name__}: {exc})\n"
                            "Falling back to VALUES built from the same MEASURE() queries.\n"
                            "Still not SUM(fct_unbilled). Other kpi_id gold rows kept. RC-1 holds."
                        )
                        gold_from_measure_values(cur, cfg.fq, f"{cfg.fq}.unbilled_usd")
                        gold_path = "VALUES_FROM_MEASURE"
                    continue
                # Skip gold verification SELECTs from the file — asserted below
                # after whichever gold path won, so we do not query a missing table
                # if CTAS failed before the fallback finished.
                compact = sql_head(stmt)
                if "GOLD_KPI_VALUE" in compact and compact.startswith("SELECT"):
                    continue
                run_statement(cur, stmt)
            if gold_path is None:
                raise SystemExit("05_store.sql had no gold INSERT-from-MEASURE() statement")

            print("\n======== CATALOG STATUS WRITE PATH ========")
            new_unbilled = fetch_kpi_row(cur, cfg.fq, UNBILLED_ID)
            if not new_unbilled and prev_unbilled and prev_status in LOCKED_STATUSES:
                print("Unbilled row missing after SQL; restoring locked prev (not approved).")
                from catalog_status import write_kpi_row
                write_kpi_row(cur, cfg.fq, prev_unbilled)
                new_unbilled = fetch_kpi_row(cur, cfg.fq, UNBILLED_ID)
            if not new_unbilled:
                raise SystemExit("Unbilled metadata row missing after 05_store.sql")
            applied = maybe_reset_approval(prev_unbilled, new_unbilled)
            cur_status = str(new_unbilled.get("status") or "")
            if prev_unbilled and prev_status in LOCKED_STATUSES:
                if cur_status == STATUS_APPROVED or cur_status != prev_status:
                    run_statement(
                        cur,
                        f"UPDATE {cfg.fq}.dim_kpi_metadata "
                        f"SET status = {sql_str(prev_status)}, "
                        f"definition_hash = {sql_str(str(prev_unbilled.get('definition_hash') or ''))} "
                        f"WHERE kpi_id = {sql_str(UNBILLED_ID)}",
                        fetch=False,
                    )
                    print(
                        f"Reverted Unbilled {cur_status} → {prev_status} "
                        "(store will not approve; approve_kpi only)."
                    )
                    cur_status = prev_status
                    new_unbilled["status"] = prev_status
            if cur_status in LOCKED_STATUSES:
                print(
                    f"Unbilled status={cur_status}; store will not set approved "
                    "(approve_kpi / 14_reapprove.py only)."
                )
            elif str(applied.get("status")) == STATUS_PROPOSED and cur_status != STATUS_PROPOSED:
                run_statement(
                    cur,
                    f"UPDATE {cfg.fq}.dim_kpi_metadata SET status = '{STATUS_PROPOSED}' "
                    f"WHERE kpi_id = '{UNBILLED_ID}'",
                    fetch=False,
                )
                print("Unbilled approval reset to proposed (pointer/object/definition changed).")
            migrate_certified_to_approved(cur, cfg.fq)
            # First-time approved insert may have an empty hash. Fill once.
            # Do not refresh a stored hash (approve_kpi / 14_reapprove.py only).
            if cur_status == STATUS_APPROVED and not str(new_unbilled.get("definition_hash") or ""):
                obj = str(new_unbilled.get("formula_object") or "")
                if not obj:
                    raise SystemExit(f"{UNBILLED_ID}: approved row missing formula_object")
                live_hash = live_definition_hash(cur, obj)
                run_statement(
                    cur,
                    f"UPDATE {cfg.fq}.dim_kpi_metadata "
                    f"SET definition_hash = {sql_str(live_hash)} "
                    f"WHERE kpi_id = {sql_str(UNBILLED_ID)} "
                    f"AND status = '{STATUS_APPROVED}' "
                    f"AND (definition_hash IS NULL OR definition_hash = '')",
                    fetch=False,
                )
                print(f"Unbilled first-time hash filled {live_hash[:12]}… (not a re-approve).")
            elif cur_status == STATUS_APPROVED:
                digest = str(new_unbilled.get("definition_hash") or "")
                print(
                    f"Unbilled already approved; hash kept {digest[:12]}… "
                    "(store is not re-approve)."
                )

            print("\n======== STORE ASSERTIONS ========")
            assert_store(cur, cfg.fq)
            end_row = fetch_kpi_row(cur, cfg.fq, UNBILLED_ID)
            print(
                f"END_STATUS={end_row.get('status') if end_row else 'missing'} "
                f"(06 does not set approved unless first-time insert)"
            )

    print(f"\nGOLD_PATH={gold_path}")
    if gold_path == "SKIPPED_NOT_APPROVED":
        print(
            "Store ok. Gold not refreshed (Unbilled not approved). "
            "Last approved snapshot kept. Enterprise $179,934.00 / 12."
        )
    else:
        print("Store ok. Unbilled metadata row present. Unbilled gold 11 rows (1/3/4/3). Enterprise $179,934.00 / 12.")
    print("This is not MetricFlow. Demo 1 is a different pack.")


if __name__ == "__main__":
    main()
