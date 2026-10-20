# EPM-DEC-001-0056: The lane module: four office lanes, seven placed processes, nothing inherited

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Step 7: lanes (competency question 9); Phase B of EPM-DEC-001-0052; the worklog's data gap that `office_lanes.json` is not linked by ID |
| Source | Claude Code session, 2026-10-19 |

## Context

`business_architecture/business_process/office_lanes.json` defines four lanes, keyed `front_office`, `middle_office`, `back_office` and `operations`, each with a name and a description. Seven process-map nodes, CM 1.2.1 to CM 1.2.7, have an `officeLane` whose value is one of those keys. The worklog notes that the lanes are not declared disjoint and that `office_lanes.json` is not linked by ID.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **A small `lane` module.** The four lanes are a SKOS code list, defined from `office_lanes.json` word for word. `lane:officeLane` links a core process to its lane.
2. **The link is by key.** A node's `officeLane` value is the lane's key, which the build checks; the lane keeps the key as its `skos:notation`. That links the two files.
3. **Nothing is inherited.** Only the seven nodes that name a lane have one. A child of CM 1.2.1 has none, as the RACI assignments inherit nothing from the hierarchy (EPM-DEC-001-0032).
4. **One lane per process.** No node names two, and a shape keeps it so. The lanes are not declared disjoint as classes, because they are concepts, not classes.
5. **Thin lanes are a query.** Front, middle and back office have one process each; operations has four. Competency question 9 is answerable.

## Alternatives considered

- **Lanes as a field of `core`.** Not chosen: a lane is an overlay of the trading organization, and a `core` release would be needed for each change.
- **Inherit a lane down the tree.** Not chosen: the map does not say a lane applies to the children.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/business_process/office_lanes.json`; `business_architecture/business_process/downstream_process_map.json`, `officeLane`; EPM-DEC-001-0032.

## Consequences

- The regression stands at 21 answerable, 6 partial and 17 waiting.
- The module is built and checked by `scripts/check.sh`; it is released only with the decision owner's approval.
