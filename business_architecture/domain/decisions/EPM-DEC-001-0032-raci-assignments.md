# EPM-DEC-001-0032: The RACI assignments: one per source entry and role, nothing inferred

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-13 |
| Questions | Step 5, slice 3: how the process map's RACI entries become `orgm:ResponsibilityAssignment` nodes, and what the ontology says about processes with no RACI |
| Source | Claude Code session, 2026-10-13, under Hamid's extension of the delegation to Steps 5 to 12 (EPM-DEC-001-0028, amended in #252) |

## Context

EPM-DEC-001-0030 defines the assignment node: exactly one process, role, RACI level and source text, and at least one source. EPM-DEC-001-0031 maps each RACI role string in the process map to one or more roles. The playbook's Step 5 gate reads: every in-scope process has RACI, and none is inferred from the hierarchy.

The process map holds RACI on 153 processes. Two cases need a rule:
- **Compound strings.** One entry can name two or three roles.
- **One role under two strings.** On "Gather Manual Data Inputs" (CM 1.1.2.2.3), the consulted list holds three strings naming Trader and Supply Coordinator, each with a different qualifier (for Petrochemicals, Blendstocks or Feedstocks), plus "Supply Coordinator - Asphalt".

## Decision

1. **One assignment per RACI entry and per role the entry names.** A compound string gives one assignment per role. Two entries that name the same role on the same process and level stay two assignments, because each keeps its own source text and qualifier. A query that asks who holds a level uses `DISTINCT` over process, level and role.
2. **Nothing is inferred.** A process without a `raci` object in the source gets no assignment, even when its parent or child has one.
3. **The IRI** is `…/organization/assignment/{process slug}--{level}--{role slug}--{hash}`, where the hash is the first eight hex digits of the SHA-256 of the source string. Reordering a source list does not change any IRI.
4. **A ledger reconciles the counts.** `raci-conservation.csv` records the RACI entries in and the assignments out, each in total and by level, and the extra roles from compound strings in total. The build fails if entries plus extra roles differ from assignments.
5. **Competency questions 3 to 5 become answerable.** The regression runner loads the organization module with the core release. Two queries must return nothing: an assignment that points outside the core scheme, at a structural anchor or at an unnamed role (Q3), and a process that has RACI but no accountable role (Q4). Structural anchors carry no RACI (the `conceptKind` decision of 2026-09-22 in the worklog), so Q4 leaves them out.

`build_assignments.py` prints the figures.

### RACI scope: decided by Hamid, 2026-10-13

Q4 lists the live concepts of the core scheme with no accountable role, other than structural anchors. They include concepts of kind process, concepts of kind capability, and concepts with no kind. Today that means every live, non-anchor concept without RACI in the source. The Step 5 gate asks for RACI on every **in-scope** process, and no recorded decision says which processes are in scope for RACI.

Claude recommended counting the processes that have RACI in the source as the RACI scope for this release, and treating the rest as the source author's backlog, not as a gap for the ontology to fill. Hamid chose that option (recorded below). So the 153 processes with RACI in the source are this release's RACI scope. Every one has RACI and an accountable role (Q4's must-be-none query), so the Step 5 gate's RACI condition holds. Q4 keeps listing the other live concepts, as the source author's backlog.

## Alternatives considered

- **One assignment per process, level and role.** Rejected: it drops the qualifier of all but one entry, and `orgm:sourceRoleText` allows exactly one value.
- **Inherit RACI from a parent process.** Rejected by the playbook's Step 5 gate.
- **IRIs from the entry's position in its list.** Rejected: a source edit that reorders a list would remint IRIs.

## Hamid's recorded words

Hamid extended the delegation in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12." Hamid did not make the design choices above himself. Claude made them under that delegation, and Hamid can reverse any of them.

Hamid decided the RACI scope himself in the same session (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/raci-scope.md`). Asked which processes need RACI for this release, he chose: "The 153 with source RACI (Recommended)".

## Evidence

`downstream_process_map.json` (`raci` on 153 processes); EPM-DEC-001-0030, 0031; `ontology-playbook.md`, Step 5; `competency-questions.md`, questions 3 to 5.

## Consequences

- `scripts/check.sh` runs `build_assignments.py --verify`, `test_assignments.py` and the regression with the organization module loaded.
- A change to the process map's RACI fails the check until the assignments are rebuilt.
