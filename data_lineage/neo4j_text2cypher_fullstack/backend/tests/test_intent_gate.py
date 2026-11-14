import pytest
from conftest import REFERER
from fakes import FakeLLM, FakeNeo4j, record

GOLD_COUNT = "MATCH (t:Table) WHERE t.layer = 'Gold' RETURN count(t) AS goldTableCount"
EMPTY_SRC = [{"listIds": [], "rows": [], "graph_data": {"nodes": [], "edges": []}, "headers": {}}]


def ask(client, question, session_id=None):
    body = {"question": question}
    if session_id:
        body["session_id"] = session_id
    return client.post("/ask", json=body, headers=REFERER).json()


def lineage_queries(graph):
    return [q for q, _ in graph.queries if ":Session" not in q]


@pytest.mark.parametrize("greeting", ["hey", "Hi!", "hello there", "good morning", "thanks!", "Thank you so much"])
def test_greeting_or_thanks_replies_without_any_llm_call_or_query(make_client, greeting):
    llm = FakeLLM([GOLD_COUNT])
    graph = FakeNeo4j({GOLD_COUNT: [record(goldTableCount=44)]})

    body = ask(make_client(llm, graph), greeting)

    assert llm.prompts == []
    assert lineage_queries(graph) == []
    assert body["cypher"] == ""
    assert body["error"] == ""
    assert body["src"] == EMPTY_SRC
    assert body["response"].startswith(("Hi!", "You're welcome!"))


def test_small_talk_uses_router_reply_and_is_recorded_on_the_session(make_client):
    reply = "I'm the Semantic Portal assistant. Ask me about tables, lineage, or reports."
    llm = FakeLLM([GOLD_COUNT], route=f'```json\n{{"intent": "small_talk", "reply": "{reply}"}}\n```')
    graph = FakeNeo4j()

    body = ask(make_client(llm, graph), "What can you do?")

    assert body["response"] == reply
    assert body["cypher"] == "" and body["src"] == EMPTY_SRC
    assert llm.cypher_prompts == []
    assert lineage_queries(graph) == []
    writes = [p for q, p in graph.queries if "MERGE (s:Session" in q]
    assert writes == [{"session_id": body["session_id"], "question": "What can you do?", "cypher": "", "answer": reply}]


@pytest.mark.parametrize("question", ["What is the capital of France?", "write me a python sorting function"])
def test_off_topic_question_is_refused_without_generating_cypher(make_client, question):
    llm = FakeLLM([GOLD_COUNT], route='{"intent": "off_topic", "reply": ""}')
    graph = FakeNeo4j({GOLD_COUNT: [record(goldTableCount=44)]})

    body = ask(make_client(llm, graph), question)

    assert body["response"].startswith("Sorry, I can only answer questions about the Lagos Refining & Supply Company")
    assert body["cypher"] == "" and body["error"] == "" and body["src"] == EMPTY_SRC
    assert len(llm.route_prompts) == 1 and question in llm.route_prompts[0]
    assert llm.cypher_prompts == []
    assert lineage_queries(graph) == []


@pytest.mark.parametrize("route", ["not json at all", '{"intent": "banana"}', RuntimeError("router timeout")])
def test_router_failure_or_junk_falls_back_to_the_cypher_pipeline(make_client, route):
    llm = FakeLLM([GOLD_COUNT], summary="There are 44 Gold tables.", route=route)
    graph = FakeNeo4j({GOLD_COUNT: [record(goldTableCount=44)]})

    body = ask(make_client(llm, graph), "How many Gold tables are there?")

    assert body["cypher"] == GOLD_COUNT
    assert body["src"][0]["rows"] == [{"goldTableCount": 44}]
    assert body["response"] == "There are 44 Gold tables."


def test_follow_up_router_prompt_carries_the_conversation(make_client):
    llm = FakeLLM([GOLD_COUNT], summary="There are 44 Gold tables.")
    graph = FakeNeo4j({GOLD_COUNT: [record(goldTableCount=44)]})
    client = make_client(llm, graph)

    first = ask(client, "How many Gold tables are there?")
    second = ask(client, "Now show them in a table", session_id=first["session_id"])

    assert "User: How many Gold tables are there?" in llm.route_prompts[-1]
    assert "CURRENT USER MESSAGE: Now show them in a table" in llm.route_prompts[-1]
    assert second["cypher"] == GOLD_COUNT
    assert len(llm.cypher_prompts) == 2


def test_chat_history_question_skips_the_router(make_client):
    llm = FakeLLM(["MATCH (s:Session)-[:HAS_MESSAGE]->(m:Message) RETURN m.question AS question"],
                  route='{"intent": "off_topic", "reply": ""}')

    body = ask(make_client(llm, FakeNeo4j()), "Show my chat history")

    assert llm.route_prompts == []
    assert body["cypher"].startswith("MATCH (s:Session)")
