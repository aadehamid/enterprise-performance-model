"""Offline tests of the demo's data: determinism, the shapes the shared assets have, the provenance labels, and the
scenario's relabelling. Expected values are written out by hand from EPM-DEC-001-0097 and the EIA cache."""
import csv
import datetime as dt
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pricing_demo import catalog, generate, public_data  # noqa: E402
from pricing_demo.config import PROVENANCE  # noqa: E402

TABLES = generate.build()


def digest(tables):
    h = hashlib.sha256()
    for system in sorted(tables):
        for name in sorted(tables[system]):
            t = tables[system][name]
            h.update(repr((system, name, t.columns, t.rows)).encode())
    return h.hexdigest()


def rows(system, table):
    t = TABLES[system][table]
    return [dict(zip(t.columns, r)) for r in t.rows]


def test_the_same_seed_gives_the_same_rows():
    assert digest(generate.build()) == digest(TABLES)


def test_127_crack_series_in_44_groups_keep_the_named_ids():
    cracks = catalog.crack_masters()
    assert len(cracks) == 127 and len({m.group for m in cracks}) == 44
    named = {m.id: m.name for m in cracks if m.provenance == "real"}
    # EPM-DEC-001-0097 item 4 and market-data 1.0.0: the six primary regional series, the blends and the NYMEX crack.
    assert named["37438"] == "CHI 3-2-1 Crack WTI, ex-RIN"
    assert named["43870"] == "USGC 3-2-1 MEH Crack, ex-RIN"
    assert {"36855", "37439", "37443", "37471", "37464", "42023", "39998"} <= set(named)
    assert {m.id for m in cracks if m.provenance == "synthesized" and int(m.id) < 60000} == {"44934", "44935"}


def test_the_five_benchmarks_and_their_tenors():
    bench = {m.id: m for m in catalog.benchmark_masters()}
    assert set(bench) == {"572", "747", "750", "752", "9471"}
    detail = rows("mpr", "pricedetail")
    tenors = {}
    for r in detail:
        if str(r["PriceMasterId"]) in bench:
            tenors.setdefault(str(r["PriceMasterId"]), set()).add(r["RelativePeriodNum"])
    assert tenors["572"] == set(range(0, 7)) and tenors["747"] == set(range(0, 8))


def test_every_price_row_is_labelled():
    for system, table in (("mpr", "pricedetail"), ("mips", "mips_priceassessment"), ("prodacct", "refinery_daily"),
                          ("ctrm", "deal"), ("mpr", "pricemaster")):
        labels = {r["DemoProvenance"] for r in rows(system, table)}
        assert labels <= set(PROVENANCE), (system, table, labels)


def test_real_rows_are_eia_values():
    wti = public_data.load("wti")
    day = dt.date(2026, 10, 20)
    spot = [r for r in rows("mpr", "pricedetail") if r["PriceMasterId"] == 747 and r["EffectiveStartDate"].date() == day]
    by_period = {r["RelativePeriodNum"]: r for r in spot}
    assert by_period[0]["SettlePrice"] == round(wti[day], 6) == 107.89 and by_period[0]["DemoProvenance"] == "real"
    assert by_period[1]["SettlePrice"] == 107.89 and by_period[1]["DemoProvenance"] == "spot-anchored"
    assert all(by_period[p]["DemoProvenance"] == "synthesized" for p in range(2, 8))


def test_nyh_ulsd_cash_is_real_and_its_basis_spot_anchored():
    groups = {r["ID"]: r for r in rows("mips", "mips_priceassessmentgroup")}
    pgroups = {r["ID"]: r for r in rows("mips", "mips_pricegroup")}
    found = {}
    for r in rows("mips", "mips_priceassessment"):
        g = groups[r["PriceAssessmentGroupID"]]
        if g["Name"] == "NYH ULSD" and r["SortOrder"] == 1 and r["updated_at"].date() == dt.date(2026, 10, 20):
            found[pgroups[g["PriceGroupID"]]["Name"]] = r
    assert found["Cash"]["Value"] == 5.265 and found["Cash"]["DemoProvenance"] == "real"
    assert found["Basis"]["Value"] == 0.0 and found["Basis"]["DemoProvenance"] == "spot-anchored"


def test_refineries_are_mpcs_13_with_their_10k_capacities():
    refineries = rows("prodacct", "refinery")
    assert len(refineries) == 13 and sum(r["CrudeCapacityMbpcd"] for r in refineries) == 2986


def test_the_sql_holds_the_shared_names_and_columns():
    sql = open(os.path.join(ROOT, "sql", "04_gold.sql")).read() + open(os.path.join(ROOT, "sql", "05_metric_views.sql")).read()
    for name in ("gold_commercial_core.mpr_mips_crack_spread_price_fact", "gold_commercial_core.mips_mpr_executive_summary_fact",
                 "semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw",
                 "semantic_sem_commercial.mips_mpr_executive_summary_fact_vw",
                 "semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw"):
        assert name in sql, name
    for field in ("MIPS_Groups_Text", "Price_Master_Name", "Effective_Month", "Relative_Period_Number", "Avg_Crack_Spread",
                  "Spread_Range", "MIPSDisplayName", "Parent_Price_group_name", "SortColumns", "Blend", "Avg_Settle_Price"):
        assert re.search(rf"- name: {field}\b", sql), field
    # The benchmark view's known defect is kept on purpose: every instrument x100, and the 160-day window.
    assert "Settle_Price_Amount * 100 ELSE" in sql and "INTERVAL 160 DAYS" in sql


def test_the_scenario_is_relabelled():
    text = open(os.path.join(ROOT, "SCENARIO.md")).read()
    body = text.split("-->", 1)[1]
    assert "FACT" not in body and "ChatGPT" not in body and body.count("**Scenario") == 30


def test_the_eia_cache_names_each_series():
    with open(os.path.join(ROOT, "data", "public", "eia_series.csv")) as f:
        meta = {r["key"]: r for r in csv.DictReader(f)}
    assert meta["wti"]["series_id"] == "PET.RWTC.D" and meta["nyh_gasoline"]["series_id"] == "PET.EER_EPMRU_PF4_Y35NY_DPG.D"
    assert set(meta) == set(public_data.EIA_SERIES)
