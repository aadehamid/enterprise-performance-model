import pandas as pd

from load_lineage import extract_lineage_pairs, extract_sttm_lineage
from load_reports import extract_consumes_pairs
from load_semantic_views import route_direct_replica
from load_sttm import MERGE_COL_DERIVED_FROM_QUERY, source_columns


def test_sttm_column_sources_pair_schema_table_and_field_by_position():
    assert source_columns(
        "mdm_core, udm_core", "LOCModel_Locations_Dim, LOCModel_Shift_Model_Parameters_Fact", "Location_Name, Source_Location_Id"
    ) == [
        ("mdm_core", "LOCModel_Locations_Dim", "Location_Name"),
        ("udm_core", "LOCModel_Shift_Model_Parameters_Fact", "Source_Location_Id"),
    ]


def test_sttm_column_source_single_field_applies_to_every_table():
    assert source_columns("replica_tmr", "TMR_YTD_Customer_Brand, TMR_YTD_Customer_Whsl", "Customer_ID") == [
        ("replica_tmr", "TMR_YTD_Customer_Brand", "Customer_ID"),
        ("replica_tmr", "TMR_YTD_Customer_Whsl", "Customer_ID"),
    ]


def test_sttm_column_source_schema_cell_splits_on_slash():
    assert source_columns("udm_core/ mdm_core", "History_Fact, Org_Dim", "Org_Code, Org_Code") == [
        ("udm_core", "History_Fact", "Org_Code"),
        ("mdm_core", "Org_Dim", "Org_Code"),
    ]


def test_sttm_column_source_takes_the_listed_schema_the_table_already_lives_in():
    known = {"mdm_core.marketing_dashboard_location_dim", "udm_core.marketing_dashboard_forecast_capture_history_fact"}
    assert source_columns(
        "udm_core/ mdm_core",
        "Marketing_Dashboard_Location_Dim, Marketing_Dashboard_Forecast_Capture_History_Fact",
        "Location_Long_Name, Forecast_Location_Name",
        known_tables=known,
    ) == [
        ("mdm_core", "Marketing_Dashboard_Location_Dim", "Location_Long_Name"),
        ("udm_core", "Marketing_Dashboard_Forecast_Capture_History_Fact", "Forecast_Location_Name"),
    ]


def test_sttm_column_source_skips_generated_and_na():
    assert source_columns("ETL Generated", "X", "Y") == []
    assert source_columns("ETL", "TextInput", "Area") == []
    assert source_columns("ETL", "Derived", "ETL Generated") == []
    assert source_columns("replica_tmr", "NA", "Y") == []
    assert source_columns("replica_tmr", "T", "") == []


def test_semantic_replica_uses_the_single_existing_parent():
    silver, replica = route_direct_replica(
        ["replica_kittyhawk.Transfer", "replica_crossreference.XRefs"],
        {"replica_kittyhawk.Transfer": ["udm_core.Kittyhawk_Transfer_Fact"]},
    )
    assert silver == ["udm_core.Kittyhawk_Transfer_Fact"]
    assert replica == ["replica_crossreference.XRefs"]


def test_semantic_replica_stays_when_two_parents_exist():
    silver, replica = route_direct_replica(
        ["replica_kittyhawk.Deal"],
        {"replica_kittyhawk.Deal": ["udm_core.Kittyhawk_Deal_Fact", "mdm_core.TMR_RW_Deal_Detail_Dim"]},
    )
    assert silver == []
    assert replica == ["replica_kittyhawk.Deal"]


def test_sttm_column_source_does_not_emit_a_comma_joined_name():
    triples = source_columns(
        "replica_eis, replica_mpr",
        "weekday, PriceDetail",
        "calendar_date, EffectiveStartDate, EffectiveEndDate,",
    )
    assert triples == [
        ("replica_eis", "weekday", "calendar_date"),
        ("replica_mpr", "PriceDetail", "EffectiveStartDate"),
    ]
    assert all("," not in ".".join(triple) for triple in triples)


