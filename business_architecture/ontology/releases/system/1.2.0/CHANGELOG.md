# system changelog

## 1.2.0 (2026-10-25)

A minor release: it adds two systems and a definition, and removes no IRI. Approved by the decision owner with item F's release plan ("Approve the plan (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0097, 0100).

- [minor] **MIPS and Databricks,** which the process map does not name, from the decision owner's pricing assets, each defined; MIPS carries "Market Information and Pricing System" as an alternative label. Databricks' definition is marked as the vendor's description (EPM-DEC-001-0097, item 12; EPM-DEC-001-0100).
- [minor] **MPR** gains a definition from the decision owner's files, with a note that they expand it two ways.
- [minor] **Shapes.** A system another source names may be defined by that source alone; a system the process map names still cites a source beside it.
- It requires core 2.3.0, the current release.

### Known gaps

- **MIPS and MPR are defined from the decision owner's pricing files,** which describe them only as the pricing views see them; a fuller description waits for their owners.
- **MPR's expansion is not settled:** the files call it both Master Price Record and Market Price Report.
- **Catalogs and schemas are not systems here.** The pricing tables' catalogs and schemas are parts of each table's full name in `data-product` (EPM-DEC-001-0100, item 5).

## 1.1.0 (2026-10-25)

A minor release: it adds definitions, sources, alternative labels and top-concept statements, changes five preferred labels and removes no IRI. Approved by the decision owner ("Approve all three (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-g-releases.md`; EPM-DEC-001-0099). The plan they approved did not list the qSKOS top-concept statements; Claude approved those additions under the delegation, which lets it approve the queue's minor releases (EPM-DEC-001-0028, amendment of 2026-10-25, evening).

- [minor] **Definitions.** 15 of the 32 systems gain a `skos:definition` in Claude's words, each citing its source beside the process map (`dcterms:source`): 12 from their vendors' own descriptions, each marked "By the vendor's description" and quoted whole in `business_architecture/reference/vendors/README.md`, and Distribution Planning Optimizer, KittyHawk and CargoTracker from the decision owner's descriptions. Their standard note goes; the other 17 keep it, and TopDay's and VALT's say they are MPC-built.
- [minor] **Labels.** Five systems take their full name as the preferred label, with the process map's abbreviation as an alternative label: Distribution Planning Optimizer (DPO), Aspen Petroleum Scheduler (APS), SAP S/4HANA (SAP), Oracle Hyperion Planning (Hyperion), AVEVA PI System (PI).
- [minor] **Top concepts** (EPM-DEC-001-0098): every system is a top concept of `sys:Systems` and every kind of `sys:SystemKind`, stated both ways.
- [minor] **Shapes.** A system has a definition and a source for it beside the process map, or a note saying why it has none.
- It requires core 2.3.0, the current release.


### Known gaps

- 17 systems have no definition. TopDay and VALT are MPC-built and wait for their owners; the other 15 are internal systems whose descriptions wait for one approval round (`ontology/business-closeout.md`, point 12; EPM-DEC-001-0099, item 10).
- Hyperion's product rests on a recommendation Claude called a guess (EPM-DEC-001-0099, item 5; `business-closeout.md`, point 14).
- XPIMS's meaning rests on the decision owner's answer: no AspenTech page read on 2026-10-25 defines XPIMS models (EPM-DEC-001-0099, item 3).

## 1.0.0 (2026-10-22)

The module's first release, a major. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0077). It holds the 32 systems, office tools and working documents that the process map's systems fields name, merged on spelling through a register, with their kind and 285 links to the 150 processes that use them (EPM-DEC-001-0055). It requires core 2.2.0.
