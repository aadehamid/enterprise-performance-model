# EPM-DEC-001-0090: Release `value-stream` 1.1.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for the release; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | The second close-out release (EPM-DEC-001-0088): MPC-P10.2 (EPM-DEC-001-0087) and the two value-stream projection gaps (EPM-DEC-001-0036, amendment of 2026-10-22) |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |

## Context

The decision owner linked the Order to Cash process "Review Credit Limit & Risk Code" to CM 1.3.7.4.2 Establish Credit Limit & Risk Code (MPC-P10.2, EPM-DEC-001-0087). The projection lists two gaps in value-stream 1.0.0: `vs:produces` and `vs:consumes` declare no range (EPM-DEC-001-0036). Only a new release closes either.

## Decision

**The decision owner's approval:** "Approve all six (Recommended)"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A minor release, 1.1.0, issued 2026-10-23.** It adds a link and two ranges and removes no IRI.
2. **The credit review realizes CM 1.3.7.4.2.** In `value_stream_order_to_cash.json` the process's `linkedProcessIds` names it, its rationale says why (the process's scope includes periodic and event-triggered reviews; CM 1.3.7.4.3 monitors exposure and does not revise a limit), and the gap-analysis entry that called it missing is removed. The module now has 73 links to core processes and no value-stream process without one.
3. **Both properties take `rdfs:range skos:Concept`.** The projection's note proposed `dp:DataProduct` for `vs:produces`, but the property's definition and shape allow a data product line too, and an OWL range of `dp:DataProduct` would let a reasoner type a line as a data product. Data products and lines are both SKOS concepts in the data-product module, so `skos:Concept` is the one concrete range that holds for every allowed value. The shapes keep the narrower check: each value is a data product or a data product line.
4. **It requires the current releases:** core 2.3.0, data-product 1.0.0 and kpi 1.1.0. 1.0.0 stays on disk as released, requiring core 2.2.0 and kpi 1.0.1.
5. **The projection** loads value-stream 1.1.0, and the two gaps leave its list: 14 remain, in kpi, party and integration. The rerun gave 33,754 triples, 3,928 nodes and 19,698 relationships, no SHACL violation in the graph (588 in-graph constraints, the mutant still caught), an empty round-trip diff and equal hashes for the sorted and shuffled loads.

## Alternatives considered

- **`rdfs:range dp:DataProduct` for `vs:produces`,** as the projection's note said. Not chosen: it is narrower than what the property allows (above).

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "Approve all six (Recommended)".

## Evidence

- `business_architecture/business_process/value_stream_order_to_cash.json`; `value-stream/vocabulary.ttl`, `shapes.ttl`; `data-product/data-products.ttl`.
- EPM-DEC-001-0036, 0054, 0077, 0087, 0088.

## Consequences

- `releases/value-stream/1.1.0/` is written; `scripts/check.sh` fails unless it equals a fresh build.
- Tag `value-stream-v1.1.0` after the merge.
