"""The acceptance tests of the README's 21 use cases (E7; README, "Use cases").

    uv run --group graph python -m pricing_demo.acceptance expected        # compute every check's figures; ask nothing
    uv run --group graph python -m pricing_demo.acceptance run [N ...]     # ask each question and judge the answer

A use case passes when the orchestrator (supervisor.py) calls the agents its row names, its answer holds every figure
a SQL check computes from the stores (within the rounding a reader would use), and the answer uses what the row's
"Where the ontology matters" column names: identifiers, definitions or labels. Use case 1 has no agent: its question
is answered by a walk through the technical graph, and the check compares the walk with Unity Catalog's observed
lineage. Use case 14 compares the answer with the hidden decision dossiers in decision_truth, which only the tests
read. `run` writes every answer, check and verdict to out/acceptance/results.json; the runs the README records are
kept in data/acceptance/.
"""
import datetime as dt
import json
import os
import re
import sys
from collections import namedtuple

from .config import OUT, source_dsn

# A figure the answer must hold: a number within tol, a string, or a tuple of strings any one of which will do.
Expect = namedtuple("Expect", "label value tol")
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
        out += [Expect(f"{name} below plan", name, None), Expect(f"{name} utilization", float(r["u"]), PCT),
                Expect(f"{name} planned", float(r["p"]), PCT)]
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


def c14(ctx):
    """The decision with the widest miss, from the hidden dossiers: the one whose actual outcome exceeds its expected
    bound by the largest multiple (D04's lost margin against its $25 million bound)."""
    rows = ctx.pg("SELECT \"DecisionId\" AS id, \"ActualOutcomeData\" AS data FROM decision_dossier "
                  "WHERE \"DecisionTime\" >= '2026-01-01' ORDER BY 1")
    lost = {r["id"]: json.loads(r["data"]).get("lost_margin_usd_million") for r in rows}
    worst = max((k for k, v in lost.items() if v), key=lambda k: lost[k] / 25.0)
    owners = ctx.q(f"SELECT Owner_Role_Slugs AS o FROM {{c}}.silver_mdm_core.decision_dim WHERE Decision_Id = '{worst}'")[0]["o"]
    role = owners.split(";")[0].replace("-", " ")
    return [Expect("decision", worst, None), Expect("owner role", role, None),
            Expect("actual lost margin, $ million", lost[worst], 0.05 * lost[worst])]


def c15(ctx):
    lows = storm_lows(ctx)
    return ([Expect("decision D01", "D01", None), Expect("decision D02", "D02", None)]
            + [Expect(f"{name} lowest utilization in the storm", low, PCT) for name, (low, _) in lows.items()])


