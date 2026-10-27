# value-stream changelog

## 1.2.0 (2026-10-26)

A minor release: it adds statements and removes no IRI. Approved by Claude under the delegation, which lets it approve the queue's minor releases ("Yes, delegate as described (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0028, amendment of 2026-10-25, evening; EPM-DEC-001-0106).

- [minor] **Top concepts both ways.** Each of the three measure relationships states `skos:topConceptOf vs:MeasureRelationship`, and the scheme states `skos:hasTopConcept` for each. The code list is flat, so every relationship is a top concept; this fixes the qSKOS finding "Omitted Top Concepts" (EPM-DEC-001-0098, item 5).
- It requires core 2.3.0, data-product 1.2.0 and kpi 1.2.0, the current releases (1.1.0 required data-product 1.0.0 and kpi 1.1.0).

## 1.1.0 (2026-10-23)

A minor release: it adds a link and two ranges, and removes no IRI. Approved by the decision owner with the close-out releases ("Approve all six (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`; EPM-DEC-001-0088, 0090).

- [minor] **The Order to Cash credit review realizes CM 1.3.7.4.2** Establish Credit Limit & Risk Code (MPC-P10.2, EPM-DEC-001-0087). Its scope note says why, and the gap note that called it missing is gone: 73 links to core processes, no value-stream process without one.
- [minor] **`vs:produces` and `vs:consumes` gain `rdfs:range skos:Concept`.** Their objects are data products and data product lines, both SKOS concepts, so the range covers both; the shapes still restrict them to those two classes. This closes the two Rule 1 gaps the projection listed (EPM-DEC-001-0036).
- It requires core 2.3.0, data-product 1.0.0 and kpi 1.1.0, the current releases.

## 1.0.0 (2026-10-22)

The module's first release, a major. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0077). It holds the Commercial Hydrocarbon Lifecycle and Order to Cash value streams: 12 stages, 21 capabilities and 58 value-stream processes, which realize core processes by IRI, produce and consume data products, and carry the seven MPC-P09 measure links as qualified, cited links (EPM-DEC-001-0054). It requires core 2.2.0, data-product 1.0.0 and kpi 1.0.1.
