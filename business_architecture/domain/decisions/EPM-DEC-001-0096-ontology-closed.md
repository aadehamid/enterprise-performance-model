# EPM-DEC-001-0096: The ontology is closed

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028, on the goal the decision owner set on 2026-10-23) |
| Date | 2026-10-23 |
| Questions | Is the ontology done, after every outstanding question is addressed? What stays open after it closes? |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md`, blocks 8 and 26 to 28 |

## Context

Phase E closed on 2026-10-22 with Steps 0 to 12 done or standing as recorded, each with its listed exceptions (EPM-DEC-001-0083). That record listed the items still waiting on the decision owner, on a process owner, on the business and on the next releases. On 2026-10-23 the decision owner answered the items that waited on them, and set the session goal: keep going until the ontology is done, after addressing all the outstanding questions.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):** the ontology is closed. Five facts close it.

1. **Every item that waited on the decision owner is answered.** Q17 is parked (EPM-DEC-001-0086). MPC-P10 is accepted (EPM-DEC-001-0087). The product values and the six close-out releases are approved (EPM-DEC-001-0088), and each release is recorded (EPM-DEC-001-0089 to 0094), with integration made a major release by the decision owner's choice (EPM-DEC-001-0094). Phase F, the `ontology` skill, is done: personal-agent-skills pull request #45 merged (EPM-DEC-001-0084). The projection guideline is now the `ontology-to-lpg` skill (EPM-DEC-001-0095).
2. **Q17 is parked with the business.** It waits for the ontology's first sharing with business consumers, and the business close-out package, `business_architecture/ontology/business-closeout.md`, lists it with every other point only the business can settle (EPM-DEC-001-0086).
3. **The six close-out releases are built and tagged:** `core-v2.3.0` (EPM-DEC-001-0089), `value-stream-v1.1.0` (0090), `data-product-v1.1.0` (0091), `party-v1.1.0` (0092), `kpi-v1.1.1` (0093) and `integration-v2.0.0` (0094). `releases/catalog.ttl` lists every release (EPM-DEC-001-0082).
4. **The projection's list of release gaps is empty.** `projection/pipeline.py`'s `RELEASE_EXCEPTIONS` is empty, and the rerun with `integration` 2.0.0 passed every check (EPM-DEC-001-0094).
5. **The regression is green.** It stands at 43 answerable, 0 partial, 0 waiting and 1 parked (`regression/run.py`, EPM-DEC-001-0086). A question parked by a recorded decision counts as green (EPM-DEC-001-0019).

**What stays open after closure.** None of it blocks the closure, and none of it is part of the ontology build:

- **With the business,** when the ontology is first shared: every point in `business-closeout.md`. These are Q17, Market Data's accountable group, the four codes and TID Nbr, the product list and its PIDX families, Forecaster, Crude RFC, PSM, four working role definitions and the 33 measures with no stated population (EPM-DEC-001-0086). Each answer is recorded as an amendment to the record the package names.
- **Parked for other reasons,** each with its trigger: the IOF Supply Chain mapping (EPM-DEC-001-0064), IRIs that resolve (EPM-DEC-001-0039), and the 462 held process-map rows, which get a fresh verdict only if their source is corrected (EPM-DEC-001-0025, 0083; `python3 scripts/epm_facts.py counts`).
- **A separate, later task:** loading the ontology into Apache Jena and exploring it there and in Neo4j Aura at the same time, which the decision owner set apart from the ontology goal (block 26). The decision owner later allowed Claude to delete the test data it loads into Aura and Jena after thorough testing; both are loaded again with the projection skill in that later task (block 27). The same later task loads the ontology into a Databricks triple store, a plain Delta triple table, and rebuilds the local Neo4j and Aura graphs from it with a check that no data is lost; OntoBricks follows, to link Unity Catalog data and metric views to the ontology (blocks 30 to 32).

## Alternatives considered

- **Keep the ontology open until the business answers the package.** Not chosen: the decision owner parked those points until the ontology is first shared (EPM-DEC-001-0086), so they cannot be answered before it closes.
- **Keep it open until the Jena and Aura exploration.** Not chosen: the decision owner made that a separate task after the ontology is complete (block 26).

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`:

- The goal: "aligned. keep gooing until the ontology is done after addressing all the outstanding question. stop the goal gracefully when you are completely done"
- The later task: "We can always do this part once we have completed the ontology creation goal 100%." and "Again this task is after we have completed ontology 100% that exploration and testing will be after that and a different task."
- The test data: "by the way you can delete data you load into aura DB and jena after your thorough testing to make sure things work and the projection happens with no loss of data."

## Evidence

- EPM-DEC-001-0019, 0025, 0028, 0039, 0064, 0082, 0083, 0084, 0086 to 0095.
- `business_architecture/ontology/business-closeout.md`; `regression/expected.csv` and `regression/run.py`; `projection/pipeline.py`.
- The tags `core-v2.3.0`, `value-stream-v1.1.0`, `data-product-v1.1.0`, `party-v1.1.0`, `kpi-v1.1.1` and `integration-v2.0.0` on origin, checked 2026-10-23.

## Consequences

- The ontology README's Status section says the ontology is closed, with this record.
- The worklog's plan table and decision log carry dated entries.
- EPM-DEC-001-0083 carries a dated note that the items it listed as waiting on the decision owner are answered.
- A later change to the ontology, such as a business answer from the package, is a new release under the module policy, recorded as usual.
