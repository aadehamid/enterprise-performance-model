# EPM-DEC-001-0055: The system module: the process map's systems, merged on spelling, named but not defined

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Step 7: systems (competency question 6); Phase B of EPM-DEC-001-0052 |
| Source | Claude Code session, 2026-10-19 |

## Context

153 nodes of the process map (`business_architecture/business_process/downstream_process_map.json`) have a `systems` field. Together they hold 37 distinct strings. Some are one system spelled two ways ("RightAngle", "Right Angle"). Three name several systems, joined by "/" ("SAP/ Hyperion", "RightAngle/ TMR/ TopDay", "Right Angle / CargoTracker"). Four name no system: "Manual", "TBD", "To be incorporated in regional Premise solution" and "Manual, to be incorporated in Crude Avails solution". Some are office software (MS Outlook, MS Teams, MS PowerPoint, MS Excel), and some are working documents (the premise documents, "Actuals Case Prep File", "RFC Hindsight Analysis Excel"). No file in the repository defines any of the systems. Every node with a `systems` field is in `core` 2.1.0.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **A new module, `system`,** with its own namespace, vocabulary, shapes, build and tests, referring to `core` processes by IRI. The systems are their own things, used by many processes, so they are not attributes of a process.
2. **A register, as for roles.** `register.csv` maps each string to the systems it names. Strings merge on spelling only, as the role register did (EPM-DEC-001-0031): "Right Angle" becomes an alternative label of RightAngle. A string joined by "/" splits into the systems it names. "APS Planning DB" has no "/", so it stays one system, apart from APS and Planning DB. The four strings that name no system create no node and no link.
3. **Named, not defined.** No source says what each system does, so none gets a definition. Each carries a note that its definition waits for its owners, and a shape rejects a definition.
4. **Three kinds.** Application (software, databases, dashboards, integrations), office tool and working document, so a question about systems can leave out e-mail and slides.
5. **A link per system and process.** `sys:supports` links a system to each process whose `systems` field names it; read the other way, the process depends on the system. Competency question 6 is answerable.

## Alternatives considered

- **Split "APS Planning DB" into APS and Planning DB.** Not chosen: the string has no separator, and the map uses "Planning DB" and "APS" separately elsewhere, so it may be a third thing.
- **Define each system from vendor material.** Not chosen: the map names the systems as the business uses them, and a vendor's description says nothing about that use.
- **Leave office tools and documents out.** Not chosen: the map names them as what the work uses; the kind lets a query leave them out.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/business_process/downstream_process_map.json`, `systems` fields; `business_architecture/ontology/competency-questions.md`, question 6; EPM-DEC-001-0031, 0040.

## Consequences

- The regression stands at 20 answerable, 6 partial and 18 waiting.
- The module is built and checked by `scripts/check.sh`; it is released only with the decision owner's approval.
