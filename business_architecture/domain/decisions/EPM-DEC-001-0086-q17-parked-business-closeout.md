# EPM-DEC-001-0086: Q17 is parked until the ontology is first shared with business consumers; a business close-out package lists what the business must settle

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for parking Q17 and for the package; its contents delegated under EPM-DEC-001-0028; *2026-11-02:* the follow-up release may be cut and shared with Q17 still open, the decision owner's decision, amendment below) |
| Date | 2026-10-23 |
| Questions | Competency question 17, "Who owns the meaning of a concept, and who only stewards the data?" (EPM-DEC-001-0045, decision 7); the items EPM-DEC-001-0083 lists as waiting on a process owner, the business or no named confirmer |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md`; `answers-2026-11-02-q17-release.md` |

## Context

On 2026-10-18 the decision owner chose to settle who owns a concept's meaning through a separate governance decision with explicit assignments, kept apart from process RACI (EPM-DEC-001-0045, decision 7). No source in the repository, and none of MPC's filings, says who owns each concept's meaning, so the assignments have to come from the business. Q17 was the only competency question still waiting (EPM-DEC-001-0083). EPM-DEC-001-0019 counts a question parked by a recorded decision as green.

The decision owner already ruled the same way for four customer-system codes: they are settled when the ontology is shared for consumption, "at which point we will confirm what these means from the business" (EPM-DEC-001-0072, amendment of 2026-10-22).

## Decision

**The decision owner's decision:** Q17 is parked until the ontology is first shared with business consumers, and a package that goes with the ontology lists what to close out with the business.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Q17 is parked.** `regression/expected.csv` gives it the status `parked:EPM-DEC-001-0086`. `regression/run.py` accepts that status, counts it as parked, and fails if a parked question lists a query. The regression now stands at 43 answerable, 0 partial, 0 waiting and 1 parked.
2. **The trigger** is the ontology's first sharing with business consumers. The business then names, for each module or concept scheme, the role that owns the meaning, the role that stewards the data and the role that keeps the systems. A minor release of `organization` then adds the qualified governance assignment that EPM-DEC-001-0045, item 7, proposes, and Q17 gets its queries.
3. **The package is `business_architecture/ontology/business-closeout.md`.** It lists each point only the business can settle: Q17; Market Data's accountable group (EPM-DEC-001-0046); the four codes and TID Nbr (EPM-DEC-001-0069, 0072); the product list (EPM-DEC-001-0088); Forecaster, Crude RFC, PSM and four working role definitions (EPM-DEC-001-0045); and the 33 measures with no stated population (EPM-DEC-001-0062). For each it gives what the ontology holds today, what the business needs to say, who can say it, and the record and module the answer goes to. It also lists, apart, the items parked for reasons that are not the business's.

## Amendment, 2026-10-28: the decision owner works through the package

On 2026-10-26 the decision owner said they might work through some of the package's points first, to narrow them down (EPM-DEC-001-0107). On 2026-10-28 Claude put points 3 to 16 to them, one at a time, each with a recommendation, and asked again about points 1 and 2.

**The decision owner's answers, point by point:**

| Point | Answer | Where it is recorded |
|---|---|---|
| 1, 2 | Both stay open: "Keep both open (Recommended)" | This amendment |
| 3 | The four codes stay undefined, and the point closes: "leave those as undefined for now and close this out" | EPM-DEC-001-0072, amendment of 2026-10-28 |
| 4 | TID Nbr keeps its reading, and the point closes: "Keep reading, close (Recommended)" | EPM-DEC-001-0072, amendment of 2026-10-28 |
| 5 | The products close; the PIDX family letters stay open: "Close products, PIDX open (Recommended)" | EPM-DEC-001-0092, amendment of 2026-10-28 |
| 6 | Forecaster stays apart and the point stays open: "Keep apart, leave open (Recommended)" | This amendment |
| 7 | The Crude RFC reading is confirmed: "Confirm the reading" | EPM-DEC-001-0045, with `organization`'s next minor release (*2026-10-28:* released as organization 2.2.0) |
| 8 | PSM is Process Safety Management: "By the was PSM = Process Safety Management". The decision owner sent it after first choosing to leave the point open | EPM-DEC-001-0045, with `organization`'s next minor release (*2026-10-28:* released as organization 2.2.0) |
| 9 | Business Planning and Analysis's definition is confirmed; the other three stay open: "Confirm 1, rest open (Recommended)" | EPM-DEC-001-0045, with `organization`'s next minor release (*2026-10-28:* released as organization 2.2.0) |
| 10, 12, 13, 14, 16 | Each stays open: "Leave open (Recommended)" | This amendment |
| 11 | Drop Tank, GasBuddy and DTN are to be defined from their vendors' own published words (Drop Tank's from a 2018 press release, its site being gone); Federal Health, and what MPC sends each of the four, stay open: "Define 3, rest open (Recommended)" | EPM-DEC-001-0099, with `party`'s next minor release (*2026-10-28:* released as party 2.1.0) |
| 15 | The decision owner believes Polaris is bought: "I think this is an off the shelf system that offers this service". The point stays open for the vendor and what Polaris does | EPM-DEC-001-0099, with `party`'s next minor release (*2026-10-28:* released as party 2.1.0) |

**What follows (Claude, under EPM-DEC-001-0028):**

- The package marks points 3 and 4 as closed, and point 5 as open for the PIDX letters only. Each row keeps its place, so the numbering does not change.
- Points 7, 8, 9, 11 and 15 change the ontology. Each release's own pull request records its answer on the named record and updates its row in the package. *2026-10-28:* points 7, 8 and 9 are released in `organization` 2.2.0 (EPM-DEC-001-0045, amendment of 2026-10-28).
- The package gains two rows from EPM-DEC-001-0108, which the decision owner cannot answer ("Others I cannot answer."): point 17, how Dealer Master's billing customer number relates to the SAP customer number; and point 18, whether Dealer Master's fuel volumes reach the Enterprise Data Lake.

## Amendment, 2026-11-02: the follow-up release may be cut with Q17 open

The follow-up release (EPM-DEC-001-0112) will be the first time the ontology is shared with business consumers, which is when this record's parking was to end. Asked whether that release may be shared with Q17 still open, the decision owner answered (`answers-2026-11-02-q17-release.md`):

> we will keep Q17 TBD for now.

> yes we can cut the release with Q17 still open. We can add it to the list of open items in the release

So the release may be cut and shared with Q17 still parked, and the regression counts it as before. The release is to ship `OPEN-ITEMS.md`, whose point 1 is Q17, as the list of what the business still has to settle.

## Alternatives considered

- **Build the meaning-owner relation now and assign later.** Not chosen by the decision owner: a relation with no assignments answers nothing, and Q17 would still wait.
- **Assign one meaning owner per module now.** Not chosen by the decision owner: it needs a role for every module from the business, which is the input this record waits for.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "I agree with 1. Can we document this as a package to go with the ontology so that we know what to close out with the business."

For the amendment of 2026-10-28, from `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-28-closeout.md`: "Keep both open (Recommended)", "leave those as undefined for now and close this out", "Keep reading, close (Recommended)", "Close products, PIDX open (Recommended)", "Keep apart, leave open (Recommended)", "Confirm the reading", "By the was PSM = Process Safety Management", "Confirm 1, rest open (Recommended)", "Leave open (Recommended)", "Define 3, rest open (Recommended)" and "I think this is an off the shelf system that offers this service".

## Evidence

- EPM-DEC-001-0019, 0045, 0046, 0062, 0069, 0072, 0083.
- `business_architecture/ontology/competency-questions.md`, question 17.

## Consequences

- Every competency question is answerable or parked by a recorded decision, so Step 11 is all green.
- EPM-DEC-001-0045's item 7, EPM-DEC-001-0083's lists and the regression README carry dated notes.
- When the business answers a point in the package, its answer is recorded as an amendment to the record the package names.
- *2026-10-28:* the decision owner worked through the package; points 3 and 4 are closed, point 5 is narrowed to the PIDX letters, and points 17 and 18 are added (amendment of 2026-10-28 above).
- *2026-10-31:* EPM-DEC-001-0110 plans a release for colleagues outside the build. The first release is validated and not shared; sharing the full version with business consumers is this record's trigger, so Claude asks the decision owner before that zip is shared and records the answer.
