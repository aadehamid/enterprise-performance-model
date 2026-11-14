import pytest
from conftest import REFERER
from fakes import FakeLLM, FakeNeo4j, node, path, record, rel

from app.generation import Agent
from app.generation.agent import SKILL_DIR, SKILL_REFERENCES

MEDALLION_HEADERS = {
    "srv": "Server",
    "ds": "Data System",
    "op": "Operational Source",
    "replica": "Replica",
    "silver": "Silver",
    "gold": "Gold",
    "semantic": "Semantic",
    "rpt": "Report",
    "owner": "Data Analyst",
}
EMPTY_MEDALLION_ROW = {k: "-" for k in MEDALLION_HEADERS}


def ask(client, question, session_id=None):
    body = {"question": question}
    if session_id:
        body["session_id"] = session_id
    return client.post("/ask", json=body, headers=REFERER)


def test_count_question_returns_scalar_row_and_summary(make_client):
    cypher = "MATCH (t:Table) WHERE t.layer = 'Gold' RETURN count(t) AS goldTableCount"
    llm = FakeLLM([cypher], summary="There are 44 Gold tables.")
    graph = FakeNeo4j({cypher: [record(goldTableCount=44)]})

    res = ask(make_client(llm, graph), "How many Gold tables are there?")

    assert res.status_code == 200
    body = res.json()
    assert set(body) == {"response", "cypher", "error", "src", "session_id"}
    assert body["response"] == "There are 44 Gold tables."
    assert body["cypher"] == cypher
    assert body["error"] == ""
    assert body["session_id"]
    assert body["src"] == [{
        "listIds": [],
        "rows": [{"goldTableCount": 44}],
        "graph_data": {"nodes": [], "edges": []},
        "headers": {"goldTableCount": "GOLDTABLECOUNT"},
    }]


def test_table_nodes_are_bucketed_by_layer_and_serialized_for_graph_view(make_client):
    cypher = "MATCH (t:Table) WHERE t.qualifiedName STARTS WITH 'wholesale_core.' RETURN t"
    fact = node("n1", ["Table", "Fact"], qualifiedName="wholesale_core.Margin_Fact", layer="Gold")
    dim = node("n2", ["Table", "Dimension"], qualifiedName="wholesale_core.Product_Dim", layer="Gold")
    llm = FakeLLM([cypher])
    graph = FakeNeo4j({cypher: [record(t=fact), record(t=dim)]})

    body = ask(make_client(llm, graph), "Show the tables in the wholesale_core schema").json()

    src = body["src"][0]
    assert src["rows"] == [
        {**EMPTY_MEDALLION_ROW, "gold": "wholesale_core.Margin_Fact"},
        {**EMPTY_MEDALLION_ROW, "gold": "wholesale_core.Product_Dim"},
    ]
    assert src["headers"] == MEDALLION_HEADERS
    assert src["listIds"] == ["n1", "n2"]
    nodes = [{**n, "labels": sorted(n["labels"])} for n in src["graph_data"]["nodes"]]
    assert nodes == [
        {"id": "n1", "labels": ["Fact", "Table"],
         "properties": {"qualifiedName": "wholesale_core.Margin_Fact", "layer": "Gold"}},
        {"id": "n2", "labels": ["Dimension", "Table"],
         "properties": {"qualifiedName": "wholesale_core.Product_Dim", "layer": "Gold"}},
    ]
    assert src["graph_data"]["edges"] == []


def test_lineage_path_fills_one_row_and_serializes_edges(make_client):
    cypher = "MATCH p = (s:Table)-[:DERIVED_FROM*1..5]->(r:Table) RETURN p"
    silver = node("s1", ["Table"], qualifiedName="udm_core.Helios_Margin_Fact", layer="Silver")
    replica = node("r1", ["Table"], qualifiedName="replica_helios.Margin_Detail", layer="Replica")
    edge = rel("e1", "DERIVED_FROM", silver, replica)
    llm = FakeLLM([cypher])
    graph = FakeNeo4j({cypher: [record(p=path(silver, edge))]})

    src = ask(make_client(llm, graph), "Trace lineage of Helios_Margin_Fact").json()["src"][0]

    assert src["rows"] == [{**EMPTY_MEDALLION_ROW, "silver": "udm_core.Helios_Margin_Fact", "replica": "replica_helios.Margin_Detail"}]
    assert sorted(n["id"] for n in src["graph_data"]["nodes"]) == ["r1", "s1"]
    assert src["graph_data"]["edges"] == [
        {"id": "e1", "source": "s1", "target": "r1", "type": "DERIVED_FROM", "properties": {}}
    ]


