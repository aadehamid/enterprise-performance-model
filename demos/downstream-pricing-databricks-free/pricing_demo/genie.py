"""Create or update the two Genie agents, bound to the metric views, from the instructions in genie/.

    uv run python -m pricing_demo.genie

An agent with the same title is updated in place, so a rerun does not make a second one. The SQL warehouse is the
one in DATABRICKS_HTTP_PATH.
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


AGENTS = {
    "Crack Spread Price Analytics": {
        "file": "crack-spread-price-analytics.md",
        "description": "Published crack-spread series in $/bbl, including the 3-2-1 crack spread (KPI-0001). Synthetic demo data.",
        "tables": [("semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw",
                    "Crack-spread metric view: 127 series in 44 MIPS groups, daily settles with forward periods 0 to 5.")],
        "questions": ["What is the latest published Chicago WTI 3-2-1 crack, ex-RIN?",
                      "What is the monthly average crack spread for each MIPS group?",
                      "What does the forward curve look like for the USGC 3-2-1 MEH crack?"],
        "examples": [("What is the latest published Chicago WTI 3-2-1 crack, ex-RIN?",
                      "SELECT Price_Master_ID, Price_Master_Name, Relative_Period_Number, MEASURE(Avg_Crack_Spread) AS crack_usd_per_bbl "
                      "FROM {c}.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw "
                      "WHERE Price_Master_ID = '37438' AND Relative_Period_Number = 0 AND Effective_Start_Datetime = "
                      + latest("mpr_mips_crack_spread_price_fact_metrics_vw", "Effective_Start_Datetime") + " GROUP BY ALL")],
    },
    "Executive Summary KPIs Analytics": {
        "file": "executive-summary-kpis-analytics.md",
        "description": "Executive Summary pricing groups: current, previous, change and forward monthly averages. Synthetic demo data.",
        "tables": [("semantic_sem_commercial.mips_mpr_executive_summary_fact_vw", "Executive Summary metric view: MIPS assessments by sheet, group and blend."),
                   ("semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw", "Benchmark metric view: five instruments, last 160 days, all scaled x100 (known defect).")],
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
                      + latest("mips_mpr_executive_summary_fact_vw", "effective_date") + " GROUP BY ALL ORDER BY 1")],
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
