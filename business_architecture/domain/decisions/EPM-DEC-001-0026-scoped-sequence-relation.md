# EPM-DEC-001-0026: A scoped sequence relation in `core`, before 1.0.0

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-12 |
| Questions | Q1 to Q18 of the #226 design round |
| Source | Design round in a Claude Code session, 2026-10-12; approval on #226 |

## Context

In #205, Hamid answered 20 held `precedes`/`follows` rows as source author. For 17 of them his answers describe a sequence that holds per trade, delivery, claim, forecast version or other unit, sometimes only under a condition, and never as completion of a whole process. `core:precedes` stays locked as a process-level finish-to-start ("The source completes before the target begins"), so it cannot carry them. On PR #225 Hamid decided: "Define a scoped sequence relation for these answers before the core 1.0.0 release, tracked in its own issue under #207." Issue #226 tracks that work. The three other rows (REL-01227, REL-00184, REL-00149) have no sequence.

## Decision

The 18 decisions, as posted on #226 ([summary](https://github.com/aadehamid/enterprise-performance-model/issues/226#issuecomment-6123931847), saved in `business_architecture/ontology/step4/review-evidence/226-design-summary.md`):

**Shape**

1. A scoped sequence is a qualified-relation node with its own IRI (EPM-DEC-001-0020), pointing at the earlier and the later process and holding the scope, any condition and the source sentence. `core:precedes` is unchanged.
2. The endpoints are the existing process nodes. The narrower part of each process is described in text; no new sub-step identities are created.
3. The scope comes from a controlled SKOS list of scope units, each with a definition.
4. Every node runs from the earlier process to the later process, whatever the direction of its source row, and cites its row ID.
5. A scoped sequence and `core:precedes` are fully separate; neither implies the other.
6. A scoped sequence may link a process to one of its own ancestors only when a source-author answer says so explicitly (REL-00112). SHACL warns on any other ancestor link.
7. P-Plan `p:isPrecededBy` is not mapped now; Step 6 looks at it again (EPM-DEC-001-0016).

**Definition and properties**

8. Term: **Scoped sequence**: "A scoped sequence states that, for each instance of a named scope unit, a stated part of an earlier process happens before a stated part of a later process. Neither process needs to complete." Parts: `core:ScopedSequence`, with `core:earlierProcess`, `core:laterProcess` and `core:sequenceScope`, one value each.
9. Ten scope units: transaction, physical movement, delivery period, posting, demurrage claim, forecast version, replenishment requirement, plan-selection decision, quote version, scheduling horizon. A new value is added only when no existing value fits.
10. A condition is optional text, at most one per node (`core:sequenceCondition`).
11. The node's `skos:definition` is the approved scope-note sentence, word for word, and the node cites its row ID and the answer comment.
12. REL-00008 and REL-01223 describe one forecast handoff at two levels. Each gets a node; the child's node points at the parent's through `core:refinesSequence`, and handoff counts leave out a refining node.
13. Each node carries `core:evidenceBasis`: *source-confirmed* or *reference-model assumption*. SHACL requires it.

**Verdicts, counting and release**

14. All 17 rows get a fresh APPROVE, emitted as scoped sequences, not as `core:precedes`. REL-01227, REL-00184 and REL-00149 stay not emitted with their recorded reasons.
15. The ledger gets its own scoped-sequence category (617 emitting / 669 held / 12 deferred / 1 external governance / 2 structured flow / 17 scoped sequence = 1318), and `epm_facts.py counts` reports 17 nodes and 16 handoffs.
16. The class, its properties and both code lists go in the `core` module. `core` 1.0.0 releases only when the relation and its SHACL shapes pass. This amends EPM-DEC-001-0013 and EPM-DEC-001-0025.
17. In later batches (#209, #210 and after), an answer that gives a sequence only per a scope unit goes straight to a scoped-sequence verdict under these rules. A new design round is needed only for a new scope unit or an answer that does not fit the definition.
18. Hamid's approval is saved under `step4/review-evidence/hamid-answers/` and quoted below.

## Alternatives considered

- A plain link between the two processes with the scope only in scope-note text (Q1): no place for a scope or condition that a query or SHACL can check.
- New sub-step identities such as "Initial trade capture" (Q2): Hamid's batch 2 answer says "Do not create a new target identity by inference", and it would reopen the finished Step 3 taxonomy.
- Free-text scope (Q3) and a controlled list of conditions (Q10).
- The name "handoff" (Q8): not every row hands something over.
- Mapping to P-Plan `p:isPrecededBy` now (Q7): it orders steps inside one plan, with no scope or condition.

## Hamid's recorded words

Hamid answered the three rounds in the session with "yes to all seven", "yes to all six" and "yes to all five". He then approved the posted summary on #226 ([comment](https://github.com/aadehamid/enterprise-performance-model/issues/226#issuecomment-6123946413), saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/226-design.md`): "Approved: Q1–Q18 as recommended in the comment above"

## Amendments to earlier records

- **EPM-DEC-001-0013:** `core` 1.0.0 also requires the scoped sequence relation and its SHACL shapes to pass.
- **EPM-DEC-001-0025:** the 17 scoped rows of #205 get their fresh verdict as scoped sequences. They count as Phase 1 rows with a fresh verdict, not as held rows.

## Evidence

`business_architecture/ontology/step4/scoped-sequence/` (`scoped-sequences.csv`, `vocabulary.ttl`, `shapes.ttl`, `scoped-sequences.ttl`, `build.py`); `review-evidence/precedes-follows-batch1-review.csv` and `-batch2-review.csv`; `review-evidence/hamid-answers/205-batch1.md`, `205-batch2.md`, `225-option1.md`, `226-design.md`; `evidence-gate.py` section 2k.
