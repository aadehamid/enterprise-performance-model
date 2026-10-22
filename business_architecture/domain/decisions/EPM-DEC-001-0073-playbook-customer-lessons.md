# EPM-DEC-001-0073: The playbook takes the method lessons of the Customer domain

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-21, for adding the lessons; their wording is Claude's, and the decision owner can change any of it) |
| Date | 2026-10-21 |
| Questions | The method lessons of the Customer domain's pull requests (#327, #329 to #333); the playbook's maintenance rule (EPM-DEC-001-0024) |
| Source | Claude Code session of 2026-10-21 (session 7); `answers-2026-10-21-release-playbook.md` |

## Context

The Customer domain went through six pull requests (EPM-DEC-001-0067 to 0072). Their reviews held them for defects of a few recurring kinds, and the playbook did not yet name a rule that would have prevented each. The decision owner asked for the session's approaches to go into the playbook and reminded Claude of its role. The playbook is the company-neutral method; project decisions go in decision records and the worklog, and the playbook changes only when the method changes (EPM-DEC-001-0024).

## Decision

**The decision owner's request:** "update ontology playbook with new guidline or approach from what we did in this session.. Remember the role of the playbook".

**What follows (Claude):** each lesson goes in the one section a reader would look in, written without project specifics:

1. **Step 5, item 2:** a role held for a period is a node of its own, with a start date, the party and the kind of role.
2. **Step 9, items 8 to 11:** a negative test asserts the violation it means; when a decision fixes a set, the build and the shapes guard the set itself; each guard's reach is stated exactly; a rule over a hierarchy follows the whole chain.
3. **Step 11, items 9 and 10:** every identity link reaches every identity query, and its test pins both IRIs of each pair; the whole check suite runs before a review.
4. **§2, Source of truth and scope:** what is derived from material that cannot be published is marked as fact or reading; a source outside the evidence order guides a reading without supporting it; an uncertain identity is not settled in the data, and an owner's "assume" is recorded as an assumption.
5. **§2, Modules:** two modules that hold the same thing are linked, not merged, with a hand-held match checked by the build where the IRIs differ.
6. **§5.6, Counts:** a sweep searches for the claim, not for the words the change used.
7. **§7:** one paragraph on how the Customer domain ran, naming the review findings that produced these rules.

## Alternatives considered

- **Put the lessons in the worklog only.** Not chosen: the worklog records the project; the next build reads the playbook for the method.
- **Add a separate lessons section.** Not chosen: each rule belongs in the step a reader is following when they need it.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-21-release-playbook.md`: "Please log everything you have done. And update ontology playbook with new guidline or approach from what we did in this session.. Remember the role of the playbook".

## Evidence

- EPM-DEC-001-0024 (the playbook changes only when the method changes).
- The review findings on #329 (the subclass guard), #330 (Q15 and `skos:exactMatch`), #331 (the lifecycle's guards and their stated reach), #332 (the "assume" wording; the missed Questions row) and #333 (the missing evidence tier; a count split across lines), each recorded in its pull request.

## Consequences

- `ontology-playbook.md` carries the rules above. The worklog records this change.
