"""A supervisor over the four Genie agents, with each subagent's description built from the ontology (EPM-DEC-001-0109,
decision 3).

    uv run python -m pricing_demo.supervisor describe            # the subagent descriptions, from the definitions views
    uv run python -m pricing_demo.supervisor setup               # try the Agent Bricks Supervisor Agent; report the outcome
    uv run python -m pricing_demo.supervisor ask "<question>"    # route a question through the orchestrator
    uv run python -m pricing_demo.supervisor genie "<agent title>" "<question>"   # ask one Genie agent directly

The decision is an Agent Bricks Supervisor Agent ("Use Supervisor Agent to create a coordinated multi-agent system
(legacy)", Databricks, updated 2026-10-14), which `setup` tries through the SDK's `supervisor_agents` API. Its fallback
is Databricks' documented multi-agent pattern ("Build a multi-agent system on Databricks Apps", updated 2026-10-14): an
orchestrator model that treats each subagent as a tool, chosen by the subagent's description. `ask` runs that pattern
from this machine: the orchestrator is a Foundation Model API chat model with tools ("Function calling on Databricks",
updated 2026-10-26), and each Genie subagent is called through the Genie Conversation API ("Use the Genie Agents API",
updated 2026-10-23).
"""
import json
import re
import sys
import time

from .config import completed, databricks_env
from .databricks import connect, current_catalog, run
from .genie import AGENTS

# A Foundation Model API chat model this workspace serves (Free Edition). The template's databricks-claude-sonnet-4-5
# is not served here. Until Plan 1, step 6, the orchestrator was databricks-meta-llama-3-3-70b-instruct; on
# 2026-10-30 a probe gave each served chat model one tool-calling question twice, and Qwen3.5 122B was the only one
# that called both agents the question needed, the same both times (delegated under EPM-DEC-001-0028).
MODEL = "databricks-qwen35-122b-a10b"
# Qwen3.5 reasons before it answers, and its reasoning counts against max_tokens.
MAX_TOKENS = 4000
SUPERVISOR_TITLE = "EPM Pricing Supervisor"
INSTRUCTIONS = (
    "You route questions about the downstream pricing demo to its Genie agents. Call the agent whose measures the "
    "question asks about; call several when it spans subject areas, then combine their answers. Before answering, "
    "name the subject areas the question touches (crack spreads; Executive Summary prices and benchmarks; market "
    "prices and freight; refinery operations, plans, decisions, events, EIA's weekly data and the outside context) and "
    "call the agent for each one, one call per agent, asking it only about its own subject area: never give a crack "
    "figure the crack agent did not return, nor a refinery figure the refinery agent did not return. Keep each measure's "
    "identifier and label as the agent gives them, say which agent each figure came from, and say when a figure is "
    "the demo's own formula or synthetic data. Never compute a figure no agent returned. Cracks are published by "
    "market, not by refinery: for a refinery's crack, ask the crack agent for its region's benchmark crack, the one the "
    "demo's R&M margin uses (sql/04_gold.sql): Gulf Coast, USGC 3-2-1 MEH Crack, ex-RIN (43870); West Coast, LA 3-2-1 "
    "Crack ANS, ex-RIN (36855); Mid-Continent, CHI 3-2-1 Crack WTI, ex-RIN (37438).")
