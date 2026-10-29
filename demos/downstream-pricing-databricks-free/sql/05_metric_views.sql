-- 05_metric_views.sql: the three pricing metric views under their shared names, with the same fields, measures, joins
-- and filters as the definitions the decision owner shared (EPM-DEC-001-0097), one view of refinery operations, and,
-- since E3 (EPM-DEC-001-0109, decision 2), a view of the market-price measures and one of process units.
-- The Executive Summary view passes every gold column through, one to one, and each view defines Record_Count.
-- The benchmark view keeps its known defect on purpose: it multiplies all five instruments by 100, which is right only
-- for NYMEX HO and RBOB, and keeps its 160-day window (EPM-DEC-001-0097, Known gaps).
-- Identifiers (E3): each measure's comment starts with the KPI or OPM identifiers it implements (kpi 1.3.0,
-- measure-identifiers.csv), or with "No identifier"; its display name and synonyms carry them too, and the view's
-- comment and its epm_measure_identifiers tag list every identifier its measures carry. The measure names stay the
-- shared ones, which the Genie agents query. Fields: Databricks, "Metric view YAML syntax reference" (comment,
-- display_name, synonyms; YAML 1.1), and "Apply tags to Unity Catalog securable objects" (tags on views).

CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Implements KPI-0001: Crack Spreads Pricing, the published settle of each crack series. Definitions: ontology_definitions.crack_spread_definitions_vw."
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
    comment: "KPI-0001: Crack Spreads Pricing, the average settle in $/bbl. Benchmark crack spreads: the market value of products made from a set ratio of crude, less the crude's price."
    display_name: "KPI-0001 Crack Spreads Pricing"
    synonyms: ["KPI-0001", "crack spread"]
  - name: Max_Crack_Spread
    expr: MAX(Crack_Spread_Price_Amount)
    comment: "KPI-0001: the highest crack-spread settle in the selection."
    display_name: "KPI-0001 Crack Spreads Pricing, highest"
    synonyms: ["KPI-0001"]
  - name: Min_Crack_Spread
    expr: MIN(Crack_Spread_Price_Amount)
    comment: "KPI-0001: the lowest crack-spread settle in the selection."
    display_name: "KPI-0001 Crack Spreads Pricing, lowest"
    synonyms: ["KPI-0001"]
  - name: Spread_Range
    expr: MEASURE(Max_Crack_Spread) - MEASURE(Min_Crack_Spread)
    comment: "KPI-0001: the highest crack-spread settle in the selection less the lowest."
    display_name: "KPI-0001 Crack Spreads Pricing, range"
    synonyms: ["KPI-0001"]
  - name: Record_Count
    expr: COUNT(1)
    comment: "No identifier: the number of rows."
$$;

ALTER VIEW ${catalog}.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw
SET TAGS ('epm_measure_identifiers' = 'KPI-0001');

CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Implements KPI-0001, OPM-0017, OPM-0018, OPM-0019, OPM-0020, OPM-0021: the Executive Summary's assessed prices, each measure by price group. Definitions: ontology_definitions.executive_summary_definitions_vw."
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
    comment: "KPI-0001, OPM-0017, OPM-0018, OPM-0019, OPM-0020, OPM-0021: the assessed price, summed. A row's group says which measure it is: the crack sheets KPI-0001, Gasoline Cash OPM-0017, Diesel Cash OPM-0018, the crude sheets and Benchmark OPM-0019, Basis OPM-0020, Renewables and NGL's OPM-0021. Filter one group and one blend: a sum across groups is not a price."
    display_name: "Assessment amount (KPI-0001, OPM-0017 to OPM-0021 by group)"
    synonyms: ["KPI-0001", "OPM-0017", "OPM-0018", "OPM-0019", "OPM-0020", "OPM-0021", "current price"]
  - name: Previous_amount
    expr: SUM(Previous_amount)
    comment: "KPI-0001, OPM-0017, OPM-0018, OPM-0019, OPM-0020, OPM-0021: the previous assessed price, summed, with the same groups as assessment_amount."
    display_name: "Previous amount (KPI-0001, OPM-0017 to OPM-0021 by group)"
    synonyms: ["KPI-0001", "OPM-0017", "OPM-0018", "OPM-0019", "OPM-0020", "OPM-0021", "previous price"]
  - name: ChangeValue
    expr: SUM(ChangeValue)
    comment: "KPI-0001, OPM-0017, OPM-0018, OPM-0019, OPM-0020, OPM-0021: the assessed price less the previous one, summed, with the same groups as assessment_amount."
    display_name: "Change (KPI-0001, OPM-0017 to OPM-0021 by group)"
    synonyms: ["KPI-0001", "OPM-0017", "OPM-0018", "OPM-0019", "OPM-0020", "OPM-0021", "day-over-day change"]
  - name: Record_Count
    expr: COUNT(1)
    comment: "No identifier: the number of rows."
