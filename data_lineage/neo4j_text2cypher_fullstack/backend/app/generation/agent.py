import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import neo4j

from app.generation.results import intent_feedback, serialize_graph, tabulate

logger = logging.getLogger("text2cypher")

SKILL_DIR = Path(__file__).resolve().parents[4] / ".agents" / "skills" / "cypher-query-generator"
SKILL_REFERENCES = (
    ("Node & Relationship Catalog (graph_schema.md)", "references/graph_schema.md"),
    ("Project Counts & Overview (project_overview.md)", "references/project_overview.md"),
    ("Cypher Syntax Traps (cypher_syntax_traps.md)", "references/cypher_syntax_traps.md"),
)

_WRITE = re.compile(
    r"(?i)\b(CREATE|MERGE|DELETE|DETACH\s+DELETE|SET|REMOVE|DROP|"
    r"LOAD\s+CSV|FOREACH)\b|apoc\.(create|merge|refactor|periodic)\b"
)

_KNOWN_LINEAGE_GAPS = {
    "sem_masterdata.customer_ship_to_snapshot_vw",
    "sem_masterdata.blend_recipe_detail_vw",
    "sem_masterdata.exchange_agreement_summary_vw",
    "sem_wholesale.lifting_forecast_open_vw",
    "sem_wholesale.rack_location_non_secured_vw",
    "sem_wholesale.supply_agreement_history_vw",
    "sem_wholesale.credit_memo_by_region_vw"
}

_ZERO_ROWS_FEEDBACK = "Query returned 0 records. Check if schemas, names, or joins were guessed."

_FEEDBACK_WORDS = ["feedback", "rating", "downvote", "upvote", "session history", "past message",
                   "chats", "chat history", "user history"]
_ARCHIVE_HEADERS = {
    "question": "Question",
    "cypher": "Cypher Query",
    "answer": "Narrative Response",
    "feedback": "Feedback Rating",
    "feedback_comment": "Feedback Comment",
    "timestamp": "Timestamp",
}

_GREETING = re.compile(
    r"(?i)^\s*(hey+|hi+|hello|hiya|howdy|yo|greetings|good\s+(morning|afternoon|evening))"
    r"(\s+(there|team|all|everyone|folks))?[\s!.,?]*$"
)
_THANKS = re.compile(
    r"(?i)^\s*(thanks|thank\s+you|thx|ty|cheers|much\s+appreciated|appreciate\s+it)"
    r"(\s+(so\s+much|a\s+lot|again|very\s+much))?[\s!.,?]*$"
)
_GREETING_REPLY = (
    "Hi! I can answer questions about the Lagos Refining & Supply Company data lineage graph, for example "
    "\"How many Gold tables are there?\" or \"Trace the lineage of wholesale_core.Margin_Fact\"."
)
_THANKS_REPLY = "You're welcome! Ask me another lineage question whenever you're ready."
_OFF_TOPIC_REPLY = (
    "Sorry, I can only answer questions about the Lagos Refining & Supply Company data lineage knowledge graph: "
    "tables, schemas, layers, lineage, reports, data systems, servers, analysts, data products, "
    "pipelines, and data models."
)
_PORTAL_SCOPE = (
    "The portal answers questions about the Lagos Refining & Supply Company Data Lineage Knowledge Graph: tables, columns, "
    "schemas, medallion layers (Operational, Replica, Silver, Gold, Semantic), upstream/downstream lineage, "
    "Power BI reports, data systems, servers, data owners and analysts, data products, Synapse/Alteryx pipelines, "
    "flat files, ER Studio data models, business areas, capability and master data domains, legacy refactoring, "
    "and this portal's own chat history and feedback."
)
_ROUTER_SUFFIX = "Intent JSON:"

_EXPAND_QUERY = """
MATCH (a) WHERE elementId(a) = $eid
MATCH (a)-[r]-(b)
RETURN DISTINCT a, r, b
LIMIT 100
"""


@dataclass(frozen=True)
class Answer:
    text: str
    cypher: str
    error: str = ""
    rows: list = field(default_factory=list)
    headers: dict = field(default_factory=dict)
    graph: dict = field(default_factory=lambda: {"nodes": [], "edges": []})
    element_ids: list = field(default_factory=list)


def assert_read_only(cypher: str) -> str:
    if _WRITE.search(cypher or ""):
        raise ValueError(f"Refusing to run non-read-only Cypher query:\n{cypher}")
    return cypher


def pre_clean_query(q: str) -> str:
    q_clean = re.sub(r'\[([^\]]+)\]\.\[([^\]]+)\]', r'\1.\2', q or "")
    q_clean = re.sub(r'\[([^\]]+)\]', r'\1', q_clean)
    q_clean = re.sub(r'(?i)\bhwt\b', 'what', q_clean)
    q_clean = re.sub(r'(?i)\bdteail\b', 'detail', q_clean)
    return q_clean