MAX_ROUNDS = 8
# A tool result keeps up to MAX_ROWS of the agent's rows, and its JSON stays under TOOL_CHARS by dropping rows from
# the end, never by cutting the JSON (step 2; until then 20 rows, then a 12,000-character cut that could split a row).
# The result says how many rows the query returned and how many it shows; CONTEXT_CHARS bounds them all together.
MAX_ROWS = 500
TOOL_CHARS = 30000
# The whole conversation sent to the model stays under CONTEXT_CHARS, about 40,000 tokens at four characters a token, so
# eight rounds of results cannot grow without limit: before each request the oldest tool results give up their rows,
# text and SQL kept, until it fits (Codex on step 2).
CONTEXT_CHARS = 160000
# A Genie message that fails (MessageStatus.FAILED, as use cases 7 and 9 did on E7's runs) is sent again up to
# GENIE_ATTEMPTS times in all, GENIE_WAIT seconds apart, and every failure is kept in the trace (step 3). If every attempt
# fails, the orchestrator gets the failure as the tool result, and the agent still counts as not called.
GENIE_ATTEMPTS = 3
GENIE_WAIT = 10
# Before the tool loop the orchestrator names the agents whose subject areas the question touches; an answer is
# accepted only once each of them, and each agent RULES require, has been called (after E7, delegated under
# EPM-DEC-001-0028).
PLAN = ("Name the agents whose subject areas this question touches, one for each subject area, from these tools:\n"
        "{tools}\nReply with JSON only: {{\"agents\": [\"<tool name>\", ...]}}.")
PLAN_ATTEMPTS = 3
# INSTRUCTIONS' own rule, enforced: a question or answer about a crack needs the crack agent, and one about a refinery's
# runs, utilization, yields or margin needs the refinery agent. The rest follow each agent's plain tables (genie.py):
# freight is the pricing agent's (FREIGHT_TABLE); plans, backcasts, decisions, events, EIA's weekly data and the
# outside context are the refinery agent's (PLANNING_TABLES).
RULES = {
    "Crack Spread Price Analytics": re.compile(r"\bcracks?\b", re.I),
    "Pricing and Market Margin Analytics": re.compile(r"\bfreight\b|\btanker\b|\bnetbacks?\b", re.I),
    "Refinery Operations Analytics": re.compile(
        r"\brefiner(?:y|ies)\b|\butili[sz]ation\b|\byields?\b|\bcrude runs\b|\bmargin capture\b|\bR&M margin\b|"
        r"\bplans?\b|\bbackcast|\bdecisions?\b|\bD\d{2}\b|\bturnarounds?\b|\bhurricane\b|\bstorm\b|\bEIA\b|\bPADDs?\b|"
        r"\bdistillate stocks\b|\boutside (?:scan|context|factor)|\bforward look\b", re.I),
}


def definitions_view(spec):
    return next(t for t, _ in spec["tables"] if t.startswith("ontology_definitions."))


def tool_name(title):
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def metric_views(spec):
    return [t.split(".")[-1] for t, _ in spec["tables"] if t.startswith("semantic_sem_commercial.")]


def other_tables(spec):
    """The plain tables an agent binds besides its metric views and its definitions view (E7)."""
    return [(t, d) for t, d in spec["tables"] if not t.startswith(("semantic_sem_commercial.", "ontology_definitions."))]


def description(title, spec, rows, computed):
    """A subagent's description: its views, and the identifiers and labels of the measures it answers for, as the
    definitions view gives them from epm_triples. A measure none of its views computes is marked so (OPM-0026). The
    plain tables the agent also binds are named with their descriptions, so a question about them reaches it."""
    measures = "; ".join(f"{i} {label}" + ("" if i in computed else " (defined, not computed)") for i, label in rows)
    text = (f"{title}: a Genie agent over {', '.join(metric_views(spec))}. It answers for these measures of the "
            f"ontology's kpi module (read from epm_triples): {measures}.")
    others = other_tables(spec)
    if others:
        text += " It also reads " + "; ".join(f"{t.split('.')[-1]} ({d})" for t, d in others)
    return text


def descriptions(cur, catalog):
    """Each agent's description, from its definitions view and its metric views' epm_measure_identifiers tags."""
    tags = dict(run(cur, f"SELECT table_name, tag_value FROM {catalog}.information_schema.table_tags WHERE schema_name = "
                         "'semantic_sem_commercial' AND tag_name = 'epm_measure_identifiers'"))
    out = {}
    for title, spec in AGENTS.items():
        rows = run(cur, f"SELECT Identifier, Label FROM {catalog}.{definitions_view(spec)} ORDER BY Identifier")
        if not rows:
            raise SystemExit(f"{definitions_view(spec)} is empty: build the definitions views first (databricks build)")
        untagged = [v for v in metric_views(spec) if not tags.get(v, "").strip()]
        if untagged:  # without the tags every measure would read as "defined, not computed"
            raise SystemExit(f"{', '.join(untagged)} has no epm_measure_identifiers tag: rebuild the metric views (databricks build)")
        computed = {i for v in metric_views(spec) for i in tags[v].split()}
        out[title] = description(title, spec, [(r[0], r[1]) for r in rows], computed)
    return out


