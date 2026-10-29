-- 04_gold.sql: the gold tables. The two pricing tables follow the shared lineage (EPM-DEC-001-0097, items 9 to 11):
-- the crack spread is the MPR settle price unchanged, restricted to the MIPS crack sheets and their level-1 group;
-- the Executive Summary joins each MIPS assessment to its group, parent group, sheet, batch and price master.

CREATE OR REPLACE TABLE ${catalog}.gold_commercial_core.mpr_mips_crack_spread_price_fact AS
SELECT pg.Price_Group_Name AS MIPS_Groups_Text, pm.Price_Master_Name, pd.Price_Master_Id AS Price_Master_ID,
       pd.Effective_Start_Datetime, pd.Effective_End_Datetime, pd.Relative_Period_Number,
       pd.Settle_Price_Amount AS Crack_Spread_Price_Amount, 'KPI Crack Spread 3-2-1' AS KPI_ID, '17' AS Source_System_Id,
       'Y' AS Record_Active_Indicator, pd.Demo_Provenance_Label, pd.Record_Update_Datetime
FROM ${catalog}.silver_udm_core.mpr_price_detail_fact pd
JOIN ${catalog}.silver_mdm_core.mpr_price_master_dim pm ON pm.Price_Master_Id = pd.Price_Master_Id
JOIN ${catalog}.silver_mdm_core.mips_price_assessment_group_dim ag ON ag.Price_Master_Id = pd.Price_Master_Id
JOIN ${catalog}.silver_mdm_core.mips_price_group_dim pg ON pg.Price_Group_Id = ag.Price_Group_Id AND pg.Level_Number = 1
JOIN ${catalog}.silver_mdm_core.mips_price_sheet_dim ps ON ps.Price_Sheet_Id = ag.Price_Sheet_Id
WHERE pd.Record_Active_Indicator = 'Y'
  AND ps.Price_Sheet_Name IN ('Crack Spreads', 'Crack Spreads - MPC', 'Crack Spreads - 3rd Party');

CREATE OR REPLACE TABLE ${catalog}.gold_commercial_core.mips_mpr_executive_summary_fact AS
SELECT ag.Price_Assessment_Group_Id AS price_assessment_group_id, ag.Persistent_Id AS persistent_id,
       COALESCE(ag.Price_Master_Id, ag.Reference_Id) AS Price_Master_ID, ag.Price_Master_Cycle_Id AS Price_Master_Cycle_ID,
       ag.Price_Assessment_Group_Description AS RowName, ag.Price_Assessment_Group_Description AS MIPSDisplayName,
       pg.Price_Group_Name, parent.Price_Group_Name AS Parent_Price_group_name, ps.Price_Sheet_Name,
       CONCAT(ps.Price_Sheet_Name, ' - ', ag.Price_Assessment_Group_Description) AS Sheet_displayname,
       pb.Effective_Datetime AS effective_datetime, CAST(pb.Effective_Datetime AS DATE) AS effective_date,
       pb.Status_Code AS Status_code, ag.Data_Source_Code AS Data_Source_code,
       pm.Price_Master_Display_Name AS price_master_Display_Name, pm.Price_Master_Display_Name AS PriceMasterName,
       f.Assessment_Amount AS assessment_amount, f.Previous_Amount AS Previous_amount,
       f.Assessment_Amount - f.Previous_Amount AS ChangeValue, f.Price_Period_Datetime,
       f.Cycle_Number AS CycleNumber, f.Cycle_Number > 0 AS IsCycle, f.Sort_Order AS SortColumns,
       f.Demo_Provenance_Label
