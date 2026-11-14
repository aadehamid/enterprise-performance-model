from conftest import REFERER
from fakes import FakeLLM, FakeNeo4j, node, record, rel


def test_expand_returns_one_hop_neighbourhood_as_graph(make_client):
    table = node("t1", ["Table"], qualifiedName="wholesale_core.Margin_Fact", layer="Gold")
    column = node("c1", ["Column"], qualifiedName="wholesale_core.Margin_Fact.Margin_Amount")
    schema = node("s1", ["Schema"], qualifiedName="wholesale_core")
    has_col = rel("r1", "HAS_COLUMN", table, column)
    contains = rel("r2", "CONTAINS", schema, table)
    graph = FakeNeo4j({("expand", "t1"): [record(a=table, r=has_col, b=column), record(a=table, r=contains, b=schema)]})

    res = make_client(FakeLLM(["unused"]), graph).post("/api/expand", json={"element_id": "t1"}, headers=REFERER)

    assert res.status_code == 200
    assert res.json() == {
        "nodes": [
            {"id": "t1", "labels": ["Table"], "properties": {"qualifiedName": "wholesale_core.Margin_Fact", "layer": "Gold"}},
            {"id": "c1", "labels": ["Column"], "properties": {"qualifiedName": "wholesale_core.Margin_Fact.Margin_Amount"}},
            {"id": "s1", "labels": ["Schema"], "properties": {"qualifiedName": "wholesale_core"}},
        ],
        "edges": [
            {"id": "r1", "source": "t1", "target": "c1", "type": "HAS_COLUMN", "properties": {}},
            {"id": "r2", "source": "s1", "target": "t1", "type": "CONTAINS", "properties": {}},
        ],
    }


def test_expand_without_element_id_is_a_bad_request(make_client):
    res = make_client(FakeLLM(["unused"]), FakeNeo4j()).post("/api/expand", json={}, headers=REFERER)

    assert res.status_code == 400
    assert res.json() == {"detail": "Missing element_id parameter."}


def test_feedback_is_written_to_the_session_last_message(make_client):
    graph = FakeNeo4j()

    res = make_client(FakeLLM(["unused"]), graph).post(
        "/api/feedback", json={"session_id": "s-1", "feedback": "poor", "comment": "wrong layer"}, headers=REFERER
    )

    assert res.status_code == 200
    assert res.json() == {"status": "success", "message": "Feedback submitted successfully."}
    writes = [(q, p) for q, p in graph.queries if "SET b.feedback" in q]
    assert len(writes) == 1
    assert "LAST_MESSAGE" in writes[0][0]
    assert writes[0][1] == {"session_id": "s-1", "feedback": "poor", "comment": "wrong layer"}


def test_feedback_without_required_fields_is_a_bad_request(make_client):
    graph = FakeNeo4j()

    res = make_client(FakeLLM(["unused"]), graph).post("/api/feedback", json={"session_id": "s-1"}, headers=REFERER)

    assert res.status_code == 400
    assert not any("SET b.feedback" in q for q, _ in graph.queries)
