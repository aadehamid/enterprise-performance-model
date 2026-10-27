# EPM-DEC-001-0107: The ontology is done: every question that waited on the build is closed, and the open points are the business's

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-26, for recording the ontology done with the business points open; the record's content delegated under EPM-DEC-001-0028) |
| Date | 2026-10-26 |
| Questions | After the closure of 2026-10-23 (EPM-DEC-001-0096), the work queue left four kinds of question open: MPC-P11, the seven process names shared inside core's scheme, the qSKOS fixes deferred to releases no queue item planned, and the business close-out points. Are they closed, and is the ontology done? |
| Source | Claude Code session of 2026-10-26 (night); `answers-2026-10-26-night.md`, blocks 2, 4, 5, 6, 7 and 11 |

## Context

EPM-DEC-001-0096 closed the ontology on 2026-10-23. The work queue that followed (EPM-DEC-001-0097 to 0103) added the pricing measures, the systems' definitions and descriptions, and the qSKOS dispositions. It left four kinds of question open, which the handoff of 2026-10-26 listed in order. On 2026-10-26 the decision owner answered the ones that were theirs and approved the night's brief (block 7).

## Decision

**The decision owner's decision:** record the ontology as done, with the business points open. Claude asked: "Points 3 to 16 need system, role and measure owners, not you. May I record the ontology as done, with those 14 points listed as open with the business?" The decision owner: "Yes, done with open points (Recommended)" (block 6).

**What closed (Claude, under EPM-DEC-001-0028):**

1. **MPC-P11 is accepted and applied.** The decision owner accepted the strong and medium links (block 2). The process map's customer processes name their systems, and `system` 1.4.0 and `party` 1.4.0 carry them (EPM-DEC-001-0104).
2. **The seven shared process names are settled.** The decision owner accepted MPC-P12, which names each of the 25 processes by its parent (block 4). `core` 2.4.0 applies it, keeping each old name as history (EPM-DEC-001-0105).
3. **The deferred qSKOS fixes are released.** EPM-DEC-001-0098, item 7, left four modules' fixes to releases no queue item planned. `core` 2.4.0 carries core's (EPM-DEC-001-0105). `lane` 1.1.0, `organization` 2.1.0 and `value-stream` 1.2.0 carry theirs (EPM-DEC-001-0106). The other modules' fixes shipped on 2026-10-25 (EPM-DEC-001-0098, item 7). Each release's `check_taxonomy.py` run shows the fixed findings gone and none added.
4. **The decision owner's two close-out points stay open by their decision.** Q17 (point 1) stays parked until the decision owner convenes the business leads, and the Risk Group stays provisionally accountable for Market Data until its mandate is confirmed (point 2): "Both stay open (Recommended)" (block 5).
5. **The checks are green on the newest releases:** 42 packages listed in `releases/catalog.ttl`; the competency regression at 43 answerable, 0 partial, 0 waiting and 1 parked (Q17), run on core 2.4.0; and the Neo4j projection of every newest release at 4,146 nodes and 21,503 relationships from 36,473 triples, with 0 SHACL violations, an empty round trip and equal hashes (`projection/projection-report.json`).

**What stays open.** None of it is build work:

- **With the business:** points 1 to 16 of `business-closeout.md`. Each names who must answer it and the record that takes the answer. The decision owner may work through some of them first, to narrow them down (block 11). Each answer is an amendment to the named record and goes into that module's next minor release.
- **In the next release of a module:**
  - `market-data` rewords the one shape message that still holds an apostrophe (EPM-DEC-001-0106).
  - `integration` and `ref-mpc` move their pins to the current releases. Today they require the releases they were built against.
- **Parked for other reasons,** each with its trigger: the IOF Supply Chain mapping (EPM-DEC-001-0064), IRIs that resolve (EPM-DEC-001-0039), and the held process-map rows (EPM-DEC-001-0025, 0083; `python3 scripts/epm_facts.py counts`).
- **Usage and integration**, such as giving Databricks agents the KPI definitions, is a separate, later task, as the store tests were for EPM-DEC-001-0096.

## Alternatives considered

- **Keep the ontology open until the business answers points 3 to 16.** Not chosen by the decision owner (block 6).

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-26-night.md`:

- MPC-P11: "Accept strong + medium (Recommended)" (block 2).
- MPC-P12: "Rename by parent (Recommended)" (block 4).
- Close-out points 1 and 2: "Both stay open (Recommended)" (block 5).
- The ontology done: "Yes, done with open points (Recommended)" (block 6).
- The night's brief: "Approve (Recommended)" (block 7).
- The open points: "I probably can work through some of thus to narrow the unanswered question down. we can do that after this goa is achieved." (block 11).

## Evidence

- EPM-DEC-001-0025, 0028, 0039, 0064, 0083, 0096, 0098, 0104, 0105, 0106.
- `business_architecture/ontology/business-closeout.md`; `regression/run.py`; `projection/projection-report.json`; `releases/catalog.ttl`.
- The tags `core-v2.4.0`, `lane-v1.1.0`, `organization-v2.1.0`, `value-stream-v1.2.0`, `system-v1.4.0` and `party-v1.4.0` on origin, checked 2026-10-27.

## Consequences

- The ontology README's Status section says the ontology is done, with this record.
- `business-closeout.md`, EPM-DEC-001-0096 and the worklog carry dated notes.
- A later change, such as a business answer, is a new release under the module policy, recorded as usual.
