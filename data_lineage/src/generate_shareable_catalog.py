"""Generate the Lagos Refining & Supply Company (LSC) synthetic lineage catalog.

The catalog follows synthetic/lsc_data_model.json and the size and shape of the production
lineage graph (about 45K nodes, 78K relationships). Every competency question in
synthetic/competency_questions.json has a planted path; manifest.json records its expected answer.

    python src/generate_shareable_catalog.py                      # writes synthetic_data/
    python src/generate_shareable_catalog.py --seed 7 --out D:/x  # another catalog

Output is deterministic for a seed and date. Load it with src/load_synthetic_catalog.py.
"""

import argparse
import hashlib
import json
import random
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from medallion import is_legacy, schema_layer

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "synthetic" / "lsc_data_model.json"
DEFAULT_OUT = ROOT / "synthetic_data"
DEFAULT_SEED = 26

SOURCE_DB_NAME = "source.duckdb"
KNOWN_LINEAGE_GAPS = (
    "sem_masterdata.customer_ship_to_snapshot_vw", "sem_masterdata.blend_recipe_detail_vw",
    "sem_masterdata.exchange_agreement_summary_vw", "sem_wholesale.lifting_forecast_open_vw",
    "sem_wholesale.rack_location_non_secured_vw", "sem_wholesale.supply_agreement_history_vw",
    "sem_wholesale.credit_memo_by_region_vw",
)
IDP = "LSC Data Platform (IDP)"
IDP_SERVER = "lsc-idp-prod.sql.azuresynapse.net"
SANDBOX = "Alteryx Sandbox"
FLAT_FILE = "LSC Commercial Files"


class Catalog:
    """Nodes keyed by label and merge key, role labels, and relationships keyed by pattern."""

    def __init__(self, model: dict):
        self.model = model
        self.key_field = {n["label"]: n["key_property"]["name"] for n in model["nodes"]}
        self.props = {n["label"]: {p["name"] for p in n["properties"]} for n in model["nodes"]}
        self.extra_labels = {n["label"]: set(n.get("metadata", {}).get("extraLabels", [])) for n in model["nodes"]}
        self.patterns = {
            (r["start_node_label"], r["type"], r["end_node_label"]): {p["name"] for p in r.get("properties", [])}
            for r in model["relationships"]
        }
        self.nodes: dict[str, dict] = defaultdict(dict)
        self.labels: dict[tuple[str, str], set] = defaultdict(set)
        self.rels: dict[tuple[str, str, str], dict] = defaultdict(dict)

    def add(self, label: str, key, **props) -> str | tuple:
        unknown = set(props) - self.props[label]
        if unknown:
            raise ValueError(f"{label} has no properties {sorted(unknown)} in the data model")
        self.nodes[label].setdefault(key, {}).update({k: v for k, v in props.items() if v is not None})
        return key

    def tag(self, label: str, extra: str, key) -> None:
        if extra not in self.extra_labels[label]:
            raise ValueError(f"{label} cannot carry :{extra}")
        self.labels[(label, extra)].add(key)

    def link(self, start: str, rel_type: str, end: str, source, target, /, **props) -> None:
        pattern = (start, rel_type, end)
        if pattern not in self.patterns:
            raise ValueError(f"{pattern} is not in the data model")
        unknown = set(props) - self.patterns[pattern]
        if unknown:
            raise ValueError(f"{pattern} has no properties {sorted(unknown)}")
        self.rels[pattern].setdefault((source, target), {}).update({k: v for k, v in props.items() if v is not None})

    def has(self, label: str, key) -> bool:
        return key in self.nodes[label]

    def check_integrity(self) -> None:
        for (label, _), keys in self.labels.items():
            missing = keys - self.nodes[label].keys()
            if missing:
                raise ValueError(f"{len(missing)} :{label} role labels point at no node, e.g. {next(iter(missing))}")
        for (start, rel_type, end), edges in self.rels.items():
            for source, target in edges:
                if source not in self.nodes[start] or target not in self.nodes[end]:
                    raise ValueError(f"({start})-[:{rel_type}]->({end}) {source} -> {target} has a missing endpoint")

    def _node_row(self, label: str, key, props: dict) -> dict:
        if label == "RoleAssignment":
            return {"type": key[0], "scope": key[1], **props}
        return {self.key_field[label]: key, **props}

    @staticmethod
    def _endpoint(row: dict, side: str, label: str, key) -> None:
        if label == "RoleAssignment":
            row[f"{side}Type"], row[f"{side}Id"] = key
        else:
            row[f"{side}Id"] = key

    def write(self, out: Path) -> dict:
        self.check_integrity()
        counts = {"nodes": {}, "labels": {}, "rels": {}}
        for sub in ("nodes", "labels", "rels"):
            (out / sub).mkdir(parents=True, exist_ok=True)
            for old in (out / sub).glob("*.jsonl"):
                old.unlink()
        for label, nodes in sorted(self.nodes.items()):
            rows = [self._node_row(label, key, props) for key, props in nodes.items()]
            _write_jsonl(out / "nodes" / f"{label}.jsonl", rows)
            counts["nodes"][label] = len(rows)
        for (label, extra), keys in sorted(self.labels.items()):
            field = self.key_field[label]
            _write_jsonl(out / "labels" / f"{label}-{extra}.jsonl", [{field: k} for k in sorted(keys)])
            counts["labels"][f"{label}:{extra}"] = len(keys)
        for (start, rel_type, end), edges in sorted(self.rels.items()):
            rows = []
            for (source, target), props in edges.items():
                row = dict(props)
                self._endpoint(row, "source", start, source)
                self._endpoint(row, "target", end, target)
                rows.append(row)
            _write_jsonl(out / "rels" / f"{start}-{rel_type}-{end}.jsonl", rows)
            counts["rels"][f"{start}-{rel_type}-{end}"] = len(rows)
        return counts


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


# --------------------------------------------------------------------------- vocabulary

BUSINESS_AREAS = {
    "Wholesale Marketing": "Rack, branded and unbranded sales of gasoline, diesel and jet; pricing and margin.",
    "Refining & Planning": "Crude slate selection, LP planning, unit yields and refinery economics.",
    "Renewable Fuels": "Renewable diesel, biodiesel and SAF production and feedstock sourcing.",
    "Supply & Trading": "Crude and refined product trading, hedging, exchanges and inventory positions.",
    "Pipelines & Terminals": "Pipeline scheduling, tank farms, truck racks and marine terminals.",
    "Refinery Operations": "Unit operations, maintenance, turnarounds and utilities.",
    "Product Quality & Lab": "Laboratory testing, product certification and off-spec handling.",
    "HSE & Process Safety": "Health, safety, environment, permits to work and MOC.",
    "Finance": "Accounting, treasury, credit, excise and planning.",
    "Procurement": "Sourcing, purchasing and supplier management.",
    "Human Resources": "Workforce, learning and payroll.",
    "Corporate IT": "Enterprise platforms and identity.",
    "Regulatory Compliance": "RINs, low-carbon fuel credits, fuel specifications and emissions filings.",
}

PRODUCT_LINES = {
    "Commercial & Marketing": ("Wholesale Marketing", ["Wholesale Marketing", "Rack Pricing", "Customer & Market", "Branded Marketing", "Unbranded Marketing", "Renewable Fuels Marketing"]),
    "Operations & Supply": ("Pipelines & Terminals", ["Supply Planning", "Terminal Ops", "Pipeline & Marine Logistics", "Refinery Operations", "Maintenance & Reliability", "Product Quality"]),
    "Corporate Functions": ("Finance", ["Finance & Accounting", "Credit & Collections", "Procurement & Sourcing"]),
    "Trading & Compliance": ("Supply & Trading", ["Crude & Product Trading", "Environmental Credits"]),
}
EXTRA_DOMAINS = [
    "HSE & Permits", "Emissions & Energy", "Workforce Analytics", "Master Data", "Enterprise Data Platform",
    "Treasury & FX", "Excise & Fuel Tax", "Asset Management", "Customer Service", "Regulatory Affairs",
    "IT Service Management", "Laboratory Systems", "Hydrocarbon Accounting",
]

STAGES = [("Plan", "Select crude, plan runs, supply and price.", 1),
          ("Make", "Refine, blend, test and certify product.", 2),
          ("Deliver", "Move, load, invoice and collect.", 3)]
PROCESSES = [
    ("Crude Slate Planning", "Plan", "P1"), ("Rack Price Setting", "Plan", "P2"), ("Refinery Scheduling", "Plan", "P3"),
    ("Crude Procurement", "Plan", "P4"), ("Unit Operations", "Make", "M1"), ("Product Blending & Certification", "Make", "M2"),
    ("Turnaround & Maintenance", "Make", "M3"), ("Emissions Reporting", "Make", "M4"), ("Order to Cash", "Deliver", "D1"),
    ("Pipeline Nominations", "Deliver", "D2"), ("Terminal Rack Loading", "Deliver", "D3"), ("RIN Compliance", "Deliver", "D4"),
]

MASTER_DATA = ["Product", "Location", "Business Associate", "Material", "Facility", "Customer", "Carrier",
               "Employee", "Chart of Accounts", "Unit of Measure", "Currency"]

