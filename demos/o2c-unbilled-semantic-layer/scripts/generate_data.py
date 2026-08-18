#!/usr/bin/env python3
"""Generate deterministic downstream O&G O2C seed CSVs.

One run with seed=42 always produces the same tickets, invoices, and
unbilled set so a Mac rerun matches the numbers in README / VERIFY.txt.

Unbilled (certified):
  status = delivered
  no invoice line as of as_of_date 2026-08-01
  value = gallons_net * contract_price_usd
"""
from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
AS_OF = date(2026, 8, 1)
START = date(2026, 6, 1)
END = date(2026, 7, 31)
N_TICKETS = 1200

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seeds"

PARTIES = [
    {
        "party_id": "APEX-PAYER",
        "party_name": "Apex Fuels LLC",
        "legal_name": "Apex Fuels LLC",
        "party_class": "marketer",
        "tax_id": "76-4412901",
        "hq_city": "Houston",
        "hq_state": "TX",
    },
    {
        "party_id": "APEX-HOU",
        "party_name": "Apex Fuels Houston Rack",
        "legal_name": "Apex Fuels LLC — Houston Rack Desk",
        "party_class": "wholesale_rack",
        "tax_id": "76-4412901",
        "hq_city": "Houston",
        "hq_state": "TX",
    },
    {
        "party_id": "APEX-DAL",
        "party_name": "Apex Fuels Dallas Dealer",
        "legal_name": "Apex Fuels LLC — Dallas Dealer Network",
        "party_class": "dealer",
        "tax_id": "76-4412901",
        "hq_city": "Dallas",
        "hq_state": "TX",
    },
    {
        "party_id": "APEX-BILL",
        "party_name": "Apex Fuels LLC Accounts Payable",
        "legal_name": "Apex Fuels LLC",
        "party_class": "shared_services",
        "tax_id": "76-4412901",
        "hq_city": "Houston",
        "hq_state": "TX",
    },
    {
        "party_id": "GCA",
        "party_name": "Gulf Coast Aviation Inc",
        "legal_name": "Gulf Coast Aviation Inc",
        "party_class": "aviation",
        "tax_id": "72-8831044",
        "hq_city": "Houston",
        "hq_state": "TX",
    },
    {
        "party_id": "METRO-PAYER",
        "party_name": "Metro Lubricants",
        "legal_name": "Metro Lubricants Company",
        "party_class": "distributor",
        "tax_id": "74-2291880",
        "hq_city": "Beaumont",
        "hq_state": "TX",
    },
    {
        "party_id": "METRO-BMT",
        "party_name": "Metro Lubes Beaumont",
        "legal_name": "Metro Lubricants Company — Beaumont",
        "party_class": "distributor_site",
        "tax_id": "74-2291880",
        "hq_city": "Beaumont",
        "hq_state": "TX",
    },
    {
        "party_id": "METRO-BILL",
        "party_name": "Metro Lubricants Shared Services",
        "legal_name": "Metro Lubricants Company",
        "party_class": "shared_services",
        "tax_id": "74-2291880",
        "hq_city": "Beaumont",
        "hq_state": "TX",
    },
]

# Ship-to is a location (terminal), not a customer role.
ROLES = [
    ("APEX-PAYER", "payer"),
    ("APEX-HOU", "sold_to"),
    ("APEX-DAL", "sold_to"),
    ("APEX-BILL", "bill_to"),
    ("GCA", "payer"),
    ("GCA", "sold_to"),
    ("GCA", "bill_to"),
    ("METRO-PAYER", "payer"),
    ("METRO-BMT", "sold_to"),
    ("METRO-BILL", "bill_to"),
]

TERMINALS = [
    {
        "terminal_code": "HSC",
        "terminal_name": "Houston Ship Channel",
        "city": "Houston",
        "state": "TX",
        "mode": "marine_rack",
    },
    {
        "terminal_code": "DAL",
        "terminal_name": "Dallas",
        "city": "Dallas",
        "state": "TX",
        "mode": "pipeline_rack",
    },
    {
        "terminal_code": "BMT",
        "terminal_name": "Beaumont",
        "city": "Beaumont",
        "state": "TX",
        "mode": "refinery_rack",
    },
]

