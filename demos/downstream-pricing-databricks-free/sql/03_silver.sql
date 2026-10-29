-- 03_silver.sql: the silver star schema. MDM dimensions in silver_mdm_core, UDM facts in silver_udm_core, with the
-- table and column names of the shared idp_sbx silver layer (EPM-DEC-001-0097, the lineage the decision owner shared).
-- Record_Active_Indicator comes from the source's delete flag; Demo_Provenance_Label carries each row's label
-- (real, spot-anchored, synthesized), a column the shared tables do not have.

CREATE OR REPLACE TABLE ${catalog}.silver_mdm_core.mpr_price_master_dim AS
SELECT CAST(Id AS STRING) AS Price_Master_Id, Name AS Price_Master_Name, DisplayName AS Price_Master_Display_Name,
       ProductId AS Product_Id, PriceTypeId AS Price_Type_Id, FrequencyId AS Frequency_Id, CountryId AS Country_Id,
       AreaStateId AS Area_State_Id, CityId AS City_Id, FacilityId AS Facitlity_Id, PublisherId AS Publisher_Id,
       PublisherCategoryId AS Publisher_Category_Id, PublisherCurrencyId AS Publisher_Currency_Id,
       PublisherUnitOfMeasureId AS Publisher_Unit_Id, MprCurrencyId AS Master_Price_Record_Currency_Id,
       MprUnitOfMeasureId AS Master_Price_Record_Unit_Id, HolidayCalendarId AS Holiday_Calendar_Id,
       ExpirationCalendarId AS Expiration_Calendar_Id, PreviousId AS Previous_Id, NextId AS Price_Next_Id,
       CAST(PriceEffectiveDate AS TIMESTAMP) AS Price_Effective_Datetime, DemoProvenance AS Demo_Provenance_Label,
       'Y' AS Record_Active_Indicator, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_price_reference.pricemaster;

CREATE OR REPLACE TABLE ${catalog}.silver_mdm_core.mips_price_batch_dim AS
SELECT ID AS Price_Batch_Id, EffectiveDate AS Effective_Datetime, Status AS Status_Code, DataSource AS Data_Source_Code,
       'Y' AS Record_Active_Indicator, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_price_assessment.mips_pricebatch;

CREATE OR REPLACE TABLE ${catalog}.silver_mdm_core.mips_price_sheet_dim AS
SELECT s.ID AS Price_Sheet_Id, s.Name AS Price_Sheet_Name, s.PriceBatchID AS Price_Batch_Id, s.Status AS Status_Code,
       c.Code AS Currency_Code, u.Code AS Unit_Of_Measure_Code, 'Y' AS Record_Active_Indicator, s._change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_price_assessment.mips_pricesheet s
LEFT JOIN ${catalog}.replica_price_assessment.mips_currency c ON c.ID = s.CurrencyID
LEFT JOIN ${catalog}.replica_price_assessment.mips_unitofmeasure u ON u.ID = s.UnitOfMeasureID;

CREATE OR REPLACE TABLE ${catalog}.silver_mdm_core.mips_price_group_dim AS
SELECT ID AS Price_Group_Id, ParentPriceGroupID AS Parent_Price_Group_Id, PriceSheetID AS Price_Sheet_Id,
       Name AS Price_Group_Name, LevelNumber AS Level_Number, 'Y' AS Record_Active_Indicator, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_price_assessment.mips_pricegroup;

CREATE OR REPLACE TABLE ${catalog}.silver_mdm_core.mips_price_assessment_group_dim AS
SELECT g.ID AS Price_Assessment_Group_Id, g.PersistentID AS Persistent_Id, CAST(g.PriceMasterID AS STRING) AS Price_Master_Id,
       CAST(g.PriceMasterIDforCycles AS STRING) AS Price_Master_Cycle_Id, CAST(g.ReferenceID AS STRING) AS Reference_Id,
       g.PriceGroupID AS Price_Group_Id, g.PriceSheetID AS Price_Sheet_Id, g.Name AS Price_Assessment_Group_Description,
       g.DataSource AS Data_Source_Code, c.Code AS Currency_Code, u.Code AS Unit_Of_Measure_Code,
       'Y' AS Record_Active_Indicator, g._change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_price_assessment.mips_priceassessmentgroup g
