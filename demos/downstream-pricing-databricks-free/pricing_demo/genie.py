"""Create or update the four Genie agents, bound to the metric views and their definitions views, from the instructions in
genie/. Since E7 the Refinery Operations agent also binds the refinery-planning tables (PLANNING_TABLES) and the
pricing agent the freight rates (FREIGHT_TABLE).

    uv run python -m pricing_demo.genie

An agent with the same title is updated in place, so a rerun does not make a second one. The SQL warehouse is the
one in DATABRICKS_HTTP_PATH. Each agent also binds its subject area's definitions view (sql/06_definitions.sql), the
ontology's definitions of the measures it answers for (EPM-DEC-001-0109, decision 4).
"""
import hashlib
import json
import os

from .config import ROOT, databricks_env
from .databricks import connect, current_catalog

def latest(view, date_dimension):
    """The latest date a metric view holds, read with MEASURE() and GROUP BY: a metric view refuses a query without a
    measure, and refuses a join (Cursor Bugbot on #380; both forms were run against the workspace on 2026-10-26)."""
    return (f"(SELECT {date_dimension} FROM (SELECT {date_dimension}, MEASURE(Record_Count) AS n "
            f"FROM {{c}}.semantic_sem_commercial.{view} GROUP BY {date_dimension} ORDER BY {date_dimension} DESC LIMIT 1))")


def definitions(view, area):
    """The definitions view an agent binds: plain rows from epm_triples, read without MEASURE()."""
    return (f"ontology_definitions.{view}", f"The ontology's definitions of the {area} measures, read from epm_triples: "
            "identifier, label, definition, grain, basis and the measures not to confuse them with.")


# The refinery-planning tables the use cases ask about (README, "Use cases"; E7, delegated under EPM-DEC-001-0028):
# plain tables, bound to the Refinery Operations agent because each is about the refineries' plans and decisions and
# the events and public data around them. Read with a plain SELECT, not MEASURE().
PLANNING_TABLES = [
    ("gold_commercial_core.refinery_plan_backcast_fact",
     "Each refinery's monthly plan version against what happened: assumed and actual benchmark crack, planned and actual "
     "crude runs, utilization and yields. Synthetic."),
    ("gold_commercial_core.decision_evidence_detail_fact",
     "The decision log's public part with each evidence item: decision, owner roles, refineries, measures, selected "
     "option, expected outcome and evidence text. Synthetic; the actual outcomes are not here."),
    ("silver_mdm_core.market_event_dim",
     "Disruption and policy events: title, category, region, refinery, start and end dates, and the public evidence for each."),
    ("silver_udm_core.eia_weekly_fact",
     "EIA's weekly data by PADD and for the U.S.: distillate and gasoline stocks, refinery utilization, crude runs, product "
     "supplied and exports. Real public data."),
    ("silver_udm_core.external_event_fact",
     "Real outside events from Parallel Decisions: a monthly scan by MPC region and a diagnosis per decision, each answer "
     "labelled observed, inferred or unknown."),
    ("silver_udm_core.forward_scan_fact",
     "A three-month forward look by region: scheduled or forecast events, the past decisions each matches and a suggested "
     "action awaiting a person. Every answer is inferred or unknown."),
]
FREIGHT_TABLE = ("silver_udm_core.freight_rate_fact",
                 "Tanker freight by route and day in $/bbl: USGC to New York Harbor and to Northwest Europe. Synthetic.")

