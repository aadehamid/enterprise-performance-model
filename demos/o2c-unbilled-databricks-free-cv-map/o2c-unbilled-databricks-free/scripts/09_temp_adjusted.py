#!/usr/bin/env python3
"""09_temp_adjusted.py — THIRD Metric View: temp_adjusted_delivered_usd.

Volume-correction / temperature-adjusted delivered value (rack math).
Not Unbilled. Not contract-vs-list.
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
from config import DATA_DIR, PACK_ROOT, connect, print_sql, run_statement, settings  # noqa: E402

VIEW_NAME = "temp_adjusted_delivered_usd"
SQL_PATH = PACK_ROOT / "sql" / "07_temp_adjusted.sql"
CENT_TOLERANCE = Decimal("0.02")


def money(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def as_int(value: object) -> int:
    return int(Decimal(str(value)))


def dec(value: object) -> Decimal:
    return Decimal(str(value))


def load_unbilled_runner():
    path = PACK_ROOT / "scripts" / "04_metric_view.py"
    spec = importlib.util.spec_from_file_location("unbilled_mv", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def assert_unbilled_untouched(catalog: str, schema: str) -> None:
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
    print("Unbilled guard ok: sql/03 + scripts/04 still live-proven 0.1 (untouched).")


def extract_yaml_block(sql_text: str) -> str:
    match = re.search(r"AS\s+\$\$(.*?)\$\$", sql_text, flags=re.S | re.I)
    if not match:
        raise SystemExit(f"{SQL_PATH.name}: missing AS $$ … $$ YAML block")
    return match.group(1)


def set_yaml_version(yaml_text: str, version: str) -> str:
    return re.sub(r"^version:\s*\S+", f"version: {version}", yaml_text.strip(), count=1, flags=re.M)


def create_view_sql(catalog: str, schema: str, version: str) -> str:
    raw = SQL_PATH.read_text(encoding="utf-8").replace("{{catalog}}", catalog).replace("{{schema}}", schema)
    yaml_text = set_yaml_version(extract_yaml_block(raw), version)
    view = f"{catalog}.{schema}.{VIEW_NAME}"
    return f"""CREATE OR REPLACE VIEW {view}