def test_column_lineage_rows_name_the_source_column(make_client):
    cypher = "MATCH (t:Table)-[:HAS_COLUMN]->(col:Column) OPTIONAL MATCH (col)-[:DERIVED_FROM]->(src:Column) RETURN t, col, src"
    gold = node("t1", ["Table", "Fact"], qualifiedName="wholesale_core.Margin_Fact", layer="Gold")
    col = node("c1", ["Column"], qualifiedName="wholesale_core.Margin_Fact.Margin_Amount")
    src = node("c2", ["Column"], qualifiedName="udm_core.Helios_Margin_Fact.Margin_Amount")
    llm = FakeLLM([cypher])
    graph = FakeNeo4j({cypher: [record(t=gold, col=col, src=src)]})

    body = ask(make_client(llm, graph), "Which source column is wholesale_core.Margin_Fact.Margin_Amount derived from?").json()

    assert "udm_core.Helios_Margin_Fact.Margin_Amount" in str(body["src"][0]["rows"])


def test_every_feedback_message_from_the_graph_reaches_the_rows(make_client):
    cypher = "MATCH (s:Session)-[hm:HAS_MESSAGE]->(m:Message) WHERE m.feedback IS NOT NULL RETURN s, hm, m"
    recs = []
    for i in range(3):
        s = node(f"s{i}", ["Session"], id=f"session-{i}")
        m = node(f"m{i}", ["Message"], id=f"message-{i}", feedback="poor")
        recs.append(record(s=s, hm=rel(f"h{i}", "HAS_MESSAGE", s, m), m=m))
    llm = FakeLLM([cypher])

    body = ask(make_client(llm, FakeNeo4j({cypher: recs})), "Can you show all the feedback in the database in a graph?").json()

    assert [r["m"] for r in body["src"][0]["rows"]] == ["message-0", "message-1", "message-2"]
    assert all(f"message-{i}" in llm.prompts[-1] for i in range(3))


def test_write_query_from_llm_is_refused_and_never_reaches_neo4j(make_client):
    llm = FakeLLM(["MATCH (t:Table) DETACH DELETE t", "MERGE (t:Table {qualifiedName: 'x'}) RETURN t"])
    graph = FakeNeo4j()

    body = ask(make_client(llm, graph), "Delete all tables").json()

    assert "non-read-only" in body["error"]
    assert body["response"] == body["error"]
    assert body["src"][0]["rows"] == []
    assert body["src"][0]["graph_data"] == {"nodes": [], "edges": []}
    sent = " ".join(q for q, _ in graph.queries)
    assert "DETACH DELETE t" not in sent
    assert "MERGE (t:Table" not in sent


def test_explain_failure_self_heals_with_corrected_query(make_client):
    bad = "MATCH (t:Table) RETRN t"
    good = "MATCH (t:Table) WHERE t.layer = 'Semantic' RETURN count(t) AS semanticTableCount"
    llm = FakeLLM([bad, good])
    graph = FakeNeo4j({good: [record(semanticTableCount=2736)]},
                      explain_errors={bad: RuntimeError("Invalid input 'RETRN'")})

    body = ask(make_client(llm, graph), "How many Semantic tables are there?").json()

    assert body["error"] == ""
    assert body["cypher"] == good
    assert body["src"][0]["rows"] == [{"semanticTableCount": 2736}]
    heal_prompt = llm.cypher_prompts[1]
    assert bad in heal_prompt and "Invalid input 'RETRN'" in heal_prompt
    assert (SKILL_DIR / "references" / "graph_schema.md").read_text(encoding="utf-8") in heal_prompt
    assert bad not in graph.executed()


def test_empty_result_triggers_self_heal(make_client):
    guessed = "MATCH (t:Table {qualifiedName: 'wholesale_core.Wrong'}) RETURN t"
    fixed = "MATCH (t:Table {qualifiedName: 'wholesale_core.Margin_Fact'}) RETURN t"
    fact = node("n1", ["Table"], qualifiedName="wholesale_core.Margin_Fact", layer="Gold")
    llm = FakeLLM([guessed, fixed])
    graph = FakeNeo4j({fixed: [record(t=fact)]})

    body = ask(make_client(llm, graph), "Show wholesale_core.Margin_Fact").json()

    assert body["cypher"] == fixed
    assert body["src"][0]["listIds"] == ["n1"]


def test_result_missing_requested_entity_type_triggers_self_heal(make_client):
    tables_only = "MATCH (t:Table {qualifiedName: 'sem_wholesale.Margin_vw'}) RETURN t"
    with_reports = ("MATCH (t:Table {qualifiedName: 'sem_wholesale.Margin_vw'}) "
                    "OPTIONAL MATCH (rpt:Report)-[c:CONSUMES]->(t) RETURN t, rpt")
    view = node("v1", ["Table", "View"], qualifiedName="sem_wholesale.Margin_vw", layer="Semantic")
    report = node("rp1", ["Report"], name="Rack Margin Dashboard")
    llm = FakeLLM([tables_only, with_reports])
    graph = FakeNeo4j({tables_only: [record(t=view)], with_reports: [record(t=view, rpt=report)]})

    body = ask(make_client(llm, graph), "Which reports consume sem_wholesale.Margin_vw?").json()

    assert body["cypher"] == with_reports
    assert body["src"][0]["rows"] == [
        {**EMPTY_MEDALLION_ROW, "semantic": "sem_wholesale.Margin_vw", "rpt": "Rack Margin Dashboard"}
    ]
    assert "Power BI Report" in llm.cypher_prompts[1]


