# system changelog

## 1.5.0 (2026-10-27)

A minor release: it adds systems and notes, and changes no definition and removes no IRI. Approved by Claude under the delegation, with the decision owner's alignment with the plan that names it ("I am aligned with all your recommendation in the input plan.", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-27-customer-inputs.md`; EPM-DEC-001-0028; EPM-DEC-001-0108).

- [minor] **Systems.** Eight systems the decision owner's customer inputs of 2026-10-27 name and the process map does not: PRM, the station point-of-sale systems, the third-party street price aggregator, Credit Card Summary, the Enterprise Data Lake, MSMIS, MCS and Terminaling Throughputs. Each is an application, defined in Claude's words from the inputs, and supports no process. PRM is not MPR. 49 systems, 47 defined.
- [minor] **Notes.** TMR's note gives the inputs' description of it, and which description is right waits for its owner. Bridger Insight's note gives the interface SAP MDG calls it through, MDG.BP.I.1001.
- It requires core 2.4.0.

### Known gaps

- TopDay and VALT have no definition; they wait for their owners (`business-closeout.md`, point 12).
- The eight new descriptions wait for each system's owner to confirm or correct them (`business-closeout.md`, point 16).

## 1.4.0 (2026-10-26)

A minor release: it adds seven systems and 21 links, and removes no IRI. Approved by Claude under the delegation, which lets it approve the queue's minor releases ("Approve (Recommended)", the decision owner's approval of the night brief of 2026-10-26, which says Claude approves the night's minor releases, saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-26-night.md`; EPM-DEC-001-0028; EPM-DEC-001-0104).

- [minor] **MPC-P11** (EPM-DEC-001-0104). The decision owner accepted the proposal's strong and medium rows, so 12 customer-lifecycle processes now name the systems they use in the process map: 21 links. Seven systems join the module: SAP MDG, Salesforce, MAGIC, Bridger Insight, Information Steward, Sirion and Customer Portal, each with the slug, labels and definition the `party` module gives it. "SAP S/4HANA" is a new register string for the existing SAP S/4HANA system, and Profisee and RightAngle gain links. 39 of the 41 systems are defined; 306 links reach 162 processes.
- It requires core 2.4.0, the current release (EPM-DEC-001-0105).

### Known gaps

- TopDay and VALT have no definition; they wait for their owners (`ontology/business-closeout.md`, point 12).
- The drafted descriptions wait for each system's owner to confirm or correct them (`business-closeout.md`, point 16).
- MPC-P11's three weak links stay out until their owners confirm them (EPM-DEC-001-0104, item 3).

## 1.3.0 (2026-10-26)

A minor release: it adds definitions and sources, and removes no IRI. Approved by Claude under the delegation, which lets it approve the queue's minor releases ("Yes, delegate as described (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0028, amendment of 2026-10-25, evening; EPM-DEC-001-0103).

- [minor] **Definitions.** The 14 internal systems gain a `skos:definition` Claude drafted from the repository: what the processes that use them, as core 2.3.0 defines them, show each does. Each cites core 2.3.0's process definitions beside the process map (TMR also the decision owner's customer inputs) and carries a note saying it was drafted from the repository. 32 of the 34 systems are now defined.
- It requires core 2.3.0.

### Known gaps

- TopDay and VALT have no definition; they wait for their owners (`ontology/business-closeout.md`, point 12).
- The 14 drafted descriptions wait for each system's owner to confirm or correct them (`business-closeout.md`, point 16).
- The systems the customer-lifecycle processes use are proposed in MPC-P11, which waits for the decision owner (EPM-DEC-001-0103).

## 1.2.0 (2026-10-25)

A minor release: it adds two systems and a definition, and removes no IRI. Approved by the decision owner with item F's release plan ("Approve the plan (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0097, 0100).

- [minor] **MIPS and Databricks,** which the process map does not name, from the decision owner's pricing assets, each defined; MIPS carries "Market Information and Pricing System" as an alternative label. Databricks' definition is marked as the vendor's description (EPM-DEC-001-0100, item 6).
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
