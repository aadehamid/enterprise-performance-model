# Step 11: competency regression

The 44 competency questions (`../competency-questions.md`, locked 2026-09-18) are the ontology's acceptance test. EPM-DEC-001-0019 defines "all green": every question is answerable from the published release, or parked by a recorded decision. For questions 40 and 43, only the part the graph supplies is tested: every live concept has one definition (Q40 excludes the retired concept, the concept on implementation hold, and CM-1-1-3-5-3, the intentional business-evidence hold), and none has a second copy (Q43).

- `expected.csv` gives each question a status:
  - `answerable`: its queries run on the release.
  - `partial`: the graph part's queries run, and `waits_for` names the rest.
  - `waits:<step or decision>`: no query yet; `waits_for` says what the question needs.
- `queries/` holds one SPARQL file per tested part. The first line is the question. A query marked "(must be none)" must return zero rows; every other query must return at least one.
- `run.py` runs the queries against the release (default `../releases/core/2.0.0/core.ttl`) together with the organization module's vocabulary, roles and assignments, and prints the coverage. `scripts/check.sh` runs it and `test_run.py`.

On core 2.0.0 with the organization module: 9 answerable, 5 partial (Q11, Q39, Q40, Q43, Q44), 30 waiting. Q8 became answerable with 2.0.0's planned inputs and outputs (EPM-DEC-001-0038). The processes that Q8 lists without inputs and outputs are the source author's backlog (Hamid, 2026-10-13). The waiting questions break down as follows:
- Step 5: meaning owners (Q17).
- Step 7: systems, data products, lanes, capabilities, value streams, Named KPIs and placement, and the agent questions that need the KPI module (Q6, Q7, Q9, Q10, Q13 to Q15, Q27 to Q38, Q41, Q42).
- EPM-DEC-001-0004: the Customer / Party module (Q19 to Q26), which waits for Hamid's customer details.

A module PR moves its questions from `waits` to `answerable` in the same PR that makes them answerable.

The status assignments are delegated under EPM-DEC-001-0028. Its amendment covering Steps 5 to 12 merged in #252; Hamid's words are "yes, extend the delegation to steps 5 to 12."
