"""The acceptance tests of the README's 21 use cases (E7; README, "Use cases").

    uv run --group graph python -m pricing_demo.acceptance expected        # compute every check's figures; ask nothing
    uv run --group graph python -m pricing_demo.acceptance run [N ...]     # ask each question and judge the answer
    uv run --group graph python -m pricing_demo.acceptance run --repeat K [N ...]  # ask each K times; all must pass
    uv run --group graph python -m pricing_demo.acceptance rejudge [--repeat K] FILE ...  # judge a recorded run again
    uv run --group graph python -m pricing_demo.acceptance compare FILE ...  # compare recorded runs, case by case

A use case passes when the orchestrator (supervisor.py) calls the agents its row names, its answer holds every figure
a SQL check computes from the stores (within the rounding a reader would use, each number tied to its own label), and
the answer uses what the row's "Where the ontology matters" column names: identifiers, definitions or labels. Use case
1 has no agent: its question is answered by a walk through the technical graph, and the check compares the walk with
Unity Catalog's observed lineage. Use case 14 compares the answer with the hidden decision dossiers in decision_truth,
which only the tests read, and takes the deciding roles from the decision trail (graph/decision-trail.ttl). `run`
writes every answer, check and verdict to out/acceptance/results.json; the runs the README records, and their
re-judgings, are kept in data/acceptance/.
"""
import datetime as dt
import json
import os
import re
import sys
from collections import namedtuple

from .config import GRAPH_SEP, OUT, ROOT, completed, source_dsn

# A figure the answer must hold: a number within tol, a string, or a tuple of strings any one of which will do. A
# number counts only where the answer ties it to its own label (see holds); cue, when given, is a regex in which {v}
# stands for the number, for a figure the label's words cannot place, as in "4 out of 13".
Expect = namedtuple("Expect", "label value tol cue", defaults=(None,))
RESULTS = os.path.join(OUT, "acceptance", "results.json")

CRACK = "Crack Spread Price Analytics"
EXEC = "Executive Summary KPIs Analytics"
PRICING = "Pricing and Market Margin Analytics"
REFINERY = "Refinery Operations Analytics"

V_CRACK = "{c}.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw"
V_OPS = "{c}.semantic_sem_commercial.refinery_operations_metrics_vw"
V_PRICE = "{c}.semantic_sem_commercial.pricing_market_margin_metrics_vw"
V_EXEC = "{c}.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw"
GOLD_OPS = "{c}.gold_commercial_core.refinery_operations_daily_fact"
BACKCAST = "{c}.gold_commercial_core.refinery_plan_backcast_fact"
EXTERNAL = "{c}.silver_udm_core.external_event_fact"
FORWARD = "{c}.silver_udm_core.forward_scan_fact"
EIA = "{c}.silver_udm_core.eia_weekly_fact"
FREIGHT = "{c}.silver_udm_core.freight_rate_fact"
USGC = "43870"  # the Gulf Coast's benchmark crack, the one the gold margin uses (sql/04_gold.sql)
PCT, USD, GAL = 0.051, 0.0051, 0.0051  # half a unit of the rounding the agents are told: one decimal for
# percentages, two for $/bbl and $/gal


def months(date):
    """The ways an answer may name a month."""
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(str(date)[:10])
    return (d.strftime("%B %Y"), d.strftime("%b %Y"), d.strftime("%Y-%m"))


def crack_by_month(q, month_list):
    rows = q(f"SELECT Effective_Month AS m, MEASURE(Avg_Crack_Spread) AS v FROM {V_CRACK} WHERE Price_Master_ID = '{USGC}' "
             f"AND Relative_Period_Number = 0 AND Effective_Month IN ({', '.join(repr(m) for m in month_list)}) GROUP BY ALL")
    return {str(r["m"])[:10]: float(r["v"]) for r in rows}


def ops_by_month(q, month_list, where, measures):
    cols = ", ".join(f"MEASURE({m}) AS {m}" for m in measures)
    rows = q(f"SELECT Production_Month AS m, {cols} FROM {V_OPS} WHERE {where} "
             f"AND Production_Month IN ({', '.join(repr(m) for m in month_list)}) GROUP BY ALL")
    return {str(r["m"])[:10]: {m: float(r[m]) for m in measures} for r in rows}


# ---- the checks: each returns the figures the answer must hold, computed from the stores ----

def c01(ctx):
    """The metric views downstream of the price reference feed, from Unity Catalog's observed lineage."""
    edges = ctx.q("SELECT DISTINCT source_table_full_name AS s, target_table_full_name AS t FROM system.access.table_lineage "
                  "WHERE source_table_full_name LIKE '{c}.%' AND target_table_full_name LIKE '{c}.%'")
    reached, frontier = set(), {f"{ctx.catalog}.replica_price_reference.pricemaster", f"{ctx.catalog}.replica_price_reference.pricedetail"}
    while frontier:
        reached |= frontier
        frontier = {e["t"] for e in edges if e["s"] in frontier} - reached
    views = sorted(t.split(".", 1)[1] for t in reached if ".semantic_sem_commercial." in t)
    return [Expect(f"metric view {v}", v, None) for v in views]


def c02(ctx):
    ms = ["2026-09-01", "2026-10-01"]
    ops = ops_by_month(ctx.q, ms, "Refinery_Name = 'Garyville, LA'", ["Margin_Capture_Pct"])
    crack = crack_by_month(ctx.q, ms)
    return ([Expect(f"Garyville margin capture {m[:7]}", ops[m]["Margin_Capture_Pct"], PCT) for m in ms]
            + [Expect(f"USGC crack {m[:7]}", crack[m], USD) for m in ms])


def c03(ctx):
    rows = ctx.q(f"SELECT Refinery_Name AS r, Region_Name AS g, MEASURE(Utilization_Pct) AS u, MEASURE(Planned_Utilization_Pct) AS p "
                 f"FROM {V_OPS} WHERE Production_Month = '2026-09-01' GROUP BY ALL")
    below = [r for r in rows if float(r["u"]) < float(r["p"])]
    out = []
    for r in below:
        name = r["r"].split(",")[0]
        cap = ops_by_month(ctx.q, ["2026-08-01", "2026-09-01"], f"Refinery_Name = '{r['r']}'", ["Margin_Capture_Pct"])
        out += [Expect(f"{name} below plan", name, None), Expect(f"{name} actual utilization", float(r["u"]), PCT),
                Expect(f"{name} planned utilization", float(r["p"]), PCT)]
        out += [Expect(f"{name} margin capture {m[:7]}", v["Margin_Capture_Pct"], PCT) for m, v in sorted(cap.items())]
    return out


