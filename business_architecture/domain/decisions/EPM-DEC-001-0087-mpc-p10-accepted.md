# EPM-DEC-001-0087: MPC-P10 is accepted: a customer onboarding process, the Order to Cash credit review linked to CM 1.3.7.4.2, and a Customer Master data product

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for the three rulings; how each is applied delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | Proposal MPC-P10 (`business_architecture/business_process/proposals/MPC-P10-customer-lifecycle.md`; EPM-DEC-001-0070) |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |

## Context

EPM-DEC-001-0070 linked the decision owner's customer lifecycle to existing processes and left three gaps as proposal MPC-P10, for the decision owner. AGENTS.md says process-map changes are suggested as proposals. As with MPC-P01 and the other proposals in EPM-DEC-001-0047, an accepted proposal is applied to the map and lands in a release the decision owner approves; the decision owner approved those releases in the same session (EPM-DEC-001-0088).

## Decision

**The decision owner's rulings:**

1. **P10.1, option A.** A new L5 process, CM 1.3.7.1.7 Coordinate Customer Onboarding, under the L4 CM 1.3.7.1 Manage Commercial Master Data Stewardship. It covers capturing the setup request, starting the credit, KYC and contract checks through their owning processes, requesting the governed master record, and confirming the customer is set up in the systems that use it. CM 1.3.6.6.1 Set Up Prospect stays as the card-program case.
2. **P10.2, option A.** The Order to Cash process "Review Credit Limit & Risk Code" (`p-otc-review-credit-limit-risk-code`) links to CM 1.3.7.4.2 Establish Credit Limit & Risk Code.
3. **P10.3.** A "Customer Master" data product on the Marketing & Sales line (`dpl-marketing-sales`), produced by CM 1.3.7.1.1 Maintain Customer and Commercial Account Master Data.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **P10.1 lands in `core` 2.3.0,** a minor release: it adds a concept and changes no released IRI. The process gets its ID, slug and definition through Steps 2 and 3, as every accepted process does. The `party` module's onboarding stage then also links to it, in `party` 1.1.0.
2. **P10.2 lands in `value-stream` 1.1.0.** The value-stream file's gap analysis entry for the process is updated to say it is linked. *2026-10-23:* the entry is removed instead, since the process is no longer a gap, and its rationale says why it realizes CM 1.3.7.4.2 (EPM-DEC-001-0090, item 2).
3. **P10.3 lands in `data-product` 1.1.0,** which the data-product module builds from `data_product_portfolio.json` (EPM-DEC-001-0053).
4. **The proposal's status** becomes Accepted, with this record.

## Alternatives considered

- **P10.1 B, widen Set Up Prospect and move it under CM 1.3.7.** Not chosen: moving a node changes its place in the taxonomy, and its card-program steps would no longer fit.
- **P10.2 B, link to CM 1.3.7.4.3 Monitor Credit Against Limit.** Not chosen: monitoring watches exposure against a limit and does not set or revise it.
- **Change nothing.** Not chosen for any of the three.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "Add a new L5 (Recommended)" (P10.1), "CM 1.3.7.4.2 (Recommended)" (P10.2) and "Add Customer Master (Recommended)" (P10.3).

## Evidence

- `business_architecture/business_process/proposals/MPC-P10-customer-lifecycle.md`.
- EPM-DEC-001-0047, 0053, 0054, 0067, 0070.

## Consequences

- The three changes ship in `core` 2.3.0, `value-stream` 1.1.0, `data-product` 1.1.0 and `party` 1.1.0, each through its own pull request and release record.
- EPM-DEC-001-0070 and 0083 carry dated notes.
