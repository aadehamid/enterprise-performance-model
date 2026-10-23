# EPM-DEC-001-0091: Release `data-product` 1.1.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for the release; the package's contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | The third close-out release (EPM-DEC-001-0088): MPC-P10.3, a Customer Master data product (EPM-DEC-001-0087) |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |

## Context

The decision owner accepted a Customer Master data product on the Marketing & Sales line, produced by CM 1.3.7.1.1 (MPC-P10.3, EPM-DEC-001-0087). Their customer inputs name a data products platform that serves the customer master, fed by the customer data store (`business_process/proposals/MPC-P10-customer-lifecycle.md`). The data-product module builds from `data_product_portfolio.json` and `links.csv` (EPM-DEC-001-0053).

## Decision

**The decision owner's approval:** "Approve all six (Recommended)"

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A minor release, 1.1.0, issued 2026-10-23.** It adds a data product and its producer link, and removes no IRI.
2. **The portfolio gains `dp-customer-master`,** status active, in `dpl-marketing-sales`. Its description is Claude's words: the governed customer master, the customer records, accounts and their attributes that the systems which serve customers share. Its notes name the producer and the source.
3. **`links.csv` gains its producer,** CM 1.3.7.1.1 Maintain Customer and Commercial Account Master Data, cited to EPM-DEC-001-0087. The process is in core 2.3.0, so the link is emitted as `dp:producedBy`.
4. **Figures:** 3 segments, 19 lines, 49 data products (16 described, 33 parked for lack of a description) and 2 process links.
5. **It requires core 2.3.0,** the current release. 1.0.0 stays on disk as released.
6. **The projection** loads data-product 1.1.0: 33,766 triples, 3,930 nodes and 19,705 relationships, no SHACL violation in the graph (588 in-graph constraints, the mutant still caught), an empty round-trip diff and equal hashes for the sorted and shuffled loads.

## Alternatives considered

- **Leave the description to the data owners and park it,** as for 33 others. Not chosen: the decision owner's inputs say what the product serves, and an active product needs a description (EPM-DEC-001-0053).

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "Approve all six (Recommended)".

## Evidence

- `business_architecture/business_process/data_product_portfolio.json`; `ontology/data-product/links.csv`.
- EPM-DEC-001-0053, 0077, 0087, 0088.

## Consequences

- `releases/data-product/1.1.0/` is written; `scripts/check.sh` fails unless it equals a fresh build.
- Tag `data-product-v1.1.0` after the merge.