def c04(ctx):
    rows = ctx.q(f"""SELECT o.m, c.crack, o.margin, o.u, o.d, o.g FROM
        (SELECT Effective_Month AS m, MEASURE(Avg_Crack_Spread) AS crack FROM {V_CRACK}
         WHERE Price_Master_ID = '{USGC}' AND Relative_Period_Number = 0 GROUP BY ALL) c
        JOIN (SELECT Production_Month AS m, MEASURE(Rm_Margin_Usd_Per_Bbl) AS margin, MEASURE(Utilization_Pct) AS u,
              MEASURE(Distillate_Yield_Pct) AS d, MEASURE(Gasoline_Yield_Pct) AS g FROM {V_OPS}
              WHERE Region_Name = 'Gulf Coast' GROUP BY ALL) o ON o.m = c.m
        WHERE o.m BETWEEN '2023-11-01' AND '2026-09-01' ORDER BY c.crack - o.margin DESC LIMIT 1""")
    r = rows[0]
    return [Expect("month", months(r["m"]), None), Expect("crack", float(r["crack"]), USD),
            Expect("R&M margin per barrel", float(r["margin"]), USD), Expect("utilization", float(r["u"]), PCT),
            Expect("distillate yield", float(r["d"]), PCT), Expect("gasoline yield", float(r["g"]), PCT)]


def c05(ctx):
    ms = ["2026-09-01", "2026-10-01"]
    brent = ctx.q(f"SELECT MEASURE(assessment_amount) / MEASURE(Record_Count) AS v FROM {V_EXEC} "
                  "WHERE MIPSDisplayName = 'ICE, BRENT ($-Bbl)' AND SortColumns = 1 AND effective_date >= '2026-10-01' GROUP BY ALL")
    prices = ctx.q(f"SELECT Blend AS b, Effective_Month AS m, MEASURE(Distillate_Market_Price) AS d, MEASURE(Gasoline_Market_Price) AS g "
                   f"FROM {V_PRICE} WHERE Blend IN ('NYH ULSD', 'NYH CBOB') AND Effective_Month IN ('2026-09-01', '2026-10-01') GROUP BY ALL")
    crack = crack_by_month(ctx.q, ms)
    ops = ops_by_month(ctx.q, ms, "Region_Name = 'Gulf Coast'", ["Distillate_Yield_Pct"])
    out = [Expect("Brent October average", float(brent[0]["v"]), USD)]
    for r in prices:
        v = r["d"] if r["b"] == "NYH ULSD" else r["g"]
        out.append(Expect(f"{r['b']} {str(r['m'])[:7]}", float(v), GAL))
    out += [Expect(f"USGC crack {m[:7]}", crack[m], USD) for m in ms]
    out += [Expect(f"Gulf Coast distillate yield {m[:7]}", ops[m]["Distillate_Yield_Pct"], PCT) for m in ms]
    return out


def c06(ctx):
    curve = ctx.q(f"SELECT DATE_TRUNC('MONTH', Price_Period_Datetime) AS m, MEASURE(assessment_amount) / MEASURE(Record_Count) AS v "
                  f"FROM {V_EXEC} WHERE Price_Group_Name = 'Cash' AND Parent_Price_group_name = 'Diesel' AND MIPSDisplayName = 'NYH ULSD' "
                  "AND effective_date = '2026-10-20' GROUP BY ALL ORDER BY 1 LIMIT 3")
    yld = ctx.q(f"SELECT MEASURE(Distillate_Yield_Pct) AS d FROM {V_OPS} WHERE Region_Name = 'Gulf Coast' "
                "AND Production_Date BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY ALL")
    return ([Expect(f"NYH ULSD forward {str(r['m'])[:7]}", float(r["v"]), GAL) for r in curve]
            + [Expect("Gulf Coast distillate yield, Q3 2026", float(yld[0]["d"]), PCT)])


def c07(ctx):
    rows = ctx.q(f"""WITH s AS (SELECT Area_Name, Week_Ending_Date, Value_Amount FROM {EIA}
                       WHERE Measure_Name = 'distillate_stocks' AND Area_Name LIKE 'PADD%'),
                     latest AS (SELECT Area_Name, Week_Ending_Date AS w, Value_Amount AS v FROM s
                                WHERE Week_Ending_Date = (SELECT MAX(Week_Ending_Date) FROM s))
                SELECT l.Area_Name, l.v, AVG(s.Value_Amount) AS avg5 FROM latest l JOIN s ON s.Area_Name = l.Area_Name
                  AND WEEKOFYEAR(s.Week_Ending_Date) = WEEKOFYEAR(l.w) AND YEAR(s.Week_Ending_Date) BETWEEN YEAR(l.w) - 5 AND YEAR(l.w) - 1
                GROUP BY l.Area_Name, l.v ORDER BY 1""")
    below = [r["Area_Name"] for r in rows if float(r["v"]) < float(r["avg5"])]
    ms = ["2026-09-01", "2026-10-01"]
    runs = ops_by_month(ctx.q, ms, "Region_Name = 'Gulf Coast'", ["Crude_Runs_Mbpd"])
    crack = crack_by_month(ctx.q, ms)
    return ([Expect(f"{a} below its five-year average", " ".join(a.split()[:2]), None) for a in below]
            + [Expect(f"USGC crack {m[:7]}", crack[m], USD) for m in ms]
            + [Expect(f"Gulf Coast crude runs {m[:7]}", round(runs[m]["Crude_Runs_Mbpd"] / trading_days(ctx, m), 1), 1.0)
               for m in ms])


def trading_days(ctx, month):
    rows = ctx.q(f"SELECT COUNT(DISTINCT Production_Date) AS n FROM {GOLD_OPS} WHERE DATE_TRUNC('MONTH', Production_Date) = '{month}'")
    return int(rows[0]["n"])


def c08(ctx):
    day = "2026-10-20"
    ulsd = ctx.q(f"SELECT MEASURE(Distillate_Market_Price) AS v FROM {V_PRICE} WHERE Blend = 'NYH ULSD' AND Effective_Date = '{day}' GROUP BY ALL")
    rates = {r["r"]: float(r["v"]) for r in ctx.q(f"SELECT Route_Code AS r, Rate_Usd_Per_Bbl AS v FROM {FREIGHT} WHERE Rate_Date = '{day}'")}
    crack = ctx.q(f"SELECT MEASURE(Avg_Crack_Spread) AS v FROM {V_CRACK} WHERE Price_Master_ID = '{USGC}' AND Relative_Period_Number = 0 "
                  f"AND Effective_Start_Datetime >= '{day}' GROUP BY ALL")
    margin = ctx.q(f"SELECT MEASURE(Rm_Margin_Usd_Per_Bbl) AS v FROM {V_OPS} WHERE Region_Name = 'Gulf Coast' AND Production_Date = '{day}' GROUP BY ALL")
    nyh = float(ulsd[0]["v"])
    return [Expect("NYH ULSD cash", nyh, GAL), Expect("USGC-NYH freight", rates["USGC-NYH"], USD),
            Expect("USGC-NWE freight", rates["USGC-NWE"], USD),
            Expect("netback to NYH after freight", nyh - rates["USGC-NYH"] / 42, 0.011),
            Expect("USGC crack", float(crack[0]["v"]), USD), Expect("Gulf Coast R&M margin per barrel", float(margin[0]["v"]), USD)]


