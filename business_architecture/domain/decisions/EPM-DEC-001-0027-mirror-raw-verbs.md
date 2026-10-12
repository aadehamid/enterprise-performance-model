# EPM-DEC-001-0027: Two mirror raw verbs, `provides-input-to` and `governs`

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-12 |
| Questions | One question, after the Phase 1 register approval |
| Source | Claude Code session, 2026-10-12; recorded on [#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6133567292) |

## Context

Hamid approved the Phase 1 answer register on 2026-10-12 ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6133390674)). In 101 of its rows the approved fact runs opposite to the workbook row's direction. 90 are stored as `T core:dependsOnOutputOf S`: a raw "S enables T" that means T consumes an output of S. 11 are stored as `T core:governedBy S`. Q3 of that approval stores each fact in the direction shown.

Corrections belong in the source workbook, not the promotion script (rule 11; `source-workbook-backlog.md`). The direction table had no raw verb that states either relationship from S's side. Step 4 numbers REL rows by segment position in the workbook, so moving a segment to T's row would renumber every later REL ID and break every list keyed by one. The direction table says later changes need a decision-log entry.

## Decision

Two raw verbs join the canonical direction table. Each is the mirror of an existing verb and uses the stored form of that verb:

| Raw verb (S, T) | Stored as | Mirror of |
|---|---|---|
| `provides-input-to` | `T core:dependsOnOutputOf S` | `uses-input` |
| `governs` | `T core:governedBy S` | `governed-by` |

A correction rewrites the row's segment in place with the new verb, so its REL ID stays the same. The raw verb stays in the fact's provenance, as for the other inverse verbs (rule 5). The rules of the stored predicate apply unchanged: the `dependsOnOutputOf` and `governedBy` no-two-cycle gates, and the governed-by emission guard, read with T as the governed process and S as the owner.

## Alternatives considered

- **Move each segment to T's row** as `uses-input` or `governed-by`. Rejected: it renumbers REL IDs after every moved segment.
- **Reinterpret the verb in the promotion script.** Rejected: rule 11 forbids changing source meaning at emission.

## Hamid's recorded words

Hamid answered the question in the Claude Code session on 2026-10-12 ([#207](https://github.com/aadehamid/enterprise-performance-model/issues/207#issuecomment-6133567292), saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/mirror-verbs.md`): "yes, add both verbs and record the decision."

## Consequences

- `mapping_v2.py` `stored_fact` and `evidence-gate.py` `_stored` map both verbs.
- The direction table in `verb-predicate-mapping-v2.md` lists both.
- `core:providesInputTo` and `core:governs` remain query-only inverse predicates; no fact is stored with them.