AGENTS = {
    "Crack Spread Price Analytics": {
        "file": "crack-spread-price-analytics.md",
        "description": "Published crack-spread series in $/bbl, including the 3-2-1 crack spread (KPI-0001). Synthetic demo data.",
        "tables": [("semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw",
                    "Crack-spread metric view: 127 series in 44 MIPS groups, daily settles with forward periods 0 to 5."),
                   definitions("crack_spread_definitions_vw", "crack-spread")],
        "questions": ["What is the latest published Chicago WTI 3-2-1 crack, ex-RIN?",
                      "What is the monthly average crack spread for each MIPS group?",
                      "What does the forward curve look like for the USGC 3-2-1 MEH crack?"],
        "examples": [("What is the latest published Chicago WTI 3-2-1 crack, ex-RIN?",
                      "SELECT Price_Master_ID, Price_Master_Name, Relative_Period_Number, MEASURE(Avg_Crack_Spread) AS crack_usd_per_bbl "
                      "FROM {c}.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw "
                      "WHERE Price_Master_ID = '37438' AND Relative_Period_Number = 0 AND Effective_Start_Datetime = "
                      + latest("mpr_mips_crack_spread_price_fact_metrics_vw", "Effective_Start_Datetime") + " GROUP BY ALL"),
                     ("What was the monthly average USGC 3-2-1 MEH crack, ex-RIN, prompt, in each month of 2026?",
                      "SELECT Price_Master_ID, Price_Master_Name, Effective_Month, MEASURE(Avg_Crack_Spread) AS crack_usd_per_bbl "
                      "FROM {c}.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw "
                      "WHERE Price_Master_ID = '43870' AND Relative_Period_Number = 0 AND Effective_Month >= '2026-01-01' "
                      "GROUP BY ALL ORDER BY Effective_Month")],
    },
    "Executive Summary KPIs Analytics": {
        "file": "executive-summary-kpis-analytics.md",
        "description": "Executive Summary pricing groups: current, previous, change and forward monthly averages. Synthetic demo data.",
        "tables": [("semantic_sem_commercial.mips_mpr_executive_summary_fact_vw", "Executive Summary metric view: MIPS assessments by sheet, group and blend."),
                   ("semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw", "Benchmark metric view: five instruments, last 160 days, all scaled x100 (known defect)."),
                   definitions("executive_summary_definitions_vw", "Executive Summary")],
        "questions": ["What is the NYH ULSD cash price today, and how much did it change?",
                      "Show the Gasoline Basis prices for all blends on the latest date.",
                      "What is the ICE Brent front-month settle?"],
        "examples": [("What is the NYH ULSD cash price on the latest date?",
                      "SELECT MIPSDisplayName, MEASURE(assessment_amount) AS price_usd_per_gal, MEASURE(ChangeValue) AS change_usd_per_gal "
                      "FROM {c}.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw WHERE Price_Group_Name = 'Cash' "
                      "AND Parent_Price_group_name = 'Diesel' AND MIPSDisplayName = 'NYH ULSD' AND SortColumns = 1 AND effective_date = "
                      + latest("mips_mpr_executive_summary_fact_vw", "effective_date") + " GROUP BY ALL"),
                     ("What is the ICE Brent front-month settle on the latest date, in $/bbl?",
                      "SELECT Price_Master_ID, Blend, MEASURE(Avg_Settle_Price) / 100 AS settle_usd_per_bbl "
                      "FROM {c}.semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw WHERE Price_Master_ID = '572' "
                      "AND Relative_Period_Number = 1 AND Effective_Date = "
                      + latest("mips_mpr_benchmark_prices_fact_vw", "Effective_Date") + " GROUP BY ALL"),
                     ("What is the monthly average NYH ULSD cash price for each forward month on the latest date?",
                      "SELECT DATE_TRUNC('MONTH', Price_Period_Datetime) AS price_month, "
                      "MEASURE(assessment_amount) / MEASURE(Record_Count) AS avg_price_usd_per_gal "
                      "FROM {c}.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw WHERE Price_Group_Name = 'Cash' "
                      "AND Parent_Price_group_name = 'Diesel' AND MIPSDisplayName = 'NYH ULSD' AND effective_date = "
                      + latest("mips_mpr_executive_summary_fact_vw", "effective_date") + " GROUP BY ALL ORDER BY 1"),
                     ("What were the NGL prices on the latest date, in cents per gallon?",
                      "SELECT MIPSDisplayName, MEASURE(assessment_amount) AS price_cents_per_gal "
                      "FROM {c}.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw WHERE Price_Group_Name = 'NGL\\'s' "
                      "AND SortColumns = 1 AND effective_date = "
                      + latest("mips_mpr_executive_summary_fact_vw", "effective_date") + " GROUP BY ALL")],
    },
    "Pricing and Market Margin Analytics": {
        "file": "pricing-and-market-margin-analytics.md",
        "description": "Gasoline, distillate and crude market prices, price comparisons and renewable and NGL prices (OPM-0017, OPM-0018, OPM-0019, OPM-0020, OPM-0021). Synthetic demo data.",
        "tables": [("semantic_sem_commercial.pricing_market_margin_metrics_vw",
                    "Market-price metric view: prompt MIPS assessments by blend and day, one measure per market-price group."),
                   definitions("pricing_market_margin_definitions_vw", "market-price"), FREIGHT_TABLE],
        "questions": ["What were the Gasoline Cash prices by blend on the latest date?",
                      "How did the Gulf Coast ULSD cash price compare with New York Harbor's last month?",
                      "What is the R&M Margin Indicator, and why does this agent give no value for it?"],
        "examples": [("What were the Gasoline Cash prices by blend on the latest date?",
                      "SELECT Blend, Unit_Of_Measure, MEASURE(Gasoline_Market_Price) AS price "
                      "FROM {c}.semantic_sem_commercial.pricing_market_margin_metrics_vw WHERE Effective_Date = "
                      + latest("pricing_market_margin_metrics_vw", "Effective_Date") + " GROUP BY ALL ORDER BY Blend"),
                     ("How did the Gulf Coast ULSD cash price compare with New York Harbor's on the latest date?",
                      "SELECT Blend, Unit_Of_Measure, MEASURE(Distillate_Market_Price) AS cash_usd_per_gal, "
                      "MEASURE(Price_Comparison) AS basis_to_nyh_usd_per_gal "
                      "FROM {c}.semantic_sem_commercial.pricing_market_margin_metrics_vw WHERE Blend IN ('USGC ULSD', 'NYH ULSD') "
                      "AND Effective_Date = " + latest("pricing_market_margin_metrics_vw", "Effective_Date") + " GROUP BY ALL"),
                     # E7: the freight table, a plain SELECT (added after the first acceptance run)
                     ("What were the two tanker freight rates on the latest date?",
                      "SELECT Route_Code, Route_Name, Rate_Date, Rate_Usd_Per_Bbl, Demo_Provenance_Label FROM {c}.silver_udm_core.freight_rate_fact "
                      "WHERE Rate_Date = (SELECT MAX(Rate_Date) FROM {c}.silver_udm_core.freight_rate_fact) ORDER BY Route_Code")],
    },
    "Refinery Operations Analytics": {
        "file": "refinery-operations-analytics.md",
        "description": "MPC's 13 refineries and their process units: utilization against plan, yields, R&M margin, margin capture and opex (OPM-0001, OPM-0002, OPM-0004, OPM-0005, OPM-0024, OPM-0025, OPM-0027). Synthetic demo data.",
        "tables": [("semantic_sem_commercial.refinery_operations_metrics_vw",
                    "Refinery operations metric view: one row per refinery and day, with planned utilization."),
                   ("semantic_sem_commercial.refinery_unit_operations_metrics_vw",
                    "Process-unit metric view: one row per unit and day, throughput and capacity."),
                   definitions("refinery_operations_definitions_vw", "refinery operations")] + PLANNING_TABLES,
        "questions": ["Which refineries ran below plan utilization in the latest month?",
                      "What were distillate and gasoline yields at the Gulf Coast refineries last quarter?",
                      "What was each process unit's utilization at Garyville in the latest month?"],
        "examples": [("Which refineries ran below plan utilization in the latest month?",
                      "SELECT Refinery_Name, MEASURE(Utilization_Pct) AS utilization_pct, MEASURE(Planned_Utilization_Pct) AS planned_pct "
                      "FROM {c}.semantic_sem_commercial.refinery_operations_metrics_vw WHERE Production_Month = "
                      + latest("refinery_operations_metrics_vw", "Production_Month") + " GROUP BY ALL ORDER BY Refinery_Name"),
                     ("What was each process unit's utilization at Garyville in the latest month?",
                      "SELECT Unit_Code, Unit_Name, MEASURE(Unit_Utilization_Pct) AS unit_utilization_pct "
                      "FROM {c}.semantic_sem_commercial.refinery_unit_operations_metrics_vw WHERE Refinery_Name = 'Garyville, LA' "
                      "AND Production_Month = " + latest("refinery_unit_operations_metrics_vw", "Production_Month")
                      + " GROUP BY ALL ORDER BY Unit_Code"),
                     # E7: one example per refinery-planning table, a plain SELECT (added after the first acceptance run)
                     ("What did each refinery's plan assume for the crack and utilization in the latest plan month, against what happened?",
                      "SELECT Refinery_Code, Plan_Month, Assumed_Benchmark_Crack_Usd_Per_Bbl, Actual_Benchmark_Crack_Usd_Per_Bbl, "
                      "Crack_Error_Usd_Per_Bbl, Planned_Utilization_Pct, Actual_Utilization_Pct, Utilization_Error_Pct "
                      "FROM {c}.gold_commercial_core.refinery_plan_backcast_fact WHERE Plan_Month = "
                      "(SELECT MAX(Plan_Month) FROM {c}.gold_commercial_core.refinery_plan_backcast_fact) ORDER BY Refinery_Code"),
                     ("Which decisions concern Galveston Bay, and what evidence do we hold for each?",
                      "SELECT Decision_Id, Decision_Datetime, Decision_Statement, Owner_Role_Slugs, Measure_Identifiers, Expected_Outcome, "
                      "Evidence_Kind, Evidence_Text FROM {c}.gold_commercial_core.decision_evidence_detail_fact "
                      "WHERE Refinery_Codes LIKE '%GB%' ORDER BY Decision_Datetime, Evidence_Id"),
                     ("What disruption and policy events does the event table hold for the Gulf Coast?",
                      "SELECT Event_Title, Event_Category, Refinery_Code, Event_Start_Date, Event_End_Date FROM {c}.silver_mdm_core.market_event_dim "
                      "WHERE Region_Name = 'Gulf Coast' ORDER BY Event_Start_Date"),
                     ("What were PADD 3's distillate stocks in each of the last four EIA weeks?",
                      "SELECT Week_Ending_Date, Value_Amount, Unit_Code FROM {c}.silver_udm_core.eia_weekly_fact "
                      "WHERE Measure_Name = 'distillate_stocks' AND Area_Name = 'PADD 3 Gulf Coast' ORDER BY Week_Ending_Date DESC LIMIT 4"),
                     ("What did the outside scan find for the West Coast in the latest month, with each answer's label?",
                      "SELECT Period_Start_Date, Question_Key, Answer_Value, Answer_Probability, Answer_Confidence, Evidence_Label "
                      "FROM {c}.silver_udm_core.external_event_fact WHERE Scan_Step = 'monthly' AND Region_Name = 'West Coast' "
                      "AND Period_Start_Date = (SELECT MAX(Period_Start_Date) FROM {c}.silver_udm_core.external_event_fact "
                      "WHERE Scan_Step = 'monthly') ORDER BY Question_Key"),
                     ("What does the forward look expect for the Mid-Continent next month?",
                      "SELECT Period_Start_Date, Question_Key, Answer_Value, Evidence_Label, Matched_Decision_Ids, Suggested_Action "
                      "FROM {c}.silver_udm_core.forward_scan_fact WHERE Region_Name = 'Mid-Continent' AND Period_Start_Date = "
                      "(SELECT MIN(Period_Start_Date) FROM {c}.silver_udm_core.forward_scan_fact) ORDER BY Question_Key")],
    },
}