def storm_lows(ctx):
    rows = ctx.q(f"""SELECT Refinery_Name AS r, MIN(Utilization_Pct) AS low,
                       AVG(CASE WHEN Production_Date < '2026-10-07' THEN Utilization_Pct END) AS pre
                     FROM {GOLD_OPS} WHERE Region_Name = 'Gulf Coast' AND Production_Date BETWEEN '2026-09-30' AND '2026-10-15'
                     GROUP BY 1 ORDER BY 1""")
    return {r["r"].split(",")[0]: (float(r["low"]), float(r["pre"])) for r in rows}


def c09(ctx):
    out = []
    for name, (low, _) in storm_lows(ctx).items():
        out += [Expect(f"{name} hit", name, None), Expect(f"{name} lowest utilization in the storm", low, PCT)]
    return out


def turnaround_lost_margin(ctx):
    """kpi's Turnaround Lost Margin (OPM-0030): the margin of the throughput lost to planned downtime. As the decision
    dossiers compute it (decisions.lost_margin): each day's runs below the refinery's average over the 28 days before
    the turnaround, at the region's benchmark crack, over the turnaround's trading days in the window."""
    rows = ctx.q(f"""WITH e AS (SELECT Refinery_Code, Event_Start_Date AS s, Event_End_Date AS t FROM {{c}}.silver_mdm_core.market_event_dim
                                WHERE Event_Key LIKE 'turnaround_%'),
                     base AS (SELECT f.Refinery_Code, AVG(f.Crude_Runs_Mbpd) AS b FROM {GOLD_OPS} f JOIN e ON e.Refinery_Code = f.Refinery_Code
                              WHERE f.Production_Date BETWEEN DATE_SUB(e.s, 28) AND DATE_SUB(e.s, 1) GROUP BY 1)
                     SELECT f.Refinery_Name AS r, SUM(GREATEST(base.b - f.Crude_Runs_Mbpd, 0) * 1000 * f.Benchmark_Crack_Usd_Per_Bbl) / 1e6 AS usd_m
                     FROM {GOLD_OPS} f JOIN e ON e.Refinery_Code = f.Refinery_Code JOIN base ON base.Refinery_Code = f.Refinery_Code
                     WHERE f.Production_Date BETWEEN e.s AND e.t GROUP BY 1 ORDER BY 1""")
    return {r["r"].split(",")[0]: float(r["usd_m"]) for r in rows}


def c10(ctx):
    return [Expect(f"{name} lost margin, $ million", v, 0.05 * v) for name, v in turnaround_lost_margin(ctx).items()]


def c11(ctx):
    before, after = "2026-10-02", "2026-10-20"
    ulsd = {str(r["d"])[:10]: float(r["v"]) for r in ctx.q(
        f"SELECT Effective_Date AS d, MEASURE(Distillate_Market_Price) AS v FROM {V_PRICE} WHERE Blend = 'NYH ULSD' "
        f"AND Effective_Date IN ('{before}', '{after}') GROUP BY ALL")}
    stocks = {str(r["w"])[:10]: float(r["v"]) for r in ctx.q(
        f"SELECT Week_Ending_Date AS w, Value_Amount AS v FROM {EIA} WHERE Measure_Name = 'distillate_stocks' "
        "AND Area_Name = 'PADD 1 East Coast' AND Week_Ending_Date IN ('2026-10-02', '2026-10-16')")}
    crack = {str(r["d"])[:10]: float(r["v"]) for r in ctx.q(
        f"SELECT CAST(Effective_Start_Datetime AS DATE) AS d, MEASURE(Avg_Crack_Spread) AS v FROM {V_CRACK} WHERE Price_Master_ID = '{USGC}' "
        f"AND Relative_Period_Number = 0 AND CAST(Effective_Start_Datetime AS DATE) IN ('{before}', '{after}') GROUP BY ALL")}
    return ([Expect(f"NYH ULSD {d}", v, GAL) for d, v in sorted(ulsd.items())]
            + [Expect(f"USGC crack {d}", v, USD) for d, v in sorted(crack.items())]
            + [Expect(f"PADD 1 distillate stocks, week to {w}", round(v), 0.6 + 0.0005 * v) for w, v in sorted(stocks.items())])


def c12(ctx):
    q3 = ctx.q(f"SELECT MEASURE(Distillate_Yield_Pct) AS d, MEASURE(Gasoline_Yield_Pct) AS g, MEASURE(Rm_Margin_Usd_Per_Bbl) AS m "
               f"FROM {V_OPS} WHERE Production_Date BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY ALL")[0]
    oct_ = ctx.q(f"SELECT MEASURE(Distillate_Yield_Pct) AS d, MEASURE(Gasoline_Yield_Pct) AS g, MEASURE(Rm_Margin_Usd_Per_Bbl) AS m "
                 f"FROM {V_OPS} WHERE Production_Month = '2026-10-01' GROUP BY ALL")[0]
    out = []
    for label, row in (("Q3 2026", q3), ("October 2026", oct_)):
        out += [Expect(f"distillate yield {label}", float(row["d"]), PCT), Expect(f"gasoline yield {label}", float(row["g"]), PCT),
                Expect(f"R&M margin per barrel {label}", float(row["m"]), USD)]
    return out


def c13(ctx):
    r = ctx.q(f"SELECT * FROM {BACKCAST} WHERE Refinery_Code = 'GV' AND Plan_Month = '2026-09-01'")[0]
    return [Expect("assumed crack", float(r["Assumed_Benchmark_Crack_Usd_Per_Bbl"]), USD),
            Expect("actual crack", float(r["Actual_Benchmark_Crack_Usd_Per_Bbl"]), USD),
            Expect("planned utilization", float(r["Planned_Utilization_Pct"]), PCT),
            Expect("actual utilization", float(r["Actual_Utilization_Pct"]), PCT)]


# Each 2026 decision's expected outcome as a bound on one dossier figure (pricing_demo/decisions.py, "expected"):
# the figure, the bound and whether the outcome had to stay at or above it ("min") or at or below it ("max").
EXPECTED_BOUNDS = {
    "D01": ("lowest_storm_utilization_pct", 48.0, "min"),   # no lower than about 48% during the storm
    "D02": ("lowest_storm_utilization_pct", 73.0, "min"),   # no lower than about 73% during the storm
    "D03": ("trading_days_after_storm", 3.0, "max"),        # back above 90% of pre-storm runs within 3 trading days
    "D04": ("lost_margin_usd_million", 25.0, "max"),        # lost margin under $25 million
    "D05": ("lost_margin_usd_million", 25.0, "max"),
    "D06": ("change_points", 1.5, "min"),                   # distillate yield about 1.5 points higher
    "D07": ("avg_domestic_premium_usd_per_bbl", 1.0, "max"),  # freight premium under $1.00/bbl
    "D08": ("change_usd_per_bbl", -2.0, "max"),             # WTI at least $2.00/bbl lower
    "D09": ("change_cents_per_gal", -5.0, "max"),           # NYH ULSD at least 5 cents/gal lower
}


class NoneRecorded(str):
    """An expected answer that the records hold no such thing: every clause of the answer that names it must deny it."""


