from types import SimpleNamespace

import neo4j
from neo4j.graph import Graph, Node, Path, Relationship

_graph = Graph()


def node(element_id: str, labels: list[str], **properties) -> Node:
    return Node(_graph, element_id, 0, labels, properties)


def rel(element_id: str, rel_type: str, start: Node, end: Node, **properties) -> Relationship:
    r = _graph.relationship_type(rel_type)(_graph, element_id, 0, properties)
    r._start_node, r._end_node = start, end
    return r


def path(start: Node, *relationships: Relationship) -> Path:
    return Path(start, *relationships)


def record(**values) -> neo4j.Record:
    return neo4j.Record(values)


LINEAGE_ROUTE = '{"intent": "lineage_question", "reply": ""}'


def _is_route(prompt: str) -> bool:
    return prompt.rstrip().endswith("Intent JSON:")


def _is_summary(prompt: str) -> bool:
    return prompt.rstrip().endswith("Answer:")


def _is_archive_sql(prompt: str) -> bool:
    return prompt.rstrip().endswith("SQL:")


class FakeLLM:
    """Answers Cypher-generation and self-heal prompts from a script; the last
    scripted Cypher repeats once the script runs out. Intent-router prompts get
    `route`, raised instead when it is an exception. Archive SQL prompts get `sql`."""

    def __init__(self, cyphers: list[str], summary: str = "Narrative summary.",
                 route: str | Exception = LINEAGE_ROUTE,
                 sql: str = "SELECT * FROM archived_messages LIMIT 0"):
        self._cyphers = list(cyphers)
        self._summary = summary
        self._route = route
        self._sql = sql
        self.prompts: list[str] = []

    def invoke(self, prompt: str):
        self.prompts.append(prompt)
        if _is_route(prompt):
            if isinstance(self._route, Exception):
                raise self._route
            return SimpleNamespace(content=self._route)
        if _is_summary(prompt):
            return SimpleNamespace(content=self._summary)
        if _is_archive_sql(prompt):
            return SimpleNamespace(content=self._sql)
        text = self._cyphers.pop(0) if len(self._cyphers) > 1 else self._cyphers[0]
        return SimpleNamespace(content=text)

    @property
    def cypher_prompts(self) -> list[str]:
        return [p for p in self.prompts if not _is_route(p) and not _is_summary(p) and not _is_archive_sql(p)]

    @property
    def route_prompts(self) -> list[str]:
        return [p for p in self.prompts if _is_route(p)]


class FakeNeo4j:
    """Stands in for neo4j.Driver.execute_query. `results` maps a Cypher string
    to the records it returns; `explain_errors` maps a Cypher string to the
    error its EXPLAIN raises."""

    def __init__(self, results: dict[str, list] | None = None,
                 explain_errors: dict[str, Exception] | None = None):
        self._results = results or {}
        self._explain_errors = explain_errors or {}
        self.queries: list[tuple[str, dict]] = []

    def execute_query(self, query, parameters=None, **kwargs):
        self.queries.append((query, parameters or {}))
        if query.startswith("EXPLAIN "):
            cypher = query[len("EXPLAIN "):]
            if cypher in self._explain_errors:
                raise self._explain_errors[cypher]
            return [], None, []
        if "elementId(a) = $eid" in query:
            return self._results.get(("expand", parameters["eid"]), []), None, []
        return self._results.get(query, []), None, []

    def executed(self) -> list[str]:
        return [q for q, _ in self.queries if not q.startswith("EXPLAIN ")]
