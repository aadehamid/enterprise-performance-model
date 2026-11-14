# Neo4j Text2Cypher Chatbot

A 3-pane chatbot that turns plain-English questions into read-only Cypher
against any Neo4j database, then summarizes the results back to English.

- **Pane 1 — Chat.** Ask in natural language; get an English answer.
- **Pane 2 — Generated Cypher.** See exactly what the LLM wrote (read-only).
- **Pane 3 — Graph.** The result subgraph rendered with Neo4j NVL.

LLM is pluggable: OpenAI, Anthropic, or Google Vertex — one env variable
switches between them.

## What you need

1. A **Neo4j instance** (Aura or self-managed) with some data in it
2. An **API key** from one of: OpenAI, Anthropic, or Google Vertex
3. **Docker + Docker Compose** (one command to run the whole stack)

## Run it

```bash
# 1. fill in credentials
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# open both files, fill in NEO4J_* and your chosen LLM provider's key

# 2. (optional) preflight: confirms DB connectivity before the slow build
pip install neo4j python-dotenv
python preflight.py

# 3. run
docker compose up --build
```

When the build finishes — backend on `:8000`, frontend on `:5173` — open
**http://localhost:5173** and ask a question.

Without Docker: `cd backend && uvicorn app.main:app --port 8000` in one
terminal, `cd frontend && npm install --legacy-peer-deps && npm run dev`
in another. Same result.

## How it works

Each question runs through `Agent.ask(question, prior_turns)` in
`backend/app/generation/agent.py`:

0. **Intent gate.** Bare greetings and thanks ("hey", "thanks!") match a
   strict regex and get a fixed reply with no LLM call. Anything else
   (except chat-history/feedback questions, which skip the gate) goes to
   one cheap LLM router call that returns
   `{"intent": "lineage_question" | "small_talk" | "off_topic", "reply": "..."}`
   with the last five turns as context. `small_talk` returns the router's
   short reply, `off_topic` returns a fixed refusal naming what the portal
   covers. Neither generates Cypher or queries the graph; the response
   has empty `cypher`, `rows` and `graph_data` and is still recorded on the
   session. The router is told to pick `lineage_question` when unsure, and
   a router error or unparseable verdict also falls through to step 1.
1. The prompt is the `cypher-query-generator` skill
   (`.agents/skills/cypher-query-generator/SKILL.md` plus its graph schema,
   project overview, merge-template and Cypher syntax-traps references),
   re-read per question,
   plus the last five conversation turns.
2. The LLM writes a Cypher query.
3. Read-only is enforced twice: a regex guard refuses write clauses before
   anything reaches Neo4j, and every query runs with `RoutingControl.READ`.
4. The query is planned with `EXPLAIN`, then run. A planning error, zero
   rows, or a result missing the entity the question asked for is fed back
   to the LLM for a corrected query, up to `retry` times (2).
5. `generation/results.py` turns the records into the table grid and the
   graph payload; a second LLM call summarizes the rows to English.

`routes.py` only maps HTTP to `agent.ask`, `agent.expand` and feedback.
Generated Cypher is shown verbatim in pane 2.

## Safety notes

- A read-only Neo4j user is ideal for the backend.
- The frontend never connects to Neo4j. It calls the backend only
  (`/ask`, `/api/expand`, `/api/feedback`; see
  `frontend/src/templates/shared/api/backend.ts`).
- Every question writes a `Session` and `Message` node (chat history).

## Limitations to set expectation

- Answer quality = LLM Cypher quality, grounded by the skill's schema
  docs. Keep `.agents/skills/cypher-query-generator/references/graph_schema.md`
  current when the graph schema changes.
- The Cypher pane is read-only display. To refine, ask a different question.

Provider-specific setup: see `SETUP.md`.