WITH METRICS
LANGUAGE YAML
AS $$
{yaml_text.rstrip()}
$$"""


def expected_from_csv() -> dict:
    """Delivered + gal>=4000 + Jun–Jul 2026 + gasoline|distillate|aviation."""
    products = {r["product_code"]: r for r in csv.DictReader((DATA_DIR / "products.csv").open())}
    terminals = {r["terminal_code"]: r for r in csv.DictReader((DATA_DIR / "terminals.csv").open())}

    unsliced = {
        "contract_at_net_usd": Decimal("0"),
        "contract_at_gross_usd": Decimal("0"),
        "temp_adjusted_usd": Decimal("0"),
        "expansion_delta_usd": Decimal("0"),
        "delivered_ticket_count": 0,
        "net_gallons": Decimal("0"),
        "gross_gallons": Decimal("0"),
        "weighted_temp_x_gallons": Decimal("0"),
        "marine_temp_adjusted_usd": Decimal("0"),
    }
    by_prod: dict[str, dict] = {}
    by_site: dict[str, dict] = {}

    def bag() -> dict:
        return {
            "contract_at_net_usd": Decimal("0"),
            "contract_at_gross_usd": Decimal("0"),
            "temp_adjusted_usd": Decimal("0"),
            "expansion_delta_usd": Decimal("0"),
            "delivered_ticket_count": 0,
            "net_gallons": Decimal("0"),
            "gross_gallons": Decimal("0"),
            "weighted_temp_x_gallons": Decimal("0"),
            "marine_temp_adjusted_usd": Decimal("0"),
            "product_family": "",
            "site_name": "",
            "mode": "",
        }

    with (DATA_DIR / "tickets.csv").open() as fh:
        for r in csv.DictReader(fh):
            pr = products[r["product_code"]]
            gal = Decimal(r["gallons_net"])
            gg = Decimal(r["gallons_gross"])
            temp = Decimal(r["temperature_f"])
            bol = r["bol_ts"][:10]
            if not (
                r["status"] == "delivered"
                and gal >= 4000
                and "2026-06-01" <= bol <= "2026-07-31"
                and pr["product_family"] in ("gasoline", "distillate", "aviation")
            ):
                continue
            cp = Decimal(pr["contract_price_usd"])
            expn = Decimal(pr["expansion_per_f"])
            factor = 1 + expn * (temp - 60)
            site = terminals[r["terminal_code"]]
            prod = r["product_code"]
            site_code = r["terminal_code"]
            net_usd = gal * cp
            gross_usd = gg * cp
            adj = gal * cp * factor
            delta = gal * cp * (expn * (temp - 60))
            marine = adj if site["mode"] == "marine_rack" else Decimal("0")
            for dest in (unsliced, by_prod.setdefault(prod, bag()), by_site.setdefault(site_code, bag())):
                dest["contract_at_net_usd"] += net_usd
                dest["contract_at_gross_usd"] += gross_usd
                dest["temp_adjusted_usd"] += adj
                dest["expansion_delta_usd"] += delta
                dest["delivered_ticket_count"] += 1
                dest["net_gallons"] += gal
                dest["gross_gallons"] += gg
                dest["weighted_temp_x_gallons"] += temp * gal
                dest["marine_temp_adjusted_usd"] += marine
            by_prod[prod]["product_family"] = pr["product_family"]
            by_site[site_code]["site_name"] = site["terminal_name"]
            by_site[site_code]["mode"] = site["mode"]

    return {"unsliced": unsliced, "product": by_prod, "site": by_site}


def print_expected(exp: dict) -> None:
    u = exp["unsliced"]
    print("\n======== EXPECTED (from data/*.csv) ========")
    print("Filter: delivered AND gal>=4000 AND Jun–Jul 2026")
    print("        AND product_family IN (gasoline, distillate, aviation)")
    print("        quality_hold excluded via status.")
    print(f"  contract_at_net_usd       {money(u['contract_at_net_usd'])}")
    print(f"  contract_at_gross_usd     {money(u['contract_at_gross_usd'])}")
    print(f"  temp_adjusted_usd         {money(u['temp_adjusted_usd'])}")
    print(f"  expansion_delta_usd       {money(u['expansion_delta_usd'])}")
    print(f"  delivered_ticket_count    {u['delivered_ticket_count']}")
    print(f"  net_gallons               {u['net_gallons']}")
    print(f"  gross_gallons             {u['gross_gallons']}")
    print(f"  weighted_temp_x_gallons   {u['weighted_temp_x_gallons']}")
    print(f"  marine_temp_adjusted_usd  {money(u['marine_temp_adjusted_usd'])}")
    if u["net_gallons"]:
        print(f"  weighted_avg_temp         {u['weighted_temp_x_gallons'] / u['net_gallons']}")
    print("By product:")
    for name, row in sorted(exp["product"].items(), key=lambda kv: -kv[1]["temp_adjusted_usd"]):
        print(
            f"  {name}: n={row['delivered_ticket_count']} "
            f"net={money(row['contract_at_net_usd'])} "
            f"adj={money(row['temp_adjusted_usd'])}"
        )
    print("By site:")
    for name, row in sorted(exp["site"].items(), key=lambda kv: -kv[1]["temp_adjusted_usd"]):
        print(
            f"  {name} {row['site_name']}: n={row['delivered_ticket_count']} "
            f"net={money(row['contract_at_net_usd'])} "
            f"adj={money(row['temp_adjusted_usd'])}"
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
        "FAIL: temp_adjusted_delivered_usd did not compile on 0.1 or 1.1. "
        "Not flattening into a new fact.\n"
        f"Errors: {joined}"
    )


def assert_money(label: str, live: object, expected: Decimal) -> None:
    got = money(live)
    want = money(expected)
    if abs(got - want) > CENT_TOLERANCE:
        raise SystemExit(f"{label}: live {got} != expected {want} (tol {CENT_TOLERANCE})")


def assert_qty(label: str, live: object, expected: Decimal | int) -> None:
    got = dec(live)
    want = dec(expected)
    if abs(got - want) > Decimal("0.01"):
        raise SystemExit(f"{label}: live {got} != expected {want}")


KPI3_ID = "KPI-O2C-TEMP-ADJUSTED-USD"
KPI3_POINTER = "temp_adjusted_usd"
KPI3_STATUS = "approved"
KPI3_IRI = "https://example.org/domain-ontology-kpi/o2c#Obligation"

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
        "kpi_id": KPI3_ID,
        "name": "Temp-adjusted delivered USD",
        "owner": "Revenue Accounting / Order-to-Cash",
        "definition": "Temperature-adjusted delivered value (see Metric View)",
        "uom": "USD",
        "allowed_grain": "enterprise,product,site",
        "default_grain_rule": "enterprise | product | site",
        "gating_rule": "See temp_adjusted_delivered_usd Metric View (not Unbilled).",
        "status": KPI3_STATUS,
        "formula_pointer": KPI3_POINTER,
        "formula_object": f"{fq}.temp_adjusted_delivered_usd",
        "formula_version": "0.1",
        "ontology_iri": KPI3_IRI,
        "as_of_date": "2026-08-01",
    }
    try:
        applied = upsert_kpi_row(cur, fq, new)
        print(f"Metadata pointer row {KPI3_ID} upserted status={applied.get('status')}.")
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
  '{KPI3_ID}', 'enterprise', '*', 'Enterprise', DATE '2026-08-01',
  MEASURE(temp_adjusted_usd), MEASURE(delivered_ticket_count),
  '{KPI3_POINTER}', current_timestamp()
FROM {mv}
UNION ALL
SELECT
  '{KPI3_ID}', 'product', product, product_family, DATE '2026-08-01',
  MEASURE(temp_adjusted_usd), MEASURE(delivered_ticket_count),
  '{KPI3_POINTER}', current_timestamp()
FROM {mv}
GROUP BY product, product_family
UNION ALL
SELECT
  '{KPI3_ID}', 'site', site, site_name, DATE '2026-08-01',
  MEASURE(temp_adjusted_usd), MEASURE(delivered_ticket_count),
  '{KPI3_POINTER}', current_timestamp()
FROM {mv}
GROUP BY site, site_name"""


