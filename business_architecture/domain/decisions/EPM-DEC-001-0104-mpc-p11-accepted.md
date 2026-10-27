# EPM-DEC-001-0104: MPC-P11 is accepted: the customer processes name the systems they use, with the strong and medium evidence, and the weak links stay out; released as system 1.4.0 and party 1.4.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-26, for accepting the proposal; how it is applied, and the two minor releases, delegated under EPM-DEC-001-0028) |
| Date | 2026-10-26 |
| Questions | Proposal MPC-P11 (`business_architecture/business_process/proposals/MPC-P11-customer-process-systems.md`; EPM-DEC-001-0099, item 11; EPM-DEC-001-0103) |
| Source | Claude Code session of 2026-10-26; `answers-2026-10-26-night.md` |

## Context

The `system` module links a system to a process only where the process map's `systems` field names it (EPM-DEC-001-0055). No customer-lifecycle process named a system, so the lifecycle reached Salesforce, SAP MDG and SAP S/4HANA only through its system stages (EPM-DEC-001-0070). EPM-DEC-001-0103 wrote proposal MPC-P11 from each customer system's role and data flows in `party`, and left it for the decision owner, because a change to the process map needs an accepted proposal (AGENTS.md).

## Decision

**The decision owner's ruling:** accept the proposal's "Proposed (strong and medium evidence)" table, and leave out its "Not proposed (weak evidence)" table.

The table has 18 rows. Two rows name more than one system (CM 1.3.7.1.7 with SAP MDG and MAGIC, and with Salesforce, SAP S/4HANA and RightAngle), so the 16 single-system rows and those two hold 21 links, across 12 processes. The option the decision owner chose said "Add all 19 proposed links"; that count was wrong, and this record counts the links themselves.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **The process map's `systems` field** of each of the 12 processes gains its systems, in `downstream_process_map.json`, under the names the `system` module's register reads: Salesforce, SAP MDG, MAGIC, Bridger Insight, Information Steward, Profisee, Sirion, Customer Portal, SAP S/4HANA and RightAngle.
2. **The `system` module** adds the seven systems the map did not name before: SAP MDG, Salesforce, MAGIC, Bridger Insight, Information Steward, Sirion and Customer Portal. Each takes the slug, label and definition the `party` module already gives it (EPM-DEC-001-0099, 0103), so the two modules describe each system once, in the same words. "SAP S/4HANA" is a new register string for the existing system `sap` (EPM-DEC-001-0099), and Profisee and RightAngle were already in the module.
3. **The weak links stay out:** Allocation Manager for CM 1.3.7.4.3, SAP S/4HANA for CM 1.3.7.4.5 and Data Products IDP for CM 1.3.7.4.4. Each can come back through a new proposal when its owner confirms it.
4. **The proposal's status** becomes Accepted, with this record.
5. **`system` 1.4.0, a minor release,** carries the seven systems and the 21 links. It adds IRIs and removes none, so a minor is enough. It requires core 2.4.0, the current release, which holds all 12 processes (EPM-DEC-001-0105); the `system` build reads 2.4.0 since that release. 39 of its 41 systems are defined, and 306 links reach 162 of the 165 processes with a `systems` field.
6. **`party` 1.4.0, a minor release,** carries seven more `skos:exactMatch` links, one from each of the seven customer systems to the `system` system of the same slug, so 12 customer systems match. The `party` build states a match wherever the `system` module holds a customer system's slug (`party/build_party.py`), so the two releases go together. It requires core 2.4.0 and system 1.4.0. EPM-DEC-001-0105 left the `party` build on core 2.3.0 until party's next release, because its output names the core version; party 1.4.0 is that release, so its build now reads core 2.4.0. The only change in party's output is that name in `lifecycle.ttl`'s header: every lifecycle link's process IRI is in both releases.
7. **party 1.4.0 rewords its one shape message that held an apostrophe,** so no `sh:message` in party's shapes holds one. The rule applies to every module; this record covers party only. EPM-DEC-001-0106 reworded lane's message and records that market-data 1.1.0 still holds one, for its next release. Party's: "A customer system's definition cites its source." becomes "The definition of a customer system cites its source." The meaning does not change. The `ontology` skill's SHACL rule 19 keeps apostrophes out of `sh:message`, because the neosemantics (n10s) validator writes the message into Cypher unescaped (personal-agent-skills #72).
8. **Claude approves both releases under the delegation.** EPM-DEC-001-0028 lets Claude approve the queue's minor releases, and the decision owner's night brief of 2026-10-26, which says Claude approves the night's minor releases, was approved with "Approve (Recommended)" (`answers-2026-10-26-night.md`, block 7).

## Alternatives considered

- **Accept the strong rows only.** Not chosen by the decision owner.
- **Reject the proposal.** Not chosen: the lifecycle would keep reaching its systems only through its system stages.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-26-night.md`, block 2: "Accept strong + medium (Recommended)". For the releases, block 7: "Approve (Recommended)", to a brief that says Claude approves the night's minor releases.

## Evidence

- `business_architecture/business_process/proposals/MPC-P11-customer-process-systems.md`.
- `business_architecture/ontology/party/systems.csv` and `definitions.csv`: each customer system's role and definition.
- EPM-DEC-001-0055, 0069, 0070, 0099, 0103.

## Consequences

- The map change and the new systems ship in `system` 1.4.0 and `party` 1.4.0, in one pull request, each with its release notes.
- The Neo4j projection, rerun on the new releases, has 4,146 nodes and 21,503 relationships from 36,473 triples, with every check passing.
- EPM-DEC-001-0103 carries a dated note.
