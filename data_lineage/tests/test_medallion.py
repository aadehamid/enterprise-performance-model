import pytest

from medallion import (
    cypher_is_legacy_schema,
    cypher_schema_layer,
    flag_bool,
    is_idp_schema,
    is_legacy,
    is_legacy_schema,
    report_key,
    resolve_report_key,
    schema_layer,
    stamp_report_keys,
)

AGENTS_MD_LAYER_RULES = [
    ("udm_core", "Silver"),
    ("mdm_core", "Silver"),
    ("replica_tmr", "Replica"),
    ("replica", "Replica"),
    ("sem_commercial", "Semantic"),
    ("sem_masterdata", "Semantic"),
    ("commercial_core", "Gold"),
    ("kpi_core", "Gold"),
    ("corporate_services_core", "Gold"),
    ("KH_Core", "Silver"),
    ("dwh", "Silver"),
    ("dwh_core", "Silver"),
    ("dwh_intelex_core", "Silver"),
    ("persistence", "Silver"),
    ("staging", "Silver"),
    ("sem_comm_kh_mpc_rstd", "Semantic"),
    ("dbo", None),
    ("TMR", None),
    ("", None),
    (None, None),
]


@pytest.mark.parametrize(("schema", "layer"), AGENTS_MD_LAYER_RULES)
def test_schema_layer_follows_agents_md(schema, layer):
    assert schema_layer(schema) == layer


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Yes", True),
        ("Y", True),
        ("yes", True),
        ("true", True),
        ("No", False),
        ("NO", False),
        ("N", False),
        ("false", False),
        (True, True),
        (False, False),
        (None, None),
        ("", None),
        ("nan", None),
        ("Maybe", "Maybe"),
    ],
)
def test_flag_bool_maps_yes_no_and_leaves_other_values(value, expected):
    assert flag_bool(value) == expected


def test_flag_bool_nan_is_null():
    assert flag_bool(float("nan")) is None


def test_report_key_uses_the_url_or_the_name():
    assert report_key("Margin", " https://app/margin ") == "https://app/margin"
    assert report_key("Margin", None) == "name:Margin"
    assert report_key("Margin", "  ") == "name:Margin"
    assert report_key("Margin", float("nan")) == "name:Margin"


def test_resolve_report_key_reuses_the_stored_url_when_the_row_has_no_url():
    stored = {"Margin": "https://app/margin"}
    assert resolve_report_key("Margin", None, stored) == "https://app/margin"
    assert resolve_report_key("Margin", "https://app/other", stored) == "https://app/other"
    assert resolve_report_key("New", None, stored) == "name:New"


def test_stamp_report_keys_writes_the_key_field():
    rows = [{"name": "Margin"}, {"Report_Name": "New", "Web_Url_Text": "https://app/new"}]
    stamp_report_keys(rows[:1], {"Margin": "https://app/margin"}, "name")
    stamp_report_keys(rows[1:], {}, "Report_Name", "Web_Url_Text")
    assert rows[0]["reportKey"] == "https://app/margin"
    assert rows[1]["reportKey"] == "https://app/new"


@pytest.mark.parametrize(
    ("qualified_name", "legacy"),
    [
        ("KH_Core.Customer", True),
        ("kh_core.Customer", True),
        ("dwh.Sales_vw", True),
        ("dwh_core.Fact", True),
        ("persistence.Location", True),
        ("staging.Load", True),
        ("sem_comm_kh_mpc_rstd.View", True),
        ("mdm_core.Currency_Union_Dim", True),
        ("udm_core.Sales_Fact", False),
        ("commercial_core.Union_Rates", False),
        ("sem_commercial.Location_Union_vw", False),
        ("NoSchemaTable", False),
    ],
)
def test_legacy_label(qualified_name, legacy):
    assert is_legacy(qualified_name) is legacy


def test_union_rule_uses_caller_layer_when_given():
    assert is_legacy("replica_eis.Location_Union_Dim_vw", layer="Semantic") is False
    assert is_legacy("APS.Location_Union", layer="Silver") is True


@pytest.mark.parametrize(
    ("schema", "idp"),
    [("replica_tmr", True), ("sem_commercial", True), ("udm_core", True), ("dwh", False), ("TMR", False)],
)
def test_idp_schema(schema, idp):
    assert is_idp_schema(schema) is idp


@pytest.mark.integration
def test_cypher_rules_match_python_for_every_schema_in_graph(graph):
    schemas = [r["s"] for r in graph.run_query("MATCH (t:Table) RETURN DISTINCT split(t.qualifiedName, '.')[0] AS s")]
    schemas += [s for s, _ in AGENTS_MD_LAYER_RULES if s]
    rows = graph.run_query(
        f"UNWIND $schemas AS s RETURN s, {cypher_schema_layer('s', 'Operational')} AS layer, "
        f"{cypher_is_legacy_schema('s')} AS legacy",
        schemas=schemas,
    )
    mismatches = [
        r for r in rows
        if r["layer"] != (schema_layer(r["s"]) or "Operational") or r["legacy"] != is_legacy_schema(r["s"])
    ]
    assert len(rows) == len(schemas) > 250
    assert mismatches == []