def hex_id(*parts):
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


def serialized(title, spec, catalog):
    text = open(os.path.join(ROOT, "genie", spec["file"])).read().replace("${catalog}", catalog)
    return json.dumps({
        "version": 2,
        "config": {"sample_questions": sorted(({"id": hex_id(title, "q", q), "question": [q]} for q in spec["questions"]),
                                              key=lambda x: x["id"])},
        "data_sources": {"tables": sorted(({"identifier": f"{catalog}.{t}", "description": [d]} for t, d in spec["tables"]),
                                          key=lambda x: x["identifier"])},
        "instructions": {
            "text_instructions": [{"id": hex_id(title, "text"), "content": [line + "\n" for line in text.splitlines()]}],
            "example_question_sqls": sorted(({"id": hex_id(title, "sql", q), "question": [q], "sql": [s.format(c=catalog)]}
                                             for q, s in spec["examples"]), key=lambda x: x["id"]),
        },
    })


def main():
    from databricks.sdk import WorkspaceClient
    e = databricks_env()
    conn, _ = connect()
    with conn, conn.cursor() as cur:
        catalog = current_catalog(cur, e)
    w = WorkspaceClient(host=e["DATABRICKS_HOST"], token=e["DATABRICKS_TOKEN"])
    warehouse = e["DATABRICKS_HTTP_PATH"].rstrip("/").rsplit("/", 1)[-1]
    existing = {s.title: s.space_id for s in (w.genie.list_spaces().spaces or [])}
    for title, spec in AGENTS.items():
        body = serialized(title, spec, catalog)
        if title in existing:
            w.genie.update_space(existing[title], serialized_space=body, description=spec["description"], title=title, warehouse_id=warehouse)
            print(f"updated Genie agent: {title}")
        else:
            space = w.genie.create_space(warehouse, body, description=spec["description"], title=title)
            print(f"created Genie agent: {title} ({space.space_id})")


if __name__ == "__main__":
    main()