$$;

ALTER VIEW ${catalog}.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw
SET TAGS ('epm_measure_identifiers' = 'KPI-0001 OPM-0017 OPM-0018 OPM-0019 OPM-0020 OPM-0021');

CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Implements OPM-0019: the five benchmark futures of Crude Market Pricing. Known gap: all five are multiplied by 100, right only for NYMEX HO and RBOB (EPM-DEC-001-0097). Definitions: ontology_definitions.executive_summary_definitions_vw."
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
    comment: "OPM-0019: Crude Market Pricing, the average settle of ICE Brent, NYMEX WTI and the related futures (natural gas, heating oil, RBOB). Every value is multiplied by 100: divide Brent, WTI and natural gas by 100."
    display_name: "OPM-0019 Crude Market Pricing, benchmark futures"
    synonyms: ["OPM-0019", "benchmark price", "settle price"]
  - name: Record_Count
    expr: COUNT(1)
    comment: "No identifier: the number of rows."
$$;

ALTER VIEW ${catalog}.semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw
SET TAGS ('epm_measure_identifiers' = 'OPM-0019');

-- Added for E3: the market-price measures at price-assessment grain, prompt assessments only. The Executive Summary
-- gold table already holds gasoline and distillate cash, basis, crude differentials, the benchmarks, renewables and
-- NGLs, so no series is added. The R&M Margin Indicator (OPM-0026) is not computed: MPC posts it monthly but does
-- not publish its basis (kpi 1.3.0, measure-details.csv), and the demo does not make one up.
CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.pricing_market_margin_metrics_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Implements OPM-0017, OPM-0018, OPM-0019, OPM-0020, OPM-0021: market prices from the MIPS assessments, one row per blend and day, prompt only (SortColumns = 1). OPM-0026 R&M Margin Indicator is not computed: MPC posts it monthly but does not publish its basis. Values are in each blend's unit as stored (Unit_Of_Measure): group by Blend. Definitions: ontology_definitions.pricing_market_margin_definitions_vw."
source: ${catalog}.gold_commercial_core.mips_mpr_executive_summary_fact
joins:
  - name: assessment_group
    source: ${catalog}.silver_mdm_core.mips_price_assessment_group_dim
    on: source.price_assessment_group_id = assessment_group.Price_Assessment_Group_Id
filter: >-
  source.SortColumns = 1
  AND source.Price_Sheet_Name NOT IN ('Crack Spreads', 'Crack Spreads - MPC', 'Crack Spreads - 3rd Party')
dimensions:
  - name: Blend
    expr: source.RowName
  - name: Price_Master_ID
    expr: source.Price_Master_ID
  - name: Price_Group_Name
    expr: source.Price_Group_Name
  - name: Parent_Price_Group_Name
    expr: source.Parent_Price_group_name
  - name: Price_Sheet_Name
    expr: source.Price_Sheet_Name
  - name: Unit_Of_Measure
    expr: assessment_group.Unit_Of_Measure_Code
  - name: Effective_Date
    expr: source.effective_date
  - name: Effective_Month
    expr: DATE_TRUNC('MONTH', source.effective_date)
  - name: Demo_Provenance_Label
    expr: source.Demo_Provenance_Label