def c16(ctx):
    rows = ctx.q(f"SELECT Refinery_Code, Planned_Distillate_Yield_Pct AS p, Actual_Distillate_Yield_Pct AS a FROM {BACKCAST} "
                 "WHERE Plan_Month = '2026-10-01'")
    beat = sum(float(r["a"]) > float(r["p"]) for r in rows)
    return [Expect("refineries above their planned distillate yield", float(beat), 0.0),
            Expect("refineries in October's plans", float(len(rows)), 0.0)]


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
    {"n": 9, "agents": [REFINERY], "check": c09,
     "question": "Which refineries did Hurricane Isaias (2026-10-07 to 2026-10-15) hit, how far did their crude utilization fall, when did they recover, and which measures moved?",
     "ontology": [["OPM-0002", "Crude Utilization"], ["OPM-0024", "OPM-0025"]]},
    {"n": 10, "agents": [REFINERY, CRACK], "check": c10,
     "question": "How much margin did the autumn 2026 turnarounds at Robinson and Anacortes cost, valuing each day's crude runs below the refinery's average over the four weeks before its turnaround at the region's benchmark crack?",
     "ontology": [["OPM-0030", "Turnaround Lost Margin", "lost margin"]]},
    {"n": 11, "agents": [EXEC, CRACK, REFINERY], "check": c11,
     "question": "After the U.S. dyed-diesel order (2026-10-05) and China's expected export restart (2026-10-08), how did the NYH ULSD cash price, the USGC 3-2-1 MEH crack and PADD 1 East Coast distillate stocks move from 2026-10-02 (the week before the order) to the latest data?",
     "ontology": [["ULSD"], ["distillate"]]},
    {"n": 12, "agents": [CRACK, REFINERY], "check": c12,
     "question": "With distillate prices strong against gasoline in October 2026, did the 13 refineries shift yield toward distillate against the third quarter of 2026, and what did their R&M margin per barrel do?",
     "ontology": [["OPM-0004", "Distillate Yield"], ["OPM-0024", "R&M Margin per Barrel"]]},
    {"n": 13, "agents": [REFINERY], "check": c13,
     "question": "For Garyville's September 2026 plan, what benchmark crack and crude utilization did the plan assume, what happened, and how much of the gap came from the market and how much from operations?",
     "ontology": [["backcast", "Regional Backcasting"]]},
    {"n": 14, "agents": [REFINERY], "check": c14,
     "question": "Which decision in 2026 missed its expected outcome by the widest margin, which role made it, and what did it actually cost?",
     "ontology": [["planner", "director", "role"]]},
    {"n": 15, "agents": [REFINERY, CRACK], "check": c15,
     "question": "When we cut runs at Garyville and Galveston Bay for Hurricane Isaias (decisions D01 and D02), how low did utilization go, and did cutting beat running through at the cracks that actually prevailed?",
     "ontology": [["OPM-0002", "OPM-0024"]]},
    {"n": 16, "agents": [REFINERY], "check": c16,
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


def holds(answer, e):
    """Whether the answer holds one expected figure."""
    if isinstance(e.value, tuple):
        return any(alt.lower() in answer.lower() for alt in e.value)
    if isinstance(e.value, str):
        return e.value.lower() in answer.lower()
    target, found = abs(e.value), [abs(n) for n in numbers(answer)]
    if any(abs(n - target) <= e.tol + 1e-9 for n in found):
        return True
    if target <= 1.5:  # a probability may be given as a percentage
        return any(abs(n - 100 * target) <= 100 * e.tol + 1e-9 for n in found)
    if target >= 1e5:  # dollars may be given in millions
        return any(abs(n * 1e6 - target) <= e.tol for n in found)
    return False


def judge(case, expected, run):
    """The verdict on one use case: which agents were missed, which figures and which ontology terms are missing."""
    answer = run.get("answer") or ""
    reasons = []
    if run.get("error"):
        reasons.append(f"error: {run['error']}")
    called = {c["agent"] for c in run.get("agents_called", [])}
    missed = [a for a in case["agents"] if a not in called]
    if missed:
        reasons.append("agents not called: " + ", ".join(missed))
    if not expected:
        reasons.append("the check found nothing to compare")
    for e in expected:
        if not holds(answer, e):
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


GRAPH_WALK = """MATCH (db:Tech:SourceDatabase {name: 'price_reference'})<-[:COPIES]-(:Tech)<-[:READS_FROM*1..6]-(v:Tech:MetricView)
OPTIONAL MATCH (v)-[:IMPLEMENTS]->(m:Resource)
OPTIONAL MATCH (m)-[:kpi__usedBy]->(role:Resource)
OPTIONAL MATCH (a:Tech:GenieAgent)-[:BINDS]->(v)
RETURN v.name AS view, collect(DISTINCT m.dcterms__identifier) AS identifiers,
       collect(DISTINCT role.skos__prefLabel) AS roles, collect(DISTINCT a.name) AS agents ORDER BY view"""


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


def run_cases(numbers_wanted=None):
    from .databricks import connect, current_catalog
    from . import supervisor
    w, described = supervisor.client()
    ids = supervisor.spaces(w)
    conn, e = connect()
    results = []
    with conn, conn.cursor() as cur:
        ctx = Context(cur, current_catalog(cur, e))
        for case in CASES:
            if numbers_wanted and case["n"] not in numbers_wanted:
                continue
            expected = case["check"](ctx)
            try:
                run = graph_answer() if case.get("mode") == "graph" else supervisor.orchestrate(w, described, ids, case["question"])
            except (Exception, SystemExit) as err:  # a failed run is a failed case, recorded with its reason
                run = {"agents_called": [], "answer": "", "error": f"{type(err).__name__}: {str(err)[:300]}"}
            verdict = judge(case, expected, run)
            results.append({"n": case["n"], "question": case["question"], "mode": case.get("mode", "orchestrator"),
                            "agents_required": case["agents"],
                            "agents_called": [{k: c[k] for k in ("agent", "question", "status")} for c in run["agents_called"]],
                            "definitions_read": definitions_read(run), "answer": run["answer"], "error": run.get("error"),
                            "expected": [{"label": x.label, "value": x.value, "tol": x.tol} for x in expected], **verdict})
            print(f"use case {case['n']}: {'pass' if verdict['passed'] else 'fail'}"
                  + ("" if verdict["passed"] else " - " + "; ".join(verdict["reasons"])), flush=True)
    return results


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
        wanted = {int(a) for a in argv[1:]}
        results = run_cases(wanted)
        os.makedirs(os.path.dirname(RESULTS), exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        with open(RESULTS, "w") as f:
            json.dump({"run_at": stamp, "results": results}, f, indent=2, default=str)
        passed = sum(r["passed"] for r in results)
        print(f"{passed} of {len(results)} passed; results in {RESULTS}")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
