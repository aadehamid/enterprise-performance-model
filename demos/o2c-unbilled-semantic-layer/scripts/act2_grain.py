#!/usr/bin/env python3
"""Act 2 — metadata is one row; grain lives on the fact."""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "o2c.duckdb"


def main() -> None:
    if not DB.exists():
        print(f"FAIL: {DB} not found. Run dbt seed && dbt run first.", file=sys.stderr)
        sys.exit(1)

    con = duckdb.connect(str(DB), read_only=True)

    print("=" * 72)
    print("ACT 2 — dim_kpi_metadata (1 row) joined to gold slices (many rows)")
    print("=" * 72)

    cols = [
        "kpi_id",
        "name",
        "owner",
        "definition",
        "uom",
        "default_grain_rule",
        "status",
        "formula_pointer",
        "as_of_date",
    ]
    row = con.execute(
        "select kpi_id, name, owner, definition, uom, default_grain_rule, "
        "status, formula_pointer, as_of_date from dim_kpi_metadata"
    ).fetchone()
    print()
    print("dim_kpi_metadata — ONE certified definition")
    for c, v in zip(cols, row):
        print(f"  {c:22s} {v}")

    n_gold = con.execute("select count(*) from gold_kpi_unbilled").fetchone()[0]
    n_tickets = con.execute("select count(*) from fct_unbilled").fetchone()[0]
    print()
    print(f"gold_kpi_unbilled rows (sold_to + terminal + day): {n_gold}")
    print(f"fct_unbilled rows (ticket grain, for audit):       {n_tickets}")
    print("Grain lives on the fact. Metadata does not explode into one row per site.")

    print()
    print("Houston vs Dallas (same KPI, same formula, different sold-to / terminal)")
    rows = con.execute(
        """
        select
            m.kpi_id,
            m.name,
            m.formula_pointer,
            g.sold_to_name,
            g.terminal_code,
            round(sum(g.unbilled_usd), 2) as unbilled_usd,
            sum(g.ticket_count) as tickets
        from dim_kpi_metadata m
        cross join gold_kpi_unbilled g
        where g.sold_to_id in ('APEX-HOU', 'APEX-DAL')
        group by 1, 2, 3, 4, 5
        order by 4, 5
        """
    ).fetchall()
    print(f"{'sold_to':<32} {'term':<6} {'unbilled_usd':>16} {'tickets':>8}")
    print("-" * 66)
    for _kid, _name, _fp, sold, term, usd, n in rows:
        print(f"{sold:<32} {term:<6} {usd:>16,.2f} {n:>8}")

    print()
    print("A KPI Store would certify this definition. This demo IS the consumption")
    print("layer: one MetricFlow metric (unbilled_usd) that both reports must call.")
    print("=" * 72)


if __name__ == "__main__":
    main()