measures:
  - name: Gasoline_Market_Price
    expr: AVG(source.assessment_amount) FILTER (WHERE source.Parent_Price_group_name = 'Gasoline' AND source.Price_Group_Name = 'Cash')
    comment: "OPM-0017: Gasoline Market Pricing, benchmark gasoline spot prices at named hubs, in $/gal as published: the Gasoline Cash group, averaged over the selected days."
    display_name: "OPM-0017 Gasoline Market Pricing"
    synonyms: ["OPM-0017", "gasoline price", "gasoline cash"]
  - name: Distillate_Market_Price
    expr: AVG(source.assessment_amount) FILTER (WHERE source.Parent_Price_group_name = 'Diesel' AND source.Price_Group_Name = 'Cash')
    comment: "OPM-0018: Distillate Market Pricing, benchmark distillate and jet spot prices at named hubs, in $/gal as published: the Diesel Cash group, averaged over the selected days."
    display_name: "OPM-0018 Distillate Market Pricing"
    synonyms: ["OPM-0018", "distillate price", "diesel price", "diesel cash"]
  - name: Crude_Market_Price
    expr: AVG(source.assessment_amount) FILTER (WHERE source.Price_Sheet_Name IN ('Crude Reporting Sheet - Domestic Roll', 'Crude Reporting Sheet Calendar Month Roll', 'Benchmark'))
    comment: "OPM-0019: Crude Market Pricing, crude oil benchmark prices and differentials, with related futures (natural gas, heating oil, RBOB), as published: the two crude reporting sheets (differentials in $/bbl) and the Benchmark sheet (futures in $/bbl, $/gal or $/MMbtu), averaged over the selected days. Group by Blend."
    display_name: "OPM-0019 Crude Market Pricing"
    synonyms: ["OPM-0019", "crude price", "crude differential"]
  - name: Price_Comparison
    expr: AVG(source.assessment_amount) FILTER (WHERE source.Price_Group_Name = 'Basis')
    comment: "OPM-0020: Price Comparison, the difference between two market markers (price A less price B): the Basis group, each hub's cash price less New York Harbor's for the same product (NYH CBOB for gasoline, NYH ULSD for distillate), in $/gal. For another pair, subtract one blend's price from the other's."
    display_name: "OPM-0020 Price Comparison"
    synonyms: ["OPM-0020", "basis", "price difference"]
  - name: Additional_Market_Price
    expr: AVG(source.assessment_amount) FILTER (WHERE source.Price_Group_Name IN ('Renewables', 'NGL\'s'))
    comment: "OPM-0021: Additional Market Prices (Renewables, NGLs), renewable feedstocks, renewable fuels and their credits, and NGLs, as published: the Renewables and NGL's groups, averaged over the selected days. Group by Blend."
    display_name: "OPM-0021 Additional Market Prices (Renewables, NGLs)"
    synonyms: ["OPM-0021", "renewables price", "NGL price", "RIN price"]
  - name: Record_Count
    expr: COUNT(1)
    comment: "No identifier: the number of rows."
$$;

ALTER VIEW ${catalog}.semantic_sem_commercial.pricing_market_margin_metrics_vw
SET TAGS ('epm_measure_identifiers' = 'OPM-0017 OPM-0018 OPM-0019 OPM-0020 OPM-0021');

CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.refinery_operations_metrics_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Implements OPM-0002, OPM-0004, OPM-0005, OPM-0024, OPM-0025, OPM-0027: refinery operations, one row per refinery and day. The R&M margin and margin capture are the demo's own formulas, not MPC's. Definitions: ontology_definitions.refinery_operations_definitions_vw."
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
    comment: "No identifier: crude charged, in thousand barrels a day, summed over the selection."
  - name: Crude_Capacity_Mbpcd
    expr: SUM(Crude_Capacity_Mbpcd)
    comment: "No identifier: crude capacity, in thousand barrels a calendar day, summed over the selection."
  - name: Utilization_Pct
    expr: 100 * SUM(Crude_Runs_Mbpd) / SUM(Crude_Capacity_Mbpcd)
    comment: "OPM-0002: Crude Utilization, fresh crude charged to the crude units as a share of crude capacity, in percent. Like MPC, the demo divides by calendar-day capacity."
    display_name: "OPM-0002 Crude Utilization"
    synonyms: ["OPM-0002", "crude utilization", "utilization"]
  - name: Planned_Utilization_Pct
    expr: 100 * SUM(Planned_Crude_Runs_Mbpd) / SUM(Crude_Capacity_Mbpcd)
    comment: "OPM-0002: Crude Utilization as planned, the month's planned crude runs as a share of crude capacity, in percent."
    display_name: "OPM-0002 Crude Utilization, planned"
    synonyms: ["OPM-0002", "planned utilization"]
  - name: Distillate_Yield_Pct
    expr: SUM(Distillate_Yield_Pct * Crude_Runs_Mbpd) / SUM(Crude_Runs_Mbpd)
    comment: "OPM-0004: Distillate Yield, distillate produced (ULSD, kerosene, jet) as a share of crude and feed charged, in percent. The demo weights each day's yield by its crude runs."
    display_name: "OPM-0004 Distillate Yield"
    synonyms: ["OPM-0004", "distillate yield"]
  - name: Gasoline_Yield_Pct
    expr: SUM(Gasoline_Yield_Pct * Crude_Runs_Mbpd) / SUM(Crude_Runs_Mbpd)
    comment: "OPM-0005: Gasoline Yield, gasoline produced (finished and blendstock) as a share of crude and feed charged, in percent. The demo weights each day's yield by its crude runs."
    display_name: "OPM-0005 Gasoline Yield"
    synonyms: ["OPM-0005", "gasoline yield"]
  - name: Rm_Margin_Usd_Per_Bbl
    expr: SUM(Rm_Margin_Usd_Per_Bbl * Crude_Runs_Mbpd) / SUM(Crude_Runs_Mbpd)
    comment: "OPM-0024: R&M Margin per Barrel. MPC's is sales revenue less the cost of refinery inputs and purchased products, per barrel of net refinery throughput. The demo's is its own: the region's benchmark crack scaled by the clean-product yield, less opex (sql/04_gold.sql)."
    display_name: "OPM-0024 R&M Margin per Barrel (demo formula)"
    synonyms: ["OPM-0024", "R&M margin", "refining margin"]
  - name: Margin_Capture_Pct
    expr: 100 * SUM(Rm_Margin_Usd_Per_Bbl * Crude_Runs_Mbpd) / SUM(Benchmark_Crack_Usd_Per_Bbl * Crude_Runs_Mbpd)
    comment: "OPM-0025: Margin Capture, reported R&M margin as a share of the R&M Margin Indicator, in percent. MPC does not publish the indicator's basis, so the demo divides its own R&M margin by the region's benchmark crack."
    display_name: "OPM-0025 Margin Capture (demo formula)"
    synonyms: ["OPM-0025", "margin capture", "capture rate"]
  - name: Opex_Usd_Per_Bbl
    expr: SUM(Opex_Usd_Per_Bbl * Crude_Runs_Mbpd) / SUM(Crude_Runs_Mbpd)
    comment: "OPM-0027: Refining Operating Costs per Barrel, excluding planned turnaround and depreciation and amortization, in $/bbl. The demo weights each day's generated cost by its crude runs."
    display_name: "OPM-0027 Refining Operating Costs per Barrel"
    synonyms: ["OPM-0027", "opex", "operating cost per barrel"]
  - name: Record_Count
    expr: COUNT(1)
    comment: "No identifier: the number of rows."
