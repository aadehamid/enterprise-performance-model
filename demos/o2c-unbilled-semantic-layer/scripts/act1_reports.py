#!/usr/bin/env python3
"""Act 1 — three reports all labeled 'Unbilled USD' that disagree.

Report A and B share the certified ticket set (delivered, net, contract,
no holds, no invoice as of 2026-08-01). Only the 'customer' group-by changes.
Report C is sloppy: gross * list, includes quality_hold, mixes party roles
into one 'customer' label.

Grand totals: A == B (same tickets), C is different.
Row counts: B has fewer rows than A (two Apex sold-tos roll to one payer).
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "o2c.duckdb"
AS_OF = "2026-08-01"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not DB.exists():
        fail(f"{DB} not found. Run dbt seed && dbt run first.")

    con = duckdb.connect(str(DB), read_only=True)

    print("=" * 72)
    print("ACT 1 — Three reports named 'Unbilled USD'")
    print(f"as_of_date = {AS_OF}")
    print("=" * 72)

    report_a = con.execute(
        """
        select
            sold_to_name as customer,
            round(sum(unbilled_usd), 2) as unbilled_usd,
            count(*) as tickets
        from fct_unbilled
        group by 1
        order by 2 desc
        """
    ).fetchall()
    a_total = round(sum(r[1] for r in report_a), 2)

    print()
    print("Report A — Unbilled USD by customer (SOLD-TO)")
    print(f"{'customer':<36} {'unbilled_usd':>16} {'tickets':>8}")
    print("-" * 64)
    for name, usd, n in report_a:
        print(f"{name:<36} {usd:>16,.2f} {n:>8}")
    print("-" * 64)
    print(f"{'GRAND TOTAL':<36} {a_total:>16,.2f}")

    report_b = con.execute(
        """
        select
            payer_name as customer,
            round(sum(unbilled_usd), 2) as unbilled_usd,
            count(*) as tickets
        from fct_unbilled
        group by 1
        order by 2 desc
        """
    ).fetchall()
    b_total = round(sum(r[1] for r in report_b), 2)

    print()
    print("Report B — Unbilled USD by customer (PAYER)")
    print(f"{'customer':<36} {'unbilled_usd':>16} {'tickets':>8}")
    print("-" * 64)
    for name, usd, n in report_b:
        print(f"{name:<36} {usd:>16,.2f} {n:>8}")
    print("-" * 64)
    print(f"{'GRAND TOTAL':<36} {b_total:>16,.2f}")

    # Report C reads the raw delivery fact so it can include quality_hold
    # and use the wrong quantity / price basis.
    report_c = con.execute(
        """
        select
            case
                when sold_to_id in ('APEX-HOU', 'APEX-DAL') then sold_to_name
                when sold_to_id = 'METRO-BMT' then payer_name
                else sold_to_name
            end as customer,
            round(sum(sloppy_value_usd), 2) as unbilled_usd,
            count(*) as tickets
        from fct_delivery
        where not is_billed
        group by 1
        order by 2 desc
        """
    ).fetchall()
    c_total = round(sum(r[1] for r in report_c), 2)

    print()
    print("Report C — Unbilled USD by customer (SLOPPY)")
    print("  gallons_gross * list_price; includes quality_hold;")
    print("  'customer' mixes sold-to (Apex) with payer (Metro).")
    print(f"{'customer':<36} {'unbilled_usd':>16} {'tickets':>8}")
    print("-" * 64)
    for name, usd, n in report_c:
        print(f"{name:<36} {usd:>16,.2f} {n:>8}")
    print("-" * 64)
    print(f"{'GRAND TOTAL':<36} {c_total:>16,.2f}")

    print()
    print("=" * 72)
    print("GRAND TOTALS (all labeled Unbilled USD)")
    print(f"  Report A (sold-to, certified ticket set): ${a_total:,.2f}")
    print(f"  Report B (payer,   certified ticket set): ${b_total:,.2f}")
    print(f"  Report C (sloppy basis + holds + mix):    ${c_total:,.2f}")
    print()
    print("Why they fight:")
    print(f"  • A and B share the same tickets, so totals match (${a_total:,.2f}).")
    print(f"    Only the customer column changes: {len(report_a)} sold-to rows vs")
    print(f"    {len(report_b)} payer rows. Two Apex sold-tos roll to one payer.")
    apex_sold = sum(r[1] for r in report_a if r[0].startswith("Apex Fuels") and "LLC" not in r[0])
    apex_payer = sum(r[1] for r in report_b if r[0] == "Apex Fuels LLC")
    print(f"  • Apex Fuels LLC (payer) = ${apex_payer:,.2f}.")
    print(f"    Sum of Apex Houston Rack + Apex Dallas Dealer = ${apex_sold:,.2f}.")
    print("    Those are the SAME tickets. Adding payer + sold-tos double-counts.")
    print(f"  • Report C is a different number (${c_total:,.2f}) because it uses")
    print("    ambient gallons, list price, and quality-hold tickets.")
    print("=" * 72)

    if abs(a_total - b_total) > 0.02:
        fail(f"Report A ({a_total}) and B ({b_total}) should share a ticket-set total.")
    if abs(a_total - c_total) < 1.0:
        fail("Report C total equals A/B — sloppy report is not visibly wrong.")
    if len(report_b) >= len(report_a):
        fail("Report B should have fewer customer rows than Report A.")

    # Stash totals for VERIFY / Act 3 comparison
    out = ROOT / "target" / "act1_totals.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"A={a_total:.2f}\nB={b_total:.2f}\nC={c_total:.2f}\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