def lesson_records(ctx):
    """Every lesson the stores record for a decision: a lesson column in the tables the agents read (the decision log,
    its evidence, the plan backcast), an evidence item whose kind or text names a lesson, and any field of the hidden
    dossiers that does. Each is (source, decision, text)."""
    found = []
    tables = ("decision_dim", "decision_evidence_detail_fact", "refinery_plan_backcast_fact")
    columns = ctx.q("SELECT table_schema AS s, table_name AS t, column_name AS c FROM {c}.information_schema.columns "
                    f"WHERE table_name IN {tables} AND LOWER(column_name) LIKE '%lesson%'")
    for col in columns:
        for r in ctx.q(f"SELECT * FROM {{c}}.{col['s']}.{col['t']} WHERE {col['c']} IS NOT NULL"):
            found.append((f"{col['t']}.{col['c']}", r.get("Decision_Id"), str(r[col["c"]])))
    for r in ctx.q("SELECT Decision_Id AS d, Evidence_Text AS x FROM {c}.gold_commercial_core.decision_evidence_detail_fact "
                   "WHERE LOWER(Evidence_Kind) LIKE '%lesson%' OR LOWER(Evidence_Text) LIKE '%lesson%'"):
        found.append(("decision_evidence_detail_fact", r["d"], r["x"]))
    for r in ctx.pg("SELECT * FROM decision_dossier"):
        for field, value in r.items():
            if "lesson" in field.lower() or "lesson" in str(value).lower():
                found.append((f"decision_dossier.{field}", r["DecisionId"], str(value)))
    return found


def miss(actual, bound, side):
    """How far an outcome fell outside its bound, as a multiple of the bound's size; 0 when the bound was met."""
    gap = bound - actual if side == "min" else actual - bound
    return max(gap, 0.0) / abs(bound)


def trail_roles():
    """Each decision's owner roles, as the decision trail (graph/decision-trail.ttl, PROV-O) associates them."""
    from rdflib import Graph, Namespace
    prov = Namespace("http://www.w3.org/ns/prov#")
    g = Graph().parse(os.path.join(ROOT, "graph", "decision-trail.ttl"))
    roles = {}
    for activity, role in g.subject_objects(prov.wasAssociatedWith):
        roles.setdefault(str(activity).rsplit("/", 1)[-1], set()).add(str(role).rsplit("/", 1)[-1].replace("-", " "))
    return roles


def c14(ctx):
    """The README's use case 14. The gap is each 2026 decision's miss against the bound its expected outcome states
    (EXPECTED_BOUNDS), with the actual figure from the hidden dossiers, which only the tests read; the two widest misses
    are D08 and D04, each several times its bound, far ahead of the rest. The roles come from the decision trail. The
    lesson is whatever the stores record (lesson_records): the answer must give each one, or, when they record none,
    say so without claiming one."""
    rows = ctx.pg("SELECT \"DecisionId\" AS id, \"ActualOutcomeData\" AS data FROM decision_dossier "
                  "WHERE \"DecisionTime\" >= '2026-01-01' ORDER BY 1")
    actual = {r["id"]: json.loads(r["data"]) for r in rows}
    gaps = {d: miss(actual[d][f], b, side) for d, (f, b, side) in EXPECTED_BOUNDS.items()}
    widest = sorted(gaps, key=gaps.get, reverse=True)[:2]
    roles = trail_roles()
    out = []
    for d in widest:
        f, _, _ = EXPECTED_BOUNDS[d]
        out += [Expect(f"decision {d}", d, None), Expect(f"{d} owner role", tuple(sorted(roles[d])), None),
                Expect(f"{d} actual outcome", actual[d][f], 0.05 * abs(actual[d][f]))]
    lessons = [x for x in lesson_records(ctx) if x[1] in widest]
    return out + ([Expect(f"lesson in {src} for {d}", text, None) for src, d, text in lessons]
                  or [Expect("the records hold no lesson", NoneRecorded("lesson"), None)])


def c15(ctx):
    lows = storm_lows(ctx)
    return ([Expect("decision D01", "D01", None), Expect("decision D02", "D02", None)]
            + [Expect(f"{name} lowest utilization in the storm", low, PCT) for name, (low, _) in lows.items()])


BEAT, PLANS = "refineries above their planned distillate yield", "refineries in October's plans"
# A part and its whole share their words ("4 out of 13 refinery plans ran a higher yield"), so each is placed by its
# role in the phrase: the part before "out of"/"of" or next to "higher"/"above", the whole after "of" or before
# "refineries"/"plans".
CUES = {
    BEAT: r"(?<!of )(?<!of \*\*)\b{v}\b(?:\*\*)?\s+(?:out\s+)?of\b|(?<!of )(?<!of \*\*)\b{v}\b[^.;\n]{0,40}\b(?:higher|above|beat|exceed)",
    PLANS: r"\bof\s+(?:\*\*)?{v}\b|\b{v}\b(?:\*\*)?\s+(?:total\s+)?(?:refiner|plan)",
}


def c16(ctx):
    rows = ctx.q(f"SELECT Refinery_Code, Planned_Distillate_Yield_Pct AS p, Actual_Distillate_Yield_Pct AS a FROM {BACKCAST} "
                 "WHERE Plan_Month = '2026-10-01'")
    beat = sum(float(r["a"]) > float(r["p"]) for r in rows)
    return [Expect(BEAT, float(beat), 0.0, CUES[BEAT]), Expect(PLANS, float(len(rows)), 0.0, CUES[PLANS])]


def c17(ctx):
    rows = ctx.q(f"SELECT YEAR(Plan_Month) AS y, AVG(ABS(Crack_Error_Usd_Per_Bbl)) AS c, AVG(ABS(Utilization_Error_Pct)) AS u "
                 f"FROM {BACKCAST} GROUP BY 1 ORDER BY 1")
    out = []
    for r in rows:
        if int(r["y"]) >= 2024:
            out += [Expect(f"mean absolute crack error {r['y']}", float(r["c"]), USD),
                    Expect(f"mean absolute utilization error {r['y']}", float(r["u"]), PCT)]
    return out


def c18(ctx):
    low, _ = storm_lows(ctx)["Galveston Bay"]
    return [Expect("decision D02", "D02", None), Expect("Galveston Bay lowest utilization in the storm", low, PCT)]


def c19(ctx):
    rows = ctx.q(f"SELECT Period_Start_Date AS m FROM {EXTERNAL} WHERE Scan_Step = 'monthly' AND Region_Name = 'Gulf Coast' "
                 "AND Question_Key = 'margin_driver' AND Answer_Value = 'weather' AND YEAR(Period_Start_Date) = 2025 ORDER BY 1")
    avg = ctx.q(f"SELECT MEASURE(Utilization_Pct) AS u, MEASURE(Margin_Capture_Pct) AS c FROM {V_OPS} "
                "WHERE Region_Name = 'Gulf Coast' AND YEAR(Production_Date) = 2025 GROUP BY ALL")[0]
    return ([Expect(f"weather month {str(r['m'])[:7]}", (dt.date.fromisoformat(str(r["m"])[:10]).strftime("%B"),
                                                         dt.date.fromisoformat(str(r["m"])[:10]).strftime("%b"), str(r["m"])[:7]), None) for r in rows]
            + [Expect("Gulf Coast utilization, 2025", float(avg["u"]), PCT),
               Expect("Gulf Coast margin capture, 2025", float(avg["c"]), PCT)])