CORE_SYSTEMS = [
    ("Helios", "Wholesale Marketing", "Refined products ERP for orders, rack pricing, margin and price batches."),
    ("Atlas", "Pipelines & Terminals", "Pipeline batch scheduling and shipper nominations."),
    ("Meridian", "Wholesale Marketing", "Rack price posting and contract pricing formulas."),
    ("Orion", "Finance", "General ledger and cost accounting."),
    ("Kestrel", "Refinery Operations", "Refinery maintenance work orders."),
    ("Nimbus", "Pipelines & Terminals", "Refined product demand forecasting by terminal."),
    ("Sable", "Human Resources", "Workforce records."),
    ("Quarry", "Procurement", "Purchasing and supplier contracts."),
    ("Lumen", "Product Quality & Lab", "Refinery laboratory sample tracking."),
    ("Harbor", "Pipelines & Terminals", "Tank farm gauging and terminal inventory."),
    ("Vector", "Pipelines & Terminals", "Truck and marine freight settlement."),
    ("Beacon", "Finance", "Customer credit and collections."),
    ("Sentinel", "HSE & Process Safety", "Incident, permit to work and MOC tracking."),
    ("Cascade", "Refinery Operations", "Gasoline and distillate blend recipes."),
    ("Ember", "HSE & Process Safety", "Flare and stack emissions monitoring."),
    ("Nova", "Renewable Fuels", "Renewable feedstock receipts and pathway certification."),
    ("Onyx", "Corporate IT", "Asset and license registry."),
    ("Pinnacle", "Wholesale Marketing", "Branded dealer and key account planning."),
    ("Quill", "Corporate IT", "Document management."),
    ("Summit", "Finance", "Budget and planning."),
    ("Talon", "Refining & Planning", "Crude unit run planning."),
    ("Vantage", "Renewable Fuels", "Renewable diesel batch tracking."),
    ("Willow", "Supply & Trading", "Physical crude and product trade capture."),
    ("Zephyr", "Refinery Operations", "Steam, power and utilities metering."),
    ("Aurora", "Wholesale Marketing", "Customer portal for liftings and BOL lookup."),
    ("Basalt", "Refinery Operations", "Process historian tag archive."),
    ("Cinder", "HSE & Process Safety", "Fire and gas system logs."),
    ("Falcon", "Pipelines & Terminals", "Truck rack loading and lifting authorisation."),
    ("Garnet", "Finance", "Fixed assets."),
    ("Halcyon", "Human Resources", "Learning records."),
    ("Indigo", "Renewable Fuels", "Renewable fuel lab results."),
    ("Juno", "Procurement", "Supplier quality audits."),
    ("Kora", "Supply & Trading", "Paper trades and hedge positions."),
    ("Lagoon", "Pipelines & Terminals", "Marine vessel nominations and demurrage."),
    ("Mosaic", "Wholesale Marketing", "Competitor rack and street price intelligence."),
    ("Nexa", "Corporate IT", "Identity and access."),
    ("Obsidian", "Finance", "Treasury and FX."),
    ("Palm", "Refining & Planning", "Refinery yield accounting and mass balance."),
    ("Raffia", "Regulatory Compliance", "RIN generation, separation and retirement."),
    ("Savanna", "Pipelines & Terminals", "Hydrocarbon accounting and loss reporting."),
    ("Tamarind", "Refinery Operations", "Operator shift logs."),
    ("Umber", "Product Quality & Lab", "Product certificates of analysis."),
    ("Volta", "Refinery Operations", "Electrical load management."),
    ("Zuma", "Corporate IT", "Service desk."),
]

PUBLIC_SYSTEMS = [
    ("RightAngle", "Supply & Trading", "Commodity trading and risk management (ION RightAngle).", True),
    ("Profisee", "Corporate IT", "Master data management hub.", True),
    ("SAP_S4", "Finance", "SAP S/4HANA finance and controlling.", True),
    ("Salesforce", "Wholesale Marketing", "CRM for wholesale accounts and dealers.", True),
    ("ServiceNow", "Corporate IT", "IT service management.", True),
    ("Workday", "Human Resources", "HR and learning.", True),
    ("IBM_Maximo", "Refinery Operations", "IBM Maximo enterprise asset management.", True),
    ("AVEVA_PI", "Refinery Operations", "AVEVA PI process historian.", True),
    ("Toptech_TMS", "Pipelines & Terminals", "Toptech TMS6 terminal automation and BOLs.", True),
    ("Enverus", "Supply & Trading", "Energy market data.", True),
    ("OPIS", "Wholesale Marketing", "OPIS rack and spot fuel price assessments.", True),
    ("ARGUS", "Supply & Trading", "Argus crude and products price reporting.", True),
    ("Kpler", "Supply & Trading", "Cargo and vessel tracking.", True),
    ("Bloomberg", "Finance", "Market and FX data.", True),
    ("ICE", "Supply & Trading", "ICE Brent and gasoil futures.", True),
    ("Platts", "Supply & Trading", "S&P Global Platts price assessments.", True),
    ("Genscape", "Pipelines & Terminals", "Storage and pipeline flow monitoring.", True),
    ("IIR", "Refining & Planning", "Refinery outage intelligence.", True),
    ("FactSet", "Finance", "Financial data.", True),
    ("LabWare_LIMS", "Product Quality & Lab", "LabWare LIMS refinery laboratory.", True),
    ("Wood Mackenzie", "Refining & Planning", "Refinery and crude market research.", False),
    ("DTN", "Wholesale Marketing", "DTN rack price and fuel inventory feeds.", False),
    ("Saviynt", "Corporate IT", "Identity governance.", False),
    ("Solarwinds", "Corporate IT", "Infrastructure monitoring.", False),
    ("Experian", "Finance", "Business credit scores.", False),
    ("Esri ArcGIS", "Pipelines & Terminals", "Pipeline and terminal GIS mapping.", False),
    ("Databricks", "Corporate IT", "Lakehouse workspace.", False),
    ("Excel", "Wholesale Marketing", "Spreadsheet uploads.", False),
    ("SharePoint", "Corporate IT", "Document libraries.", False),
    ("Power BI", "Corporate IT", "Power BI service metadata.", False),
    ("Oracle EBS", "Finance", "Acquired-entity ledger.", False),
    ("EIA", "Supply & Trading", "US Energy Information Administration statistics.", False),
    ("EPA", "Regulatory Compliance", "EPA EMTS RIN and fuel program registers.", False),
    ("Aspen PIMS", "Refining & Planning", "Aspen PIMS refinery LP planning cases.", False),
    ("Allegro", "Supply & Trading", "Allegro ETRM position exports.", False),
    ("OPEC", "Supply & Trading", "OPEC basket prices.", False),
    ("PHMSA", "HSE & Process Safety", "Pipeline and Hazardous Materials Safety Administration filings.", False),
]

PLANTS = {"EPE": "Epe Refinery", "BDG": "Badagry Refinery", "APP": "Apapa Marine Terminal", "IKJ": "Ikeja Rack Terminal",
          "ONT": "Onitsha Depot", "KAN": "Kano Depot", "ABJ": "Abuja Depot", "IBD": "Ibadan Depot",
          "CAL": "Calabar Marine Terminal", "ILJ": "Ilaje Crude Terminal", "TEM": "Tema Terminal",
          "RTM": "Rotterdam Trading Desk", "HOU": "Houston Trading Desk"}
REGIONS = ["LAGOS", "NORTH", "EAST", "DELTA", "EXPORT"]
PLANT_APPS = [("BlendPlan", "Refinery Operations", "Blend planning and scheduling"),
              ("LIMS", "Product Quality & Lab", "Site laboratory system"),
              ("TankGauge", "Pipelines & Terminals", "Automatic tank gauging"),
              ("DocLib", "Corporate IT", "Site document library"),
              ("OpsLog", "Refinery Operations", "Operator logbook"),
              ("PermitToWork", "HSE & Process Safety", "Electronic permit to work"),
              ("SitePortal", "Refinery Operations", "Site reporting portal"),
              ("LabSync", "Product Quality & Lab", "Analyzer data capture")]

ENTITIES = {
    "Wholesale Marketing": ["Sales_Order", "Sales_Order_Line", "Customer", "Customer_Ship_To", "Rack_Price", "Price_Batch",
                            "Margin_Detail", "Lifting_Contract", "Branded_Dealer", "Invoice", "Invoice_Line", "Supply_Agreement",
                            "Deal", "Deal_Leg", "Transaction_Type", "Product", "Product_Grade", "Rack_Location",
                            "Spot_Price", "Competitor_Rack_Price", "Lifting_Forecast", "Credit_Memo"],
    "Refining & Planning": ["Crude_Assay", "Crude_Slate", "Unit_Yield", "LP_Case", "Unit_Run", "Feed_Rate",
                            "Operating_Plan", "Refinery_Margin"],
    "Renewable Fuels": ["Feedstock_Lot", "Pretreatment_Run", "RD_Batch", "Carbon_Intensity_Score", "Pathway",
                        "Biodiesel_Blend", "SAF_Batch"],
    "Supply & Trading": ["Trade", "Trade_Leg", "Hedge_Position", "Nomination", "Exchange_Agreement", "Inventory_Position"],
    "Pipelines & Terminals": ["Pipeline_Batch", "Batch_Cycle", "Carrier", "Tariff_Rate", "Freight_Invoice", "Tank",
                              "Tank_Inventory", "Terminal", "Rack_Lifting", "Vessel_Nomination", "Bill_Of_Lading",
                              "Product_Transfer", "Demand_Forecast", "Supply_Plan", "Pipeline_Segment", "Meter_Ticket"],
    "Refinery Operations": ["Work_Order", "Equipment", "Maintenance_Plan", "Turnaround", "Turnaround_Task", "Blend_Recipe",
                            "Unit_Schedule", "Shift_Log", "Unit_Outage", "Energy_Meter", "Tag_Reading",
                            "Utility_Consumption", "Spare_Part"],
    "Product Quality & Lab": ["Lab_Sample", "Lab_Result", "Test_Method", "Product_Spec", "Certificate_Of_Analysis",
                              "Instrument", "Off_Spec_Event", "Batch_Certification"],
    "HSE & Process Safety": ["Incident", "Permit_To_Work", "Emission_Reading", "Inspection", "Corrective_Action",
                             "MOC_Request", "Waste_Manifest", "Safety_Observation"],
    "Finance": ["GL_Account", "Journal_Entry", "Cost_Center", "Profit_Center", "Budget", "Fixed_Asset", "Payment",
                "Credit_Limit", "Collection_Case", "FX_Rate", "Excise_Tax", "Tax_Code"],
    "Procurement": ["Purchase_Order", "Purchase_Order_Line", "Supplier", "Supplier_Contract", "Goods_Receipt",
                    "Supplier_Audit", "Material", "Requisition"],
    "Human Resources": ["Employee", "Position", "Org_Unit", "Training_Record", "Course", "Timesheet", "Leave_Request"],
    "Corporate IT": ["Application", "License", "Ticket", "User_Account", "Access_Grant", "Document", "Asset_Tag"],
    "Regulatory Compliance": ["RIN_Transaction", "RIN_Separation", "LCFS_Credit", "Compliance_Obligation",
                              "Fuel_Spec_Filing", "Emissions_Allowance"],
}

SEM_AREAS = {
    "wholesale": "Wholesale Marketing", "refining": "Refining & Planning", "renewables": "Renewable Fuels",
    "trading": "Supply & Trading", "logistics": "Pipelines & Terminals", "operations": "Refinery Operations",
    "quality": "Product Quality & Lab", "hse": "HSE & Process Safety", "finance": "Finance", "procurement": "Procurement",
    "hr": "Human Resources", "it": "Corporate IT", "compliance": "Regulatory Compliance",
}

OPERATIONAL_SUFFIXES = ["", "_Hdr", "_Dtl", "_Hist", "_Audit", "_Stg", "_Xref", "_Log", "_Arch", "_Ext", "_Map", "_Snap"]

ABBREVIATIONS = {
    "Amount": "AMT", "Margin": "MRGN", "Customer": "CUST", "Product": "PROD", "Number": "NO", "Quantity": "QTY",
    "Price": "PRC", "Date": "DT", "Code": "CD", "Name": "NM", "Description": "DESC", "Facility": "FCLTY",
    "Material": "MATL", "Order": "ORD", "Line": "LN", "Currency": "CRNCY", "Status": "STAT", "Type": "TYP",
    "Unit": "UNIT", "Barrels": "BBL", "Batch": "BTCH", "Supplier": "SUPP", "Invoice": "INV", "Created": "CRT",
    "Updated": "UPD", "Volume": "VOL", "Gravity": "GRAV", "Cost": "CST", "Net": "NET", "Gross": "GRS", "Key": "KEY",
    "Id": "ID", "Timestamp": "TS", "Active": "ACTV", "Flag": "FLG", "Location": "LOC", "Region": "RGN",
}