FROM ${catalog}.silver_udm_core.mips_price_assessment_fact f
JOIN ${catalog}.silver_mdm_core.mips_price_assessment_group_dim ag ON ag.Price_Assessment_Group_Id = f.Price_Assessment_Group_Id
JOIN ${catalog}.silver_mdm_core.mips_price_group_dim pg ON pg.Price_Group_Id = ag.Price_Group_Id
LEFT JOIN ${catalog}.silver_mdm_core.mips_price_group_dim parent ON parent.Price_Group_Id = pg.Parent_Price_Group_Id
JOIN ${catalog}.silver_mdm_core.mips_price_sheet_dim ps ON ps.Price_Sheet_Id = ag.Price_Sheet_Id
JOIN ${catalog}.silver_mdm_core.mips_price_batch_dim pb ON pb.Price_Batch_Id = f.Price_Batch_Id
LEFT JOIN ${catalog}.silver_mdm_core.mpr_price_master_dim pm ON pm.Price_Master_Id = COALESCE(ag.Price_Master_Id, ag.Reference_Id);

-- Refinery operations: the measures kpi already holds (utilization, yields, R&M margin per barrel, margin capture,
-- costs) for the demo, computed here from the generated production accounting and the region's published crack.
-- The demo's formulas are not the ontology's definitions; each measure's definition lives in the kpi module.
CREATE OR REPLACE TABLE ${catalog}.gold_commercial_core.refinery_operations_daily_fact AS
WITH crack AS (
  SELECT CAST(Effective_Start_Datetime AS DATE) AS Price_Date, Price_Master_ID, Crack_Spread_Price_Amount
  FROM ${catalog}.gold_commercial_core.mpr_mips_crack_spread_price_fact WHERE Relative_Period_Number = 0
)
SELECT p.Refinery_Code, r.Refinery_Name, r.Region_Name, p.Production_Date, p.Crude_Runs_Mbpd, p.Crude_Capacity_Mbpcd,
       ROUND(100 * p.Crude_Runs_Mbpd / p.Crude_Capacity_Mbpcd, 2) AS Utilization_Pct,
       p.Gasoline_Yield_Pct, p.Distillate_Yield_Pct, p.Other_Yield_Pct, p.Opex_Usd_Per_Bbl,
       t.Planned_Crude_Runs_Mbpd, t.Planned_Utilization_Pct,
       c.Price_Master_ID AS Benchmark_Crack_Price_Master_ID, c.Crack_Spread_Price_Amount AS Benchmark_Crack_Usd_Per_Bbl,
       ROUND(c.Crack_Spread_Price_Amount * (p.Gasoline_Yield_Pct + p.Distillate_Yield_Pct) / 81.5 - p.Opex_Usd_Per_Bbl, 2)
         AS Rm_Margin_Usd_Per_Bbl,
       p.Demo_Provenance_Label
FROM ${catalog}.silver_udm_core.refinery_production_daily_fact p
JOIN ${catalog}.silver_mdm_core.refinery_dim r ON r.Refinery_Code = p.Refinery_Code
LEFT JOIN ${catalog}.silver_udm_core.refinery_plan_target_fact t
  ON t.Refinery_Code = p.Refinery_Code AND t.Plan_Month = DATE_TRUNC('MONTH', p.Production_Date)
LEFT JOIN crack c ON c.Price_Date = p.Production_Date
  AND c.Price_Master_ID = CASE r.Region_Name WHEN 'Gulf Coast' THEN '43870' WHEN 'West Coast' THEN '36855' ELSE '37438' END;

-- Process units (added 2026-10-28): each unit's throughput against its capacity, by refinery and day. Its grain is
-- unit-day, finer than the refinery operations view's refinery-day, so it gets its own gold table.
CREATE OR REPLACE TABLE ${catalog}.gold_commercial_core.refinery_unit_operations_daily_fact AS
SELECT u.Refinery_Code, r.Refinery_Name, r.Region_Name, u.Unit_Code, u.Unit_Name, u.Production_Date,
       u.Unit_Throughput_Mbpd, u.Unit_Capacity_Mbpd,
       ROUND(100 * u.Unit_Throughput_Mbpd / u.Unit_Capacity_Mbpd, 2) AS Unit_Utilization_Pct, u.Demo_Provenance_Label
FROM ${catalog}.silver_udm_core.refinery_unit_daily_fact u
JOIN ${catalog}.silver_mdm_core.refinery_dim r ON r.Refinery_Code = u.Refinery_Code;