def c20(ctx):
    rows = {r["k"]: r for r in ctx.q(f"SELECT Question_Key AS k, Answer_Value AS a, Answer_Probability AS p, Evidence_Label AS l "
                                     f"FROM {EXTERNAL} WHERE Scan_Step = 'diagnosis' AND Decision_Id = 'D08'")}
    cause, adverse = rows["outside_cause"], rows["adverse_event"]
    return [Expect("outside factor", cause["a"], None), Expect("its label", cause["l"], None),
            Expect("adverse-event probability", float(adverse["p"]), 0.011), Expect("its label", adverse["l"], None)]


def c21(ctx):
    rows = ctx.q(f"SELECT Period_Start_Date AS m, Question_Key AS k, Matched_Decision_Ids AS d FROM {FORWARD} "
                 "WHERE Matched_Decision_Ids IS NOT NULL AND Matched_Decision_Ids <> '' ORDER BY 1")
    out = []
    for r in rows:
        out += [Expect(f"{r['k']} in {str(r['m'])[:7]}", months(r["m"]), None)]
        out += [Expect(f"matched {d}", d, None) for d in r["d"].split(";")]
    return out + [Expect("label", "inferred", None)]


# Each case's agents are the agents its README row names in "Agents and sources" (Crack Spread, Refinery operations,
# Executive Summary, Pricing and Market Margin); a row that names none needs the agent that binds the tables it names
# (Refinery Operations Analytics for the decision log, the backcast and the outside context, since E7).
CASES = [
    {"n": 1, "mode": "graph", "agents": [], "check": c01,
     "question": "If the price reference feed is late today, which KPIs, metric views and Genie agents are affected, and who uses those measures?",
     "ontology": [["KPI-0001"], ["OPM-0019"], ["Planner"]]},
    {"n": 2, "agents": [REFINERY, CRACK], "check": c02,
     "question": "Did margin capture drop at Garyville in October 2026 against September 2026, and was the crack spread the cause?",
     "ontology": [["OPM-0025", "Margin Capture"], ["demo's own", "demo formula", "the demo's", "synthetic"]]},
    {"n": 3, "agents": [REFINERY, CRACK], "check": c03,
     "question": "Which refineries ran below plan crude utilization in September 2026, did their margin capture fall from August to September 2026, and how did their region's benchmark crack move over the same weeks?",
     "ontology": [["OPM-0002", "Crude Utilization"]]},
    {"n": 4, "agents": [CRACK, REFINERY], "check": c04,
     "question": "Between November 2023 and September 2026, which month had the widest gap between the Gulf Coast benchmark crack (USGC 3-2-1 MEH Crack, ex-RIN, prompt) and the Gulf Coast refineries' R&M margin per barrel, and what were their crude utilization and distillate and gasoline yields that month?",
     "ontology": [["KPI-0001", "market indicator"], ["OPM-0024", "operational metric"]]},
    {"n": 5, "agents": [EXEC, PRICING, CRACK, REFINERY], "check": c05,
     "question": "In October 2026, when ICE Brent front-month averaged above $110/bbl, how did the NYH ULSD and NYH CBOB cash prices and the USGC 3-2-1 MEH crack compare with September 2026, and did the Gulf Coast refineries' distillate yield shift?",
     "ontology": [["OPM-0017", "OPM-0018", "cash"]]},
    {"n": 6, "agents": [EXEC, REFINERY], "check": c06,
     "question": "How does the NYH ULSD cash forward curve on 2026-10-20, for its first three forward months, compare with the distillate yield the Gulf Coast refineries ran in the third quarter of 2026?",
     "ontology": [["OPM-0018", "OPM-0004", "distillate"]]},
    {"n": 7, "agents": [REFINERY, CRACK], "check": c07,
     "question": "In the latest EIA week, which PADDs had distillate stocks below their five-year average for that week, and how did the Gulf Coast refineries' average daily crude runs and the USGC 3-2-1 MEH crack move from September to October 2026?",
     "ontology": [["PADD 3"], ["Gulf Coast"]]},
    {"n": 8, "agents": [PRICING, CRACK, REFINERY], "check": c08,
     "question": "On 2026-10-20, what was the Gulf Coast diesel netback to New York Harbor after freight (NYH ULSD cash less the USGC to New York Harbor tanker rate), what was the USGC to Northwest Europe rate, and how do they compare with the USGC 3-2-1 MEH crack and the Gulf Coast refineries' R&M margin per barrel that day?",
     "ontology": [["synthetic"], ["OPM-0018", "OPM-0024"]]},
    {"n": 9, "agents": [REFINERY, CRACK], "check": c09,
     "question": "Which refineries did Hurricane Isaias (2026-10-07 to 2026-10-15) hit, how far did their crude utilization fall, when did they recover, and which measures moved?",
     "ontology": [["OPM-0002", "Crude Utilization"], ["OPM-0024", "OPM-0025"]]},
    {"n": 10, "agents": [REFINERY, CRACK], "check": c10,
     "question": "How much margin did the autumn 2026 turnarounds at Robinson and Anacortes cost, valuing each day's crude runs below the refinery's average over the four weeks before its turnaround at the region's benchmark crack?",
     "ontology": [["OPM-0030", "Turnaround Lost Margin", "lost margin"]]},
    {"n": 11, "agents": [EXEC, CRACK], "check": c11,
     "question": "After the U.S. dyed-diesel order (2026-10-05) and China's expected export restart (2026-10-08), how did the NYH ULSD cash price, the USGC 3-2-1 MEH crack and PADD 1 East Coast distillate stocks move from 2026-10-02 (the week before the order) to the latest data?",
     "ontology": [["ULSD"], ["distillate"]]},
    {"n": 12, "agents": [CRACK, REFINERY], "check": c12,
     "question": "With distillate prices strong against gasoline in October 2026, did the 13 refineries shift yield toward distillate against the third quarter of 2026, and what did their R&M margin per barrel do?",
     "ontology": [["OPM-0004", "Distillate Yield"], ["OPM-0024", "R&M Margin per Barrel"]]},
    {"n": 13, "agents": [REFINERY, CRACK], "check": c13,
     "question": "For Garyville's September 2026 plan, what benchmark crack and crude utilization did the plan assume, what happened, and how much of the gap came from the market and how much from operations?",
     "ontology": [["backcast", "Regional Backcasting"]]},
    {"n": 14, "agents": [REFINERY], "check": c14,
     "question": "Which decisions this year (2026) had the largest gap between expected and actual outcome, which role made them, and what did the backcast record as the lesson?",
     "ontology": [["planner", "director", "trader", "role"]]},
    {"n": 15, "agents": [REFINERY, CRACK], "check": c15,
     "question": "When we cut runs at Garyville and Galveston Bay for Hurricane Isaias (decisions D01 and D02), how low did utilization go, and did cutting beat running through at the cracks that actually prevailed?",
     "ontology": [["OPM-0002", "OPM-0024"]]},
    {"n": 16, "agents": [REFINERY, CRACK], "check": c16,
     "question": "For October 2026, how many refineries ran a higher distillate yield than their plan version assumed, out of how many plans, and did the October shift toward distillate pay off against the plans' yields?",
     "ontology": [["OPM-0004", "Distillate Yield"]]},
    {"n": 17, "agents": [REFINERY], "check": c17,
     "question": "Is our forecasting improving: what was the mean absolute error between planned and actual benchmark crack, and between planned and actual crude utilization, for the plan months of 2024, 2025 and 2026?",
     "ontology": [["OPM-0002", "Crude Utilization"]]},
    {"n": 18, "agents": [REFINERY, CRACK], "check": c18,
     "question": "Why did we cut runs at Galveston Bay during Hurricane Isaias? Label what the records show, what is inferred and what we cannot know.",
     "ontology": [["observed", "records show"], ["inferred"], ["unknown", "cannot know"], ["OPM-0002", "OPM-0024", "refinery-galveston-bay"]]},
    {"n": 19, "agents": [REFINERY, CRACK], "check": c19,
     "question": "In 2025, in which months did the outside scan name weather as the main driver of Gulf Coast refining margins, with what evidence label, and did the Gulf Coast refineries' crude utilization and margin capture fall below their 2025 averages in those months?",
     "ontology": [["inferred", "observed"]]},
    {"n": 20, "agents": [REFINERY], "check": c20,
     "question": "D08 deferred part of November 2026's crude purchases after the G7 release: did an outside factor bear on how it turned out, or was it the decision? Give the evidence labels.",
     "ontology": [["inferred", "observed"]]},
    {"n": 21, "agents": [REFINERY], "check": c21,
     "question": "Looking three months ahead from October 2026, what is scheduled or forecast that touches a past decision, and what should someone review before planning?",
     "ontology": [["inferred"]]},
]

