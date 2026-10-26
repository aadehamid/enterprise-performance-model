# system changelog

## 1.1.0 (2026-10-25)

A minor release: it adds definitions, sources, alternative labels and top-concept statements, changes five preferred labels and removes no IRI. Approved by the decision owner ("Approve all three (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-g-releases.md`; EPM-DEC-001-0099).

- [minor] **Definitions.** 15 of the 32 systems gain a `skos:definition` in Claude's words, each citing its source beside the process map (`dcterms:source`): 12 from their vendors' own descriptions, each marked "By the vendor's description" and quoted whole in `business_architecture/reference/vendors/README.md`, and Distribution Planning Optimizer, KittyHawk and CargoTracker from the decision owner's descriptions. Their standard note goes; the other 17 keep it, and TopDay's and VALT's say they are MPC-built.
- [minor] **Labels.** Five systems take their full name as the preferred label, with the process map's abbreviation as an alternative label: Distribution Planning Optimizer (DPO), Aspen Petroleum Scheduler (APS), SAP S/4HANA (SAP), Oracle Hyperion Planning (Hyperion), AVEVA PI System (PI).
- [minor] **Top concepts** (EPM-DEC-001-0098): every system is a top concept of `sys:Systems` and every kind of `sys:SystemKind`, stated both ways.
- [minor] **Shapes.** A system has a definition and a source for it beside the process map, or a note saying why it has none.
- It requires core 2.3.0, the current release.

## 1.0.0 (2026-10-22)

The module's first release, a major. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0077). It holds the 32 systems, office tools and working documents that the process map's systems fields name, merged on spelling through a register, with their kind and 285 links to the 150 processes that use them (EPM-DEC-001-0055). It requires core 2.2.0.