def tools(described):
    return [{"type": "function", "function": {
        "name": tool_name(title), "description": text,
        "parameters": {"type": "object", "properties": {"question": {"type": "string", "description": "The question for this agent."}},
                       "required": ["question"]}}} for title, text in described.items()]


def workspace():
    from databricks.sdk import WorkspaceClient
    e = databricks_env()
    return WorkspaceClient(host=e["DATABRICKS_HOST"], token=e["DATABRICKS_TOKEN"])


def client():
    """The workspace client and the subagent descriptions, read from the demo's catalog."""
    conn, e = connect()
    with conn, conn.cursor() as cur:
        described = descriptions(cur, current_catalog(cur, e))
    return workspace(), described


def spaces(w):
    found = {s.title: s.space_id for s in (w.genie.list_spaces().spaces or [])}
    missing = [t for t in AGENTS if t not in found]
    if missing:
        raise SystemExit(f"Genie agents not found: {missing}; run python -m pricing_demo.genie first")
    return {t: found[t] for t in AGENTS}


def ask_genie(w, space_id, question):
    """The agent's answer (ask_once), after up to GENIE_ATTEMPTS tries when its message fails, with each failure."""
    from databricks.sdk.errors import OperationFailed
    errors = []
    for attempt in range(1, GENIE_ATTEMPTS + 1):
        try:
            return {**ask_once(w, space_id, question), "attempts": attempt, "errors": errors}
        except OperationFailed as err:
            errors.append(str(err)[:300])
            if attempt < GENIE_ATTEMPTS:
                time.sleep(GENIE_WAIT)
    return {"status": "MessageStatus.FAILED", "text": f"error: the agent failed {GENIE_ATTEMPTS} times; ask it a narrower "
            "question", "rows": [], "row_count": 0, "attempts": GENIE_ATTEMPTS, "errors": errors}


def ask_once(w, space_id, question):
    """The agent's text and SQL, the first MAX_ROWS rows of its result, and how many rows the query returned."""
    m = w.genie.start_conversation_and_wait(space_id, question)
    parts, rows, row_count = [], [], 0
    for a in m.attachments or []:
        if a.text and a.text.content:
            parts.append(a.text.content)
        if a.query:
            parts.append(f"SQL: {a.query.query}")
            result = w.genie.get_message_attachment_query_result(space_id, m.conversation_id, m.message_id, a.attachment_id)
            sr = result.statement_response
            if sr and sr.result and sr.result.data_array:
                cols = [c.name for c in sr.manifest.schema.columns]
                rows = [dict(zip(cols, r)) for r in sr.result.data_array[:MAX_ROWS]]
                row_count = max(sr.manifest.total_row_count or 0, len(sr.result.data_array))
    if m.error:
        parts.append(f"error: {m.error.error}")
    return {"status": str(m.status), "text": "\n".join(parts), "rows": rows, "row_count": row_count}


def no_rows(result, **extra):
    return {**result, "rows": [], "rows_shown": 0, **extra}