$$;

ALTER VIEW ${catalog}.semantic_sem_commercial.refinery_operations_metrics_vw
SET TAGS ('epm_measure_identifiers' = 'OPM-0002 OPM-0004 OPM-0005 OPM-0024 OPM-0025 OPM-0027');

-- Added for E3: process units, one row per unit and day, from the unit gold table (its grain is finer than the
-- refinery operations view's). The demo's unit capacity is its generated capacity; it holds no separate constrained
-- capacity.
CREATE OR REPLACE VIEW ${catalog}.semantic_sem_commercial.refinery_unit_operations_metrics_vw
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Implements OPM-0001: process units, one row per unit and day. The demo's unit capacity is its generated capacity, with no separate constrained capacity. Definitions: ontology_definitions.refinery_operations_definitions_vw."
source: ${catalog}.gold_commercial_core.refinery_unit_operations_daily_fact
dimensions:
  - name: Refinery_Name
    expr: Refinery_Name
  - name: Region_Name
    expr: Region_Name
  - name: Unit_Code
    expr: Unit_Code
  - name: Unit_Name
    expr: Unit_Name
  - name: Production_Date
    expr: Production_Date
  - name: Production_Month
    expr: DATE_TRUNC('MONTH', Production_Date)
measures:
  - name: Unit_Throughput_Mbpd
    expr: SUM(Unit_Throughput_Mbpd)
    comment: "No identifier: unit throughput, in thousand barrels a day, summed over the selection."
  - name: Unit_Capacity_Mbpd
    expr: SUM(Unit_Capacity_Mbpd)
    comment: "No identifier: unit capacity, in thousand barrels a day, summed over the selection."
  - name: Unit_Utilization_Pct
    expr: 100 * SUM(Unit_Throughput_Mbpd) / SUM(Unit_Capacity_Mbpd)
    comment: "OPM-0001: Unit Utilization, a process unit's throughput as a share of its capacity, for one refinery, in percent. Group by unit and refinery: over several days it is the capacity-weighted average of the daily shares."
    display_name: "OPM-0001 Unit Utilization"
    synonyms: ["OPM-0001", "unit utilization"]
  - name: Record_Count
    expr: COUNT(1)
    comment: "No identifier: the number of rows."
$$;

ALTER VIEW ${catalog}.semantic_sem_commercial.refinery_unit_operations_metrics_vw
SET TAGS ('epm_measure_identifiers' = 'OPM-0001');
