# data-product changelog

## 1.1.0 (2026-10-23)

A minor release: it adds a data product and its producer link, and removes no IRI. Approved by the decision owner with the close-out releases ("Approve all six (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`; EPM-DEC-001-0088, 0091).

- [minor] **Customer Master**, a data product on the Marketing & Sales line, produced by CM 1.3.7.1.1 Maintain Customer and Commercial Account Master Data (MPC-P10.3, EPM-DEC-001-0087): 49 data products, 16 of them described, and 2 process links.
- It requires core 2.3.0, the current release.

## 1.0.0 (2026-10-22)

The module's first release, a major. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0077). It holds the portfolio's 3 segments, 19 product lines and 48 data products as definitions, never data values (EPM-DEC-001-0005, 0053). The 15 Commercial data products are defined from the portfolio's descriptions; the 33 Midstream and Corporate data products are in the package as parked items, each with a note that its definition waits for its data owners, because the portfolio names them without a description. Loss Control is produced by CM 1.1.3.7.13 (EPM-DEC-001-0048). `dp:DataProduct` is mapped to `dcat:Dataset`, not imported. It requires core 2.2.0.