LEFT JOIN ${catalog}.replica_price_assessment.mips_currency c ON c.ID = g.CurrencyID
LEFT JOIN ${catalog}.replica_price_assessment.mips_unitofmeasure u ON u.ID = g.UnitOfMeasureID;

CREATE OR REPLACE TABLE ${catalog}.silver_udm_core.mpr_price_detail_fact AS
SELECT Id AS Price_Detail_Id, CAST(PriceMasterId AS STRING) AS Price_Master_Id, EffectiveStartDate AS Effective_Start_Datetime,
       EffectiveEndDate AS Effective_End_Datetime, RelativePeriodNum AS Relative_Period_Number,
       ContractPeriod AS Contract_Period_Short_Code, ContractPeriodDate AS Contract_Period_Datetime, FlowDate AS Flow_Datetime,
       CycleNum AS Cycle_Number, CAST(SettlePrice AS DECIMAL(18,6)) AS Settle_Price_Amount,
       CAST(HighPrice AS DECIMAL(18,6)) AS High_Price_Amount, CAST(LowPrice AS DECIMAL(18,6)) AS Low_Price_Amount,
       DataSource AS Data_Source_Name, CASE WHEN CDC_DELETED_FLAG = 'Y' THEN 'N' ELSE 'Y' END AS Record_Active_Indicator,
       DemoProvenance AS Demo_Provenance_Label, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_price_reference.pricedetail;

CREATE OR REPLACE TABLE ${catalog}.silver_udm_core.mips_price_assessment_fact AS
SELECT ID AS Price_Assessment_Id, PriceAssessmentGroupID AS Price_Assessment_Group_Id, PriceSheetID AS Price_Sheet_Id,
       PriceBatchID AS Price_Batch_Id, CAST(PricePeriod AS TIMESTAMP) AS Price_Period_Datetime,
       CAST(Value AS DECIMAL(18,6)) AS Assessment_Amount, CAST(PreviousValue AS DECIMAL(18,6)) AS Previous_Amount,
       CycleNum AS Cycle_Number, SortOrder AS Sort_Order, DemoProvenance AS Demo_Provenance_Label,
       'Y' AS Record_Active_Indicator, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_price_assessment.mips_priceassessment;

-- Operations: the refineries, their daily production and plan, and trading deals with their freight.
CREATE OR REPLACE TABLE ${catalog}.silver_mdm_core.refinery_dim AS
SELECT RefineryCode AS Refinery_Code, RefineryName AS Refinery_Name, Region AS Region_Name,
       CrudeCapacityMbpcd AS Crude_Capacity_Mbpcd, 'real' AS Demo_Provenance_Label, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_production_accounting.refinery;

CREATE OR REPLACE TABLE ${catalog}.silver_udm_core.refinery_production_daily_fact AS
SELECT RefineryCode AS Refinery_Code, ProductionDate AS Production_Date, CAST(CrudeRunsMbpd AS DECIMAL(10,1)) AS Crude_Runs_Mbpd,
       CrudeCapacityMbpcd AS Crude_Capacity_Mbpcd, CAST(GasolineYieldPct AS DECIMAL(6,2)) AS Gasoline_Yield_Pct,
       CAST(DistillateYieldPct AS DECIMAL(6,2)) AS Distillate_Yield_Pct, CAST(OtherYieldPct AS DECIMAL(6,2)) AS Other_Yield_Pct,
       CAST(OpexUsdPerBbl AS DECIMAL(8,2)) AS Opex_Usd_Per_Bbl, DemoProvenance AS Demo_Provenance_Label, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_production_accounting.refinery_daily;

CREATE OR REPLACE TABLE ${catalog}.silver_udm_core.refinery_plan_target_fact AS
SELECT RefineryCode AS Refinery_Code, PlanMonth AS Plan_Month, CAST(PlannedCrudeRunsMbpd AS DECIMAL(10,1)) AS Planned_Crude_Runs_Mbpd,
       CAST(PlannedUtilizationPct AS DECIMAL(6,2)) AS Planned_Utilization_Pct, CAST(PlannedGasolineYieldPct AS DECIMAL(6,2)) AS Planned_Gasoline_Yield_Pct,
       CAST(PlannedDistillateYieldPct AS DECIMAL(6,2)) AS Planned_Distillate_Yield_Pct, DemoProvenance AS Demo_Provenance_Label,
       _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_aspen_pims.plan_target;

