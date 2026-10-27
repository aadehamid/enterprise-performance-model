# lane changelog

## 1.1.0 (2026-10-26)

A minor release: it adds statements and rewords a shape message, and removes no IRI. Approved by Claude under the delegation, which lets it approve the queue's minor releases ("Yes, delegate as described (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0028, amendment of 2026-10-25, evening; EPM-DEC-001-0106).

- [minor] **Top concepts both ways.** Each of the four lanes states `skos:topConceptOf lane:OfficeLanes`, and the scheme states `skos:hasTopConcept` for each. The code list is flat, so every lane is a top concept; this fixes the qSKOS finding "Omitted Top Concepts" (EPM-DEC-001-0098, item 5).
- [patch] **A shape message without an apostrophe.** "A process's lane is one of the four office lanes." becomes "The lane of a process is one of the four office lanes.", because n10s writes `sh:message` into Cypher unescaped and a single quote breaks its validator (the `ontology` skill's SHACL rule 19, personal-agent-skills #72).
- It requires core 2.3.0, the current release (1.0.0 required core 2.2.0).

## 1.0.0 (2026-10-22)

The module's first release, a major. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0077). It holds the four office lanes as a code list and the seven processes the process map places in them; nothing is inherited down the tree (EPM-DEC-001-0056). It requires core 2.2.0.