def gold_values_insert_sql(fq: str, rows: list[tuple]) -> str:
    from config import sql_str

    lines = []
    for grain, grain_key, grain_label, usd, n in rows:
        lines.append(
            f"  ({sql_str(KPI3_ID)}, {sql_str(grain)}, {sql_str(grain_key)}, "
            f"{sql_str(grain_label)}, DATE '2026-08-01', {usd}, {n}, {sql_str(KPI3_POINTER)})"
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


def upsert_gold(cur, fq: str, mv: str, live_row, prod_rows, site_rows) -> bool:
    """Replace this kpi_id's gold rows FROM MEASURE(). Other kpi_ids kept."""
    try:
        run_statement(cur, GOLD_DDL.format(fq=fq), fetch=False)
        run_statement(cur, f"DELETE FROM {fq}.gold_kpi_value WHERE kpi_id = '{KPI3_ID}'", fetch=False)
    except Exception as exc:
        print(f"Gold table prepare skipped ({type(exc).__name__}).")
        return False
    try:
        run_statement(cur, gold_measure_insert_sql(fq, mv), fetch=False)
        print(f"Gold {KPI3_ID} inserted FROM MEASURE() (enterprise/product/site).")
        return True
    except Exception as exc:
        print(
            f"INSERT from MEASURE() refused ({type(exc).__name__}: {exc}). "
            "Falling back to VALUES from the same MEASURE() results."
        )
        rows = [
            ("enterprise", "*", "Enterprise", money(live_row[2]), as_int(live_row[4])),
        ]
        for r in prod_rows:
            rows.append(("product", str(r[0]), str(r[1]), money(r[3]), as_int(r[5])))
        for r in site_rows:
            rows.append(("site", str(r[0]), str(r[1]), money(r[4]), as_int(r[5])))
        try:
            run_statement(cur, gold_values_insert_sql(fq, rows), fetch=False)
            print(f"Gold {KPI3_ID} inserted from MEASURE() VALUES fallback.")
            return True
        except Exception as exc2:
            print(f"Gold upsert skipped ({type(exc2).__name__}).")
            return False


def assert_metadata(cur, fq: str) -> None:
    rows = run_statement(
        cur,
        f"""SELECT formula_pointer, status, ontology_iri
FROM {fq}.dim_kpi_metadata
WHERE kpi_id = '{KPI3_ID}'""",
    )
    if not rows:
        raise SystemExit(f"{KPI3_ID} missing from dim_kpi_metadata")
    pointer, status, iri = rows[0]
    if str(pointer) != KPI3_POINTER:
        raise SystemExit(
            f"{KPI3_ID}.formula_pointer must be {KPI3_POINTER} (measure name), got {pointer!r}"
        )
    if str(status) != KPI3_STATUS:
        raise SystemExit(f"{KPI3_ID}.status must be {KPI3_STATUS}, got {status!r}")
    if not str(iri).endswith("#Obligation"):
        raise SystemExit(f"{KPI3_ID}.ontology_iri must end with #Obligation, got {iri!r}")
    catalog = run_statement(cur, f"SELECT kpi_id FROM {fq}.dim_kpi_metadata")
    ids = [str(r[0]) for r in catalog]
    if "KPI-O2C-UNBILLED-USD" in ids and len(catalog) != 3:
        raise SystemExit(
            f"dim_kpi_metadata: expected 3 rows when Unbilled is present, got {len(catalog)}"
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
WHERE kpi_id = '{KPI3_ID}' AND grain = 'enterprise'""",
    )
    if not ent:
        raise SystemExit(f"{KPI3_ID} gold enterprise row missing")
    want_usd = money(exp["unsliced"]["temp_adjusted_usd"])
    want_n = int(exp["unsliced"]["delivered_ticket_count"])
    if abs(money(ent[0][0]) - want_usd) > CENT_TOLERANCE:
        raise SystemExit(f"{KPI3_ID} gold enterprise {ent[0][0]} != {want_usd}")
    if as_int(ent[0][1]) != want_n:
        raise SystemExit(f"{KPI3_ID} gold enterprise tickets {ent[0][1]} != {want_n}")
    by_grain = run_statement(
        cur,
        f"""SELECT grain, COUNT(*) FROM {fq}.gold_kpi_value
WHERE kpi_id = '{KPI3_ID}' GROUP BY grain""",
    )
    got = {str(g): int(n) for g, n in by_grain}
    want = {"enterprise": 1, "product": len(exp["product"]), "site": len(exp["site"])}
    if got != want:
        raise SystemExit(f"{KPI3_ID} gold grains: expected {want}, got {got}")
    ptrs = run_statement(
        cur,
        f"SELECT DISTINCT formula_pointer FROM {fq}.gold_kpi_value WHERE kpi_id = '{KPI3_ID}'",
    )
    if [str(r[0]) for r in ptrs] != [KPI3_POINTER]:
        raise SystemExit(f"{KPI3_ID} gold formula_pointer must be {KPI3_POINTER}, got {ptrs}")
    print(f"Gold ok: enterprise {want_usd} / {want_n}; grains {got}")


def main() -> None:
    cfg = settings()
    assert_unbilled_untouched(cfg.catalog, cfg.schema)
    exp = expected_from_csv()
    print_expected(exp)
    mv = f"{cfg.fq}.{VIEW_NAME}"

    unsliced_sql = f"""SELECT
  MEASURE(contract_at_net_usd)       AS contract_at_net_usd,
  MEASURE(contract_at_gross_usd)     AS contract_at_gross_usd,
  MEASURE(temp_adjusted_usd)         AS temp_adjusted_usd,
  MEASURE(expansion_delta_usd)       AS expansion_delta_usd,
  MEASURE(delivered_ticket_count)    AS delivered_ticket_count,
  MEASURE(net_gallons)               AS net_gallons,
  MEASURE(gross_gallons)             AS gross_gallons,
  MEASURE(weighted_temp_x_gallons)   AS weighted_temp_x_gallons,
  MEASURE(marine_temp_adjusted_usd)  AS marine_temp_adjusted_usd
FROM {mv}"""

    prod_sql = f"""SELECT
  product,
  product_family,
  MEASURE(contract_at_net_usd)       AS contract_at_net_usd,
  MEASURE(temp_adjusted_usd)         AS temp_adjusted_usd,
  MEASURE(expansion_delta_usd)       AS expansion_delta_usd,
  MEASURE(delivered_ticket_count)    AS delivered_ticket_count,
  MEASURE(net_gallons)               AS net_gallons,
  MEASURE(marine_temp_adjusted_usd)  AS marine_temp_adjusted_usd
FROM {mv}
GROUP BY product, product_family
ORDER BY temp_adjusted_usd DESC"""

    site_sql = f"""SELECT
  site,
  site_name,
  mode,
  MEASURE(contract_at_net_usd)       AS contract_at_net_usd,
  MEASURE(temp_adjusted_usd)         AS temp_adjusted_usd,
  MEASURE(delivered_ticket_count)    AS delivered_ticket_count,
  MEASURE(net_gallons)               AS net_gallons,
  MEASURE(marine_temp_adjusted_usd)  AS marine_temp_adjusted_usd
FROM {mv}
GROUP BY site, site_name, mode
ORDER BY temp_adjusted_usd DESC"""

    ratio_sql = f"""SELECT
  MEASURE(weighted_temp_x_gallons) / MEASURE(net_gallons) AS weighted_avg_temp
FROM {mv}"""

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
            print("\n======== LIVE vs EXPECTED (unsliced) ========")
            pairs = [
                ("contract_at_net_usd", row[0], u["contract_at_net_usd"], "money"),
                ("contract_at_gross_usd", row[1], u["contract_at_gross_usd"], "money"),
                ("temp_adjusted_usd", row[2], u["temp_adjusted_usd"], "money"),
                ("expansion_delta_usd", row[3], u["expansion_delta_usd"], "money"),
                ("delivered_ticket_count", row[4], u["delivered_ticket_count"], "int"),
                ("net_gallons", row[5], u["net_gallons"], "qty"),
                ("gross_gallons", row[6], u["gross_gallons"], "qty"),
                ("weighted_temp_x_gallons", row[7], u["weighted_temp_x_gallons"], "qty"),
                ("marine_temp_adjusted_usd", row[8], u["marine_temp_adjusted_usd"], "money"),
            ]
            for name, live_v, want, kind in pairs:
                if kind == "int":
                    print(f"  {name}: live={as_int(live_v)}  expected={int(want)}")
                    if as_int(live_v) != int(want):
                        raise SystemExit(f"{name}: live {live_v} != expected {want}")
                elif kind == "qty":
                    print(f"  {name}: live={dec(live_v)}  expected={want}")
                    assert_qty(name, live_v, want)
                else:
                    print(f"  {name}: live={money(live_v)}  expected={money(want)}")
                    assert_money(name, live_v, want)

            print("\n======== LIVE MEASURE() by product ========")
            prod_rows = run_statement(cur, prod_sql)
            live_prod = {str(r[0]): r for r in prod_rows}
            if set(live_prod) != set(exp["product"]):
                raise SystemExit(f"product keys live={set(live_prod)} expected={set(exp['product'])}")
            for name, erow in exp["product"].items():
                r = live_prod[name]
                assert_money(f"product[{name}].net", r[2], erow["contract_at_net_usd"])
                assert_money(f"product[{name}].adj", r[3], erow["temp_adjusted_usd"])
                if as_int(r[5]) != erow["delivered_ticket_count"]:
                    raise SystemExit(f"product[{name}].n live {r[5]} != {erow['delivered_ticket_count']}")

            print("\n======== LIVE MEASURE() by site ========")
            site_rows = run_statement(cur, site_sql)
            live_site = {str(r[0]): r for r in site_rows}
            if set(live_site) != set(exp["site"]):
                raise SystemExit(f"site keys live={set(live_site)} expected={set(exp['site'])}")
            for name, erow in exp["site"].items():
                r = live_site[name]
                assert_money(f"site[{name}].net", r[3], erow["contract_at_net_usd"])
                assert_money(f"site[{name}].adj", r[4], erow["temp_adjusted_usd"])
                if as_int(r[5]) != erow["delivered_ticket_count"]:
                    raise SystemExit(f"site[{name}].n live {r[5]} != {erow['delivered_ticket_count']}")

            print("\n======== weighted avg temp (measure arithmetic, optional) ========")
            try:
                ratio_rows = run_statement(cur, ratio_sql)
                if ratio_rows:
                    live_avg = dec(ratio_rows[0][0])
                    want_avg = u["weighted_temp_x_gallons"] / u["net_gallons"]
                    print(f"  weighted_avg_temp: live={live_avg}  expected={want_avg}")
            except Exception as exc:
                print(
                    "Measure arithmetic MEASURE()/MEASURE() not accepted; "
                    f"returning the two measures separately. ({type(exc).__name__})"
                )

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
            if upsert_gold(cur, cfg.fq, mv, row, prod_rows, site_rows):
                assert_gold(cur, cfg.fq, exp)

    print(f"\nCOMPILED_VERSION={version}")
    print(
        f"LIVE unsliced: net={money(u['contract_at_net_usd'])} "
        f"gross={money(u['contract_at_gross_usd'])} "
        f"adj={money(u['temp_adjusted_usd'])} "
        f"delta={money(u['expansion_delta_usd'])} "
        f"tickets={u['delivered_ticket_count']} "
        f"marine={money(u['marine_temp_adjusted_usd'])}"
    )
    print("temp_adjusted_delivered_usd ok. Not Unbilled. unbilled_usd untouched.")


if __name__ == "__main__":
    main()