def documented_gap(cypher: str) -> str:
    cypher_lower = (cypher or "").lower()
    for gap_table in _KNOWN_LINEAGE_GAPS:
        if gap_table in cypher_lower:
            return (
                f"The table '{gap_table}' exists in your Silver/Semantic metadata, "
                f"but it is currently a documented lineage gap in the source STTM excel sheets. "
                f"Therefore, no upstream data flow is available in the database yet."
            )
    return ""


def _text(llm_output) -> str:
    return getattr(llm_output, "content", str(llm_output)).strip()


def _strip_fences(text: str) -> str:
    return text.replace("```cypher", "").replace("```", "").strip()


def _history_context(prior_turns) -> str:
    recent = list(prior_turns)[-5:]
    if not recent:
        return ""
    lines = "".join(
        f"{'User' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('content')}\n" for msg in recent
    )
    return f"\n### RECENT CONVERSATION HISTORY CONTEXT:\n{lines}"


class Agent:
    """Answers a plain-English question about the lineage graph.

    `llm` needs `invoke(prompt) -> object with .content`; `driver` needs
    neo4j's `execute_query`; `archive` needs `run_sqlite_query(sql)`.
    """

    def __init__(self, driver, llm, archive=None, database="governancemetadata", retry=2, skill_dir=SKILL_DIR):
        self._driver = driver
        self._llm = llm
        self._archive = archive
        self._db = database
        self._retry_limit = retry
        self._skill_dir = Path(skill_dir)
        if not (self._skill_dir / "SKILL.md").is_file():
            raise FileNotFoundError(f"cypher-query-generator skill not found at {self._skill_dir}")

    def ask(self, question: str, prior_turns=()) -> Answer:
        cleaned = pre_clean_query(question)
        logger.info(f"Original Query: {question} -> Cleaned Query: {cleaned}")

        reply = self._conversational_reply(cleaned, prior_turns)
        if reply is not None:
            return Answer(text=reply, cypher="")

        try:
            skill = self._skill_prompt()
            cypher = self._generate_cypher(skill, cleaned, prior_turns)
        except Exception as e:
            cypher, recs, error = "", None, f"Cypher generation failed: {e}"
        else:
            cypher, recs, error = self._run_with_self_heal(skill, question, cypher, prior_turns) if cypher else ("", None, "")

        if recs is None:
            print(f"=== T2C PIPELINE FAILED ===\ncypher={cypher}\nerror={error}\n===")
            return Answer(text=error or "I couldn't run a valid query for that question.", cypher=cypher, error=error)

        rows, ids, headers = tabulate(recs, question)
        if self._archive and any(w in question.lower() for w in _FEEDBACK_WORDS):
            rows, headers = self._merge_archived_messages(question, rows, headers)

        graph = serialize_graph(recs)
        text = self._summarize(question, cypher, rows)
        print(f"=== T2C PIPELINE SUCCESS === cypher_len={len(cypher)} "
              f"rows={len(rows)} ids={len(ids)} nodes={len(graph['nodes'])}")
        return Answer(text=text, cypher=cypher, rows=rows[:100], headers=headers, graph=graph, element_ids=ids)

    def expand(self, element_id: str) -> dict:
        recs, _, _ = self._driver.execute_query(
            _EXPAND_QUERY, {"eid": element_id}, database_=self._db, routing_=neo4j.RoutingControl.READ
        )
        return serialize_graph(recs)

    def _conversational_reply(self, question: str, prior_turns):
        """The reply for small talk or an off-topic message, or None when the
        question should go through Cypher generation. Router failures and
        unrecognised verdicts count as lineage questions."""
        if _GREETING.match(question):
            return _GREETING_REPLY
        if _THANKS.match(question):
            return _THANKS_REPLY
        if any(w in question.lower() for w in _FEEDBACK_WORDS):
            return None
        intent, reply = self._route(question, prior_turns)
        logger.info(f"Intent router: {intent}")
        if intent == "small_talk":
            return reply if 0 < len(reply) <= 500 else _GREETING_REPLY
        if intent == "off_topic":
            return _OFF_TOPIC_REPLY
        return None

    def _route(self, question: str, prior_turns) -> tuple[str, str]:
        prompt = (
            "You are the intent router for a data lineage chat portal. " + _PORTAL_SCOPE + "\n"
            f"{_history_context(prior_turns)}\n"
            "Classify the CURRENT USER MESSAGE into exactly one intent:\n"
            "- lineage_question: anything that could be answered by querying the knowledge graph, including "
            "follow-ups to the conversation above (e.g. 'now show them in a table', 'what about Silver?', "
            "'and the reports?'), questions naming a table, schema, report, system, or person, and any request "
            "you are unsure about.\n"
            "- small_talk: greetings, thanks, farewells, or questions about the assistant itself "
            "(e.g. 'who are you', 'what can you do', 'how are you').\n"
            "- off_topic: clearly unrelated to the knowledge graph or the portal (general knowledge, coding help, "
            "math, news, weather, writing tasks).\n"
            "When in doubt, choose lineage_question.\n"
            "For small_talk, also write a short friendly reply of at most two sentences that says what the portal "
            "can answer. For other intents leave reply empty.\n"
            "Respond with ONLY a JSON object: {\"intent\": \"...\", \"reply\": \"...\"}\n\n"
            f"CURRENT USER MESSAGE: {question}\n\n{_ROUTER_SUFFIX}"
        )
        try:
            raw = _text(self._llm.invoke(prompt))
            verdict = json.loads(raw[raw.index("{"):raw.rindex("}") + 1])
            return str(verdict.get("intent", "")).strip().lower(), str(verdict.get("reply") or "").strip()
        except Exception as e:
            logger.warning("intent router failed, falling back to Cypher generation: %s", e)
            return "lineage_question", ""

    def _run_with_self_heal(self, skill, question, cypher, prior_turns):
        """Runs the query, feeding errors, empty results, and intent mismatches
        back to the LLM up to `retry` times. Returns (cypher, records, error);
        records stay None when nothing ran successfully."""
        current, recs, attempt = cypher, None, 0
        while True:
            try:
                gap = documented_gap(current)
                if gap:
                    return cypher, recs, gap
                recs = self._run_read_only(current)
                feedback = _ZERO_ROWS_FEEDBACK if len(recs) == 0 else intent_feedback(question, recs)
                if feedback:
                    attempt += 1
                    if attempt <= self._retry_limit:
                        logger.info(f"{feedback} Auto-correcting retry #{attempt}...")
                        current = self._self_heal(skill, question, current, feedback, prior_turns)
                        continue
                return current, recs, ""
            except Exception as e:
                attempt += 1
                if attempt > self._retry_limit:
                    return current, recs, f"Execution failed after {self._retry_limit} correction attempts: {e}"
                logger.info(f"Query execution failed: {e}. Auto-correcting retry #{attempt}...")
                current = self._self_heal(skill, question, current, str(e), prior_turns)

    def _run_read_only(self, cypher: str):
        assert_read_only(cypher)
        self._driver.execute_query(f"EXPLAIN {cypher}", database_=self._db, routing_=neo4j.RoutingControl.READ)
        recs, _, _ = self._driver.execute_query(cypher, database_=self._db, routing_=neo4j.RoutingControl.READ)
        return recs

    def _skill_prompt(self) -> str:
        prompt = (self._skill_dir / "SKILL.md").read_text(encoding="utf-8")
        prompt += "\n\n--- \n## ADDITIONAL REFERENCE GROUNDING (ON-DEMAND CONTEXT):\n"
        for title, rel_path in SKILL_REFERENCES:
            ref = self._skill_dir / rel_path
            if ref.is_file():
                prompt += f"\n### {title}:\n{ref.read_text(encoding='utf-8')}\n"
        return prompt

    def _generate_cypher(self, skill: str, question: str, prior_turns) -> str:
        prompt = (
            f"{skill}\n\n"
            f"{_history_context(prior_turns)}\n"
            f"--- \n"
            f"Task: Generate a single, read-only Cypher query for the Lagos Refining & Supply Company Data Lineage Knowledge Graph.\n"
            f"Current User Question: {question}\n\n"
            f"Follow all output, naming, and lineage traversal rules exactly. Use OPTIONAL MATCH for all hops beyond the anchor node.\n"
            f"If the current user question is a follow-up asking to filter, count, format, list, show details, show in a table, or adjust the previous query, "
            f"use the RECENT CONVERSATION HISTORY CONTEXT to identify the target schema, table, or report discussed, and construct the conformed Cypher query accordingly.\n\n"
            f"Generate ONLY the raw Cypher query. Do not wrap in markdown blocks, do not include ':use', and do not explain the query."
        )
        return _strip_fences(_text(self._llm.invoke(prompt)))

    def _self_heal(self, skill: str, question: str, bad_cypher: str, error_msg: str, prior_turns) -> str:
        prompt = (
            f"{skill}\n\n"
            f"{_history_context(prior_turns)}\n"
            f"--- \n"
            f"YOUR PRIOR GENERATED CYPHER QUERY FAILED OR RETURNED 0 RECORDS. YOU MUST CORRECT IT NOW.\n"
            f"Current User Question: {question}\n"
            f"Prior Bad Cypher: {bad_cypher}\n"
            f"Error / Feedback: {error_msg}\n\n"
            f"Carefully evaluate your prior query against the rules. Ensure all relationship variables are aliased, "
            f"use OPTIONAL MATCH for hops beyond the anchor table, use DERIVED_FROM*1..5, and verify that "
            f"Table nodes match on qualifiedName. "
            f"Return ONLY the corrected, raw Cypher query. No markdown blocks, no formatting."
        )
        try:
            return _strip_fences(_text(self._llm.invoke(prompt)))
        except Exception as e:
            logger.error("Auto-correction invoke failed: %s", e)
            return bad_cypher

    def _summarize(self, question: str, cypher: str, rows: list) -> str:
        sample = rows[:30]
        q_lower = (question or "").lower()
        wants_table = any(w in q_lower for w in ["table", "grid", "rows", "tabular", "list", "count", "aggregate"])
        target_tab_guidance = (
            "politely guide the user to check the conformed 'Table Grid' tab in the dashboard pane to the right."
            if wants_table else
            "politely guide the user to check the interactive 'Graph View' tab in the dashboard pane to the right to explore the visual lineage flow."
        )
        prompt = (
            "You are an expert commercial data analyst at Lagos Refining & Supply Company. Answer the user's question in clear "
            "English using ONLY the query results provided below. Be extremely concise.\n\n"
            "CRITICAL FORMATTING RULE 1: Do NOT draw, render, or construct any markdown tables or raw text grids inside your reply. "
            "Instead, describe what is being displayed in natural, readable paragraphs or bullet points, "
            f"summarize key conformed insights, and {target_tab_guidance}\n\n"
            "CRITICAL FORMATTING RULE 2: If the query results contain a list of multiple elements or node instances (such as multiple tables, "
            "columns, reports, etc.) and the list is longer than 5 items, do NOT list all of them in this narrative response. "
            "Instead, list only a few representative examples (up to 3-5), state the total count of items returned, "
            "and instruct the user to click the conformed 'Table Grid' tab on the right dashboard to view the complete list.\n\n"
            f"Question: {question}\n\nCypher query used: {cypher}\n\n"
            f"Results ({len(rows)} rows, showing up to 30): {sample}\n\nAnswer:"
        )
        try:
            return _text(self._llm.invoke(prompt))
        except Exception as e:
            logger.warning("summarize failed: %s", e)
            return f"Query ran successfully and returned {len(rows)} row(s)."

    def _merge_archived_messages(self, question: str, rows: list, headers: dict):
        try:
            sql = self._generate_sql(question)
            print(f"Parallel Archival Search -> Generated SQLite Query: {sql}")
            archived = self._archive.run_sqlite_query(sql)
            print(f"Parallel Archival Search -> SQLite Query returned {len(archived)} archived row(s).")
            merged = rows + [{k: s_row.get(k) or "" for k in _ARCHIVE_HEADERS} for s_row in archived]
            seen = set()
            deduped = []
            for r in merged:
                key = (r.get("question"), r.get("timestamp"))
                if "question" not in r or key not in seen:
                    seen.add(key)
                    deduped.append(r)
            return sorted(deduped, key=lambda x: x.get("timestamp") or "", reverse=True), {**headers, **_ARCHIVE_HEADERS}
        except Exception as ex:
            print(f"Warning during SQLite Parallel Search & Merge: {ex}")
            return rows, headers

    def _generate_sql(self, question: str) -> str:
        prompt = (
            "You are an expert SQL generator. Write a single read-only SQLite SELECT query to search the table named `archived_messages`.\n"
            "The table `archived_messages` has the following columns: `session_id`, `question`, `cypher`, `answer`, `feedback`, `feedback_comment`, `timestamp`.\n"
            "Return ONLY the raw SQL query. Do not include markdown code block syntax (like ```sql), do not include comments, and do not explain the query. Just return the raw SQL string.\n\n"
            f"Question: {question}\n\nSQL:"
        )
        try:
            sql = _text(self._llm.invoke(prompt))
            sql = re.sub(r"```(sql)?", "", sql).strip()
            if sql.startswith('"') and sql.endswith('"'):
                sql = sql[1:-1].strip()
            if sql.startswith("'") and sql.endswith("'"):
                sql = sql[1:-1].strip()
            if "select" not in sql.lower() or any(w in sql.lower() for w in ["insert", "update", "delete", "drop", "create", "alter"]):
                return "SELECT * FROM archived_messages LIMIT 0"
            return sql
        except Exception as e:
            logger.warning("Failed to generate SQL query: %s", e)
            return "SELECT * FROM archived_messages LIMIT 0"
