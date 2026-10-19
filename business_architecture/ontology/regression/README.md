# Step 11: competency regression

The 44 competency questions (`../competency-questions.md`, locked 2026-09-18) are the ontology's acceptance test. EPM-DEC-001-0019 defines "all green": every question is answerable from the published release, or parked by a recorded decision. For questions 40 and 43, only the part the graph supplies is tested: every live concept has one definition (Q40 excludes the retired concept, the concept on implementation hold, and CM-1-1-3-5-3, the intentional business-evidence hold), and none has a second copy (Q43).

- `expected.csv` gives each question a status:
  - `answerable`: its queries run on the release.
  - `partial`: the graph part's queries run, and `waits_for` names the rest.
  - `waits:<step or decision>`: no query yet; `waits_for` says what the question needs.
- `queries/` holds one SPARQL file per tested part. The first line is the question. A query marked "(must be none)" must return zero rows; every other query must return at least one.
- `run.py` runs the queries against the release (default `../releases/core/2.1.0/core.ttl`) together with the organization module's vocabulary, roles and assignments and the kpi module's vocabulary and measures, and prints the coverage. `scripts/check.sh` runs it and `test_run.py`.

On core 2.1.0 with the organization and kpi modules: 17 answerable, 6 partial (Q11, Q37, Q39, Q40, Q43, Q44), 21 waiting. Core 2.1.0 adds evidence nodes, which no question reads, so its figures equal 2.0.0's. The kpi module (EPM-DEC-001-0043) made Q13, Q14, Q27, Q29, Q30, Q32, Q33 and Q36 answerable and Q37 partial. Q8 became answerable with 2.0.0's planned inputs and outputs (EPM-DEC-001-0038). The processes that Q8 lists without inputs and outputs are the source author's backlog (Hamid, 2026-10-13). The waiting questions break down as follows:
- EPM-DEC-001-0045: meaning owners (Q17), a separate governance decision (Hamid, 2026-10-18).
- Step 7: systems, data products, lanes, capabilities, value streams, the rest of Named KPIs and placement, and the agent questions (Q6, Q7, Q9, Q10, Q15, Q28, Q31, Q34, Q35, Q38, Q41, Q42).
- EPM-DEC-001-0004: the Customer / Party module (Q19 to Q26), which waits for Hamid's customer details.

A module PR moves its questions from `waits` to `answerable` in the same PR that makes them answerable.

The status assignments are delegated under EPM-DEC-001-0028. Its amendment covering Steps 5 to 12 merged in #252; Hamid's words are "yes, extend the delegation to steps 5 to 12."
