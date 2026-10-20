# EPM-DEC-001-0041: the ontology stays proprietary, all rights reserved

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-18; the follow-on items delegated under EPM-DEC-001-0028) |
| Date | 2026-10-18 |
| Questions | Licence package, question 1 (`decision-packages/2026-10-14/licence.md`); EPM-DEC-001-0037, For the decision owner item 3 |
| Source | Claude Code session, 2026-10-18 |

## Context

EPM-DEC-001-0037 left the licence open after the decision owner decided not to host the namespace (EPM-DEC-001-0039). The worklog's "License policy — decided 2026-09-18" already says the ontology artifacts are proprietary, all rights reserved. The licence package found that the repository was public with no LICENSE file, and that the `core` release headers carry a `dcterms:license` IRI in the placeholder namespace that names no licence text.

## Decision

**The decision owner's decision:** the ontology is proprietary.

**What follows (Claude, under EPM-DEC-001-0028):**
1. No open licence is applied. The ontology README's licence line stays as it is.
2. EPM-DEC-001-0037, For the decision owner item 3, is closed: not hosted (EPM-DEC-001-0039), proprietary (this record).
3. The released packages do not change. The next `core` release writes a `dcterms:rights` statement that says all rights reserved and carries APQC's attribution, in place of the dangling `dcterms:license` IRI. *2026-10-18:* done in `core` 2.1.0 (EPM-DEC-001-0044).
4. Separately, the decision owner had the repository made private on 2026-10-18 so that internal names may be used (EPM-DEC-001-0040). *2026-10-19:* public again temporarily, for the current goal (EPM-DEC-001-0050). *2026-10-19, later:* the goal was reached (PRs #298 to #301 merged), and the repository is private again (EPM-DEC-001-0050). *2026-10-19, amendment of EPM-DEC-001-0050:* public while work needs it, private at the end of each session or goal. That is not the package's option C, which kept the licence open; the licence is decided here.

## Alternatives considered

- **CC BY 4.0.** Not chosen: The decision owner chose proprietary, and the worklog notes a licence "can be opened later; cannot be un-opened".

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-18.md`: "5. Make it propriatery". Items 1 to 4 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and the decision owner can reverse them.

## Evidence

`decision-packages/2026-10-14/licence.md`; the worklog section "License policy — decided 2026-09-18"; `business_architecture/ontology/README.md`, the licence line; EPM-DEC-001-0037 and 0039.

## Consequences

- EPM-DEC-001-0037 item 3 and the worklog's decision log say the licence is decided.