def test_known_lineage_gap_is_explained_without_querying(make_client):
    cypher = "MATCH (t:Table {qualifiedName: 'sem_wholesale.Lifting_Forecast_Open_vw'})-[:DERIVED_FROM]->(u) RETURN u"
    llm = FakeLLM([cypher])
    graph = FakeNeo4j()

    body = ask(make_client(llm, graph), "Where does sem_wholesale.Lifting_Forecast_Open_vw come from?").json()

    assert "documented lineage gap" in body["response"]
    assert body["src"][0]["rows"] == []
    assert not any(cypher in q for q, _ in graph.queries)


def test_follow_up_question_sends_prior_turn_to_llm(make_client):
    cypher = "MATCH (t:Table) WHERE t.layer = 'Gold' RETURN count(t) AS goldTableCount"
    llm = FakeLLM([cypher], summary="There are 44 Gold tables.")
    graph = FakeNeo4j({cypher: [record(goldTableCount=44)]})
    client = make_client(llm, graph)

    first = ask(client, "How many Gold tables are there?").json()
    ask(client, "Now show them in a table", session_id=first["session_id"])

    follow_up_prompt = llm.cypher_prompts[-1]
    assert "User: How many Gold tables are there?" in follow_up_prompt
    assert "Assistant: There are 44 Gold tables." in follow_up_prompt
    assert "Now show them in a table" in follow_up_prompt


def test_each_answer_is_recorded_on_the_session(make_client):
    cypher = "MATCH (t:Table) WHERE t.layer = 'Gold' RETURN count(t) AS goldTableCount"
    llm = FakeLLM([cypher], summary="There are 44 Gold tables.")
    graph = FakeNeo4j({cypher: [record(goldTableCount=44)]})

    body = ask(make_client(llm, graph), "How many Gold tables are there?").json()

    writes = [p for q, p in graph.queries if "MERGE (s:Session" in q]
    assert writes == [{
        "session_id": body["session_id"],
        "question": "How many Gold tables are there?",
        "cypher": cypher,
        "answer": "There are 44 Gold tables.",
    }]


def test_agent_refuses_to_start_without_the_cypher_skill(tmp_path):
    with pytest.raises(FileNotFoundError):
        Agent(FakeNeo4j(), FakeLLM(["unused"]), skill_dir=tmp_path)


def test_every_listed_skill_reference_exists_and_reaches_the_prompt():
    cypher = "MATCH (t:Table) RETURN count(t) AS tableCount"
    llm = FakeLLM([cypher])
    Agent(FakeNeo4j({cypher: [record(tableCount=1)]}), llm).ask("How many tables are there?")

    for title, rel_path in SKILL_REFERENCES:
        ref = SKILL_DIR / rel_path
        assert ref.is_file(), f"{rel_path} is listed in SKILL_REFERENCES but missing from {SKILL_DIR}"
        assert f"### {title}:\n{ref.read_text(encoding='utf-8')}" in llm.cypher_prompts[0]


def test_generation_prompt_carries_syntax_traps_but_not_the_vendored_neo4j_skill():
    cypher = "MATCH (t:Table) RETURN count(t) AS tableCount"
    llm = FakeLLM([cypher])
    Agent(FakeNeo4j({cypher: [record(tableCount=1)]}), llm).ask("How many tables are there?")

    prompt = llm.cypher_prompts[0]
    traps = (SKILL_DIR / "references" / "cypher_syntax_traps.md").read_text(encoding="utf-8")
    assert traps in prompt
    vendored = SKILL_DIR.parent / "neo4j-cypher-skill"
    for rel_path, marker in (("SKILL.md", "name: neo4j-cypher-skill"),
                             ("references/syntax-traps.md", "# Common Syntax Traps"),
                             ("references/schema-guardrail.md", "# Schema Guardrail Reference")):
        assert marker in (vendored / rel_path).read_text(encoding="utf-8")
        assert marker not in prompt


def test_skill_edits_apply_to_the_next_question_without_restart(tmp_path):
    cypher = "MATCH (t:Table) RETURN count(t) AS tableCount"
    skill = tmp_path / "SKILL.md"
    skill.write_text("Skill v1", encoding="utf-8")
    llm = FakeLLM([cypher, cypher])
    agent = Agent(FakeNeo4j({cypher: [record(tableCount=1)]}), llm, skill_dir=tmp_path)

    agent.ask("How many tables are there?")
    skill.write_text("Skill v2", encoding="utf-8")
    agent.ask("How many tables are there?")

    assert "Skill v1" in llm.cypher_prompts[0]
    assert "Skill v2" in llm.cypher_prompts[-1]


def test_request_without_allowed_referer_is_rejected(make_client):
    llm = FakeLLM(["MATCH (n) RETURN n"])
    res = make_client(llm, FakeNeo4j()).post("/ask", json={"question": "anything"})

    assert res.status_code >= 400
    assert "Forbidden" in res.json()["detail"]
    assert llm.prompts == []