PRODUCTS = [
    {
        "product_code": "RBOB",
        "product_name": "RBOB Gasoline",
        "product_family": "gasoline",
        "contract_price_usd": 2.1840,
        "list_price_usd": 2.2690,
        "expansion_per_f": 0.00069,
        "uom": "US gallon",
    },
    {
        "product_code": "ULSD",
        "product_name": "Ultra-Low Sulfur Diesel",
        "product_family": "distillate",
        "contract_price_usd": 2.3120,
        "list_price_usd": 2.4070,
        "expansion_per_f": 0.00045,
        "uom": "US gallon",
    },
    {
        "product_code": "JETA",
        "product_name": "Jet-A",
        "product_family": "aviation",
        "contract_price_usd": 2.1560,
        "list_price_usd": 2.2480,
        "expansion_per_f": 0.00051,
        "uom": "US gallon",
    },
]
PRODUCT_BY_CODE = {p["product_code"]: p for p in PRODUCTS}

# sold-to book: home terminal, payer, bill-to, product mix, typical gallons
BOOKS = {
    "APEX-HOU": {
        "payer_id": "APEX-PAYER",
        "bill_to_id": "APEX-BILL",
        "home_terminal": "HSC",
        "n": 480,
        "products": [("RBOB", 0.60), ("ULSD", 0.40)],
        "gal_lo": 4200,
        "gal_hi": 8500,
        "hold_rate": 0.055,
        "cross_rate": 0.04,
        "cross_terminals": ["DAL", "BMT"],
    },
    "APEX-DAL": {
        "payer_id": "APEX-PAYER",
        "bill_to_id": "APEX-BILL",
        "home_terminal": "DAL",
        "n": 300,
        "products": [("RBOB", 0.55), ("ULSD", 0.45)],
        "gal_lo": 3800,
        "gal_hi": 8200,
        "hold_rate": 0.06,
        "cross_rate": 0.04,
        "cross_terminals": ["HSC"],
    },
    "METRO-BMT": {
        "payer_id": "METRO-PAYER",
        "bill_to_id": "METRO-BILL",
        "home_terminal": "BMT",
        "n": 240,
        "products": [("ULSD", 0.80), ("RBOB", 0.20)],
        "gal_lo": 3000,
        "gal_hi": 7800,
        "hold_rate": 0.05,
        "cross_rate": 0.04,
        "cross_terminals": ["HSC"],
    },
    "GCA": {
        "payer_id": "GCA",
        "bill_to_id": "GCA",
        "home_terminal": "HSC",
        "n": 180,
        "products": [("JETA", 1.0)],
        "gal_lo": 2200,
        "gal_hi": 11000,
        "hold_rate": 0.09,
        "cross_rate": 0.03,
        "cross_terminals": ["DAL"],
    },
}


def daterange(start: date, end: date) -> list[date]:
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]


