-- One database per source system, under the names README.md maps to the real systems.
CREATE DATABASE price_assessment;       -- Market Price Assessment System
CREATE DATABASE price_reference;        -- Price Reference Master
CREATE DATABASE reference_data_hub;     -- Commercial Reference Data Hub
CREATE DATABASE rightangle;             -- RightAngle, the Commodity Trading and Risk Management (CTRM) system
CREATE DATABASE aspen_pims;             -- Aspen PIMS, the refinery planning model
CREATE DATABASE production_accounting;  -- Refinery Production Accounting
CREATE DATABASE eia_weekly;             -- EIA Weekly Petroleum Status Report, by PADD (public data)
CREATE DATABASE decision_truth;         -- the decision dossiers: hidden truth, loaded but never replicated