MEASURES = [("Quantity", "decimal(18,4)"), ("Net_Barrels", "decimal(18,3)"), ("Unit_Price", "decimal(18,6)"),
            ("Amount_NGN", "decimal(19,2)"), ("Amount_USD", "decimal(19,2)"), ("Cost_Amount", "decimal(19,2)"),
            ("Volume_Litres", "decimal(18,3)"), ("Gross_Amount", "decimal(19,2)"), ("API_Gravity", "decimal(6,2)")]
ATTRIBUTES = [("Status_Code", "varchar(10)"), ("Description", "nvarchar(255)"), ("Type_Code", "varchar(20)"),
              ("Currency_Code", "char(3)"), ("Unit_Of_Measure", "varchar(10)"), ("Region_Code", "varchar(10)"),
              ("Created_Date", "date"), ("Posting_Date", "date"), ("Is_Active", "bit"), ("Comment_Text", "nvarchar(500)")]
FOREIGN_KEYS = ["Facility_Key", "Product_Key", "Customer_Key", "Supplier_Key", "Location_Key", "Material_Key",
                "Cost_Center_Key", "Employee_Key"]
AUDIT = [("Source_System_Code", "varchar(20)", "ETL Generated"), ("Load_Dttm", "datetime2", "ETL Generated"),
         ("Record_Hash", "varbinary(32)", "ETL Generated")]

VIEW_VARIANTS = ["", "_Detail", "_Summary", "_Daily", "_Monthly", "_By_Terminal", "_By_Customer", "_By_Region",
                 "_Secured", "_Non_Secured", "_Current", "_History", "_Snapshot", "_KPI", "_Trend", "_Exceptions",
                 "_Weekly", "_YTD", "_Open", "_Closed"]

FIRST_NAMES = ["Adaeze", "Babatunde", "Chiamaka", "Chinedu", "Damilola", "Emeka", "Folake", "Funmilayo", "Gbenga",
               "Halima", "Ifeoma", "Ikenna", "Jumoke", "Kayode", "Kelechi", "Lami", "Mojisola", "Musa", "Nkechi",
               "Obinna", "Olumide", "Oluwaseun", "Remi", "Sade", "Segun", "Tobi", "Tunde", "Uche", "Yetunde",
               "Zainab", "Amara", "Bisi", "Dayo", "Efe", "Femi", "Ngozi", "Rotimi", "Temitope", "Usman", "Wale",
               "Grace", "Daniel", "Sarah", "Michael", "Priya", "Lars", "Elena", "Marco", "Hannah", "Kwame"]
LAST_NAMES = ["Adeyemi", "Okafor", "Balogun", "Eze", "Ibrahim", "Nwosu", "Ogunleye", "Okonkwo", "Bello", "Afolabi",
              "Chukwu", "Danjuma", "Fashola", "Igwe", "Lawal", "Mohammed", "Nnamdi", "Obi", "Okeke", "Olawale",
              "Onyeka", "Salami", "Usman", "Yusuf", "Akande", "Ajayi", "Mensah", "Van Dijk", "Morales", "Fischer",
              "Iyer", "Haddad", "Osei", "Abiodun", "Ekwueme", "Ogbu", "Adebayo", "Nwachukwu", "Anyanwu", "Oladipo"]

REPORT_KINDS = ["Dashboard", "Scorecard", "Analysis", "Tracker", "Report", "Monitor", "Overview", "Explorer",
                "Workbench", "Insights"]

# Reports a downstream analyst expects to find by name; the rest are composed from entities and kinds.
# Each name maps to the entities its views must cover.
SIGNATURE_REPORTS = {
    "3-2-1 Crack Spread Dashboard": ["Spot_Price", "Refinery_Margin", "Crude_Slate"],
    "Daily Refinery Margin": ["Refinery_Margin", "Margin_Detail", "Crude_Slate"],
    "Crude Run & Yield Report": ["Unit_Run", "Unit_Yield", "Feed_Rate"],
    "Crude Slate Economics": ["Crude_Slate", "Crude_Assay"],
    "LP Plan vs Actual": ["LP_Case", "Operating_Plan", "Unit_Yield"],
    "Unit Availability Scorecard": ["Unit_Outage", "Unit_Schedule", "Equipment"],
    "Turnaround Readiness Tracker": ["Turnaround", "Turnaround_Task", "Work_Order"],
    "Flare Emissions Monitor": ["Emission_Reading", "Emissions_Allowance"],
    "Rack-to-Spot Margin Analysis": ["Rack_Price", "Spot_Price", "Margin_Detail"],
    "Rack Price Posting History": ["Rack_Price", "Price_Batch", "Competitor_Rack_Price"],
    "Branded Dealer Volume Scorecard": ["Branded_Dealer", "Rack_Lifting"],
    "Unbranded Rack Liftings": ["Rack_Lifting", "Lifting_Contract"],
    "Lifting vs Contract Entitlement": ["Lifting_Contract", "Rack_Lifting", "Lifting_Forecast"],
    "Terminal Throughput Dashboard": ["Terminal", "Rack_Lifting", "Meter_Ticket"],
    "Tank Inventory Days of Supply": ["Tank_Inventory", "Tank", "Demand_Forecast"],
    "Pipeline Nomination Variance": ["Nomination", "Pipeline_Batch"],
    "Pipeline Batch Schedule": ["Pipeline_Batch", "Batch_Cycle", "Pipeline_Segment"],
    "Marine Demurrage Tracker": ["Vessel_Nomination", "Freight_Invoice"],
    "Product Loss & Gain Report": ["Meter_Ticket", "Tank_Inventory", "Product_Transfer"],
    "Bill of Lading Exceptions": ["Bill_Of_Lading", "Rack_Lifting"],
    "Truck Rack Wait Times": ["Rack_Lifting", "Terminal"],
    "Trading P&L by Book": ["Trade", "Trade_Leg", "Deal"],
    "Hedge Effectiveness Report": ["Hedge_Position", "Trade"],
    "Inventory Position & Exposure": ["Inventory_Position", "Hedge_Position"],
    "Exchange Balance Report": ["Exchange_Agreement", "Product_Transfer"],
    "RIN Obligation Tracker": ["Compliance_Obligation", "RIN_Transaction"],
    "RIN Inventory & Separation": ["RIN_Separation", "RIN_Transaction"],
    "LCFS Credit Position": ["LCFS_Credit", "Carbon_Intensity_Score"],
    "Renewable Diesel Margin": ["RD_Batch", "Feedstock_Lot"],
    "Feedstock Carbon Intensity": ["Carbon_Intensity_Score", "Feedstock_Lot", "Pathway"],
    "Off-Spec Product Events": ["Off_Spec_Event", "Lab_Result"],
    "Certificate of Analysis Lookup": ["Certificate_Of_Analysis", "Batch_Certification"],
    "Gasoline Blend Giveaway": ["Blend_Recipe", "Product_Spec"],
    "Octane & RVP Compliance": ["Product_Spec", "Lab_Result", "Fuel_Spec_Filing"],
    "Excise Tax by Terminal": ["Excise_Tax", "Tax_Code"],
    "Credit Exposure by Customer": ["Credit_Limit", "Collection_Case", "Customer"],
}


def _pascal_words(entity: str) -> list[str]:
    return entity.split("_")


def _abbrev(column: str) -> str:
    return "_".join(ABBREVIATIONS.get(w, w.upper()[:6]) for w in column.split("_"))


def _iso(ts: datetime) -> str:
    return ts.replace(microsecond=0).isoformat()


# --------------------------------------------------------------------------- generator

