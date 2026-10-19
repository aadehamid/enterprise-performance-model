**Posted by Claude:** design round for the scoped sequence relation. The decision owner accepted each recommendation below in a chat design round on 2026-10-12. Reply to this comment with your approval so the decision record can quote it.

**Shape**

- **Q1.** A scoped sequence is a qualified-relation node with its own IRI (EPM-DEC-001-0020). It points at the earlier and the later process and holds the scope, any condition and the source sentence. `core:precedes` is unchanged.
- **Q2.** The endpoints are the existing process nodes. The narrower part of each process ("initial capture", "claim-specific posting") is described in text. No new sub-step identities are created.
- **Q3.** The scope comes from a controlled SKOS list of scope units, each with a definition.
- **Q4.** Every node runs from the earlier process to the later process, whatever the direction of its source row. Each node cites its row ID.
- **Q5.** A scoped sequence and `core:precedes` are fully separate. Neither implies the other.
- **Q6.** A scoped sequence may link a process to one of its own ancestors, but only when a source-author answer says so explicitly (REL-00112). SHACL warns on any other ancestor link.
- **Q7.** P-Plan `p:isPrecededBy` is not mapped now. Step 6 looks at it again (EPM-DEC-001-0016).

**Definition and properties**

- **Q8.** Term: **Scoped sequence**. Definition: "A scoped sequence states that, for each instance of a named scope unit, a stated part of an earlier process happens before a stated part of a later process. Neither process needs to complete." Parts: the class `core:ScopedSequence`, plus `core:earlierProcess`, `core:laterProcess` and `core:sequenceScope`, with exactly one value each.
- **Q9.** The scope list has 10 units:

  | Scope unit | Rows |
  |---|---|
  | Transaction (a trade or deal) | REL-00193, REL-00206, REL-00200, REL-00188, REL-00351, REL-00319 |
  | Physical movement | REL-01289 |
  | Delivery period (a delivery, production or settlement period) | REL-01291, REL-00307 |
  | Posting (a receivable, payable or adjustment) | REL-00374 |
  | Demurrage claim | REL-01294 |
  | Forecast version | REL-00008, REL-01223 |
  | Replenishment requirement | REL-00068 |
  | Plan-selection decision | REL-00112 |
  | Quote version (a quote or renewal) | REL-00930 |
  | Scheduling horizon | REL-01241 |

  A new value is added only when no existing value fits.
- **Q10.** A condition is optional text (`core:sequenceCondition`, at most one). It applies to REL-00188, REL-00351, REL-01289, REL-00112 and REL-00930.
- **Q11.** The node's `skos:definition` is the approved scope-note sentence, copied word for word. The node cites its row ID and the answer comment.
- **Q12.** REL-00008 and REL-01223 each get a node. The child's node points at the parent's node through `core:refinesSequence`. Counts of handoffs leave out a node that refines another, so the two rows count as one handoff.
- **Q13.** Each node carries `core:evidenceBasis`: either *source-confirmed* or *reference-model assumption*. SHACL requires it.

**Verdicts, counting and release**

- **Q14.** All 17 rows get a fresh APPROVE, emitted as scoped sequences, not as `core:precedes`. REL-01227, REL-00184 and REL-00149 stay not emitted, with their recorded reasons.
- **Q15.** The ledger gets its own scoped-sequence category: 617 emitting / 669 held / 12 deferred / 1 external governance / 2 structured flow / 17 scoped sequence = 1318. `epm_facts.py counts` reports "17 nodes, 16 handoffs".
- **Q16.** The class, its properties and both lists go in the `core` module. Core 1.0.0 releases only when the relation and its SHACL shapes pass. This amends EPM-DEC-001-0013 and 0025.
- **Q17.** In later batches (#209, #210 and after), an answer that gives a sequence only per a scope unit goes straight to a scoped-sequence verdict under these rules. A new design round is needed only for a new scope unit or an answer that doesn't fit the definition.
- **Q18.** Your reply below is saved under `step4/review-evidence/decision-owner-answers/`. EPM-DEC-001-0026 quotes it.

**To approve,** reply: `Approved: Q1–Q18 as recommended in the comment above.`

