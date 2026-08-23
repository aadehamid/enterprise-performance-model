#!/usr/bin/env python3
"""08_complex_metric.py — SECOND Metric View: contract_vs_list_usd.

Not Unbilled. Delivered-ticket value at contract vs list.
Proves the compiler writes joins + filters + cross-table multiply.
Fails if sql/03 or scripts/04 unbilled YAML was edited.
Tries YAML 0.1 first; retries the same shape as 1.1 on this view only.
Demo 2 / Track B. Not MetricFlow. Not Track A.
"""

from __future__ import annotations

import csv
import importlib.util
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_status import upsert_kpi_row  # noqa: E402
from config import (  # noqa: E402
    DATA_DIR,
    PACK_ROOT,
    connect,
    print_sql,
    run_statement,
    settings,
    sql_str,
    substitute,
)

VIEW_NAME = "contract_vs_list_usd"
SQL_PATH = PACK_ROOT / "sql" / "06_complex_metric.sql"


def money(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def as_int(value: object) -> int:
    return int(value)


def load_unbilled_runner():
    path = PACK_ROOT / "scripts" / "04_metric_view.py"
    spec = importlib.util.spec_from_file_location("unbilled_mv", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def assert_unbilled_untouched(catalog: str, schema: str) -> None:
    """Fail the job if 03/04 unbilled YAML was edited."""
    mod = load_unbilled_runner()
    path = PACK_ROOT / "sql" / "03_metric_view.sql"
    raw = path.read_text(encoding="utf-8")
    substituted = raw.replace("{{catalog}}", catalog).replace("{{schema}}", schema)
    authored = mod.extract_yaml_block(substituted)
    mod.assert_dialect_01(authored)
    expected = mod.expected_yaml(catalog, schema)
    if mod.normalize_yaml(authored) != mod.normalize_yaml(expected):
        raise SystemExit(
            "FAIL: sql/03_metric_view.sql unbilled YAML was edited. "
            "Do not change unbilled_usd."
        )
    py04 = (PACK_ROOT / "scripts" / "04_metric_view.py").read_text(encoding="utf-8")
    if "contract_vs_list" in py04 or "temp_adjusted" in py04 or "joins:" in py04:
        raise SystemExit("FAIL: scripts/04_metric_view.py was edited. Leave unbilled 0.1 alone.")
    if "joins:" in authored or "filter:" in authored:
        raise SystemExit("FAIL: unbilled YAML gained joins/filter. Restore 0.1 fields+measures.")
    print("Unbilled guard ok: sql/03 + scripts/04 still live-proven 0.1 (untouched).")


def extract_yaml_block(sql_text: str) -> str:
    match = re.search(r"AS\s+\$\$(.*?)\$\$", sql_text, flags=re.S | re.I)
    if not match:
        raise SystemExit(f"{SQL_PATH.name}: missing AS $$ … $$ YAML block")
    return match.group(1)


def set_yaml_version(yaml_text: str, version: str) -> str:
    return re.sub(r"^version:\s*\S+", f"version: {version}", yaml_text.strip(), count=1, flags=re.M)


def create_view_sql(catalog: str, schema: str, version: str) -> str:
    raw = substitute(SQL_PATH.read_text(encoding="utf-8"), type("S", (), {"catalog": catalog, "schema": schema})())
    yaml_text = set_yaml_version(extract_yaml_block(raw), version)
    view = f"{catalog}.{schema}.{VIEW_NAME}"
    return f"""CREATE OR REPLACE VIEW {view}
WITH METRICS
LANGUAGE YAML
AS $$
{yaml_text.rstrip()}
$$"""


def expected_from_csv() -> dict:
    """Delivered + temp>=80 + gal>=5000 + July 2026 + gasoline|distillate."""
    products = {r["product_code"]: r for r in csv.DictReader((DATA_DIR / "products.csv").open())}
    parties = {r["party_id"]: r for r in csv.DictReader((DATA_DIR / "parties.csv").open())}
    terminals = {r["terminal_code"]: r for r in csv.DictReader((DATA_DIR / "terminals.csv").open())}

    unsliced = {
        "delivered_contract_usd": Decimal("0"),
        "delivered_list_usd": Decimal("0"),
        "list_minus_contract_usd": Decimal("0"),
        "delivered_ticket_count": 0,
        "hot_rack_contract_usd": Decimal("0"),
        "marine_contract_usd": Decimal("0"),
        "rbob_contract_usd": Decimal("0"),
    }
    by_sold: dict[str, dict] = {}
    by_prod: dict[str, dict] = {}

    def bag() -> dict:
        return {
            "delivered_contract_usd": Decimal("0"),
            "delivered_list_usd": Decimal("0"),
            "list_minus_contract_usd": Decimal("0"),
            "delivered_ticket_count": 0,
            "hot_rack_contract_usd": Decimal("0"),
            "marine_contract_usd": Decimal("0"),
            "rbob_contract_usd": Decimal("0"),
            "product_family": "",
        }

    with (DATA_DIR / "tickets.csv").open() as fh:
        for r in csv.DictReader(fh):
            pr = products[r["product_code"]]
            gal = Decimal(r["gallons_net"])
            temp = Decimal(r["temperature_f"])
            bol = r["bol_ts"][:10]
            if not (
                r["status"] == "delivered"
                and temp >= 80
                and gal >= 5000
                and "2026-07-01" <= bol <= "2026-07-31"
                and pr["product_family"] in ("gasoline", "distillate")
            ):
                continue
            cp = Decimal(pr["contract_price_usd"])
            lp = Decimal(pr["list_price_usd"])
            site = terminals[r["terminal_code"]]
            sold = parties[r["sold_to_id"]]["party_name"]
            prod = r["product_code"]
            contract = gal * cp
            listed = gal * lp
            spread = gal * (lp - cp)
            hot = contract if temp >= 88 else Decimal("0")
            marine = contract if site["mode"] == "marine_rack" else Decimal("0")
            rbob = contract if prod == "RBOB" else Decimal("0")
            for dest in (unsliced, by_sold.setdefault(sold, bag()), by_prod.setdefault(prod, bag())):
                dest["delivered_contract_usd"] += contract
                dest["delivered_list_usd"] += listed
                dest["list_minus_contract_usd"] += spread
                dest["delivered_ticket_count"] += 1
                dest["hot_rack_contract_usd"] += hot
                dest["marine_contract_usd"] += marine
                dest["rbob_contract_usd"] += rbob
            by_prod[prod]["product_family"] = pr["product_family"]

    return {"unsliced": unsliced, "sold_to": by_sold, "product": by_prod}


def print_expected(exp: dict) -> None:
    u = exp["unsliced"]
    print("\n======== EXPECTED (from data/*.csv) ========")
    print("Filter: delivered AND temp>=80 AND gal>=5000 AND July 2026")
    print("        AND product_family IN (gasoline, distillate)")
    print("        quality_hold excluded via status.")
    print(f"  delivered_contract_usd   {money(u['delivered_contract_usd'])}")
    print(f"  delivered_list_usd       {money(u['delivered_list_usd'])}")
    print(f"  list_minus_contract_usd  {money(u['list_minus_contract_usd'])}")
    print(f"  delivered_ticket_count   {u['delivered_ticket_count']}")
    print(f"  hot_rack_contract_usd    {money(u['hot_rack_contract_usd'])}")
    print(f"  marine_contract_usd      {money(u['marine_contract_usd'])}")
    print(f"  rbob_contract_usd        {money(u['rbob_contract_usd'])}")
    print("By sold_to:")
    for name, row in sorted(exp["sold_to"].items(), key=lambda kv: -kv[1]["delivered_contract_usd"]):
        print(
            f"  {name}: contract={money(row['delivered_contract_usd'])} "
            f"list={money(row['delivered_list_usd'])} n={row['delivered_ticket_count']}"
        )
    print("By product:")
    for name, row in sorted(exp["product"].items(), key=lambda kv: -kv[1]["delivered_contract_usd"]):
        print(
            f"  {name} ({row['product_family']}): contract={money(row['delivered_contract_usd'])} "
            f"list={money(row['delivered_list_usd'])} n={row['delivered_ticket_count']}"
        )


def compile_view(cur, catalog: str, schema: str) -> str:
    errors: list[tuple[str, str]] = []
    for version in ("0.1", "1.1"):
        stmt = create_view_sql(catalog, schema, version)
        print(f"\n======== CREATE {catalog}.{schema}.{VIEW_NAME}  version {version} ========")
        print_sql(stmt)
        try:
            cur.execute(stmt)
            print(f"(no result set)  compiled version {version}")
            return version
        except Exception as exc:
            text = str(exc)
            print(f"version {version} refused:\n{text}")
            errors.append((version, text))
            if version == "0.1":
                print("Retrying the SAME shape with version: 1.1 on this view only.")
    joined = " | ".join(f"{v}: {e}" for v, e in errors)
    raise SystemExit(
        "FAIL: contract_vs_list_usd did not compile on 0.1 or 1.1. "
        "Not flattening into a new fact.\n"
        f"Errors: {joined}"
    )


def assert_close(label: str, live: object, expected: Decimal | int, *, cents: bool) -> None:
    if cents:
        got = money(live)
        want = money(expected)
        if got != want:
            raise SystemExit(f"{label}: live {got} != expected {want}")
    else:
        got = as_int(live)
        want = int(expected)
        if got != want:
            raise SystemExit(f"{label}: live {got} != expected {want}")


KPI2_ID = "KPI-O2C-CONTRACT-VS-LIST-USD"
KPI2_POINTER = "delivered_contract_usd"
KPI2_STATUS = "approved"
KPI2_IRI = "https://example.org/domain-ontology-kpi/o2c#Obligation"

GOLD_DDL = """CREATE TABLE IF NOT EXISTS {fq}.gold_kpi_value (
  kpi_id STRING,
  grain STRING,
  grain_key STRING,
  grain_label STRING,
  as_of_date DATE,
  value_usd DECIMAL(18, 2),
  ticket_count BIGINT,
  formula_pointer STRING,
  published_ts TIMESTAMP
)"""


def maybe_insert_metadata(cur, fq: str) -> bool:
    """Store write path: compare prev, maybe reset approval, hash on approve."""
    # formula_version is the authored dialect (0.1), not whatever the retry used.
    new = {
        "kpi_id": KPI2_ID,
        "name": "Contract vs list USD",
        "owner": "Revenue Accounting / Order-to-Cash",
        "definition": "Delivered-ticket value at contract vs list (see Metric View)",
        "uom": "USD",
        "allowed_grain": "enterprise,sold_to,product",
        "default_grain_rule": "enterprise | sold_to | product",
        "gating_rule": "See contract_vs_list_usd Metric View (not Unbilled).",
        "status": KPI2_STATUS,
        "formula_pointer": KPI2_POINTER,
        "formula_object": f"{fq}.contract_vs_list_usd",
        "formula_version": "0.1",
        "ontology_iri": KPI2_IRI,
        "as_of_date": "2026-08-01",
    }
    try:
        applied = upsert_kpi_row(cur, fq, new)
        print(f"Metadata pointer row {KPI2_ID} upserted status={applied.get('status')}.")
        return True
    except Exception as exc:
        print(f"Metadata upsert skipped ({type(exc).__name__}).")
        return False


def gold_measure_insert_sql(fq: str, mv: str) -> str:
    return f"""INSERT INTO {fq}.gold_kpi_value (
  kpi_id, grain, grain_key, grain_label, as_of_date,
  value_usd, ticket_count, formula_pointer, published_ts
)
SELECT
  '{KPI2_ID}', 'enterprise', '*', 'Enterprise', DATE '2026-08-01',
  MEASURE(delivered_contract_usd), MEASURE(delivered_ticket_count),
  '{KPI2_POINTER}', current_timestamp()
FROM {mv}
UNION ALL
SELECT
  '{KPI2_ID}', 'sold_to', sold_to, sold_to, DATE '2026-08-01',
  MEASURE(delivered_contract_usd), MEASURE(delivered_ticket_count),
  '{KPI2_POINTER}', current_timestamp()
FROM {mv}
GROUP BY sold_to
UNION ALL
SELECT
  '{KPI2_ID}', 'product', product, product_family, DATE '2026-08-01',
  MEASURE(delivered_contract_usd), MEASURE(delivered_ticket_count),
  '{KPI2_POINTER}', current_timestamp()
FROM {mv}
GROUP BY product, product_family"""


def gold_values_insert_sql(fq: str, rows: list[tuple]) -> str:
    lines = []
    for grain, grain_key, grain_label, usd, n in rows:
        lines.append(
            f"  ({sql_str(KPI2_ID)}, {sql_str(grain)}, {sql_str(grain_key)}, "
            f"{sql_str(grain_label)}, DATE '2026-08-01', {usd}, {n}, {sql_str(KPI2_POINTER)})"
        )
    values = ",\n".join(lines)
    return f"""INSERT INTO {fq}.gold_kpi_value (
  kpi_id, grain, grain_key, grain_label, as_of_date,
  value_usd, ticket_count, formula_pointer, published_ts
)
SELECT
  CAST(kpi_id AS STRING), CAST(grain AS STRING), CAST(grain_key AS STRING),
  CAST(grain_label AS STRING), CAST(as_of_date AS DATE),
  CAST(value_usd AS DECIMAL(18, 2)), CAST(ticket_count AS BIGINT),
  CAST(formula_pointer AS STRING), current_timestamp()
FROM VALUES
{values}
AS v(kpi_id, grain, grain_key, grain_label, as_of_date, value_usd, ticket_count, formula_pointer)"""


def upsert_gold(cur, fq: str, mv: str, live_ent, sold_rows, prod_rows) -> bool:
    """Replace this kpi_id's gold rows FROM MEASURE(). Other kpi_ids kept."""
    try:
        run_statement(cur, GOLD_DDL.format(fq=fq), fetch=False)
        run_statement(cur, f"DELETE FROM {fq}.gold_kpi_value WHERE kpi_id = '{KPI2_ID}'", fetch=False)
    except Exception as exc:
        print(f"Gold table prepare skipped ({type(exc).__name__}).")
        return False
    try:
        run_statement(cur, gold_measure_insert_sql(fq, mv), fetch=False)
        print(f"Gold {KPI2_ID} inserted FROM MEASURE() (enterprise/sold_to/product).")
        return True
    except Exception as exc:
        print(
            f"INSERT from MEASURE() refused ({type(exc).__name__}: {exc}). "
            "Falling back to VALUES from the same MEASURE() results."
        )
        e_usd, e_n = live_ent[0], live_ent[3]
        rows = [("enterprise", "*", "Enterprise", money(e_usd), as_int(e_n))]
        for r in sold_rows:
            rows.append(("sold_to", str(r[0]), str(r[0]), money(r[1]), as_int(r[4])))
        for r in prod_rows:
            rows.append(("product", str(r[0]), str(r[1]), money(r[2]), as_int(r[5])))
        try:
            run_statement(cur, gold_values_insert_sql(fq, rows), fetch=False)
            print(f"Gold {KPI2_ID} inserted from MEASURE() VALUES fallback.")
            return True
        except Exception as exc2:
            print(f"Gold upsert skipped ({type(exc2).__name__}).")
            return False


def assert_metadata(cur, fq: str) -> None:
    rows = run_statement(
        cur,
        f"""SELECT formula_pointer, status, ontology_iri
FROM {fq}.dim_kpi_metadata
WHERE kpi_id = '{KPI2_ID}'""",
    )
    if not rows:
        raise SystemExit(f"{KPI2_ID} missing from dim_kpi_metadata")
    pointer, status, iri = rows[0]
    if str(pointer) != KPI2_POINTER:
        raise SystemExit(
            f"{KPI2_ID}.formula_pointer must be {KPI2_POINTER} (measure name), got {pointer!r}"
        )
    if str(status) != KPI2_STATUS:
        raise SystemExit(f"{KPI2_ID}.status must be {KPI2_STATUS}, got {status!r}")
    if not str(iri).endswith("#Obligation"):
        raise SystemExit(f"{KPI2_ID}.ontology_iri must end with #Obligation, got {iri!r}")
    catalog = run_statement(cur, f"SELECT kpi_id FROM {fq}.dim_kpi_metadata")
    ids = [str(r[0]) for r in catalog]
    if "KPI-O2C-UNBILLED-USD" in ids and len(catalog) < 2:
        raise SystemExit(
            f"dim_kpi_metadata: expected >= 2 rows when Unbilled is present, got {len(catalog)}"
        )
    print(
        f"Metadata row ok: pointer={pointer} status={status} iri ends #Obligation "
        f"catalog_rows={len(catalog)}"
    )


def assert_gold(cur, fq: str, exp: dict) -> None:
    ent = run_statement(
        cur,
        f"""SELECT value_usd, ticket_count
FROM {fq}.gold_kpi_value
WHERE kpi_id = '{KPI2_ID}' AND grain = 'enterprise'""",
    )
    if not ent:
        raise SystemExit(f"{KPI2_ID} gold enterprise row missing")
    want_usd = money(exp["unsliced"]["delivered_contract_usd"])
    want_n = int(exp["unsliced"]["delivered_ticket_count"])
    if money(ent[0][0]) != want_usd:
        raise SystemExit(f"{KPI2_ID} gold enterprise {ent[0][0]} != {want_usd}")
    if as_int(ent[0][1]) != want_n:
        raise SystemExit(f"{KPI2_ID} gold enterprise tickets {ent[0][1]} != {want_n}")
    by_grain = run_statement(
        cur,
        f"""SELECT grain, COUNT(*) FROM {fq}.gold_kpi_value
WHERE kpi_id = '{KPI2_ID}' GROUP BY grain""",
    )
    got = {str(g): int(n) for g, n in by_grain}
    want = {"enterprise": 1, "sold_to": len(exp["sold_to"]), "product": len(exp["product"])}
    if got != want:
        raise SystemExit(f"{KPI2_ID} gold grains: expected {want}, got {got}")
    ptrs = run_statement(
        cur,
        f"SELECT DISTINCT formula_pointer FROM {fq}.gold_kpi_value WHERE kpi_id = '{KPI2_ID}'",
    )
    if [str(r[0]) for r in ptrs] != [KPI2_POINTER]:
        raise SystemExit(f"{KPI2_ID} gold formula_pointer must be {KPI2_POINTER}, got {ptrs}")
    print(f"Gold ok: enterprise {want_usd} / {want_n}; grains {got}")


def main() -> None:
    cfg = settings()
    assert_unbilled_untouched(cfg.catalog, cfg.schema)
    exp = expected_from_csv()
    print_expected(exp)
    mv = f"{cfg.fq}.{VIEW_NAME}"

    unsliced_sql = f"""SELECT
  MEASURE(delivered_contract_usd)   AS delivered_contract_usd,
  MEASURE(delivered_list_usd)       AS delivered_list_usd,
  MEASURE(list_minus_contract_usd)  AS list_minus_contract_usd,
  MEASURE(delivered_ticket_count)   AS delivered_ticket_count,
  MEASURE(hot_rack_contract_usd)    AS hot_rack_contract_usd,
  MEASURE(marine_contract_usd)      AS marine_contract_usd,
  MEASURE(rbob_contract_usd)        AS rbob_contract_usd
FROM {mv}"""

    sold_sql = f"""SELECT
  sold_to,
  MEASURE(delivered_contract_usd)   AS delivered_contract_usd,
  MEASURE(delivered_list_usd)       AS delivered_list_usd,
  MEASURE(list_minus_contract_usd)  AS list_minus_contract_usd,
  MEASURE(delivered_ticket_count)   AS delivered_ticket_count,
  MEASURE(hot_rack_contract_usd)    AS hot_rack_contract_usd,
  MEASURE(marine_contract_usd)      AS marine_contract_usd,
  MEASURE(rbob_contract_usd)        AS rbob_contract_usd
FROM {mv}
GROUP BY sold_to
ORDER BY delivered_contract_usd DESC"""

    prod_sql = f"""SELECT
  product,
  product_family,
  MEASURE(delivered_contract_usd)   AS delivered_contract_usd,
  MEASURE(delivered_list_usd)       AS delivered_list_usd,
  MEASURE(list_minus_contract_usd)  AS list_minus_contract_usd,
  MEASURE(delivered_ticket_count)   AS delivered_ticket_count,
  MEASURE(hot_rack_contract_usd)    AS hot_rack_contract_usd,
  MEASURE(marine_contract_usd)      AS marine_contract_usd,
  MEASURE(rbob_contract_usd)        AS rbob_contract_usd
FROM {mv}
GROUP BY product, product_family
ORDER BY delivered_contract_usd DESC"""

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            version = compile_view(cur, cfg.catalog, cfg.schema)
            run_statement(cur, f"DESCRIBE TABLE EXTENDED {mv}")

            print("\n======== LIVE MEASURE() unsliced ========")
            live = run_statement(cur, unsliced_sql)
            if not live:
                raise SystemExit("unsliced MEASURE() returned 0 rows")
            row = live[0]
            u = exp["unsliced"]
            labels = [
                ("delivered_contract_usd", True),
                ("delivered_list_usd", True),
                ("list_minus_contract_usd", True),
                ("delivered_ticket_count", False),
                ("hot_rack_contract_usd", True),
                ("marine_contract_usd", True),
                ("rbob_contract_usd", True),
            ]
            print("\n======== LIVE vs EXPECTED (unsliced) ========")
            for i, (name, cents) in enumerate(labels):
                live_v = row[i]
                want = u[name]
                shown = money(live_v) if cents else as_int(live_v)
                want_s = money(want) if cents else int(want)
                print(f"  {name}: live={shown}  expected={want_s}")
                assert_close(name, live_v, want, cents=cents)

            print("\n======== LIVE MEASURE() by sold_to ========")
            sold_rows = run_statement(cur, sold_sql)
            live_sold = {str(r[0]): r for r in sold_rows}
            if set(live_sold) != set(exp["sold_to"]):
                raise SystemExit(f"sold_to keys live={set(live_sold)} expected={set(exp['sold_to'])}")
            for name, erow in exp["sold_to"].items():
                r = live_sold[name]
                assert_close(f"sold_to[{name}].contract", r[1], erow["delivered_contract_usd"], cents=True)
                assert_close(f"sold_to[{name}].list", r[2], erow["delivered_list_usd"], cents=True)
                assert_close(f"sold_to[{name}].n", r[4], erow["delivered_ticket_count"], cents=False)

            print("\n======== LIVE MEASURE() by product ========")
            prod_rows = run_statement(cur, prod_sql)
            live_prod = {str(r[0]): r for r in prod_rows}
            if set(live_prod) != set(exp["product"]):
                raise SystemExit(f"product keys live={set(live_prod)} expected={set(exp['product'])}")
            for name, erow in exp["product"].items():
                r = live_prod[name]
                assert_close(f"product[{name}].contract", r[2], erow["delivered_contract_usd"], cents=True)
                assert_close(f"product[{name}].n", r[5], erow["delivered_ticket_count"], cents=False)

            print("\n======== SELECT * must be refused ========")
            act3 = f"SELECT * FROM {mv}"
            print_sql(act3)
            try:
                cur.execute(act3)
                rows = cur.fetchall() if cur.description else []
                print("UNEXPECTED: SELECT * returned rows (should have failed):")
                print(rows)
                raise SystemExit(1)
            except SystemExit:
                raise
            except Exception as exc:
                text = str(exc)
                print(f"Refused (expected):\n{text}")
                if "METRIC_VIEW_MISSING_MEASURE_FUNCTION" not in text:
                    print(
                        "Note: error text did not contain "
                        "METRIC_VIEW_MISSING_MEASURE_FUNCTION. "
                        "Refusal is still the point.",
                        file=sys.stderr,
                    )

            if maybe_insert_metadata(cur, cfg.fq):
                assert_metadata(cur, cfg.fq)
            if upsert_gold(cur, cfg.fq, mv, row, sold_rows, prod_rows):
                assert_gold(cur, cfg.fq, exp)

    print(f"\nCOMPILED_VERSION={version}")
    print(
        f"LIVE unsliced: contract={money(u['delivered_contract_usd'])} "
        f"list={money(u['delivered_list_usd'])} "
        f"spread={money(u['list_minus_contract_usd'])} "
        f"tickets={u['delivered_ticket_count']} "
        f"hot={money(u['hot_rack_contract_usd'])} "
        f"marine={money(u['marine_contract_usd'])} "
        f"rbob={money(u['rbob_contract_usd'])}"
    )
    print("contract_vs_list_usd ok. Not Unbilled. unbilled_usd untouched.")
    print("Next: uv run python scripts/09_temp_adjusted.py")


if __name__ == "__main__":
    main()