def pick_weighted(pairs, rng: random.Random) -> str:
    codes, weights = zip(*pairs)
    return rng.choices(list(codes), weights=list(weights), k=1)[0]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    days = daterange(START, END)
    # Slight July overweight so late-month invoice lag creates unbilled naturally.
    day_weights = [1.0 + (0.35 if d.month == 7 else 0.0) for d in days]

    deliveries = []
    seq = 1
    for sold_to_id, book in BOOKS.items():
        for _ in range(book["n"]):
            bol_date = rng.choices(days, weights=day_weights, k=1)[0]
            hour = rng.randint(5, 21)
            minute = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
            bol_ts = datetime(bol_date.year, bol_date.month, bol_date.day, hour, minute, 0)
            product_code = pick_weighted(book["products"], rng)
            product = PRODUCT_BY_CODE[product_code]
            if rng.random() < book["cross_rate"]:
                terminal_code = rng.choice(book["cross_terminals"])
            else:
                terminal_code = book["home_terminal"]
            gallons_net = round(rng.uniform(book["gal_lo"], book["gal_hi"]), 1)
            temperature_f = round(rng.uniform(74.0, 98.0), 1)
            gallons_gross = round(
                gallons_net * (1.0 + product["expansion_per_f"] * (temperature_f - 60.0)),
                1,
            )
            status = "quality_hold" if rng.random() < book["hold_rate"] else "delivered"
            deliveries.append(
                {
                    "ticket_id": f"BOL-2026-{seq:06d}",
                    "bol_ts": bol_ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "bol_date": bol_date.isoformat(),
                    "terminal_code": terminal_code,
                    "sold_to_id": sold_to_id,
                    "payer_id": book["payer_id"],
                    "bill_to_id": book["bill_to_id"],
                    "product_code": product_code,
                    "gallons_net": f"{gallons_net:.1f}",
                    "gallons_gross": f"{gallons_gross:.1f}",
                    "temperature_f": f"{temperature_f:.1f}",
                    "status": status,
                    "_bol_date": bol_date,
                    "_net": gallons_net,
                    "_gross": gallons_gross,
                    "_contract": product["contract_price_usd"],
                    "_list": product["list_price_usd"],
                }
            )
            seq += 1

    assert len(deliveries) == N_TICKETS

    # Partial billing: quality_hold is never billed. Of delivered tickets,
    # leave ~28% unbilled on purpose, plus any whose 3–14 day lag would
    # push the invoice past as_of 2026-08-01.
    billed = []
    for t in deliveries:
        t["_billed"] = False
        if t["status"] != "delivered":
            continue
        lag = rng.randint(3, 14)
        inv_date = t["_bol_date"] + timedelta(days=lag)
        if inv_date > AS_OF:
            continue
        if rng.random() < 0.28:
            continue
        t["_billed"] = True
        t["_inv_date"] = inv_date
        billed.append(t)

    # One invoice per payer per ISO week. Apex Houston + Dallas tickets in
    # the same week share an invoice (billed to the payer, not the sold-to).
    groups: dict[tuple, list] = {}
    for t in billed:
        iso = t["_inv_date"].isocalendar()
        key = (t["payer_id"], t["bill_to_id"], iso[0], iso[1])
        groups.setdefault(key, []).append(t)

    invoices = []
    invoice_lines = []
    inv_seq = 1
    for (payer_id, bill_to_id, year, week), tickets in sorted(groups.items()):
        invoice_id = f"INV-2026-{inv_seq:04d}"
        inv_seq += 1
        invoice_date = max(t["_inv_date"] for t in tickets)
        amount = 0.0
        for t in tickets:
            line_amt = round(t["_net"] * t["_contract"], 2)
            amount += line_amt
            invoice_lines.append(
                {
                    "invoice_id": invoice_id,
                    "ticket_id": t["ticket_id"],
                    "product_code": t["product_code"],
                    "line_gallons_net": f"{t['_net']:.1f}",
                    "line_amount_usd": f"{line_amt:.2f}",
                }
            )
        invoices.append(
            {
                "invoice_id": invoice_id,
                "invoice_date": invoice_date.isoformat(),
                "payer_id": payer_id,
                "bill_to_id": bill_to_id,
                "invoice_status": "posted",
                "invoice_amount_usd": f"{round(amount, 2):.2f}",
                "line_count": len(tickets),
            }
        )

    # Write seeds (no private helper columns).
    write_csv(
        SEEDS / "parties.csv",
        PARTIES,
        [
            "party_id",
            "party_name",
            "legal_name",
            "party_class",
            "tax_id",
            "hq_city",
            "hq_state",
        ],
    )
    write_csv(
        SEEDS / "party_roles.csv",
        [{"party_id": p, "role_code": r} for p, r in ROLES],
        ["party_id", "role_code"],
    )
    write_csv(
        SEEDS / "terminals.csv",
        TERMINALS,
        ["terminal_code", "terminal_name", "city", "state", "mode"],
    )
    write_csv(
        SEEDS / "products.csv",
        PRODUCTS,
        [
            "product_code",
            "product_name",
            "product_family",
            "contract_price_usd",
            "list_price_usd",
            "expansion_per_f",
            "uom",
        ],
    )
    write_csv(
        SEEDS / "deliveries.csv",
        deliveries,
        [
            "ticket_id",
            "bol_ts",
            "terminal_code",
            "sold_to_id",
            "payer_id",
            "bill_to_id",
            "product_code",
            "gallons_net",
            "gallons_gross",
            "temperature_f",
            "status",
        ],
    )
    write_csv(
        SEEDS / "invoices.csv",
        invoices,
        [
            "invoice_id",
            "invoice_date",
            "payer_id",
            "bill_to_id",
            "invoice_status",
            "invoice_amount_usd",
            "line_count",
        ],
    )
    write_csv(
        SEEDS / "invoice_lines.csv",
        invoice_lines,
        [
            "invoice_id",
            "ticket_id",
            "product_code",
            "line_gallons_net",
            "line_amount_usd",
        ],
    )

    # Sanity: the three "Unbilled USD" formulas must not all agree.
    billed_ids = {t["ticket_id"] for t in billed}
    party_name = {p["party_id"]: p["party_name"] for p in PARTIES}

    def report_a_b(tickets):
        total = 0.0
        by_sold = {}
        by_pay = {}
        for t in tickets:
            if t["status"] != "delivered" or t["ticket_id"] in billed_ids:
                continue
            usd = t["_net"] * t["_contract"]
            total += usd
            sn = party_name[t["sold_to_id"]]
            pn = party_name[t["payer_id"]]
            by_sold[sn] = by_sold.get(sn, 0.0) + usd
            by_pay[pn] = by_pay.get(pn, 0.0) + usd
        return total, by_sold, by_pay

    def report_c(tickets):
        total = 0.0
        by_cust = {}
        for t in tickets:
            # Sloppy: still trying to be unbilled but uses gross * list, includes holds.
            if t["ticket_id"] in billed_ids:
                continue
            usd = t["_gross"] * t["_list"]
            if t["sold_to_id"] in ("APEX-HOU", "APEX-DAL"):
                label = party_name[t["sold_to_id"]]
            elif t["sold_to_id"] == "METRO-BMT":
                label = party_name[t["payer_id"]]
            else:
                label = party_name[t["sold_to_id"]]
            total += usd
            by_cust[label] = by_cust.get(label, 0.0) + usd
        return total, by_cust

    a_total, by_sold, by_pay = report_a_b(deliveries)
    c_total, _ = report_c(deliveries)
    delivered = sum(1 for t in deliveries if t["status"] == "delivered")
    holds = sum(1 for t in deliveries if t["status"] == "quality_hold")
    unbilled_n = delivered - len(billed)
    unbilled_rate = unbilled_n / delivered if delivered else 0.0

    print(f"Wrote seeds to {SEEDS}")
    print(f"  tickets          : {len(deliveries)}")
    print(f"  delivered        : {delivered}")
    print(f"  quality_hold     : {holds}")
    print(f"  billed lines     : {len(billed)}")
    print(f"  unbilled delivered: {unbilled_n} ({unbilled_rate:.1%} of delivered)")
    print(f"  invoices         : {len(invoices)}")
    print(f"  Report A/B total : ${a_total:,.2f}  (net * contract, delivered, unbilled)")
    print(f"  Report C total   : ${c_total:,.2f}  (gross * list, includes holds)")
    print(f"  Report A rows    : {len(by_sold)} sold-tos")
    print(f"  Report B rows    : {len(by_pay)} payers")
    print("  Report A by sold-to:")
    for k, v in sorted(by_sold.items(), key=lambda kv: -kv[1]):
        print(f"    {k:32s} ${v:,.2f}")
    print("  Report B by payer:")
    for k, v in sorted(by_pay.items(), key=lambda kv: -kv[1]):
        print(f"    {k:32s} ${v:,.2f}")
    if abs(a_total - c_total) < 1.0:
        raise SystemExit("FAIL: Report A/B and Report C totals are equal — adjust generator.")
    if not (0.25 <= unbilled_rate <= 0.40):
        raise SystemExit(
            f"FAIL: unbilled rate {unbilled_rate:.1%} is outside 25–40% of delivered."
        )
    if len(by_pay) >= len(by_sold):
        raise SystemExit("FAIL: Report B should have fewer customer rows than Report A.")
    print("Generator checks passed.")


if __name__ == "__main__":
    main()
