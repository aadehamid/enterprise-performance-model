# data-product changelog

## 1.2.0 (2026-10-25)

A minor release: it adds classes, properties, two code lists, the pricing platform tables and the Genie agents, changes four line labels, and removes no IRI. Approved by the decision owner with item F's release plan ("Approve the plan (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0097, 0100).

- [minor] **Data product kinds.** `dp:DataProductKind`: foundational and derived, with definitions, the criteria in scope notes, and six sources at tier 5 (EPM-DEC-001-0097, item 14).
- [minor] **Pricing platform tables.** 33 tables and views of the decision owner's pricing assets, each with its full name, layer (`dp:Layer`: replica, silver, gold, metric view) and sandbox mark: 21 replicas, which copy MIPS, MPR or KittyHawk and are no data products; 7 silver data products, foundational; 2 gold tables and 3 metric views, derived. Each data product is part of Master Pricing (`dcterms:isPartOf`), with its kind, test and reason (EPM-DEC-001-0097, items 7, 8, 13 to 16).
- [minor] **Lineage.** `prov:wasDerivedFrom` at every hop, 40 links, and between the value columns only (EPM-DEC-001-0097, items 9 to 11). Each metric view names the measures it serves (`dp:servesMeasure`) and the systems its lineage reaches (`dp:dependsOnSystem`) (items 1, 2, 4, 12).
- [minor] **Genie agents.** Crack Spread Price Analytics and Executive Summary KPIs Analytics, as `prov:SoftwareAgent` consumers that `prov:used` their metric views (item 14).
- [minor] **Shapes** check the kinds' criteria: a foundational data product is derived only from replicas; a derived one from at least one other data product (item 15).
- [minor] **Labels** (EPM-DEC-001-0098, item 6): the lines HR, IT, S&BD and SC take "product line", with the portfolio's name in a history note. **Top concepts** for `dp:DataProducts` and `dp:PortfolioStatus`, stated both ways (items 4 and 5).
- It requires core 2.3.0, kpi 1.2.0 and system 1.2.0.

### Known gaps

- **The benchmark view's scaling.** It multiplies all five instruments by 100, right for NYMEX Heating Oil (752) and RBOB (9471) but wrong for ICE Brent (572), NYMEX WTI Cushing (747) and NYMEX Natural Gas (750).
- **The benchmark view's 160-day window.**
- **The KPI ID's lineage.** The crack-spread gold table's `KPI_ID` is a constant with no silver source.
- **Validated, not read.** The gold joins were checked against the data or read from column lineage, not from pipeline code.
- **Reads with no column flowing** in the crack-spread gold build, from `mips_price_batch_dim` and `mips_price_assessment_fact`.
- **The lineage's reach:** 180 days of Unity Catalog lineage; the replicas are the top it records.
- **Sandbox names.** Every name is the `idp_sbx` sandbox's (or `synapse_dev`'s, for replicas) until production names are recorded.

## 1.1.0 (2026-10-23)

A minor release: it adds a data product and its producer link, and removes no IRI. Approved by the decision owner with the close-out releases ("Approve all six (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`; EPM-DEC-001-0088, 0091).

- [minor] **Customer Master**, a data product on the Marketing & Sales line, produced by CM 1.3.7.1.1 Maintain Customer and Commercial Account Master Data (MPC-P10.3, EPM-DEC-001-0087): 49 data products, 16 of them described, and 2 process links.
- It requires core 2.3.0, the current release.

## 1.0.0 (2026-10-22)

The module's first release, a major. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0077). It holds the portfolio's 3 segments, 19 product lines and 48 data products as definitions, never data values (EPM-DEC-001-0005, 0053). The 15 Commercial data products are defined from the portfolio's descriptions; the 33 Midstream and Corporate data products are in the package as parked items, each with a note that its definition waits for its data owners, because the portfolio names them without a description. Loss Control is produced by CM 1.1.3.7.13 (EPM-DEC-001-0048). `dp:DataProduct` is mapped to `dcat:Dataset`, not imported. It requires core 2.2.0.