# ---- judging, offline-testable ----
NUMBER = re.compile(r"([-−])?\$?(\d[\d,]*(?:\.\d+)?)\s*(million|billion|thousand|mm\b|m\b|k\b)?", re.I)
SCALE = {"million": 1e6, "mm": 1e6, "m": 1e6, "billion": 1e9, "thousand": 1e3, "k": 1e3}


def numbers(text):
    out = []
    for sign, digits, scale in NUMBER.findall(text or ""):
        v = float(digits.replace(",", "")) * (-1 if sign else 1)
        out.append(v)
        if scale:
            out.append(v * SCALE[scale.lower()])
    return out


MONTHS = [dt.date(2000, m, 1) for m in range(1, 13)]
# words that name a unit or a statistic rather than a figure: every price is "per barrel", so they place nothing
STOP = {"the", "of", "in", "and", "to", "per", "week", "million", "their", "its", "for", "after", "barrel", "bbl",
        "gal", "gallon", "average", "mean"}
QUARTERS = {"q1": "first quarter", "q2": "second quarter", "q3": "third quarter", "q4": "fourth quarter"}


def label_terms(label):
    """The words an answer may tie a figure to, from its label: each a tuple of spellings, any one of which will do.
    Dates become the ways an answer names them; other words keep their first four letters, so plural and tense vary."""
    terms = []
    for tok in re.findall(r"\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|Q[1-4]|\d{4}|[A-Za-z&']+", label):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", tok):
            d = dt.date.fromisoformat(tok)
            terms.append((tok, f"{d:%B} {d.day}", f"{d:%b} {d.day}", f"{d.month}/{d.day}"))
        elif re.fullmatch(r"\d{4}-\d{2}", tok):
            d = dt.date.fromisoformat(tok + "-01")
            terms.append((tok, f"{d:%B}".lower(), f"{d:%b}".lower()))
        elif tok.lower() in QUARTERS:
            terms.append((tok.lower(), QUARTERS[tok.lower()]))
        elif tok.isdigit():
            terms.append((tok,))
        else:
            w = tok.lower().strip("'")
            month = next((m for m in MONTHS if w in (f"{m:%B}".lower(), f"{m:%b}".lower())), None)
            if month:
                terms.append((f"{month:%B}".lower(), f"{month:%b}".lower()))
            elif w not in STOP and len(w) >= 3:
                terms.append((w[:4],))
    return list(dict.fromkeys(terms))


CLAUSE = re.compile(r"[\n;]|(?<!\d)\.(?!\d)|\.(?=\s)|,(?!\d)"
                    r"|\s(?:and|but|while|whereas|compared\s+(?:to|with)|versus|vs\.?|against)\s", re.I)


def near(e, value):
    """Whether one number in the answer is within the figure's tolerance (a probability may be given as a percentage,
    dollars in millions)."""
    target, v = abs(e.value), abs(value)
    return (abs(v - target) <= e.tol + 1e-9 or (target <= 1.5 and abs(v - 100 * target) <= 100 * e.tol + 1e-9)
            or (target >= 1e5 and abs(v * 1e6 - target) <= e.tol))


# a word that negates; "absent" and "missing" count, so "the lesson was not absent" holds two and fails
NEGATION = re.compile(r"\b(?:no|not|none|never|nor|neither|without|absent|missing|lacks?|lacking)\b|n't\b", re.I)


def shares(term, terms):
    """Whether a term shares a spelling with any of terms ("october" with "2026-10")."""
    return any(set(term) & set(t) for t in terms)


def distance(terms, clause, m):
    """How far the nearest of the terms sits from number match m in the clause, or None; a term after the number
    ("$57.11 in October") binds more closely than one before it."""
    spots = [j.start() for t in terms for alt in t for j in re.finditer(re.escape(alt.lower()), clause.lower())]
    return min((i - m.end() if i >= m.end() else 1.5 * (m.start() - i) for i in spots), default=None)


def holds(answer, e, siblings=()):
    """Whether the answer holds one expected figure. A string or tuple must appear. A number must appear in the same
    clause as a term of its own label (a NoneRecorded value instead needs every clause that names it to hold exactly one negating word, so a double
    negative fails); where a term only another figure's label has (the other month, "actual" against
    "planned") is in the clause too, the number must be nearer to a term only its own label has, so a value stated
    against another figure's label does not count. A figure with a cue must match its cue instead."""
    text = answer or ""
    if isinstance(e.value, NoneRecorded):
        parts = [p for c in CLAUSE.split(text) for p in c.split(":")]  # a colon joins two statements here
        named = [c for c in parts if re.search(rf"\b{e.value}s?\b", c, re.I)]
        return bool(named) and all(len(NEGATION.findall(c)) == 1 for c in named)
    if isinstance(e.value, tuple):
        return any(alt.lower() in text.lower() for alt in e.value)
    if isinstance(e.value, str):
        return e.value.lower() in text.lower()
    if e.cue:
        return any(near(e, float(m.group(1).replace(",", ""))) and re.search(e.cue.replace("{v}", re.escape(m.group(1))), text, re.I)
                   for m in re.finditer(r"(\d[\d,]*(?:\.\d+)?)", text))
    numeric = [o for o in siblings if o is not e and isinstance(o.value, (int, float))]
    mine = label_terms(e.label)
    other_terms = [t for o in numeric for t in label_terms(o.label)]
    theirs = [t for t in other_terms if not shares(t, mine)]
    distinct = [t for t in mine if not shares(t, other_terms)] or mine
    for clause in CLAUSE.split(text):
        for m in NUMBER.finditer(clause):
            if not any(near(e, v) for v in numbers(m.group(0))):
                continue
            other = distance(theirs, clause, m)
            if other is None:  # no other figure's term here: any term of its own label places it
                if distance(mine, clause, m) is not None:
                    return True
            else:  # another figure's term is here too: only the terms that set this label apart decide
                own = distance(distinct, clause, m)
                if own is not None and own <= other:
                    return True
    return False