class LscGenerator:
    """Builds the LSC catalog one domain area at a time, then plants the competency paths."""

    def __init__(self, seed: int, today: datetime):
        self.rng = random.Random(seed)
        self.today = today
        self.cat = Catalog(json.loads(MODEL_PATH.read_text(encoding="utf-8")))
        self.uuid_rng = random.Random(seed + 1)
        self.system_area: dict[str, str] = {}
        self.system_tables: dict[str, list[str]] = defaultdict(list)
        self.replica_of: dict[str, str] = {}
        self.columns: dict[str, list[str]] = defaultdict(list)
        self.tables_by_layer: dict[str, list[str]] = defaultdict(list)
        self.entity_of: dict[str, str] = {}
        self.gold_area_of: dict[str, str] = {}
        self.reports: list[str] = []
        self.report_names: dict[str, str] = {}
        self.cdds: list[str] = []
        self.manifest: dict = {}

    def uid(self) -> str:
        return str(uuid.UUID(int=self.uuid_rng.getrandbits(128), version=4))

    def past(self, max_days: int = 720, min_days: int = 1) -> str:
        return _iso(self.today - timedelta(days=self.rng.randint(min_days, max_days), seconds=self.rng.randint(0, 86399)))

    # --- organisation -------------------------------------------------------

    def build_organisation(self) -> None:
        c = self.cat
        for name, desc in BUSINESS_AREAS.items():
            c.add("BusinessArea", name, description=desc, createdAt=self.past())
        for line, (area, domains) in PRODUCT_LINES.items():
            c.add("DataProductLine", line)
            c.link("BusinessArea", "HAS_PRODUCT_LINE", "DataProductLine", area, line)
            for d in domains:
                c.add("CapabilityDataDomain", d, description=f"{d} data and analytics.", createdAt=self.past())
                c.link("DataProductLine", "OWNS", "CapabilityDataDomain", line, d)
        for d in EXTRA_DOMAINS:
            c.add("CapabilityDataDomain", d, description=f"{d} data and analytics.", createdAt=self.past())
        self.cdds = list(c.nodes["CapabilityDataDomain"])
        for name, desc, order in STAGES:
            c.add("ValueStreamStage", name, description=desc, sequenceOrder=order)
            c.link("BusinessArea", "HAS_STAGE", "ValueStreamStage", "Refinery Operations", name)
        c.link("ValueStreamStage", "NEXT_STAGE", "ValueStreamStage", "Plan", "Make")
        c.link("ValueStreamStage", "NEXT_STAGE", "ValueStreamStage", "Make", "Deliver")
        c.link("ValueStreamStage", "LOOPS_BACK_TO", "ValueStreamStage", "Deliver", "Plan")
        for name, stage, label in PROCESSES:
            c.add("BusinessProcess", name, description=f"{name} across LSC refineries and terminals.", sequenceLabel=label)
            c.link("BusinessProcess", "BELONGS_TO_STAGE", "ValueStreamStage", name, stage)
        c.link("BusinessProcess", "INFORMS", "BusinessProcess", "Crude Slate Planning", "Refinery Scheduling")
        processes = [p[0] for p in PROCESSES]
        while len(c.rels[("CapabilityDataDomain", "SUPPORTS", "BusinessProcess")]) < 46:
            c.link("CapabilityDataDomain", "SUPPORTS", "BusinessProcess", self.rng.choice(self.cdds), self.rng.choice(processes))
        c.add("Policy", "SOX", description="SOX financial reporting controls.", isSoxRelevant=True,
              confidentialityClassification="Confidential", createdAt=self.past())
        c.add("Policy", "Confidentiality", description="LSC data confidentiality standard.",
              confidentialityClassification="Restricted", createdAt=self.past())
        for name in MASTER_DATA:
            c.add("MasterDataDomain", name, status=self.rng.choice(["Active", "Active", "In Design"]),
                  sourceFile="LSC_Master_Data_Domains_2026.xlsx", createdAt=self.past())
        for i in range(291):
            while True:
                person = f"{self.rng.choice(FIRST_NAMES)} {self.rng.choice(LAST_NAMES)}"
                if not c.has("Person", person):
                    break
            c.add("Person", person, createdAt=self.past() if i % 20 == 0 else None)

    # --- systems and servers ------------------------------------------------

    def build_systems(self) -> None:
        c = self.cat
        specs: list[tuple[str, str, str, str]] = []
        for name, area, desc in CORE_SYSTEMS:
            specs.append((name, area, desc, "core"))
        for name, area, desc, with_tables in PUBLIC_SYSTEMS:
            specs.append((name, area, desc, "public" if with_tables else "public-feed"))
        for code, city in PLANTS.items():
            for app, area, desc in PLANT_APPS:
                specs.append((f"{app}_{code}", area, f"{desc} at {city}.", "plant" if app in ("BlendPlan", "LIMS") else "plant-feed"))
        for region in REGIONS:
            specs.append((f"BlendPlan_FEED_{region}", "Refining & Planning", f"Crude and feedstock planning for {region.title()} region.", "plant-feed"))
        for name, area, desc in CORE_SYSTEMS:
            specs.append((f"{name}_Reporting", area, f"Reporting replica of {name}.", "derived"))
            specs.append((f"{name}_DW", area, f"Departmental warehouse built on {name}.", "derived"))
        for name, area, _ in CORE_SYSTEMS[:20]:
            specs.append((f"{name}_Archive", area, f"Archive database for {name}.", "derived"))
        envs = ["dev", "qa", "sit"]
        i = 0
        while len(specs) < 400:
            name, area, _ = CORE_SYSTEMS[i % len(CORE_SYSTEMS)]
            specs.append((f"lscnpd{name.lower()}{envs[i // len(CORE_SYSTEMS)]}sqldb", area, f"Non-production {name} database.", "derived"))
            i += 1
        for name in ["helios_reporting", "HELIOS-Reporting", "Atlas Reporting", "kestrel"]:
            specs.append((name, "Corporate IT", "Unreconciled duplicate registration from a scanner import.", "derived"))
        specs.append((IDP, "Corporate IT", "Azure Synapse medallion platform.", "platform"))
        specs.append((SANDBOX, "Wholesale Marketing", "Self-service Alteryx workflows being sunset.", "platform"))
        specs.append(("Commercial Analysis", "Wholesale Marketing", "Alteryx sandbox for commercial analysts.", "platform"))

        servers: list[str] = []
        for n, (name, area, desc, kind) in enumerate(specs):
            self.system_area[name] = area
            platform = {"platform": "Azure Synapse"}.get(kind)
            if name in (SANDBOX, "Commercial Analysis"):
                platform = "Alteryx Sandbox"
            full = kind in ("core", "public", "plant", "platform") or n % 2 == 0
            c.add("DataSystem", name, description=desc,
                  scope=self.rng.choice(["Enterprise", "Business Unit", "Site"]) if full else None,
                  systemId=f"LSC-SYS-{1000 + n}" if full else None,
                  isRecordActive=(kind != "derived" or n % 7 != 0) if full else None,
                  applicationType=self.rng.choice(["COTS", "Custom", "SaaS", "Data Feed"]) if kind in ("core", "public", "public-feed") else None,
                  ingestionMethod=self.rng.choice(["Synapse Pipeline", "ADF Copy", "SFTP", "API", "Manual Upload"]) if kind in ("core", "public", "plant") else None,
                  refreshFrequency=self.rng.choice(["Daily", "Hourly", "Weekly", "Monthly"]) if kind in ("core", "public") else None,
                  confidentialityClassification=self.rng.choice(["Internal", "Confidential", "Restricted"]) if kind in ("core", "public") else None,
                  isSoxRelevant=(area == "Finance") if kind == "core" else None,
                  dataModality=self.rng.choice(["Structured", "Semi-structured"]) if kind == "core" else None,
                  applicationService=f"{area} Applications" if kind == "core" else None,
                  purviewReplicaSchemaName=f"replica_{name.lower()}" if kind in ("core", "public", "plant") else None,
                  platform=platform,
                  status="sunsetting" if name in (SANDBOX, "Commercial Analysis") else None,
                  createdAt=self.past() if full else None)
            if n % 5 in (0, 1, 2) or kind == "platform":
                c.link("DataSystem", "BELONGS_TO", "BusinessArea", name, area)
            if kind in ("core", "public"):
                server = f"{name.upper().replace(' ', '')}.prod.db.lsc.internal"
            elif kind == "platform":
                server = IDP_SERVER if name == IDP else "alteryx-gallery.lsc.internal"
            elif kind.startswith("plant"):
                server = f"sqlsrv-{name.split('_')[-1].lower()}-01.lsc.internal"
            elif n % 5 in (0, 1):
                server = None
            else:
                server = f"sqlsrv-{n:03d}.lsc.internal"
            if server:
                if not c.has("Server", server):
                    if len(servers) >= 210 and kind != "platform":
                        server = self.rng.choice(servers)
                    else:
                        c.add("Server", server, createdAt=self.past() if len(servers) % 7 == 0 else None)
                        servers.append(server)
                c.link("Server", "HOSTS", "DataSystem", server, name)
        for name in self.rng.sample([s[0] for s in specs if s[3] in ("core", "public")], 15):
            c.link("DataSystem", "SUBJECT_TO", "Policy", name, "SOX" if self.system_area[name] == "Finance" else "Confidentiality")
        self.specs = specs

    # --- physical tables ----------------------------------------------------

    def _schema(self, qualified: str, layer: str | None = None, **props) -> str:
        layer = layer or schema_layer(qualified)
        self.cat.add("Schema", qualified, name=qualified if self.rng.random() < 0.55 else None, layer=layer,
                     createdAt=self.past() if self.rng.random() < 0.7 else None, **props)
        if is_legacy(qualified + ".x", layer) and layer != "Operational":
            self.cat.tag("Schema", "Legacy", qualified)
        return qualified

    def _table(self, qualified: str, layer: str, *, roles=(), source_file=None, **props) -> str:
        schema, name = qualified.split(".", 1)
        c = self.cat
        c.add("Table", qualified, name=name, layer=layer,
              tableName=name if self.rng.random() < 0.4 else None,
              sourceFile=source_file, createdAt=self.past() if self.rng.random() < 0.75 else None,
              updatedAt=self.past(60) if self.rng.random() < 0.45 else None, **props)
        for role in roles:
            c.tag("Table", role, qualified)
        if is_legacy(qualified, layer) and layer != "Operational":
            c.tag("Table", "Legacy", qualified)
        if c.has("Schema", schema):
            c.link("Schema", "CONTAINS", "Table", schema, qualified)
        self.tables_by_layer[layer].append(qualified)
        return qualified

    def _columns(self, table: str, entity: str, style: str, n_extra: int) -> list[str]:
        """style is 'source' (abbreviated upper-case names) or 'conformed' (Pascal_Snake)."""
        words = _pascal_words(entity)
        base = [(f"{entity}_Id", "bigint", "PK"), (f"{entity}_Number", "varchar(30)", "BK")]
        fks = [(fk, "bigint", "FK") for fk in self.rng.sample(FOREIGN_KEYS, 2)]
        body = [(m, t, None) for m, t in self.rng.sample(MEASURES, 3)] + [(a, t, None) for a, t in self.rng.sample(ATTRIBUTES, 4)]
        extra = [(f"{words[-1]}_{a}", t, None) for a, t in self.rng.sample(ATTRIBUTES, min(n_extra, len(ATTRIBUTES)))]
        cols = base + fks + body + extra + [("Timestamp", "datetime2", None)]
        if style == "conformed":
            cols += [(a, t, k) for a, t, k in AUDIT]
        made = []
        for name, dtype, key in cols:
            col_name = _abbrev(name) if style == "source" else name
            qn = f"{table}.{col_name}"
            if self.cat.has("Column", qn):
                continue
            definition = None
            if style == "conformed" and self.rng.random() < 0.8:
                definition = f"{name.replace('_', ' ')} of the {entity.replace('_', ' ').lower()}."
            self.cat.add("Column", qn, name=col_name, dataType=dtype if self.rng.random() < 0.9 else None,
                         sourceDataType=dtype.replace("varchar", "VARCHAR2").replace("bigint", "NUMBER(19)") if style == "conformed" and self.rng.random() < 0.7 else None,
                         keyType=key, isPrimaryKey=(key == "PK") if style == "conformed" else None,
                         definition=definition, sourceFile=f"STTM_{table.split('.', 1)[1]}.xlsx" if style == "conformed" else None,
                         createdAt=self.past() if self.rng.random() < 0.4 else None)
            self.cat.link("Table", "HAS_COLUMN", "Column", table, qn)
            made.append(qn)
        self.columns[table].extend(made)
        return made

    def build_operational_and_replica(self) -> None:
        c = self.cat
        with_tables = [s for s in self.specs if s[3] in ("core", "public", "plant")]
        per_system = {"core": 30, "public": 13, "plant": 22}
        for name, area, _, kind in with_tables:
            schema = self._schema(name, "Operational")
            c.link("DataSystem", "HOSTS", "Schema", name, schema)
            if kind == "core":
                c.link("DataSystem", "HOSTS", "Schema", f"{name}_Reporting", schema)
            replica_schema = f"replica_{name.lower()}"
            self._schema(replica_schema)
            c.link("DataSystem", "HOSTS", "Schema", IDP, replica_schema)
            entities = ENTITIES[area]
            count = per_system[kind] + self.rng.randint(-4, 4)
            for i in range(count):
                entity = entities[i % len(entities)]
                suffix = OPERATIONAL_SUFFIXES[(i // len(entities)) % len(OPERATIONAL_SUFFIXES)]
                op = f"{name}.{entity.replace('_', '')}{suffix}"
                if c.has("Table", op):
                    continue
                self._table(op, "Operational", sourceDataSystem=name if i == 0 else None)
                c.link("DataSystem", "CONTAINS", "Table", name, op)
                self.system_tables[name].append(op)
                if self.rng.random() < 0.11:
                    self._columns(op, entity, "source", 1)
                if self.rng.random() < 0.81:
                    rep = f"{replica_schema}.{entity}{suffix}"
                    self._table(rep, "Replica", source_file=f"STTM_{name}_Replica.xlsx" if self.rng.random() < 0.5 else None)
                    c.link("Table", "REPLICATED_TO", "Table", op, rep)
                    self.replica_of[rep] = entity
                    if self.rng.random() < 0.45:
                        self._columns(rep, entity, "source", 6)
        for name in self.rng.sample([s[0] for s in with_tables], 9):
            c.link("DataSystem", "REPLICATED_TO", "Schema", name, f"replica_{name.lower()}")
        c.add("FlatFile", FLAT_FILE, createdAt=self.past())
        self._schema("replica_files_commercial")
        c.link("DataSystem", "HOSTS", "Schema", IDP, "replica_files_commercial")
        for i, entity in enumerate(["Price_Adjustment", "Rack_Price_Override", "Budget_Upload", "Target_Volume", "Customer_Segment",
                                    "Freight_Accrual", "Competitor_Rack_Survey", "Unit_Capacity", "Holiday_Calendar",
                                    "Sales_Target", "FX_Override", "Product_Hierarchy", "Region_Map"]):
            t = self._table(f"replica_files_commercial.{entity}", "Operational", source_file=f"{entity}.xlsx")
            c.link("FlatFile", "CONTAINS", "Table", FLAT_FILE, t)

    def build_silver_gold(self) -> None:
        c = self.cat
        for s in ("udm_core", "mdm_core"):
            self._schema(s, role="IDP conformed core")
            c.link("DataSystem", "HOSTS", "Schema", IDP, s)
        replicas = [t for t in self.tables_by_layer["Replica"] if t in self.replica_of]
        by_entity = defaultdict(list)
        for rep in replicas:
            by_entity[self.replica_of[rep]].append(rep)
        silver = []
        n_target = 640
        entities = list(by_entity)
        self.rng.shuffle(entities)
        i = 0
        while len(silver) < n_target:
            entity = entities[i % len(entities)]
            sources = by_entity[entity]
            src = self.rng.choice(sources)
            system = src.split(".")[0].replace("replica_", "").title()
            is_dim = i % 5 in (1, 3)
            schema = "mdm_core" if is_dim else "udm_core"
            suffix = "_Dim" if is_dim else "_Fact"
            variant = "" if i < len(entities) else f"_{['Daily', 'Hist', 'Snapshot', 'Agg', 'Bridge', 'Xref', 'Detail'][i // len(entities) % 7]}"
            qn = f"{schema}.{system}_{entity}{variant}{suffix}"
            i += 1
            if c.has("Table", qn):
                continue
            roles = ()
            if is_dim and len(c.labels[("Table", "Dimension")]) < 84 and self.rng.random() < 0.6:
                roles = ("Dimension",)
            elif not is_dim and len(c.labels[("Table", "Fact")]) < 42 and self.rng.random() < 0.2:
                roles = ("Fact",)
            self._table(qn, "Silver", roles=roles, source_file=f"STTM_{system}_{entity}.xlsx",
                        sttmLink=f"https://lsc.sharepoint.com/sites/DataPlatform/STTM/{system}_{entity}.xlsx" if self.rng.random() < 0.2 else None)
            silver.append(qn)
            self.entity_of[qn] = entity
            for rep in self.rng.sample(sources, min(len(sources), self.rng.choice([1, 2, 2, 3, 4]))):
                c.link("Table", "DERIVED_FROM", "Table", qn, rep)
            if self.rng.random() < 0.9:
                self._columns(qn, entity, "conformed", self.rng.randint(6, 10))
        for _ in range(4):
            entity = self.rng.choice(["Currency", "Facility", "Customer", "Product"])
            qn = f"mdm_core.LSC_{entity}_Union_Dim"
            if not c.has("Table", qn):
                self._table(qn, "Silver", source_file="STTM_Union_Dims.xlsx")
                for src in self.rng.sample(silver, 2):
                    c.link("Table", "DERIVED_FROM", "Table", qn, src)
        for _ in range(25):
            a, b = self.rng.sample(silver, 2)
            c.link("Table", "DERIVED_FROM", "Table", a, b)
        self.silver = silver

        gold_area = {"wholesale_core": "Wholesale Marketing", "refining_core": "Refining & Planning",
                     "renewables_core": "Renewable Fuels", "trading_core": "Supply & Trading",
                     "logistics_core": "Pipelines & Terminals"}
        for g, area in gold_area.items():
            self._schema(g)
            c.link("DataSystem", "HOSTS", "Schema", IDP, g)
            c.link("Schema", "BELONGS_TO", "BusinessArea", g, area)
        gold = []
        gold_names = {
            "wholesale_core": ["Net_Sales_Fact", "Lifting_Entitlement_Fact", "Customer_Profitability_Fact", "Price_Realization_Fact",
                               "Customer_Dim", "Rack_Location_Dim", "Lifting_Plan_Fact", "Branded_Volume_Fact", "Rack_Price_Dim",
                               "Deal_Position_Fact"],
            "refining_core": ["Crude_Run_Fact", "Unit_Yield_Fact", "Crude_Grade_Dim", "Unit_Availability_Fact",
                              "Crack_Spread_Fact", "Process_Unit_Dim", "Refinery_Margin_Fact", "Product_Giveaway_Fact"],
            "renewables_core": ["Feedstock_Dim", "RD_Yield_Fact", "Renewable_Sales_Fact", "Carbon_Intensity_Fact",
                                "Pathway_Dim", "Renewable_Spec_Dim", "Feedstock_Supplier_Dim"],
            "trading_core": ["Trade_PnL_Fact", "Inventory_Position_Fact", "Hedge_Effectiveness_Fact", "Counterparty_Dim",
                             "Trade_Book_Dim", "Pricing_Index_Dim"],
            "logistics_core": ["Tariff_Cost_Fact", "Tank_Inventory_Fact", "Pipeline_Throughput_Fact", "Carrier_Dim",
                               "Terminal_Dim", "Nomination_Variance_Fact", "Rack_Lifting_Fact", "Pipeline_Segment_Dim",
                               "Tank_Utilization_Fact"],
        }
        n_fact = n_dim = 0
        for g, names in gold_names.items():
            for nm in names:
                qn = f"{g}.{nm}"
                roles = ()
                if nm.endswith("_Fact") and n_fact < 16:
                    roles, n_fact = ("Fact",), n_fact + 1
                elif nm.endswith("_Dim") and n_dim < 11:
                    roles, n_dim = ("Dimension",), n_dim + 1
                self._table(qn, "Gold", roles=roles, source_file=f"STTM_{g}_{nm}.xlsx")
                gold.append(qn)
                self.gold_area_of[qn] = gold_area[g]
                for src in self._related_silver(nm, gold_area[g], self.rng.choice([3, 5, 6, 7])):
                    c.link("Table", "DERIVED_FROM", "Table", qn, src)
                if self.rng.random() < 0.6:
                    self._columns(qn, nm.rsplit("_", 1)[0], "conformed", self.rng.randint(3, 7))
                    self._derive_columns(qn)
                if self.rng.random() < 0.5:
                    c.link("Table", "DERIVED_FROM", "Table", qn, self.rng.choice(replicas))
        self.gold = gold
        for t in silver:
            self._derive_columns(t)

    def _related_silver(self, gold_name: str, area: str, k: int) -> list[str]:
        """k Silver tables for a Gold table: shared name words first, then the Gold area's entities, then any."""
        words = set(gold_name.split("_")) - {"Fact", "Dim"}
        named = [s for s in self.silver if words & set(self.entity_of[s].split("_"))]
        local = [s for s in self.silver if self.entity_of[s] in ENTITIES[area] and s not in named]
        picks = self.rng.sample(named, min(k, len(named)))
        rest = [s for s in local if s not in picks] or [s for s in self.silver if s not in picks]
        return picks + self.rng.sample(rest, min(k - len(picks), len(rest)))

    def _silver_for(self, view: str) -> str:
        same = [s for s in self.silver if self.entity_of[s] == self.entity_of[view]]
        return self.rng.choice(same or self.silver)

    def _derive_columns(self, table: str) -> None:
        """Wire each conformed column to a same-named or abbreviated column of an upstream table."""
        c = self.cat
        upstream = [tgt for (src, tgt) in c.rels[("Table", "DERIVED_FROM", "Table")] if src == table]
        for col in self.columns.get(table, []):
            name = col.rsplit(".", 1)[1]
            if name in {a[0] for a in AUDIT}:
                c.nodes["Column"][col]["transformation"] = "ETL Generated"
                continue
            for up in [u for u in upstream if self.columns.get(u)][:2]:
                candidates = [f"{up}.{name}", f"{up}.{_abbrev(name)}"]
                hit = next((x for x in candidates if c.has("Column", x)), None)
                if hit is None and self.rng.random() < 0.8:
                    hit = self.rng.choice(self.columns[up])
                if hit:
                    c.link("Column", "DERIVED_FROM", "Column", col, hit)
                    if self.rng.random() < 0.3:
                        c.nodes["Column"][col]["transformation"] = self.rng.choice([
                            f"Direct map from {hit}", f"CAST({hit} AS decimal(18,4))", f"ISNULL({hit}, 0)",
                            f"TRIM(UPPER({hit}))", f"Lookup {hit} against mdm_core.Facility_Dim.Facility_Key",
                            f"CONVERT(date, {hit})"])

    def build_legacy(self) -> None:
        c = self.cat
        legacy_schemas = ["dwh", "dwh_core", "dwh_refining", "dwh_finance", "dwh_quality", "persistence", "staging"]
        for s in legacy_schemas:
            self._schema(s, isCrossCutting=(s == "dwh_core"), refactorTarget="udm_core" if s.startswith("dwh") else None)
        targets = self.silver + self.gold
        made = 0
        for i in range(114):
            schema = legacy_schemas[i % len(legacy_schemas)]
            base = self.rng.choice(self.silver).split(".", 1)[1].rsplit("_", 1)[0]
            is_view = i % 5 == 0 and made < 22
            qn = f"{schema}.{'vw_' if is_view else 'LSC_'}{base}"
            if c.has("Table", qn):
                continue
            self._table(qn, "Silver", roles=("View",) if is_view else (), source_file="Legacy_DWH_Inventory.xlsx",
                        viewDefinition=f"CREATE VIEW {qn} AS SELECT * FROM {schema}.LSC_{base}" if is_view else None,
                        comment="Pre-IDP warehouse object." if i % 9 == 0 else None)
            if is_view:
                made += 1
            if len(c.rels[("Table", "REFACTORED_TO", "Table")]) < 88:
                c.link("Table", "REFACTORED_TO", "Table", qn, self.rng.choice(targets))
            if i % 16 == 0:
                self._columns(qn, base.split("_")[-1], "conformed", 2)
        self.legacy = [t for t in c.labels[("Table", "Legacy")]]
        for t in self.rng.sample(self.gold, 9):
            c.link("Table", "MIGRATED_FROM", "DataSystem", t, SANDBOX)
        candidates = self.gold + self.rng.sample(self.silver, 90)
        for t in candidates[:110]:
            c.link("DataSystem", "MIGRATED_TO", "Table", SANDBOX, t)

    def build_semantic(self) -> None:
        c = self.cat
        subs = ["", "_pricing", "_planning", "_ops", "_kpi"]
        area_of = {"sem_masterdata": "Corporate IT"}
        area_of.update({f"sem_{a}{s}": ba for a, ba in SEM_AREAS.items() for s in subs})
        schemas = list(area_of)[:62]
        for s in schemas:
            self._schema(s)
            c.link("DataSystem", "HOSTS", "Schema", IDP, s)
        for s in self.rng.sample(schemas, 30):
            c.link("Schema", "BELONGS_TO", "BusinessArea", s, area_of[s])
        upstream = self.silver + self.gold
        views, plain = [], []
        entity_pool = sorted({e for es in ENTITIES.values() for e in es})
        i = 0
        while len(views) < 2275 or len(plain) < 458:
            schema = schemas[i % len(schemas)]
            pool = entity_pool if schema == "sem_masterdata" else ENTITIES[area_of[schema]]
            rounds = i // len(schemas)
            entity = pool[(rounds + i % len(schemas)) % len(pool)]
            variant = VIEW_VARIANTS[(rounds * 3 + i % len(schemas)) % len(VIEW_VARIANTS)]
            if entity.endswith(variant.lstrip("_")) and variant:
                variant = ""
            want_view = len(views) < 2275 and (len(plain) >= 458 or i % 6 != 5)
            qn = f"{schema}.{entity}{variant}{'_vw' if want_view else '_Agg'}"
            i += 1
            if c.has("Table", qn):
                continue
            definition = None
            if want_view and self.rng.random() < 0.065:
                src = self.rng.choice(upstream)
                definition = f"CREATE VIEW {qn} AS\nSELECT s.*\nFROM {src} AS s\nWHERE s.Is_Active = 1"
            self._table(qn, "Semantic", roles=("View",) if want_view else (), viewDefinition=definition,
                        sttmLink=f"https://lsc.sharepoint.com/sites/DataPlatform/Views/{qn}.sql" if definition else None,
                        tableauReportEntity=f"{entity.replace('_', ' ')} extract" if definition else None)
            (views if want_view else plain).append(qn)
            self.entity_of[qn] = entity
        self.views = views
        lineage_views = self.rng.sample([v for v in views if v.lower() not in KNOWN_LINEAGE_GAPS], 760)
        self.lineage_views = lineage_views
        for v in lineage_views:
            c.link("Table", "DERIVED_FROM", "Table", v, self._silver_for(v))
            if self.rng.random() < 0.08:
                c.link("Table", "DERIVED_FROM", "Table", v, self._silver_for(v))
        for v in self.rng.sample(lineage_views, 19):
            area = area_of[v.split(".", 1)[0]]
            c.link("Table", "DERIVED_FROM", "Table", v,
                   self.rng.choice([g for g in self.gold if self.gold_area_of[g] == area] or self.gold))
        for v in self.rng.sample(lineage_views, 48):
            other = self.rng.choice([w for w in views if self.entity_of[w] == self.entity_of[v]] or views)
            if other != v:
                c.link("Table", "DERIVED_FROM", "Table", v, other)

    # --- consumption and governance ----------------------------------------

    def _expression(self, view: str, columns: list[str]) -> str:
        schema, item = view.split(".", 1)
        cols = ", ".join(f'"{col}"' for col in columns)
        return (f'let\n    Source = Sql.Database("{IDP_SERVER}", "lsc_idp"),\n'
                f'    Nav = Source{{[Schema="{schema}", Item="{item}"]}}[Data],\n'
                f'    Selected = Table.SelectColumns(Nav, {{{cols}}})\nin\n    Selected')

    def _view_columns(self, view: str) -> list[str]:
        if self.columns.get(view):
            return [q.rsplit(".", 1)[1] for q in self.columns[view]]
        entity = view.split(".", 1)[1].split("_vw")[0].split("_Agg")[0]
        cols = [f"{entity.split('_')[0]}_Key", f"{entity.split('_')[0]}_Name", "Facility_Key", "Posting_Date"]
        cols += [m for m, _ in self.rng.sample(MEASURES, 2)]
        if self.rng.random() < 0.3:
            cols.append("Timestamp")
        return cols

    def _report(self, name: str, area: str, with_url: bool = True) -> str:
        url = f"https://app.powerbi.com/groups/{self.uid()}/reports/{self.uid()}" if with_url else None
        key = url or f"name:{name}"
        self.cat.add("Report", key, name=name, webUrl=url, workspaceName=f"LSC - {area}" if url else None,
                     connectionType=self.rng.choice(["DirectQuery", "Import", "Import", "LiveConnection"]),
                     source="Power BI Scanner API" if url else "Legacy report inventory",
                     state=self.rng.choice(["Active", "Active", "Active", "Deprecated"]) if self.rng.random() < 0.7 else None,
                     lastSeen=self.past(30, 0) if url else None,
                     sourceFile="Legacy_Report_Inventory.xlsx" if not url else None,
                     createdAt=self.past(), updatedAt=self.past(30))
        self.reports.append(key)
        self.report_names[key] = name
        return key

    def build_reports(self) -> None:
        c = self.cat
        names = set()
        areas = list(BUSINESS_AREAS)
        entity_pool = sorted({e for es in ENTITIES.values() for e in es})
        signature = iter(SIGNATURE_REPORTS)
        while len(self.reports) < 2623:
            area = self.rng.choice(areas)
            entity = self.rng.choice(entity_pool).replace("_", " ")
            region = self.rng.choice(["", "", "", " Lagos", " North", " Export", " West Africa", " Europe", " Americas"])
            name = f"{entity} {self.rng.choice(REPORT_KINDS)}{region}"
            if self.rng.random() < 0.15:
                name = f"{area} {name}"
            elif not region:
                name = f"LSC {name}"
            name = next(signature, name)
            if name in names:
                name = f"{name} v{self.rng.randint(2, 4)}"
            if name in names:
                continue
            names.add(name)
            key = self._report(name, area, with_url=self.rng.random() < 0.947)
            with_expr = bool(c.nodes["Report"][key].get("webUrl"))
            pool = [v for v in self.lineage_views if self.entity_of[v] in SIGNATURE_REPORTS.get(name, ())] or self.lineage_views
            for view in self.rng.sample(pool, min(len(pool), self.rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9]))):
                c.link("Report", "CONSUMES", "Table", key, view,
                       expression=self._expression(view, self._view_columns(view)) if with_expr else None,
                       source="Power BI Scanner API" if with_expr else None,
                       lastSeen=self.past(30, 0) if with_expr else None)
        for key in self.rng.sample(self.reports, 197):
            c.link("Report", "BELONGS_TO", "CapabilityDataDomain", key, self.rng.choice(self.cdds))
        for t in self.rng.sample(self.silver + self.gold, 176):
            c.link("Table", "BELONGS_TO", "CapabilityDataDomain", t, self.rng.choice(self.cdds))

    def build_governance(self) -> None:
        c = self.cat
        products = [("Rack Margin Analytics", "Wholesale Marketing"), ("Rack Price Batch Monitoring", "Rack Pricing"),
                    ("Customer 360", "Customer & Market"), ("Branded Dealer Insights", "Branded Marketing"),
                    ("Unbranded Spot Sales", "Unbranded Marketing"), ("Renewable Diesel Margin", "Renewable Fuels Marketing"),
                    ("Tank & Terminal Visibility", "Terminal Ops"), ("Pipeline Nomination Control", "Pipeline & Marine Logistics"),
                    ("Refinery Reliability", "Maintenance & Reliability"), ("Product Certification", "Product Quality"),
                    ("Working Capital", "Credit & Collections"), ("Supplier Performance", "Procurement & Sourcing")]
        for name, cdd in products:
            c.add("DataProduct", name, sourceFile="LSC_Data_Products_2026.xlsx", createdAt=self.past())
            c.link("DataProduct", "BELONGS_TO", "CapabilityDataDomain", name, cdd)
        while len(c.rels[("DataProduct", "REALIZED_BY", "Table")]) < 351:
            c.link("DataProduct", "REALIZED_BY", "Table", self.rng.choice(products)[0], self.rng.choice(self.views))
        mdd_targets = self.silver + self.gold + self.tables_by_layer["Operational"]
        while len(c.rels[("MasterDataDomain", "REALIZED_IN", "Table")]) < 160:
            c.link("MasterDataDomain", "REALIZED_IN", "Table", self.rng.choice(MASTER_DATA), self.rng.choice(mdd_targets))

        pipelines = [("PL_Wholesale_Margin", "DF_Wholesale_Margin", None), ("PL_Wholesale_Price_Batch", "DF_Price_Batch", None),
                     ("PL_Refining_Yields", "DF_Unit_Yields", "Unit_Yield_Accounting.yxmd"),
                     ("PL_Renewables_Feedstock", "DF_Feedstock_CI", "Feedstock_CI.yxmd"),
                     ("PL_Trading_Positions", "DF_Trade_Positions", "Trade_Positions.yxmd"),
                     ("PL_Logistics_Tariffs", "DF_Tariff_Cost", "Tariff_Accrual.yxmd"),
                     ("PL_Logistics_Tanks", "DF_Tank_Inventory", "Tank_Inventory.yxmd")]
        for name, flow, alteryx in pipelines:
            c.add("DataPipeline", name, synapseDataflow=flow, alteryxWorkflow=alteryx,
                  sourceFile="LSC_Synapse_Pipeline_Inventory.xlsx", createdAt=self.past())
        replicas = self.tables_by_layer["Replica"]
        for name, _, _ in pipelines[2:]:
            for rep in self.rng.sample(replicas, 5):
                c.link("DataPipeline", "READS", "Table", name, rep)
            c.link("DataPipeline", "LOADS", "Table", name, self.rng.choice(self.gold))
        while len(c.rels[("DataPipeline", "LOADS", "Table")]) < 7:
            c.link("DataPipeline", "LOADS", "Table", self.rng.choice(pipelines[2:])[0], self.rng.choice(self.gold))

        model_systems = [n for n, _, _ in CORE_SYSTEMS[1:12]] + ["RightAngle", "Profisee", "SAP_S4"]
        n_models = 0
        for cdd in self.cdds:
            for kind in ("Conceptual", "Logical"):
                if n_models >= 40 or self.rng.random() < 0.3:
                    continue
                name = f"{cdd.replace(' & ', '_').replace(' ', '_')}_{kind}_Data_Model_v{self.rng.randint(1, 3)}"
                c.add("DataModel", name, fileName=f"{name}.DM1", modelType=kind,
                      folderLink=f"https://lsc.sharepoint.com/sites/DataArchitecture/Models/{name}",
                      sourceFile="LSC_ER_Studio_Model_Inventory.xlsx", createdAt=self.past())
                if n_models < 36:
                    c.link("DataModel", "MODELS", "CapabilityDataDomain", name, cdd)
                if n_models % 2 == 0 and len(c.rels[("DataModel", "BELONGS_TO", "DataSystem")]) < 18:
                    c.link("DataModel", "BELONGS_TO", "DataSystem", name, self.rng.choice(model_systems))
                n_models += 1

        people = list(c.nodes["Person"])
        scopes = [("Report", k, self.report_names[k]) for k in self.rng.sample(self.reports, 1515)]
        scopes += [("Table", t, t) for t in self.rng.sample(self.views + self.gold + self.silver, 799)]
        for label, target, scope in scopes:
            role = "Data Analyst" if self.rng.random() < 0.7 else "Data Analyst Backup"
            key = (role, scope)
            c.add("RoleAssignment", key, type=role, status="Active" if self.rng.random() < 0.93 else "Pending",
                  createdAt=self.past(365))
            c.link("RoleAssignment", "APPLIES_TO", label, key, target)
            c.link("Person", "HAS_ROLE", "RoleAssignment", self.rng.choice(people), key)
            if self.rng.random() < 0.05:
                c.link("Person", "HAS_ROLE", "RoleAssignment", self.rng.choice(people), key)

    # --- competency paths ---------------------------------------------------

    def plant_competency_paths(self) -> None:
        c = self.cat
        m = self.manifest
        # Margin chain: Helios -> replica -> udm_core -> wholesale_core -> sem_wholesale -> reports (questions 3, 4, 5, 8, 9).
        op = self._table("Helios.MarginDetail", "Operational")
        c.link("DataSystem", "CONTAINS", "Table", "Helios", op)
        rep = self._table("replica_helios.Margin_Detail", "Replica", source_file="STTM_Helios_Replica.xlsx")
        c.link("Table", "REPLICATED_TO", "Table", op, rep)
        silver = self._table("udm_core.Helios_Margin_Fact", "Silver", roles=("Fact",), source_file="STTM_Helios_Margin.xlsx")
        gold = self._table("wholesale_core.Margin_Fact", "Gold", roles=("Fact",), source_file="STTM_wholesale_core_Margin_Fact.xlsx")
        view = self._table("sem_wholesale.Margin_vw", "Semantic", roles=("View",),
                           viewDefinition="CREATE VIEW sem_wholesale.Margin_vw AS\nSELECT m.*\nFROM wholesale_core.Margin_Fact AS m")
        c.link("Table", "DERIVED_FROM", "Table", silver, rep)
        c.link("Table", "DERIVED_FROM", "Table", gold, silver)
        c.link("Table", "DERIVED_FROM", "Table", view, gold)
        cols = {rep: ["MRGN_AMT", "CUST_NO", "PROD_CD", "FCLTY_CD", "PSTG_DT"],
                silver: ["Margin_Amount", "Customer_Key", "Product_Key", "Facility_Key", "Posting_Date"],
                gold: ["Margin_Amount", "Customer_Key", "Product_Key", "Facility_Key", "Posting_Date"]}
        for table, names in cols.items():
            for name in names:
                qn = f"{table}.{name}"
                c.add("Column", qn, name=name, dataType="decimal(19,2)" if "AMT" in name or "Amount" in name else "varchar(30)",
                      keyType="FK" if name.endswith("_Key") else None, sourceFile=f"STTM_{table.split('.', 1)[1]}.xlsx")
                c.link("Table", "HAS_COLUMN", "Column", table, qn)
                self.columns[table].append(qn)
        for up, down in ((rep, silver), (silver, gold)):
            for a, b in zip(cols[up], cols[down]):
                c.link("Column", "DERIVED_FROM", "Column", f"{down}.{b}", f"{up}.{a}")
        c.nodes["Column"][f"{silver}.Margin_Amount"]["transformation"] = f"CAST({rep}.MRGN_AMT AS decimal(19,2))"
        margin_reports = [self._report("Rack Margin Dashboard", "Wholesale Marketing"),
                          self._report("Customer Profitability Scorecard", "Wholesale Marketing")]
        for key in margin_reports:
            c.link("Report", "CONSUMES", "Table", key, view,
                   expression=self._expression(view, ["Margin_Amount", "Customer_Key", "Product_Key", "Posting_Date"]),
                   source="Power BI Scanner API", lastSeen=self.past(10, 0))
            c.link("Report", "BELONGS_TO", "CapabilityDataDomain", key, "Wholesale Marketing")
        c.link("DataProduct", "REALIZED_BY", "Table", "Rack Margin Analytics", view)
        c.link("DataPipeline", "READS", "Table", "PL_Wholesale_Margin", rep)
        c.link("DataPipeline", "LOADS", "Table", "PL_Wholesale_Margin", gold)

        # Product dimension: master data and legacy refactor (questions 6, 7).
        product = self._table("wholesale_core.Product_Dim", "Gold", roles=("Dimension",), source_file="STTM_wholesale_core_Product_Dim.xlsx")
        c.link("Table", "DERIVED_FROM", "Table", product, self.rng.choice(self.silver))
        c.link("MasterDataDomain", "REALIZED_IN", "Table", "Product", product)
        legacy = self._table("dwh.LSC_Product_Master", "Silver", source_file="Legacy_DWH_Inventory.xlsx")
        c.link("Table", "REFACTORED_TO", "Table", legacy, product)

        # Price batch: view loaded through a gold dim that a pipeline loads (question 15).
        pb_rep = self._table("replica_helios.Price_Batch", "Replica", source_file="STTM_Helios_Replica.xlsx")
        pb_op = self._table("Helios.PriceBatch", "Operational")
        c.link("DataSystem", "CONTAINS", "Table", "Helios", pb_op)
        c.link("Table", "REPLICATED_TO", "Table", pb_op, pb_rep)
        pb_gold = self._table("wholesale_core.Price_Batch_Dim", "Gold", roles=("Dimension",), source_file="STTM_wholesale_core_Price_Batch_Dim.xlsx")
        pb_view = self._table("sem_wholesale.Price_Batch_Dim_vw", "Semantic", roles=("View",),
                              viewDefinition="CREATE VIEW sem_wholesale.Price_Batch_Dim_vw AS\nSELECT b.*\nFROM wholesale_core.Price_Batch_Dim AS b")
        c.link("Table", "DERIVED_FROM", "Table", pb_gold, pb_rep)
        c.link("Table", "DERIVED_FROM", "Table", pb_view, pb_gold)
        c.link("DataPipeline", "READS", "Table", "PL_Wholesale_Price_Batch", pb_rep)
        c.link("DataPipeline", "LOADS", "Table", "PL_Wholesale_Price_Batch", pb_gold)
        c.link("DataProduct", "REALIZED_BY", "Table", "Rack Price Batch Monitoring", pb_view)
        pb_report = self._report("Rack Price Batch Monitor", "Wholesale Marketing")
        c.link("Report", "CONSUMES", "Table", pb_report, pb_view,
               expression=self._expression(pb_view, ["Price_Batch_Key", "Batch_Date", "Price_List_Key", "Timestamp"]),
               source="Power BI Scanner API", lastSeen=self.past(10, 0))

        # Transaction type: RightAngle source moving to Profisee (question 14).
        tt_op = self._table("RightAngle.TransactionType", "Operational")
        c.link("DataSystem", "CONTAINS", "Table", "RightAngle", tt_op)
        tt_rep = self._table("replica_rightangle.Transaction_Type", "Replica", source_file="STTM_RightAngle_Replica.xlsx")
        c.link("Table", "REPLICATED_TO", "Table", tt_op, tt_rep)
        tt_dim = self._table("mdm_core.RightAngle_Transaction_Type_Dim", "Silver", roles=("Dimension",),
                             source_file="STTM_RightAngle_Transaction_Type.xlsx")
        c.link("Table", "DERIVED_FROM", "Table", tt_dim, tt_rep)
        prof = self._table("Profisee.TransactionType", "Operational", comment="Planned replacement source for transaction types.")
        c.link("DataSystem", "CONTAINS", "Table", "Profisee", prof)
        tt_view = self._table("sem_masterdata.TransactionType_vw", "Semantic", roles=("View",),
                              viewDefinition="CREATE VIEW sem_masterdata.TransactionType_vw AS\nSELECT t.*\nFROM mdm_core.RightAngle_Transaction_Type_Dim AS t")
        c.link("Table", "DERIVED_FROM", "Table", tt_view, tt_dim)
        view_cols = ["Transaction_Type_Key", "Transaction_Type_Code", "Transaction_Type_Name", "Is_Active", "Timestamp"]
        for name in view_cols:
            for table in (tt_dim, tt_view):
                qn = f"{table}.{name}"
                c.add("Column", qn, name=name, dataType="datetime2" if name == "Timestamp" else "varchar(50)",
                      sourceFile="STTM_RightAngle_Transaction_Type.xlsx")
                c.link("Table", "HAS_COLUMN", "Column", table, qn)
            c.link("Column", "DERIVED_FROM", "Column", f"{tt_view}.{name}", f"{tt_dim}.{name}")
        with_ts = self._report("Trading Deal Activity", "Wholesale Marketing")
        without_ts = self._report("Transaction Type Reference", "Corporate IT")
        c.link("Report", "CONSUMES", "Table", with_ts, tt_view,
               expression=self._expression(tt_view, ["Transaction_Type_Key", "Transaction_Type_Name", "Timestamp"]),
               source="Power BI Scanner API", lastSeen=self.past(10, 0))
        c.link("Report", "CONSUMES", "Table", without_ts, tt_view,
               expression=self._expression(tt_view, ["Transaction_Type_Code", "Transaction_Type_Name", "Is_Active"]),
               source="Power BI Scanner API", lastSeen=self.past(10, 0))

        # Helios data models (question 11).
        helios_models = ["Helios_Conceptual_Data_Model_v2", "Helios_Logical_Data_Model_v3"]
        for name, kind in zip(helios_models, ("Conceptual", "Logical")):
            c.add("DataModel", name, fileName=f"{name}.DM1", modelType=kind,
                  folderLink=f"https://lsc.sharepoint.com/sites/DataArchitecture/Models/{name}",
                  sourceFile="LSC_ER_Studio_Model_Inventory.xlsx", createdAt=self.past())
            c.link("DataModel", "BELONGS_TO", "DataSystem", name, "Helios")
            c.link("DataModel", "MODELS", "CapabilityDataDomain", name, "Wholesale Marketing")

        gold_count = len(self.tables_by_layer["Gold"])
        wholesale = sorted(t for (s, t) in c.rels[("Schema", "CONTAINS", "Table")] if s == "wholesale_core")
        m.update({
            "q01_gold_table_count": gold_count,
            "q02_wholesale_core_tables": wholesale,
            "q03_margin_replica_source": rep,
            "q04_margin_amount_sources": [f"{silver}.Margin_Amount", f"{rep}.MRGN_AMT"],
            "q05_margin_view_reports": sorted(self.report_names[k] for k in margin_reports),
            "q06_product_master_data_domain": "Product",
            "q07_product_legacy_source": legacy,
            "q08_margin_data_product": {"dataProduct": "Rack Margin Analytics", "capabilityDataDomain": "Wholesale Marketing"},
            "q09_margin_pipeline": "PL_Wholesale_Margin",
            "q11_helios_data_models": helios_models,
            "q14_transaction_type_reports": sorted([self.report_names[with_ts], self.report_names[without_ts]]),
            "q14_reports_using_timestamp": [self.report_names[with_ts]],
            "q15_price_batch_gold_table": pb_gold,
            "q15_price_batch_pipeline": "PL_Wholesale_Price_Batch",
        })

    # --- portal chat history -----------------------------------------------

    def build_chat(self) -> None:
        c = self.cat
        templates = [
            ("Show the full lineage of {view}", "MATCH upPath = (sem:Table {{qualifiedName: '{view}'}})-[:DERIVED_FROM*1..5]->(up:Table) RETURN upPath",
             "{view} is built from {n} upstream tables across Gold, Silver and Replica."),
            ("Which reports consume {view}?", "MATCH (r:Report)-[c:CONSUMES]->(t:Table {{qualifiedName: '{view}'}}) RETURN r, c, t",
             "{n} reports consume {view}."),
            ("How many tables are in {schema}?", "MATCH (s:Schema {{qualifiedName: '{schema}'}})-[:CONTAINS]->(t:Table) RETURN count(t) AS tables",
             "{schema} contains {n} tables."),
            ("What columns does {table} have?", "MATCH (t:Table {{qualifiedName: '{table}'}})-[h:HAS_COLUMN]->(c:Column) RETURN t, h, c",
             "{table} has {n} columns."),
            ("Who is the data analyst for {report}?", "MATCH (p:Person)-[:HAS_ROLE]->(ra:RoleAssignment {{scope: '{report}'}}) RETURN p.name, ra.type",
             "{report} has {n} assigned analysts."),
            ("Which master data domain covers {table}?", "MATCH (m:MasterDataDomain)-[r:REALIZED_IN]->(t:Table {{qualifiedName: '{table}'}}) RETURN m, r, t",
             "No master data domain is realized in {table}."),
            ("List the data products in {cdd}", "MATCH (dp:DataProduct)-[b:BELONGS_TO]->(c:CapabilityDataDomain {{name: '{cdd}'}}) RETURN dp, b, c",
             "{cdd} owns {n} data products."),
            ("Which systems replicate into {schema}?", "MATCH (ds:DataSystem)-[:CONTAINS]->(op:Table)-[:REPLICATED_TO]->(r:Table)<-[:CONTAINS]-(:Schema {{qualifiedName: '{schema}'}}) RETURN DISTINCT ds.name",
             "{schema} is fed by {n} source systems."),
        ]
        poor_comments = ["Wrong layer, I asked for Gold.", "Returned a Replica table, not the view.", "Missing the reports.",
                         "Graph was empty.", "It guessed the schema name.", "Too many nodes to read.",
                         "Did not include the pipeline.", "Answer said zero but the view exists.",
                         "Lineage stopped at Silver.", "Wrong data system."]
        good_comments = ["Exactly what I needed.", "Clear lineage.", "Helpful for the impact review.", None, None]
        sessions = []
        messages = 0
        feedback_slots = ["poor"] * 10 + ["good"] * 20 + [None] * 170
        self.rng.shuffle(feedback_slots)
        cuts = sorted(self.rng.sample(range(1, 200), 49))
        session_turns = [b - a for a, b in zip([0, *cuts], [*cuts, 200])]
        for turns in session_turns:
            sid = self.uid()
            sessions.append(sid)
            c.add("Session", sid)
            start = self.today - timedelta(days=self.rng.randint(1, 21), hours=self.rng.randint(0, 10))
            prev = None
            for t in range(turns):
                q_tpl, cy_tpl, a_tpl = self.rng.choice(templates)
                fill = {"view": self.rng.choice(self.views), "schema": self.rng.choice(list(c.nodes["Schema"])),
                        "table": self.rng.choice(self.silver + self.gold), "report": self.report_names[self.rng.choice(self.reports)],
                        "cdd": self.rng.choice(self.cdds), "n": self.rng.randint(0, 14)}
                fb = feedback_slots[messages]
                mid = self.uid()
                c.add("Message", mid, question=q_tpl.format(**fill), cypher=cy_tpl.format(**fill), answer=a_tpl.format(**fill),
                      feedback=fb, feedbackComment=self.rng.choice(poor_comments) if fb == "poor" else (self.rng.choice(good_comments) if fb else None),
                      timestamp=_iso(start + timedelta(minutes=3 * t + self.rng.randint(0, 2))))
                c.link("Session", "HAS_MESSAGE", "Message", sid, mid)
                if prev:
                    c.link("Message", "NEXT", "Message", prev, mid)
                prev = mid
                messages += 1
            c.link("Session", "LAST_MESSAGE", "Message", sid, prev)
        self.manifest.update({
            "q12_messages_with_feedback": 30,
            "q13_poor_feedback_count": 10,
            "sessions": len(sessions),
            "messages": messages,
        })

    def build_powerbi_workspace(self) -> None:
        """Rows a Power BI workspace export would hold, with the catalog aligned to what load_powerbi_lineage writes.

        A URL report with at least one Power M expression becomes a PowerBI_Workspace report, so the
        loader's prune keeps it. Every 40th such report names its creator. Loading source.duckdb over
        the catalog then changes no counts.
        """
        c = self.cat
        consumes = c.rels[("Report", "CONSUMES", "Table")]
        by_report: dict[str, list[str]] = defaultdict(list)
        for (report, view), props in consumes.items():
            if props.get("expression"):
                by_report[report].append(view)
        area_of = {s: ba for (s, ba) in c.rels[("Schema", "BELONGS_TO", "BusinessArea")] if s.startswith("sem_")}
        people = sorted(c.nodes["Person"])
        report_rows, table_rows = [], []
        for n, report in enumerate(sorted(r for r in by_report if c.nodes["Report"][r].get("webUrl"))):
            props = c.nodes["Report"][report]
            props["source"] = "PowerBI_Workspace"
            dataset = hashlib.sha1(report.encode()).hexdigest()[:32]
            creator = None
            if n % 40 == 0:
                creator = people[int(dataset, 16) % len(people)]
                key = ("Report Creator", props["name"])
                c.add("RoleAssignment", key, type="Report Creator", status="Active")
                c.link("Person", "HAS_ROLE", "RoleAssignment", creator, key)
                c.link("RoleAssignment", "APPLIES_TO", "Report", key, report)
            report_rows.append({
                "Dataset_Id": dataset, "Report_Name": props["name"], "Creator_Principal_Display_Name": creator,
                "State_Code": props.get("state"), "Web_Url_Text": props["webUrl"],
                "Embed_Url_Text": props["webUrl"].replace("/reports/", "/reportEmbed?reportId="),
            })
            for view in sorted(by_report[report]):
                consumes[(report, view)]["source"] = "PowerBI_Workspace"
                schema, item = view.split(".", 1)
                if schema in area_of:
                    c.link("DataSystem", "BELONGS_TO", "BusinessArea", IDP, area_of[schema])
                table_rows.append({
                    "Dataset_Id": dataset, "Workspace_Name": props.get("workspaceName"), "Table_Name": item,
                    "Source_Text": consumes[(report, view)]["expression"],
                    "Connection_Type_Code": props.get("connectionType"), "Server_Name": IDP_SERVER,
                    "Database_File_Name": IDP, "Schema_Name": schema, "View_Name": item,
                })
        self.powerbi = {
            "PowerBi_Report_Dim_vw": report_rows,
            "PowerBi_Dataset_Table_Dim_vw": table_rows,
            "Schema_Business_Area_vw": [{"Schema_Name": s, "Business_Area": ba} for s, ba in sorted(area_of.items())],
        }
        self.manifest["powerbi_export"] = {name: len(rows) for name, rows in self.powerbi.items()}

    def run(self) -> Catalog:
        self.build_organisation()
        self.build_systems()
        self.build_operational_and_replica()
        self.build_silver_gold()
        self.build_legacy()
        self.build_semantic()
        self.build_reports()
        self.build_governance()
        self.plant_competency_paths()
        self.build_chat()
        self.build_powerbi_workspace()
        self.clear_known_lineage_gaps()
        return self.cat

    def clear_known_lineage_gaps(self) -> None:
        """The portal's _KNOWN_LINEAGE_GAPS names these views; they must exist and have no lineage."""
        derived = self.cat.rels[("Table", "DERIVED_FROM", "Table")]
        lookup = {t.lower(): t for t in self.cat.nodes["Table"]}
        gaps = [lookup[g] for g in KNOWN_LINEAGE_GAPS]
        for edge in [e for e in derived if e[0] in gaps]:
            del derived[edge]
        self.manifest["known_lineage_gaps"] = gaps