CREATE OR REPLACE TABLE ${catalog}.silver_udm_core.ctrm_deal_fact AS
SELECT d.DealId AS Deal_Id, d.TradeDate AS Trade_Date, d.Direction AS Direction_Code, d.Product AS Product_Name,
       d.Origin AS Origin_Name, d.Destination AS Destination_Name, d.VolumeBbl AS Volume_Bbl,
       CAST(d.FreightUsdPerBbl AS DECIMAL(8,2)) AS Freight_Usd_Per_Bbl, m.Mode AS Transport_Mode,
       CAST(m.FreightCostUsd AS DECIMAL(14,2)) AS Freight_Cost_Usd, m.LoadDate AS Load_Date,
       d.DemoProvenance AS Demo_Provenance_Label, d._change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_rightangle.deal d JOIN ${catalog}.replica_rightangle.movement m ON m.DealId = d.DealId;

-- Added 2026-10-28 for the three-year extension: process units, product tanker freight, the scenario's event table
-- and EIA's weekly series by PADD. These have no counterpart in the shared idp_sbx layer; the names follow its style.
CREATE OR REPLACE TABLE ${catalog}.silver_udm_core.refinery_unit_daily_fact AS
SELECT RefineryCode AS Refinery_Code, UnitCode AS Unit_Code, UnitName AS Unit_Name, ProductionDate AS Production_Date,
       CAST(UnitThroughputMbpd AS DECIMAL(10,1)) AS Unit_Throughput_Mbpd, CAST(UnitCapacityMbpd AS DECIMAL(10,1)) AS Unit_Capacity_Mbpd,
       DemoProvenance AS Demo_Provenance_Label, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_production_accounting.unit_daily;

CREATE OR REPLACE TABLE ${catalog}.silver_udm_core.freight_rate_fact AS
SELECT RouteCode AS Route_Code, RouteName AS Route_Name, VesselClass AS Vessel_Class, RateDate AS Rate_Date,
       CAST(RateUsdPerBbl AS DECIMAL(8,2)) AS Rate_Usd_Per_Bbl, DemoProvenance AS Demo_Provenance_Label,
       _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_rightangle.freight_rate;

CREATE OR REPLACE TABLE ${catalog}.silver_mdm_core.market_event_dim AS
SELECT EventId AS Event_Id, EventKey AS Event_Key, Title AS Event_Title, Category AS Event_Category, Region AS Region_Name,
       RefineryCode AS Refinery_Code, StartDate AS Event_Start_Date, EndDate AS Event_End_Date, Source AS Source_Text,
       SourceKind AS Source_Kind, EvidenceStatus AS Evidence_Status, EvidenceProbability AS Evidence_Probability,
       EvidenceCitations AS Evidence_Citations, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_reference_data_hub.market_event;

CREATE OR REPLACE TABLE ${catalog}.silver_mdm_core.eia_weekly_series_dim AS
SELECT SeriesKey AS Series_Key, SeriesId AS Series_Id, Measure AS Measure_Name, Area AS Area_Name, Description AS Series_Description,
       Units AS Unit_Code, PulledOn AS Pulled_On_Date, DemoProvenance AS Demo_Provenance_Label, _change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_eia_weekly.series;

CREATE OR REPLACE TABLE ${catalog}.silver_udm_core.eia_weekly_fact AS
SELECT v.SeriesKey AS Series_Key, v.SeriesId AS Series_Id, s.Measure AS Measure_Name, s.Area AS Area_Name,
       v.WeekEnding AS Week_Ending_Date, CAST(v.Value AS DECIMAL(14,2)) AS Value_Amount, s.Units AS Unit_Code,
       v.DemoProvenance AS Demo_Provenance_Label, v._change_ts AS Record_Update_Datetime
FROM ${catalog}.replica_eia_weekly.weekly_value v JOIN ${catalog}.replica_eia_weekly.series s ON s.SeriesKey = v.SeriesKey;