def judge(case, expected, run):
    """The verdict on one use case: which agents were missed, which figures and which ontology terms are missing."""
    answer = run.get("answer") or ""
    reasons = []
    if run.get("error"):
        reasons.append(f"error: {run['error']}")
    called = {c["agent"] for c in run.get("agents_called", []) if completed(c)}
    missed = [a for a in case["agents"] if a not in called]
    if missed:
        reasons.append("agents not called: " + ", ".join(missed))
    if not expected:
        reasons.append("the check found nothing to compare")
    for e in expected:
        if not holds(answer, e, expected):
            want = e.value if not isinstance(e.value, tuple) else e.value[0]
            reasons.append(f"missing {e.label}: {want}")
    for group in case["ontology"]:
        if not any(term.lower() in answer.lower() for term in group):
            reasons.append("no ontology term: " + " or ".join(group))
    return {"passed": not reasons, "reasons": reasons}


def definitions_read(run):
    """Whether any agent's SQL read an ontology definitions view."""
    return any("ontology_definitions" in (c.get("text") or "") for c in run.get("agents_called", []))


# ---- live: the stores, the graph walk and the orchestrator ----

class Context:
    def __init__(self, cur, catalog):
        self.cur, self.catalog = cur, catalog

    def q(self, sql):
        self.cur.execute(sql.replace("{c}", self.catalog))
        cols = [d[0] for d in self.cur.description]
        return [dict(zip(cols, r)) for r in self.cur.fetchall()]

    def pg(self, sql):
        import psycopg
        with psycopg.connect(f"{source_dsn().rstrip('/')}/decision_truth") as conn, conn.cursor() as cur:
            cur.execute(sql)
            cols = [d.name for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]


GRAPH_WALK = f"""MATCH (db:Tech:SourceDatabase {{name: 'price_reference'}})<-[:COPIES]-(:Tech)<-[:READS_FROM*1..6]-(v:Tech:MetricView)
OPTIONAL MATCH (v)-[:IMPLEMENTS]->(m:Resource)
OPTIONAL MATCH (m)-[:kpi{GRAPH_SEP}usedBy]->(role:Resource)
OPTIONAL MATCH (a:Tech:GenieAgent)-[:BINDS]->(v)
RETURN v.name AS view, collect(DISTINCT m.dcterms{GRAPH_SEP}identifier) AS identifiers,
       collect(DISTINCT role.skos{GRAPH_SEP}prefLabel) AS roles, collect(DISTINCT a.name) AS agents ORDER BY view"""


def graph_answer():
    """Use case 1's answer: the walk through the technical graph, from the price reference database to the metric
    views, the measures they implement with their identifiers, the roles that use them, and the agents that bind them."""
    from neo4j import GraphDatabase
    from .tech_graph import neo4j_login
    uri, user, password = neo4j_login("pipeline")
    with GraphDatabase.driver(uri, auth=(user, password)) as driver, driver.session() as session:
        rows = session.run(GRAPH_WALK).data()
    lines = [f"{r['view']}: measures {', '.join(sorted(r['identifiers']))}; used by {', '.join(sorted(str(x) for x in r['roles']))}; "
             f"agents {', '.join(r['agents'])}" for r in rows]
    return {"agents_called": [], "answer": "\n".join(lines)}


def run_cases(numbers_wanted=None, stamp=None, repeat=1):
    from .databricks import connect, current_catalog
    stamp = stamp or now()
    from . import supervisor
    w, described = supervisor.client()
    ids = supervisor.spaces(w)
    conn, e = connect()
    results = []
    with conn, conn.cursor() as cur:
        ctx = Context(cur, current_catalog(cur, e))
        selected = [c for c in CASES if not numbers_wanted or c["n"] in numbers_wanted]
        for case, attempt in [(c, k) for c in selected for k in range(1, repeat + 1)]:
            try:
                expected = case["check"](ctx)
            except Exception as err:  # a check that cannot run fails its case, and the run goes on (after E7: a
                # dropped tunnel to decision_truth ended a whole run at use case 14)
                expected, run = [], {"agents_called": [], "answer": "",
                                     "error": f"the check failed: {type(err).__name__}: {str(err)[:300]}"}
            else:
                try:
                    run = graph_answer() if case.get("mode") == "graph" else supervisor.orchestrate(w, described, ids, case["question"])
                except (Exception, SystemExit) as err:  # a failed run is a failed case, recorded with its reason and
                    # the agents the orchestrator had already called
                    run = {"agents_called": getattr(err, "agents_called", []), "plan": getattr(err, "plan", None), "answer": "",
                           "error": f"{type(err).__name__}: {str(err)[:300]}"}
            verdict = judge(case, expected, run)
            results.append({"n": case["n"], "attempt": attempt, "question": case["question"], "mode": case.get("mode", "orchestrator"),
                            "agents_required": case["agents"],
                            "agents_called": [{k: c[k] for k in ("agent", "question", "status", "attempts", "errors") if k in c}
                                              for c in run["agents_called"]],
                            "plan": run.get("plan"), "definitions_read": definitions_read(run), "answer": run["answer"],
                            "error": run.get("error"),
                            "expected": [recorded(x) for x in expected], **verdict})
            print(f"use case {case['n']}" + (f" (attempt {attempt} of {repeat})" if repeat > 1 else "")
                  + f": {'pass' if verdict['passed'] else 'fail'}"
                  + ("" if verdict["passed"] else " - " + "; ".join(verdict["reasons"])), flush=True)
            save(results, stamp, repeat)  # after every case, so a run that stops keeps the cases it finished
    return results


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def save(results, stamp, repeat=1):
    """Write a run's results so far to RESULTS, stamped with the time the run started, with the attempts asked per case."""
    os.makedirs(os.path.dirname(RESULTS), exist_ok=True)
    with open(RESULTS, "w") as f:
        json.dump({"run_at": stamp, "repeat": repeat, "results": results}, f, indent=2, default=str)


def recorded(e):
    """One expected figure as a run records it; a NoneRecorded value keeps its kind, so rejudge can restore it."""
    kind = {"kind": "none recorded"} if isinstance(e.value, NoneRecorded) else {}
    return {"label": e.label, "value": e.value, "tol": e.tol, **kind}