def tool_content(result):
    """The tool message for one agent's result: whole JSON under TOOL_CHARS, rows dropped from the end to fit, with
    the count of rows shown beside the count the query returned."""
    rows = result.get("rows") or []
    keep = len(rows)
    while True:
        text = json.dumps({**result, "rows": rows[:keep], "rows_shown": keep}, default=str)
        if len(text) <= TOOL_CHARS:
            return text
        if keep == 0:
            break
        keep = min(keep - 1, keep * TOOL_CHARS // len(text))
    body = result.get("text", "")  # no rows left and still too long: shorten the text until the JSON, escapes and all, fits
    while body:
        body = body[:len(body) // 2]
        text = json.dumps(no_rows(result, text=body + " [cut to fit]"), default=str)
        if len(text) <= TOOL_CHARS:
            return text
    return json.dumps(no_rows({"status": result.get("status")}, text="[too long to show]"))


def fit(messages):
    """Keep the conversation under CONTEXT_CHARS: the oldest tool results with rows give them up first."""
    sizes = [len(json.dumps(m, default=str)) for m in messages]
    total = sum(sizes)
    for k, m in enumerate(messages):
        if total <= CONTEXT_CHARS:
            return
        if m.get("role") != "tool":
            continue
        body = json.loads(m["content"])
        if body.get("rows"):
            m["content"] = json.dumps(no_rows(body, note="rows dropped to keep the conversation within the model's context"),
                                      default=str)
            new = len(json.dumps(m, default=str))
            total += new - sizes[k]
            sizes[k] = new
    if total > CONTEXT_CHARS:
        raise ValueError(f"the conversation is over {CONTEXT_CHARS} characters even without tool rows")


def chat(w, messages, tool_specs=None):
    body = {"messages": messages, "max_tokens": MAX_TOKENS, "temperature": 0}
    if tool_specs:
        body.update(tools=tool_specs, tool_choice="auto")
    message = w.api_client.do("POST", f"/serving-endpoints/{MODEL}/invocations", body=body)["choices"][0]["message"]
    return {**message, "content": text(message.get("content"))}


def text(content):
    """A reply's text. Qwen3.5 sends a list of parts, a reasoning summary and then the text; only the text is kept, so the
    reasoning neither reaches the answer nor goes back to the model."""
    if isinstance(content, list):
        return "".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return content


def names(titles):
    """The tool names of these agents, in AGENTS' order."""
    return ", ".join(tool_name(t) for t in AGENTS if t in titles)


def ruled(text):
    """The agents RULES require for a text."""
    return [t for t, pattern in RULES.items() if pattern.search(text or "")]


def planned(w, described, question):
    """The agents the orchestrator names for the question before calling any; a name it invents is dropped. A plan
    that names no known agent is asked again, and after PLAN_ATTEMPTS the question stops: every question the
    orchestrator gets needs an agent (Codex on #411)."""
    by_tool = {tool_name(t): t for t in AGENTS}
    listing = "\n".join(f"- {tool_name(t)}: {text}" for t, text in described.items())
    for _ in range(PLAN_ATTEMPTS):
        reply = chat(w, [{"role": "system", "content": PLAN.format(tools=listing)}, {"role": "user", "content": question}])
        found = re.search(r"\{.*\}", reply.get("content") or "", re.S)
        try:
            names = json.loads(found.group(0))["agents"] if found else []
        except (ValueError, KeyError, TypeError):
            names = []
        if not isinstance(names, list):  # "agents": null or a string is no plan either (Bugbot on #411)
            names = []
        plan = [by_tool[n] for n in dict.fromkeys(n for n in names if isinstance(n, str)) if n in by_tool]
        if plan:
            return plan
    raise ValueError(f"no plan naming a known agent after {PLAN_ATTEMPTS} attempts")


def missing(required, called):
    """The required agents with no completed call: a call whose every attempt failed does not count."""
    return [t for t in AGENTS if t in required and t not in {c["agent"] for c in called if completed(c)}]


class OrchestrationError(SystemExit):
    """The orchestrator stopped without an answer; agents_called holds the agents it had already called, and plan
    the agents it had planned, if it got that far (Bugbot on #411)."""

    def __init__(self, message, agents_called, plan=None):
        super().__init__(message)
        self.agents_called, self.plan = agents_called, plan


def orchestrate(w, described, ids, question):
    """Route a question through the orchestrator: each agent it called, with the agent's text and SQL, and the answer.
    An answer is sent back until every agent the plan named, or RULES require of the question or the answer, is called."""
    tool_specs = tools(described)
    by_tool = {tool_name(t): t for t in AGENTS}
    called, plan = [], None
    try:
        plan = planned(w, described, question)
        required = set(plan) | set(ruled(question))
        brief = names(required)
        messages = [{"role": "system", "content": INSTRUCTIONS},
                    {"role": "user", "content": question + (f"\n\n(Call at least these agents: {brief}.)" if brief else "")}]
        for _ in range(MAX_ROUNDS):
            fit(messages)
            reply = chat(w, messages, tool_specs)
            calls = reply.get("tool_calls") or []
            messages.append({k: v for k, v in reply.items() if k in ("role", "content", "tool_calls")})
            if not calls:
                answer = reply.get("content") or ""
                required |= set(ruled(answer))
                gaps = missing(required, called)
                if not gaps:
                    return {"agents_called": called, "answer": answer, "plan": plan}
                messages.append({"role": "user", "content": "Not yet: call the " + names(gaps)
                                 + " agent before answering, asking it only about its own subject area, then answer again."})
                continue
            for call in calls:
                title = by_tool[call["function"]["name"]]  # a tool name the model invents raises KeyError
                sub = json.loads(call["function"]["arguments"])["question"]
                result = ask_genie(w, ids[title], sub)
                called.append({"agent": title, "question": sub, "status": result["status"], "text": result["text"],
                               "attempts": result.get("attempts", 1), "errors": result.get("errors", [])})
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": tool_content(result)})
    except Exception as err:  # keep the agents already called beside the reason it stopped
        raise OrchestrationError(f"{type(err).__name__}: {err}; agents called: {[c['agent'] for c in called]}", called, plan) from err
    raise OrchestrationError(f"no answer after {MAX_ROUNDS} rounds; agents called: {[c['agent'] for c in called]}", called, plan)


def ask(question):
    """Route a question through the orchestrator; print each agent it called and the final answer."""
    w, described = client()
    result = orchestrate(w, described, spaces(w), question)
    called = [{k: c[k] for k in ("agent", "question", "status")} for c in result["agents_called"]]
    print(json.dumps({"agents_called": called, "answer": result["answer"]}, indent=2))


def setup():
    """Try the Agent Bricks Supervisor Agent, with the four Genie agents as tools. Report the outcome either way."""
    from databricks.sdk.service.supervisoragents import GenieSpace, SupervisorAgent, Tool
    w, described = client()
    ids = spaces(w)
    try:
        existing = next((a for a in w.supervisor_agents.list_supervisor_agents() if a.display_name == SUPERVISOR_TITLE), None)
        agent = existing or w.supervisor_agents.create_supervisor_agent(SupervisorAgent(
            display_name=SUPERVISOR_TITLE, description="Routes pricing-demo questions to its four Genie agents.",
            instructions=INSTRUCTIONS))
        have = {t.tool_id for t in w.supervisor_agents.list_tools(agent.name)}
        for title, text in described.items():
            if tool_name(title) not in have:
                w.supervisor_agents.create_tool(agent.name, Tool(tool_type="genie_space", description=text,
                                                                 genie_space=GenieSpace(id=ids[title])), tool_id=tool_name(title))
        print(f"Supervisor Agent ready: {agent.name} (endpoint {agent.endpoint_name})")
    except Exception as err:  # Free Edition refuses new Supervisor Agents; the fallback is `ask`
        print(f"Supervisor Agent not created ({type(err).__name__}): {str(err).split(' Config:')[0]}")
        print("Fallback: the documented multi-agent pattern, run from this machine with `ask`.")


def main(argv):
    command = argv[0] if argv else "describe"
    if command == "describe":
        _, described = client()
        for title, text in described.items():
            print(f"{title}\n  {text}")
    elif command == "setup":
        setup()
    elif command == "ask":
        ask(argv[1])
    elif command == "genie":
        w = workspace()
        print(json.dumps(ask_genie(w, spaces(w)[argv[1]], argv[2]), indent=2, default=str))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
