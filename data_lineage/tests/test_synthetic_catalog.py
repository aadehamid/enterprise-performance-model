import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pytest
from neo4j.exceptions import ClientError

from generate_shareable_catalog import KNOWN_LINEAGE_GAPS, SOURCE_DB_NAME, generate
from load_synthetic_catalog import INGEST_PATH, assert_safe_target, count_mismatches, create_constraint, parse_steps
from verify_synthetic_catalog import QUESTIONS_PATH, expected_value, leak_failures, profile_failures, report_lineage_failures

MODEL_PATH = Path(__file__).resolve().parents[1] / "synthetic" / "lsc_data_model.json"
TODAY = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def catalog(tmp_path_factory):
    out = tmp_path_factory.mktemp("lsc")
    return out, generate(out, seed=26, today=TODAY)


@pytest.fixture(scope="module")
def steps():
    return parse_steps(INGEST_PATH.read_text(encoding="utf-8"))


def _files(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name != SOURCE_DB_NAME
    }


def _source_tables(root: Path) -> dict[str, list[tuple]]:
    with duckdb.connect(str(root / SOURCE_DB_NAME), read_only=True) as con:
        names = [r[0] for r in con.sql("SELECT table_name FROM information_schema.tables ORDER BY 1").fetchall()]
        return {n: sorted(con.sql(f"SELECT * FROM sem_internal_x.{n}").fetchall(), key=str) for n in names}


def test_same_seed_writes_identical_files(catalog, tmp_path):
    out, _ = catalog
    generate(tmp_path, seed=26, today=TODAY)
    assert _files(tmp_path) == _files(out)
    assert _source_tables(tmp_path) == _source_tables(out)


def test_powerbi_export_covers_every_workspace_report_and_edge(catalog):
    out, manifest = catalog
    rows = lambda label: [json.loads(line) for line in (out / label).read_text(encoding="utf-8").splitlines()]
    workspace_reports = {r["reportKey"] for r in rows("nodes/Report.jsonl") if r.get("source") == "PowerBI_Workspace"}
    workspace_edges = [r for r in rows("rels/Report-CONSUMES-Table.jsonl") if r.get("source") == "PowerBI_Workspace"]
    tables = _source_tables(out)
    assert len(tables["PowerBi_Report_Dim_vw"]) == len(workspace_reports) == manifest["expected"]["powerbi_export"]["PowerBi_Report_Dim_vw"]
    assert len(tables["PowerBi_Dataset_Table_Dim_vw"]) == len(workspace_edges)


def test_catalog_matches_production_profile(catalog):
    assert profile_failures(catalog[1]["counts"]) == []


def test_catalog_has_no_source_company_names(catalog):
    assert leak_failures(catalog[0]) == []


def test_every_generated_file_has_an_ingest_step(catalog, steps):
    out, manifest = catalog
    step_files = {s.data_file for s in steps if s.data_file}
    written = {p.relative_to(out).as_posix() for p in out.rglob("*.jsonl")}
    assert written <= step_files
    assert len(manifest["counts"]["rels"]) == len(written & {f for f in step_files if f.startswith("rels/")})


def test_ingest_covers_every_model_node_and_relationship(steps):
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    targets = {(s.kind, s.target) for s in steps}
    for node in model["nodes"]:
        assert ("constraint", node["label"]) in targets
        assert ("node", node["label"]) in targets
    for rel in model["relationships"]:
        assert ("rel", f"{rel['start_node_label']}-{rel['type']}-{rel['end_node_label']}") in targets


def test_labels_the_portal_writes_allow_a_missing_id(steps):
    constraints = {s.target: s.query for s in steps if s.kind == "constraint"}
    for label in ("Session", "Message"):
        assert constraints[label].endswith("(n.id) IS UNIQUE")


