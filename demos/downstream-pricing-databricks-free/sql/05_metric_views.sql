-- 05_metric_views.sql: the three pricing metric views under their shared names, with the same fields, measures, joins
-- and filters as the definitions the decision owner shared (EPM-DEC-001-0097), and one view of refinery operations.
-- The Executive Summary view passes every gold column through, one to one, and each view defines Record_Count.
-- The benchmark view keeps its known defect on purpose: it multiplies all five instruments by 100, which is right only
-- for NYMEX HO and RBOB, and keeps its 160-day window (EPM-DEC-001-0097, Known gaps).

CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: ${catalog}.gold_commercial_core.mpr_mips_crack_spread_price_fact
filter: Record_Active_Indicator = 'Y'
dimensions:
  - name: MIPS_Groups_Text
    expr: MIPS_Groups_Text
  - name: Price_Master_Name
    expr: Price_Master_Name
  - name: Price_Master_ID
    expr: Price_Master_ID
  - name: Effective_Start_Datetime
    expr: Effective_Start_Datetime
  - name: Effective_Month
    expr: DATE_TRUNC('MONTH', Effective_Start_Datetime)
  - name: Relative_Period_Number
    expr: Relative_Period_Number
measures:
  - name: Avg_Crack_Spread
    expr: AVG(Crack_Spread_Price_Amount)
  - name: Max_Crack_Spread
    expr: MAX(Crack_Spread_Price_Amount)
  - name: Min_Crack_Spread
    expr: MIN(Crack_Spread_Price_Amount)
  - name: Spread_Range
    expr: MEASURE(Max_Crack_Spread) - MEASURE(Min_Crack_Spread)
  - name: Record_Count
    expr: COUNT(1)
$$;

CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: ${catalog}.gold_commercial_core.mips_mpr_executive_summary_fact
dimensions:
  - name: price_assessment_group_id
    expr: price_assessment_group_id
  - name: persistent_id
    expr: persistent_id
  - name: Price_Master_ID
    expr: Price_Master_ID
  - name: RowName
    expr: RowName
  - name: MIPSDisplayName
    expr: MIPSDisplayName
  - name: Price_Group_Name
    expr: Price_Group_Name
  - name: Parent_Price_group_name
    expr: Parent_Price_group_name
  - name: Price_Sheet_Name
    expr: Price_Sheet_Name
  - name: effective_datetime
    expr: effective_datetime
  - name: effective_date
    expr: effective_date
  - name: price_master_Display_Name
    expr: price_master_Display_Name
  - name: PriceMasterName
    expr: PriceMasterName
  - name: Price_Period_Datetime
    expr: Price_Period_Datetime
  - name: SortColumns
    expr: SortColumns
  - name: Price_Master_Cycle_ID
    expr: Price_Master_Cycle_ID
  - name: Sheet_displayname
    expr: Sheet_displayname
  - name: Status_code
    expr: Status_code
  - name: Data_Source_code
    expr: Data_Source_code
  - name: CycleNumber
    expr: CycleNumber
  - name: IsCycle
    expr: IsCycle
  - name: Demo_Provenance_Label
    expr: Demo_Provenance_Label
measures:
  - name: assessment_amount
    expr: SUM(assessment_amount)
  - name: Previous_amount
    expr: SUM(Previous_amount)
  - name: ChangeValue
    expr: SUM(ChangeValue)
  - name: Record_Count
    expr: COUNT(1)
$$;

CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: ${catalog}.silver_udm_core.mpr_price_detail_fact
joins:
  - name: price_master
    source: ${catalog}.silver_mdm_core.mpr_price_master_dim
    on: source.Price_Master_Id = price_master.Price_Master_Id
filter: >-
  source.Price_Master_Id IN ('747','752','572','750','9471')
  AND source.Effective_Start_Datetime >= CURRENT_DATE() - INTERVAL 160 DAYS
  AND source.Relative_Period_Number <= CASE WHEN source.Price_Master_Id = '572' THEN 6 ELSE 7 END
  AND TRIM(price_master.Price_Master_Display_Name) IN ('ICE BRENT', 'NYMEX HO', 'NYMEX Natural Gas', 'NYMEX RBOB', 'NYMEX WTI (CUSH)')
dimensions:
  - name: Price_Master_ID
    expr: source.Price_Master_Id
  - name: Blend
    expr: TRIM(price_master.Price_Master_Display_Name)
  - name: Price_Master_Name
    expr: price_master.Price_Master_Name
  - name: Effective_Date
    expr: CAST(source.Effective_Start_Datetime AS DATE)
  - name: Effective_Start_Datetime
    expr: source.Effective_Start_Datetime
  - name: Contract_Period_Datetime
    expr: CAST(source.Contract_Period_Datetime AS TIMESTAMP)
  - name: Relative_Period_Number
    expr: source.Relative_Period_Number
  - name: Settle_Price_Amount
    expr: CASE WHEN source.Price_Master_Id IN ('747','752','572','750','9471') THEN source.Settle_Price_Amount * 100 ELSE source.Settle_Price_Amount END
measures:
  - name: Avg_Settle_Price
    expr: AVG(CASE WHEN source.Price_Master_Id IN ('747','752','572','750','9471') THEN source.Settle_Price_Amount * 100 ELSE source.Settle_Price_Amount END)
  - name: Record_Count
    expr: COUNT(1)
$$;

CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.refinery_operations_metrics_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: ${catalog}.gold_commercial_core.refinery_operations_daily_fact
dimensions:
  - name: Refinery_Name
    expr: Refinery_Name
  - name: Region_Name
    expr: Region_Name
  - name: Production_Date
    expr: Production_Date
  - name: Production_Month
    expr: DATE_TRUNC('MONTH', Production_Date)
measures:
  - name: Crude_Runs_Mbpd
    expr: SUM(Crude_Runs_Mbpd)
  - name: Crude_Capacity_Mbpcd
    expr: SUM(Crude_Capacity_Mbpcd)
  - name: Utilization_Pct
    expr: 100 * SUM(Crude_Runs_Mbpd) / SUM(Crude_Capacity_Mbpcd)
  - name: Planned_Utilization_Pct
    expr: 100 * SUM(Planned_Crude_Runs_Mbpd) / SUM(Crude_Capacity_Mbpcd)
  - name: Distillate_Yield_Pct
    expr: SUM(Distillate_Yield_Pct * Crude_Runs_Mbpd) / SUM(Crude_Runs_Mbpd)
  - name: Gasoline_Yield_Pct
    expr: SUM(Gasoline_Yield_Pct * Crude_Runs_Mbpd) / SUM(Crude_Runs_Mbpd)
  - name: Rm_Margin_Usd_Per_Bbl
    expr: SUM(Rm_Margin_Usd_Per_Bbl * Crude_Runs_Mbpd) / SUM(Crude_Runs_Mbpd)
  - name: Margin_Capture_Pct
    expr: 100 * SUM(Rm_Margin_Usd_Per_Bbl * Crude_Runs_Mbpd) / SUM(Benchmark_Crack_Usd_Per_Bbl * Crude_Runs_Mbpd)
  - name: Opex_Usd_Per_Bbl
    expr: SUM(Opex_Usd_Per_Bbl * Crude_Runs_Mbpd) / SUM(Crude_Runs_Mbpd)
  - name: Record_Count
    expr: COUNT(1)
$$;
