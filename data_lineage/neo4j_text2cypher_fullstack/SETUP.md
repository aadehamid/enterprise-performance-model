# Neo4j Text2Cypher Chatbot

Natural language -> Cypher (LLM) -> read-only execution -> English answer.
3-pane UI: **chat** | **generated Cypher (read-only)** | **graph**.
Config = a Neo4j URI/user/password + one named LLM provider.

## Pipeline

1. Ask in plain English. Greetings, small talk and off-topic questions are
   answered conversationally by an intent gate (regex fast path, then one
   LLM router call) without generating or running Cypher.
2. The LLM writes a read-only Cypher query from the `cypher-query-generator`
   skill prompt (shown verbatim in pane 2).
3. It runs read-only. A planning error, empty result or off-target result is
   sent back to the LLM for a corrected query, up to two times.
4. The LLM summarizes rows to English (pane 1).
5. The result subgraph renders in pane 3.

## LLM provider (pick one via LLM_PROVIDER)

All three are native `neo4j-graphrag` wrappers — no custom adapters. The
image ships all three SDKs, so switching is purely an env change.

| LLM_PROVIDER | Auth env | Example LLM_MODEL |
|---|---|---|
| `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-3-5-sonnet-latest` |
| `google` | GCP service-account JSON (see below) | `gemini-1.5-pro` |

`openai` and `anthropic` are paste-a-key. **`google` is different and
heavier**: Vertex AI authenticates via Google Cloud ADC, not an API key.
You must (1) create a GCP service account with Vertex AI access, download
its JSON key, save it as `backend/gcp-sa.json`, (2) uncomment the
`gcp-sa.json` volume line in `docker-compose.yml`, (3) set `GOOGLE_PROJECT`
in `backend/.env`. If you only need OpenAI/Anthropic, ignore all of that.

## Setup

1. `backend/.env`: Neo4j creds (use a **read-only** user), `LLM_PROVIDER`,
   and that provider's key/model. `frontend/.env`: same Neo4j creds.
2. `python preflight.py` (connectivity + read-only-user check).
3. `docker compose up --build`  ->  http://localhost:5173

## Read-only safety

Library EXPLAIN + read routing; a write-clause guard in `agent.py`; and
you should connect with a read-only Neo4j user (preflight verifies).

## Honest limitations

- **No retry, by design.** A wrong query shows as a wrong/empty result
  plus the Cypher and error. Nothing auto-corrects — that's the
  transparency you asked for, but it means weak model output is visible
  and final. Pick a strong model.
- **The Cypher pane is read-only** — you see what was generated; you
  cannot edit/re-run it from the UI. To iterate, rephrase the question.
- Answer quality = the model's Cypher quality. Raw Text2Cypher has no
  schema-specific priors (unlike a purpose-built agent). For complex
  multi-hop questions on a rich schema, expect misses.
- Google/Vertex setup is materially more involved than the other two.
- Not run end-to-end here (needs your DB + provider creds). Pipeline,
  read-only guards, the 3-provider factory, no-retry behaviour, and
  library API contracts were verified by source inspection + mocked tests;
  all code compiles.
