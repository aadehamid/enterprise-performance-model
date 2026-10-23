# EPM-DEC-001-0093: Release `kpi` 1.1.1

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for the release; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | The fifth close-out release (EPM-DEC-001-0088): kpi's one projection gap (EPM-DEC-001-0036) |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |

## Context

The projection lists one gap in kpi 1.1.0: `pop:populationEvidence`, which the package carries from the population vocabulary (EPM-DEC-001-0079), declares no range (EPM-DEC-001-0036).

## Decision

**The decision owner's approval:** "Approve all six (Recommended)"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A patch release, 1.1.1, issued 2026-10-23.** `pop:populationEvidence` gains `rdfs:range xsd:string`, the datatype each of its eight values already has. Nothing else in the module changes, and no IRI changes.
2. **It requires core 2.3.0,** the current release. Every process IRI the measures name is in 2.3.0, which only adds a concept to 2.2.0 (EPM-DEC-001-0089). 1.1.0 stays on disk as released, requiring 2.2.0, and value-stream 1.1.0 keeps requiring it.
3. **The projection** loads kpi 1.1.1. The gap leaves its list: 5 remain, all in integration. The rerun gave 34,055 triples, 3,972 nodes and 19,841 relationships, no SHACL violation in the graph over 602 in-graph constraints (the mutant still caught), an empty round-trip diff and equal hashes for the sorted and shuffled loads.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "Approve all six (Recommended)".

## Evidence

- `population/vocabulary.ttl`, `population/population.ttl`.
- EPM-DEC-001-0036, 0062, 0079, 0088, 0089.

## Consequences

- `releases/kpi/1.1.1/` is written; `scripts/check.sh` fails unless it equals a fresh build.
- Tag `kpi-v1.1.1` after the merge.