def test_platform_system_runs_on_its_synapse_server(catalog):
    out, _ = catalog
    rows = [json.loads(line) for line in (out / "rels" / "Server-HOSTS-DataSystem.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {r["sourceId"] for r in rows if r["targetId"] == "LSC Data Platform (IDP)"} == {"lsc-idp-prod.sql.azuresynapse.net"}


def test_portal_lineage_gaps_exist_without_lineage(catalog):
    agent_src = (MODEL_PATH.parents[1] / "neo4j_text2cypher_fullstack/backend/app/generation/agent.py").read_text(encoding="utf-8")
    assign = next(n for n in ast.parse(agent_src).body if isinstance(n, ast.Assign) and n.targets[0].id == "_KNOWN_LINEAGE_GAPS")
    assert ast.literal_eval(assign.value) == set(KNOWN_LINEAGE_GAPS)
    out, manifest = catalog
    sources = {json.loads(line)["sourceId"] for line in (out / "rels/Table-DERIVED_FROM-Table.jsonl").read_text(encoding="utf-8").splitlines()}
    gaps = manifest["expected"]["known_lineage_gaps"]
    assert len(gaps) == len(KNOWN_LINEAGE_GAPS)
    assert not sources & set(gaps)


def test_portal_prompt_files_name_only_catalog_objects(catalog):
    out, _ = catalog
    root = MODEL_PATH.parents[1]
    known = set()
    for label in ("Table", "Column", "Schema"):
        known |= {json.loads(line)["qualifiedName"].lower()
                  for line in (out / "nodes" / f"{label}.jsonl").read_text(encoding="utf-8").splitlines()}
    ref = re.compile(r"\b((?:sem_\w+|replica_\w+|\w+_core|dwh\w*|persistence|staging)\.[A-Za-z]\w*(?:\.[A-Za-z]\w*)?)")
    skill = root / ".agents/skills/cypher-query-generator"
    prompt_files = [skill / "SKILL.md", *sorted((skill / "references").glob("*.md")),
                    root / "llm_graph_cypher_query_generation_context.md"]
    missing = {(f.name, r) for f in prompt_files for r in ref.findall(f.read_text(encoding="utf-8"))
               if r.lower() not in known}
    assert missing == set()


def test_every_report_traces_back_to_an_operational_table(catalog):
    out, _ = catalog
    assert report_lineage_failures(out) == []


def test_every_power_bi_report_and_edge_is_in_the_workspace_export(catalog):
    out, _ = catalog
    reports = [json.loads(line) for line in (out / "nodes/Report.jsonl").read_text(encoding="utf-8").splitlines()]
    consumes = [json.loads(line) for line in (out / "rels/Report-CONSUMES-Table.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(r["source"] == "PowerBI_Workspace" for r in reports if r.get("webUrl"))
    url_reports = {r["reportKey"] for r in reports if r.get("webUrl")}
    assert all(c["source"] == "PowerBI_Workspace" and c["expression"] for c in consumes if c["sourceId"] in url_reports)


def test_every_competency_question_has_a_planted_answer(catalog):
    manifest = catalog[1]
    for q in json.loads(QUESTIONS_PATH.read_text(encoding="utf-8")):
        if q.get("small_talk"):
            continue
        assert expected_value(manifest, q["expect"]), q["id"]


def test_message_timestamps_stay_inside_the_archive_window(catalog):
    out, _ = catalog
    rows = [json.loads(line) for line in (out / "nodes" / "Message.jsonl").read_text(encoding="utf-8").splitlines()]
    ages = {(TODAY - datetime.fromisoformat(r["timestamp"])).days for r in rows}
    assert len(rows) == 200
    assert max(ages) < 30


def test_count_mismatches_names_the_drifted_pattern():
    expected = {"nodes": {"Table": 3}, "labels": {}, "rels": {"Table-DERIVED_FROM-Table": 2}}
    actual = {"nodes": {"Table": 3}, "labels": {}, "rels": {"Table-DERIVED_FROM-Table": 1}}
    assert count_mismatches(expected, actual) == ["rels Table-DERIVED_FROM-Table: database 1 vs manifest 2"]


class _FakeLoader:
    database = "governancemetadata"

    def __init__(self, total, marker):
        self.answers = iter([[{"n": total}], [{"n": marker}]])

    def run_query(self, _query):
        return next(self.answers)


def test_refuses_a_populated_database_without_the_lsc_catalog():
    with pytest.raises(SystemExit, match="Refusing to load"):
        assert_safe_target(_FakeLoader(total=45000, marker=0))


class _CommunityLoader:
    def __init__(self):
        self.ran = []

    def run_write(self, query):
        if "NODE KEY" in query:
            raise ClientError("Node key constraint requires Neo4j Enterprise Edition")
        self.ran.append(query)


def test_every_constraint_falls_back_to_unique_on_community(steps):
    loader = _CommunityLoader()
    constraints = [s.query for s in steps if s.kind == "constraint"]
    for query in constraints:
        create_constraint(loader, query)
    assert len(loader.ran) == len(constraints)
    assert all("IS UNIQUE" in q and "NODE KEY" not in q for q in loader.ran)
    assert any("(n.type, n.scope) IS UNIQUE" in q for q in loader.ran)


def test_accepts_an_empty_database_or_an_lsc_reload():
    assert_safe_target(_FakeLoader(total=0, marker=0))
    assert_safe_target(_FakeLoader(total=44885, marker=1))
