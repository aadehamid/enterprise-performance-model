# EPM-DEC-001-0104: MPC-P11 is accepted: the customer processes name the systems they use, with the strong and medium evidence, and the weak links stay out

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-26, for accepting the proposal; how it is applied delegated under EPM-DEC-001-0028) |
| Date | 2026-10-26 |
| Questions | Proposal MPC-P11 (`business_architecture/business_process/proposals/MPC-P11-customer-process-systems.md`; EPM-DEC-001-0099, item 11; EPM-DEC-001-0103) |
| Source | Claude Code session of 2026-10-26; `answers-2026-10-26-night.md` |

## Context

The `system` module links a system to a process only where the process map's `systems` field names it (EPM-DEC-001-0055). No customer-lifecycle process named a system, so the lifecycle reached Salesforce, SAP MDG and SAP S/4HANA only through its system stages (EPM-DEC-001-0070). EPM-DEC-001-0103 wrote proposal MPC-P11 from each customer system's role and data flows in `party`, and left it for the decision owner, because a change to the process map needs an accepted proposal (AGENTS.md).

## Decision

**The decision owner's ruling:** accept the proposal's "Proposed (strong and medium evidence)" table, and leave out its "Not proposed (weak evidence)" table.

The table has 19 rows. Two rows name more than one system (CM 1.3.7.1.7 with SAP MDG and MAGIC, and with Salesforce, SAP S/4HANA and RightAngle), so the rows hold 21 links, across 12 processes. The question put to the decision owner counted 19 links; this record counts the links themselves.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **The process map's `systems` field** of each of the 12 processes gains its systems, in `downstream_process_map.json`, under the names the `system` module's register reads: Salesforce, SAP MDG, MAGIC, Bridger Insight, Information Steward, Profisee, Sirion, Customer Portal, SAP S/4HANA and RightAngle.
2. **The `system` module** adds the seven systems the map did not name before: SAP MDG, Salesforce, MAGIC, Bridger Insight, Information Steward, Sirion and Customer Portal. Each takes the slug, label and definition the `party` module already gives it (EPM-DEC-001-0099, 0103), so the two modules describe each system once, in the same words. "SAP S/4HANA" is a new register string for the existing system `sap` (EPM-DEC-001-0099), and Profisee and RightAngle were already in the module.
3. **The weak links stay out:** Allocation Manager for CM 1.3.7.4.3, SAP S/4HANA for CM 1.3.7.4.5 and Data Products IDP for CM 1.3.7.4.4. Each can come back through a new proposal when its owner confirms it.
4. **The proposal's status** becomes Accepted, with this record.

## Alternatives considered

- **Accept the strong rows only.** Not chosen by the decision owner.
- **Reject the proposal.** Not chosen: the lifecycle would keep reaching its systems only through its system stages.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-26-night.md`, answer 1: "Accept strong + medium (Recommended)".

## Evidence

- `business_architecture/business_process/proposals/MPC-P11-customer-process-systems.md`.
- `business_architecture/ontology/party/systems.csv` and `definitions.csv`: each customer system's role and definition.
- EPM-DEC-001-0055, 0069, 0070, 0099, 0103.

## Consequences

- The map change and the new systems land in `system`'s next release, through its own pull request and release notes.
- EPM-DEC-001-0103 carries a dated note.