# Labels renamed on 2026-10-31 so that both figures of a pair name what sets them apart (#421): "planned utilization"
# had tied 93.2% to the actual figure, whose label was only "Robinson utilization". Rejudge reads a recorded run's
# figures under their current names; a current name matches none of the old ones.
RENAMED = {3: [(r"^(.+?)(?<! actual)(?<! planned) utilization$", r"\1 actual utilization"),
               (r"^(.+) planned$", r"\1 planned utilization")]}


def current_label(n, label):
    """A figure's label as use case n names it now."""
    for old, new in RENAMED.get(n, []):
        label = re.sub(old, new, label)
    return label


def restored(x, n=None):
    """One expected figure as rejudge rebuilds it from a run's record of use case n."""
    value = NoneRecorded(x["value"]) if x.get("kind") == "none recorded" else (
        tuple(x["value"]) if isinstance(x["value"], list) else x["value"])
    label = current_label(n, x["label"])
    return Expect(label, value, x["tol"], CUES.get(label))


def rejudge(path, repeat=None):
    """Judge a recorded run again with the current checks, with no new call: each recorded answer against the figures
    the run recorded, the current agents and ontology terms, and each figure's cue. A case whose question has changed
    since the run fails, since its recorded answer answers another question."""
    run = json.load(open(path))
    if repeat:
        run["repeat"] = repeat
    cases = {c["n"]: c for c in CASES}
    out = []
    for r in run["results"]:
        case = cases[r["n"]]
        if r["question"] != case["question"]:  # the question changed after this run, so the answer is to another one
            verdict = {"passed": False, "reasons": ["the question changed after the run (2026-10-29), so the recorded "
                                                    "answer answers another question"]}
        else:
            verdict = judge(case, [restored(x, r["n"]) for x in r["expected"]], r)
        out.append({**r, "agents_required": list(case["agents"]),  # the agents this verdict required, not the run's
                    "original": {"passed": r["passed"], "reasons": r["reasons"], "agents_required": r.get("agents_required")},
                    **verdict})
    return {"run_at": run["run_at"], "repeat": repeat_of(run), "rejudged_on": dt.date.today().isoformat(), "results": out}


def repeat_of(run):
    """The attempts a run asked per case, as it records them since step 3's review. A run recorded before with no
    attempt numbers asked each case once; one with attempt numbers but no count cannot say how many it asked, so it
    is refused until `rejudge --repeat K` records the count (Codex on step 3)."""
    if run.get("repeat"):
        return run["repeat"]
    if any("attempt" in r for r in run["results"]):
        raise SystemExit("this run recorded attempts but not how many it asked per case: rejudge it with --repeat K")
    return 1


def load(path):
    with open(path) as f:
        run = json.load(f)
    return run["results"], repeat_of(run)


def summary(path):
    return summarize(*load(path))


def by_case(results):
    """Each case's attempts: one on a plain run, K on a run with --repeat K."""
    out = {}
    for r in results:
        out.setdefault(r["n"], []).append(r)
    return out


def summarize(results, repeat=1):
    """One recorded run in figures, each a list of case numbers but calls: the cases passed (a case asked K times passes
    only when all K attempts are recorded and pass: the decision owner, 2026-10-30: "They cannot be giving different
    answers for the same question"), the cases with fewer than K attempts (a run that stopped), the agent calls, and the
    cases where an attempt's SQL read a definitions view or an attempt missed a required agent."""
    cases = by_case(results)
    return {"passed": [n for n, rs in cases.items() if len(rs) >= repeat and all(r["passed"] for r in rs)],
            "incomplete": [n for n, rs in cases.items() if len(rs) < repeat], "cases": len(cases),
            "calls": sum(len(r["agents_called"]) for r in results),
            "definitions_read": sorted({r["n"] for r in results if r.get("definitions_read")}),
            "agent_missed": sorted({r["n"] for r in results if any(x.startswith("agents not called") for x in r["reasons"])}),
            "reasons": {kind: sum(x.startswith(prefix) for r in results for x in r["reasons"])
                        for kind, prefix in (("figures", "missing "), ("terms", "no ontology term"), ("agents", "agents not called"))}}


def cell(attempts, repeat=1):
    """A case's verdict on one run: pass or fail, with the count passed when it was asked more than once, or incomplete
    when the run stopped before all its attempts."""
    passed = sum(r["passed"] for r in attempts)
    if len(attempts) < repeat:
        return f"incomplete ({passed}/{len(attempts)} of {repeat})"
    word = "pass" if passed == len(attempts) else "fail"
    return word if len(attempts) == 1 else f"{word} ({passed}/{len(attempts)})"


def compare(paths):
    """The lines `compare` prints: each run's summary, then each case's verdict on every run."""
    runs = [load(p) for p in paths]
    lines = []
    for p, (run, repeat) in zip(paths, runs):
        s = summarize(run, repeat)
        lines.append(f"{os.path.basename(p)}: {len(s['passed'])} of {s['cases']} passed ({', '.join(map(str, s['passed'])) or 'none'}); "
                     f"{s['calls']} agent calls; definitions read in {len(s['definitions_read'])}; "
                     f"a required agent missed in {len(s['agent_missed'])}"
                     + (f"; incomplete: {', '.join(map(str, s['incomplete']))}" if s["incomplete"] else "")
                     + "; failure reasons: " + ", ".join(f"{v} {k}" for k, v in s["reasons"].items()))
    indexed = [(by_case(run), repeat) for run, repeat in runs]
    for n in sorted({n for run, _ in indexed for n in run}):
        cells = [cell(run[n], repeat) if n in run else "-" for run, repeat in indexed]
        lines.append(f"use case {n}: " + " ".join(cells))
    return lines


def expected_only():
    from .databricks import connect, current_catalog
    conn, e = connect()
    with conn, conn.cursor() as cur:
        ctx = Context(cur, current_catalog(cur, e))
        for case in CASES:
            print(case["n"], [(x.label, x.value) for x in case["check"](ctx)], flush=True)


def main(argv):
    command = argv[0] if argv else "expected"
    if command == "expected":
        expected_only()
    elif command == "run":
        args, repeat = argv[1:], 1
        if "--repeat" in args:
            i = args.index("--repeat")
            repeat = int(args[i + 1])
            del args[i:i + 2]
        wanted = {int(a) for a in args}
        stamp = now()
        results = run_cases(wanted, stamp, repeat)
        save(results, stamp, repeat)  # also when no case matched
        s = summarize(results, repeat)
        print(f"{len(s['passed'])} of {s['cases']} passed" + (f" on all {repeat} attempts" if repeat > 1 else "")
              + f"; results in {RESULTS}")
    elif command == "rejudge":
        args, repeat = argv[1:], None
        if "--repeat" in args:
            i = args.index("--repeat")
            repeat = int(args[i + 1])
            del args[i:i + 2]
        for path in args:
            result = rejudge(path, repeat)
            target = path.replace(".json", "-rejudged.json")
            with open(target, "w") as f:
                json.dump(result, f, indent=2, default=str)
            s = summarize(result["results"], result["repeat"])
            print(f"{path}: {len(s['passed'])} of {s['cases']} pass when re-judged; "
                  + ", ".join(map(str, s["passed"])) + f"; written to {target}")
    elif command == "compare":
        print("\n".join(compare(argv[1:])))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