def write_source_db(path: Path, tables: dict[str, list[dict]]) -> None:
    """Power BI workspace export as DuckDB tables in sem_internal_x, the schema load_powerbi_lineage reads."""
    import duckdb
    import pandas as pd

    path.unlink(missing_ok=True)
    with duckdb.connect(str(path)) as con:
        con.execute("CREATE SCHEMA sem_internal_x")
        for name, rows in tables.items():
            frame = pd.DataFrame(rows, dtype="string")
            con.register("frame", frame)
            con.execute(f"CREATE TABLE sem_internal_x.{name} AS SELECT * FROM frame")
            con.unregister("frame")


def generate(out: Path, seed: int = DEFAULT_SEED, today: datetime | None = None) -> dict:
    today = today or datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
    gen = LscGenerator(seed, today)
    catalog = gen.run()
    counts = catalog.write(out)
    write_source_db(out / SOURCE_DB_NAME, gen.powerbi)
    manifest = {"company": "Lagos Refining & Supply Company (LSC)", "seed": seed, "generatedFor": today.date().isoformat(),
                "counts": counts, "expected": gen.manifest}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    manifest = generate(args.out, args.seed)
    nodes = sum(manifest["counts"]["nodes"].values())
    rels = sum(manifest["counts"]["rels"].values())
    print(f"Wrote {nodes} nodes and {rels} relationships to {args.out}")


if __name__ == "__main__":
    main()