def test_sttm_multi_schema_source_pairs_schema_and_table_by_position():
    sttm = pd.DataFrame(
        {
            "Physical Table Name": ["udm_core.LOCModel_Shift_Model_Performance_Summary_Fact"] * 2,
            "Source": ["mdm_core, udm_core", "replica_tmr"],
            "Source Table Name": ["LOCModel_Locations_Dim, LOCModel_Shift_Model_Parameters_Fact", "A, B"],
        }
    )
    _, sources = extract_sttm_lineage(sttm)
    assert sources == {
        "mdm_core.LOCModel_Locations_Dim",
        "udm_core.LOCModel_Shift_Model_Parameters_Fact",
        "replica_tmr.A",
        "replica_tmr.B",
    }


def test_sttm_column_level_sources_are_not_table_lineage():
    sttm = pd.DataFrame(
        {
            "Physical Table Name": ["udm_core.X_Fact"] * 2,
            "Source": ["config", "replica_tmr"],
            "Source Table Name": ["Lookup", "T"],
        }
    )
    assert extract_sttm_lineage(sttm)[1] == {"replica_tmr.T"}


def test_mapping_pairs_strip_invisible_characters():
    mapping = pd.DataFrame(
        {
            "Semantic View / Direct Table Connection": ["sem_commercial.Kpler_Trade_vw\u200b"],
            "UDM Table": ["udm_core.Kpler_Trade_Fact\nNo Insight"],
            "IDP Replica Entities": ["replica_kpler.Trades, replica_kpler.Vessels"],
        }
    )
    assert extract_lineage_pairs(mapping) == {
        ("sem_commercial.Kpler_Trade_vw", "udm_core.Kpler_Trade_Fact"),
        ("udm_core.Kpler_Trade_Fact", "replica_kpler.Trades"),
        ("udm_core.Kpler_Trade_Fact", "replica_kpler.Vessels"),
    }


def test_direct_connection_tables_split_on_commas():
    mapping = pd.DataFrame(
        {
            "Report": ["NGP Econ Reporting Dashboard"],
            "Live Report or Connected to IDP?": ["Live"],
            "If No IDP, Source System?": ["Refining_OLAP"],
            "Semantic View / Direct Table Connection": ["planningCategories, pimsResults"],
        }
    )
    assert extract_consumes_pairs(mapping) == {
        ("NGP Econ Reporting Dashboard", "Refining_OLAP.planningCategories", "Operational"),
        ("NGP Econ Reporting Dashboard", "Refining_OLAP.pimsResults", "Operational"),
    }


def test_sttm_source_stub_takes_its_schema_layer(graph):
    rows = [
        {"tgtColQN": f"__pytest__.tgt.c{i}", "srcColQN": f"{schema}.__pytest_stub__.c", "srcColName": "c",
         "srcTableQN": f"{schema}.__pytest_stub__", "srcTableName": "__pytest_stub__",
         "srcSchemaQN": schema if schema != "-" else None, "sourceFile": "pytest"}
        for i, schema in enumerate(["mdm_core", "udm_core", "replica_kh", "commercial_core", "-"])
    ]
    with graph.driver.session(database=graph.database) as session:
        tx = session.begin_transaction()
        try:
            tx.run(MERGE_COL_DERIVED_FROM_QUERY, rows=rows).consume()
            layers = {r["qn"]: r["layer"] for r in tx.run(
                "MATCH (t:Table) WHERE t.name = '__pytest_stub__' RETURN t.qualifiedName AS qn, t.layer AS layer")}
        finally:
            tx.rollback()
    assert layers == {
        "mdm_core.__pytest_stub__": "Silver",
        "udm_core.__pytest_stub__": "Silver",
        "replica_kh.__pytest_stub__": "Replica",
        "commercial_core.__pytest_stub__": "Gold",
        "-.__pytest_stub__": "Replica",
    }